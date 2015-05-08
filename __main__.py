from queue import DiskDeferredPriorityQueue


DDPQ = DiskDeferredPriorityQueue


if __name__ == '__main__':
    x = DDPQ()
    for _ in xrange(1000):
        x.push(3, 'Bitches')
    print 'Write to disk mother fucker', x._file
    x.push(2, 'Nate')
    x.push(1, 'Bitches')
    x.push(2, 'Nate')
    print x._queue
