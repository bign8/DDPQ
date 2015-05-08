# DDPQ [![Build Status](https://travis-ci.org/bign8/DDPQ.svg?branch=master)](https://travis-ci.org/bign8/DDPQ)
Disk Deferred Priority Queue in Python

## Reasons
Have you ever wanted to search through a space of `2^30` nodes but found your regular A* search algorithm overfilled memory?
Well grieve no more, as the disk deferred priority queue is here and ready for business!

### TODO

- Actually test this thing
- Add other Disk Deferred data structures
  - Stack, Queue, DeQueue, etc...
- Have some fun!!!
- Cover with some generative tests
- Track minimum value on disk
  - Maintain second queue of items that are not good enough for tail of queue in memory

### Structure operation Descriptions

#### Stack
Insertion: Once an upper threshold is reached on the size of the stack in memory, the bottom is written to disk.
Removal: Once a lower threshold is reached on the size of the stack in memory, the last page of items is read from disk and appended to the end of the stack.
Inner-workings: a stack of temporary files is kept, as the reading to/from disk occurs in a regular order

#### Queue
Contains a queue of queues or temporary files.
The first and last queues in the list are always in memory queues, the remaining items in the queue are temporary files.
Initially these queues are the same, but if the tail (insertion) queue grows too large, then it is written to disk and is inserted into the master queue, followed by a new empty queue.
Similarily on the front of the master queue, if the queue grows too small, then the next queue is read from file and appended to the original queue.
The edge case here is when going from a single queue in memory to an input-temporary-output queue in memory.

#### DeQueue
Same as queue where growing and shrinking conditions appear on both sides of the queue.

#### Priority queue
Here a single file based priority queue is maintained in valid order along with two in memory queues.
As the in memory queue grows too large, the tail is lopped off and written to disk.
Conversley, once the in memory queue reaches a lower threshold, the head of the file is read from disk and is merged with the in memory queue.
The edge case here is what happens when an item comes in with a worse priority than the best priority written to disk.
In this case, the second memory based priority queue is used to store the elements that need to be merged to the disk based queue.
Once this queue reaches a target size it is merged with disk based queue.
Also note, that due to way `heapq.merge` works, we can simply include this in any of our memory based iterators where we merge using external memory and these item should automatically fall into their appropriate places.
