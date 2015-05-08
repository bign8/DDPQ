from ddpq import DDPQ

def test_priority():
    x = DDPQ()
    x.push(3, 'Third')
    x.push(1, 'First')
    x.push(2, 'Second')
    assert len(x._queue) == 3
    assert x.pop() == (1, 'First')
    assert x.pop() == (2, 'Second')
    assert x.pop() == (3, 'Third')

def test_write():
    # for _ in xrange(1000):
    #     x.push(3, 'Bitches')
    pass
