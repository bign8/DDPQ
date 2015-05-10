from ddpq import DDPQ
from random import random

def test_priority():
    x = DDPQ()
    x.push(3, 'Third')
    x.push(1, 'First')
    x.push(2, 'Second')
    assert len(x._queue) == 3
    assert x.pop() == (1, 'First')
    assert x.pop() == (2, 'Second')
    assert x.pop() == (3, 'Third')

def test_priority_static():
    cases = [
        [[1, 2, 3], [1, 2, 3]],
        [[1, 3, 2], [1, 2, 3]],
        [[2, 1, 3], [1, 2, 3]],
        [[2, 3, 1], [1, 2, 3]],
        [[3, 1, 2], [1, 2, 3]],
        [[3, 2, 1], [1, 2, 3]],
    ]

    def test(given, output):
        x = DDPQ()
        for item in given:
            x.push(item, 'Item {}'.format(item))
        print x._queue
        assert len(x._queue) == 3
        result = [x.pop()[0] for _ in xrange(len(x._queue))]
        assert result == output, 'Results do not match suggested output'

    for given, out in cases:
        yield test, given, out

def test_priority_dynamic():
    def test(i):
        x = DDPQ()
        # Generate
        for j in xrange(int(4000)):
            x.push(random(), 'Item {}'.format(j))
        # Verify
        last, count = x.pop(), 0
        while len(x):
            assert last[0] < x.peek()[0], '{}: {} >= {}'.format(
                count, last[0], x.peek()[0]
            )
            last = x.pop()
            count += 1

    for i in xrange(10):
        yield test, i

def test_length():
    x = DDPQ()
    length = int(random() * 1000)
    for _ in xrange(length):
        x.push(random(), 'Item')
    assert len(x) == length, 'Testing length functionality'
