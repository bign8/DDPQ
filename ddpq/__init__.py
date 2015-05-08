"""
Disk Deferred Priority Queue

# Sources:
http://neopythonic.blogspot.com/2008/10/sorting-million-32-bit-integers-in-2mb.html
https://docs.python.org/2/library/heapq.html
http://stackoverflow.com/a/5508707/3220865
https://docs.python.org/2/library/tempfile.html
http://stackoverflow.com/a/3954627/3220865

# TODO:
- Make thread safe
- Use separate threads for reading and writing from file (as to not block)
"""

from ddpq.queue import DiskDeferredPriorityQueue
DDPQ = DiskDeferredPriorityQueue
