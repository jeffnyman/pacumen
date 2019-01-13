import heapq


class Node:
    """
    Represents a node context, which means a particular state. Also included
    is the priority value of that state and the path to the node.
    """
    def __init__(self, state, path=None, priority=0):
        if path is None:
            path = []

        self.state = state
        self.path = path
        self.priority = priority

    def __repr__(self):
        return "({0},{1},{2})".format(self.state, self.path, self.priority)


class Stack:
    """
    A container with a last-in-first-out (LIFO) queuing policy.
    """
    def __init__(self):
        self.list = []

    def push(self, item):
        self.list.append(item)

    def pop(self):
        return self.list.pop()

    def is_empty(self):
        return len(self.list) == 0


class Queue:
    """
    A container with a first-in-first-out (FIFO) queuing policy.
    """
    def __init__(self):
        self.list = []

    def push(self, item):
        self.list.insert(0, item)

    def pop(self):
        return self.list.pop()

    def is_empty(self):
        return len(self.list) == 0


class PriorityQueue:
    """
    Implements a priority queue data structure. Each inserted item
    has a priority associated with it and the client is usually interested
    in quick retrieval of the lowest-priority item in the queue.
    """
    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def is_empty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        """
        If item already in priority queue with higher priority, update its priority and rebuild the heap.
        If item already in priority queue with equal or lower priority, do nothing.
        If item not in priority queue, do the same thing as self.push.
        """
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)


class StaticPriorityQueue:
    """
    Implements a priority queue similar to the above implementation but
    simpler in that this queue does not allow you to change the priority
    of an item. You are able to insert the same item multiple times with
    different priorities.
    """
    def __init__(self):
        self.heap = []

    def push(self, item, priority):
        pair = (priority, item)
        heapq.heappush(self.heap, pair)

    def pop(self):
        (priority, item) = heapq.heappop(self.heap)
        return priority, item

    def is_empty(self):
        return len(self.heap) == 0


class PriorityQueueWithFunction(PriorityQueue):
    """
    Implements a priority queue with the same push/pop signature of the
    Queue and the Stack classes. This is designed for drop-in replacement for
    those two classes. The caller has to provide a priority function, which
    extracts each item's priority.
    """
    def __init__(self, priority_function):
        self.priority_function = priority_function
        PriorityQueue.__init__(self)

    def push(self, item, priority=None):
        """
        Adds an item to the queue with priority from the priority function.
        """
        PriorityQueue.push(self, item, self.priority_function(item))
