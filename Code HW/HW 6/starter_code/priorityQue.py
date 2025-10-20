"""
No task for you here! But if you want to look at an implmentation you can look here!
"""


class MinPriorityQueue:
    """
    There are two structures within this PQ.

    The first is a binary min-heap (stored as a list).
    self.heap is the array representation of your binary min-heap.
    remember, heap[0] contains the key at the ROOT of the heap.
    For any index i , heap[2i + 1] and heap[2i + 2] contain the left and right child of the ith key respectively.
    Remember: parents must have LOWER priorities than their children!


    The second is a hash table mapping elements -> indexes in the heap. This will let us quickly look up elements and
    update their priorities.

    In the context of Dijkstra our "elements" are the names of nodes.
    Our "priorities" are the shortest paths lengths from s to the associated element.
    (Note this is why we only need to have "decreaseKey"! We never make the best known shortest path longer)
    """

    def __init__(self):
        self.heap = []
        self.position_map = {}

    def insert(self, element, priority):
        self.heap.append((element, priority))
        self.position_map[element] = len(self.heap) - 1
        self._push_swap_up(len(self.heap) - 1)

    def minimum(self):
        # Note: we are returning a (element, prioirty) for Dijkstra, so it easy to get the best path length so far
        if not self.heap:
            return None
        return self.heap[0]

    def extract_min(self):
        if not self.heap:
            return None
        min_elem, min_priority = self.heap[0]
        last_index = len(self.heap) - 1
        self._swap(0, last_index)
        self.heap.pop()
        self.position_map.pop(min_elem, None)
        if self.heap:
            self._push_swap_down(0)
        return min_elem, min_priority

    def decrease_key(self, element, new_priority):
        if element not in self.position_map:
            return
        i = self.position_map[element]
        if new_priority >= self.heap[i][1]:
            return
        self.heap[i] = (element, new_priority)
        self._push_swap_up(i)

    @staticmethod
    def _find_parent_index_from_index(i):
        return int((i - 1) / 2)

    def _find_child_indexes_from_index(self, i):
        left = 2 * i + 1
        right = 2 * i + 2
        n = len(self.heap)
        return left if left < n else None, right if right < n else None

    def _push_swap_up(self, i):
        while i > 0:
            p = self._find_parent_index_from_index(i)
            if self.heap[p][1] <= self.heap[i][1]:
                break
            self._swap(i, p)
            i = p

    def _push_swap_down(self, i):
        while True:
            left, right = self._find_child_indexes_from_index(i)
            smallest = i
            if left is not None and self.heap[left][1] < self.heap[smallest][1]:
                smallest = left
            if right is not None and self.heap[right][1] < self.heap[smallest][1]:
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    def _swap(self, i, j):
        if i == j:
            return
        # Get the priority and elements from the heap at the two locations
        ei, pi = self.heap[i]
        ej, pj = self.heap[j]

        # swap them in the heap
        self.heap[i], self.heap[j] = (ej, pj), (ei, pi)

        # swap them in the map
        self.position_map[ei] = j
        self.position_map[ej] = i

