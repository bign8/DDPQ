import tempfile, heapq, pickle, threading


DELTA = 900
TARGET = 1000
INFINITE = float("inf")


def _data_from_file(f):
    if not f:
        raise StopIteration
    f.seek(0)
    try:
        while True:
            yield pickle.load(f)
    except EOFError:
        raise StopIteration


def _data_from_heap(heap):
    while len(heap):
        yield heapq.heappop(heap)
    raise StopIteration


class DiskDeferredPriorityQueue:
    def __init__(self, queue=[]):
        self._queue = queue[:]
        self._latent_queue = []
        heapq.heapify(self._queue)
        self._size = 0
        self._file = None
        self._best_stored_item = INFINITE
        self._queue_lock = threading.RLock()
        self._check(len(self._queue))

    def __len__(self):
        return self._size

    def push(self, key, item):
        self._queue_lock.acquire()
        if key < self._best_stored_item:
            heapq.heappush(self._queue, (key, item))
        else:
            heapq.heappush(self._latent_queue, (key, item))
        self._check(1)
        self._queue_lock.release()

    def pop(self):
        self._queue_lock.acquire()
        item = heapq.heappop(self._queue)
        self._check(-1)
        self._queue_lock.release()
        return item

    def peek(self):
        if not self._size:
            raise IndexError
        return self._queue[0]

    def clear(self):
        self._queue_lock.acquire()
        self._size = 0
        self._best_stored_item = INFINITE
        self._file = None
        self._queue = []
        self._latent_queue = []
        self._queue_lock.release()

    def _check(self, delta):
        self._queue_lock.acquire()
        self._size += delta
        mem_size = len(self._queue)
        if mem_size > TARGET + DELTA:
            self._purge()
        elif len(self._latent_queue) > TARGET:
            self._latent_purge()
        elif mem_size < (TARGET - DELTA) and self._file:
            self._marshal()
        self._queue_lock.release()

    def _purge(self):
        self._queue_lock.acquire()
        queue = []
        for _ in xrange(min(TARGET - DELTA, len(self._queue))):
            heapq.heappush(queue, heapq.heappop(self._queue))
        to_store = self._queue
        self._queue = queue
        self._queue_lock.release()

        # File access (threaded out?)
        data_iter = heapq.merge(
            _data_from_file(self._file),
            _data_from_heap(to_store),
            _data_from_heap(self._latent_queue)  # cleans out latest_queue
        )
        self._file = self._spool_iter_to_file(data_iter)

    def _latent_purge(self):
        # File access (threaded out?)
        data_iter = heapq.merge(
            _data_from_file(self._file),
            _data_from_heap(self._latent_queue)  # cleans out latest_queue
        )
        self._file = self._spool_iter_to_file(data_iter)

    def _marshal(self):
        # File access (threaded out?)
        disk_data = []
        file_iter = heapq.merge(
            _data_from_file(self._file),
            _data_from_heap(self._latent_queue)  # cleans out latest_queue
        )
        try:
            for _ in xrange(TARGET):
                disk_data.append(file_iter.next())
        except StopIteration:
            pass
        self._file = self._spool_iter_to_file(file_iter)
        # END file access

        self._queue_lock.acquire()
        self._queue = list(
            heapq.merge(_data_from_heap(self._queue), disk_data)
        )
        self._queue_lock.release()

    def _spool_iter_to_file(self, data_iter):
        self._best_stored_item = INFINITE
        result, buffer = None, []

        try:
            peek = data_iter.next()
            buffer.append(pickle.dumps(peek))
            self._best_stored_item = peek[0]
            result = tempfile.TemporaryFile()
        except StopIteration:
            return None

        for x in data_iter:
            buffer.append(pickle.dumps(x))
            if len(buffer) >= TARGET:
                result.write(''.join(buffer))
                del buffer[:]
        if buffer:
            result.write(''.join(buffer))
        return result
