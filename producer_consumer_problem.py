import threading
import time
import random
from collections import deque
class BoundedBuffer:
    """A fixed-capacity buffer (queue) shared between producers and consumers."""
    def __init__(self, capacity: int):
        self.buffer = deque()
        self.capacity = capacity
        self.condition = threading.Condition()
    def produce(self, item, producer_name):
        with self.condition:
            # Wait while buffer is full
            while len(self.buffer) >= self.capacity:
                print(f"[{producer_name}] Buffer FULL. Waiting...")
                self.condition.wait()
            self.buffer.append(item)
            print(f"[{producer_name}] Produced: {item} "
                  f"(buffer size = {len(self.buffer)}/{self.capacity})")
            self.condition.notify_all()
    def consume(self, consumer_name):
        with self.condition:
            # Wait while buffer is empty
            while len(self.buffer) == 0:
                print(f"[{consumer_name}] Buffer EMPTY. Waiting...")
                self.condition.wait()
            item = self.buffer.popleft()
            print(f"[{consumer_name}] Consumed: {item} "
                  f"(buffer size = {len(self.buffer)}/{self.capacity})")
            
            self.condition.notify_all()
            return item
def producer_task(buffer: BoundedBuffer, name: str, items_to_produce: int):
    for i in range(items_to_produce):
        item = f"{name}-item-{i}"
        time.sleep(random.uniform(0.05, 0.3))  # simulate work
        buffer.produce(item, name)
def consumer_task(buffer: BoundedBuffer, name: str, items_to_consume: int):
    for _ in range(items_to_consume):
        time.sleep(random.uniform(0.1, 0.4))  # simulate work
        buffer.consume(name)
def main():
    BUFFER_CAPACITY = 5
    ITEMS_PER_PRODUCER = 8
    NUM_PRODUCERS = 2
    NUM_CONSUMERS = 2
    buffer = BoundedBuffer(BUFFER_CAPACITY)
    threads = []
    for p in range(NUM_PRODUCERS):
        t = threading.Thread(
            target=producer_task,
            args=(buffer, f"Producer-{p+1}", ITEMS_PER_PRODUCER),
            name=f"Producer-{p+1}",
        )
        threads.append(t)
    total_items = NUM_PRODUCERS * ITEMS_PER_PRODUCER
    items_per_consumer = total_items // NUM_CONSUMERS
    for c in range(NUM_CONSUMERS):
        t = threading.Thread(
            target=consumer_task,
            args=(buffer, f"Consumer-{c+1}", items_per_consumer),
            name=f"Consumer-{c+1}",
        )
        threads.append(t)
    print(f"Starting {NUM_PRODUCERS} producer(s) and {NUM_CONSUMERS} "
          f"consumer(s) with buffer capacity {BUFFER_CAPACITY}\n")
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("\nAll producers and consumers have finished.")
    print(f"Final buffer contents: {list(buffer.buffer)}")
if __name__ == "__main__":
    main()
