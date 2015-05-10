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
        assert len(x._queue) == 3
        result = [x.pop()[0] for _ in xrange(len(x._queue))]
        assert result == output, 'Results do not match suggested output'

    for given, out in cases:
        yield test, given, out

def test_priority_dynamic():
    def test(i):
        x = DDPQ()
        # Generate
        for j in xrange(4000):
            x.push(random(), 'Item {}'.format(j))
        # Verify
        last, count = x.pop(), 0
        while len(x):
            assert last[0] < x.peek()[0], '{}: {} >= {}'.format(
                count, last[0], x.peek()[0]
            )
            last = x.pop()
            count += 1

    for i in xrange(5):
        yield test, i

def test_spool_iter_to_file():
    # TODO: improve this test
    x = DDPQ()
    def item_iter():
        for i in xrange(1000):
            yield i, 'Item {}'.format(i)
    result = x._spool_iter_to_file(item_iter())
    assert result.tell() == 25780

def test_length():
    x = DDPQ()
    length = int(random() * 1000)
    for _ in xrange(length):
        x.push(random(), 'Item')
    assert len(x) == length, 'Testing length functionality'

def test_peek():
    def test(with_data):
        x = DDPQ()
        if with_data:
            x.push(0, 'Item')
        try:
            item = x.peek()
        except IndexError:
            return True
        assert item[0] == 0

    for include_data in [True, False]:
        yield test, include_data

def test_clear():
    x = DDPQ()
    for _ in xrange(5):
        x.push(random(), 'Item')
    assert len(x) == 5
    x.clear()
    assert len(x) == 0

# if __name__ == '__main__':
#     tests = [
#         test_priority,
#         test_priority_static,
#         test_priority_dynamic,
#         test_spool_iter_to_file,
#         test_length,
#         test_peek,
#         test_clear
#     ]
#     for test in tests:
#         test_iter = test()
#         if test_iter:
#             for x in test_iter:
#                 x[0](*x[1:])
