import heapq


class PrioritySet(object):
    def __init__(self):
        self.heap = []
        self.set = set()

    def push(self, d, pri):
        if d not in self.set:
            heapq.heappush(self.heap, (pri, d))
            self.set.add(d)
        # else:
        #     existing_pri, existing_d = heapq.heappop(self.heap)
        #     if existing_pri > pri:
        #         heapq.heappush(self.heap, (pri, d))
        #     else:
        #         heapq.heappush(self.heap, (existing_pri, existing_d))

    def pop(self):
        pri, d = heapq.heappop(self.heap)
        self.set.remove(d)
        return d

    def size(self):
        return len(self.set)
