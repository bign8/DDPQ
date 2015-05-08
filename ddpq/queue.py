import sys, array, tempfile, heapq, pickle, threading
from itertools import chain


DELTA = 900
TARGET = 1000


def _data_from_file(f):
    if not f:
        raise StopIteration
    f.seek(0)
    try:
        while True:
            yield pickle.dump(f)
    except EOFError:
        raise StopIteration


class DiskDeferredPriorityQueue:
    def __init__(self, queue=[]):
        self._queue = queue[:]
        heapq.heapify(self._queue)
        self._size = 0
        self._mem_size = 0
        self._queue_lock = threading.RLock()
        self._file = None
        self._check(len(self._queue))

    def __len__(self):
        return self._size

    def push(self, key, item):
        self._queue_lock.acquire()
        heapq.heappush(self._queue, (key, item))
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
        self._mem_size = 0
        self._file = None
        self._queue = []
        self._queue_lock.release()

    def _check(self, delta):
        self._queue_lock.acquire()
        self._size += delta
        self._mem_size += delta
        if self._mem_size > TARGET + DELTA:
            self._purge()
        elif self._mem_size < (TARGET - DELTA) and self._file:
            self._marshal()
        self._queue_lock.release()

    def _purge(self):
        self._queue_lock.acquire()
        to_store = self._queue[TARGET:]
        self._queue = self._queue[:TARGET]
        self._queue_lock.release()

        # File access (threaded out?)
        data_iter = heapq.merge(_data_from_file(self._file), to_store)
        self._file = self._spool_iter_to_file(data_iter)

    def _marshal(self):
        # File access (threaded out?)
        disk_data = []
        file_iter = _data_from_file(self._file)
        try:
            for _ in xrange(TARGET):
                disk_data.append(file_iter.next())
            # ensure we aren't perfectly at end of file
            test = file_iter.next()
            file_iter = chain([test], file_iter)
        except StopIteration:
            pass
        self._file = self._spool_iter_to_file(file_iter)
        # END file access

        self._queue_lock.acquire()
        self._queue = heapq.merge(self._queue, disk_data)
        self._queue_lock.release()

    def _spool_iter_to_file(data_iter):
        buffer = []
        result = tempfile.TemporaryFile()
        for x in data_iter:
            buffer.append(pickle.dumps(x))
            if len(buffer) >= TARGET:
                result.write(''.join(buffer))
                del buffer[:]
        if buffer:
            result.write(''.join(buffer))
        return result if result.tell() else None
