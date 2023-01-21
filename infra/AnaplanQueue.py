from __future__ import annotations

import queue
from abc import ABCMeta, abstractmethod

from utils.singleton import Singleton


class AnaplanQueueManager(Singleton):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_queue(
        self, queue_name, queue_class_type=None, max_size=None, block_time=None
    ):
        pass


class InMemoryAnaplanQueueManager(AnaplanQueueManager):
    def __init__(self):
        super(InMemoryAnaplanQueueManager, self).__init__()
        self.queues = {}

    def get_queue(
        self,
        queue_name: str,
        queue_class_type: __class__ = None,
        max_size: int = 0,
        block_time: int = None,
    ) -> AnaplanQueue:
        queue_class = queue_class_type if queue_class_type else InMemoryAnaplanQueue

        if queue_name not in self.queues:
            new_queue = queue_class(queue_name, max_size, block_time)
            self.queues[queue_name] = new_queue

        return self.queues.get(queue_name)


class AnaplanQueue:
    __metaclass__ = ABCMeta

    def get(self, block: bool = False) -> object:
        pass

    def put(self, item: object, block: bool = False) -> None:
        pass

    def size(self) -> int:
        pass

    def is_empty(self) -> bool:
        pass

    def is_full(self) -> bool:
        pass


class InMemoryAnaplanQueue(AnaplanQueue):
    def __init__(self, name: str, max_size: int = 10000, block_time: int = None):
        super().__init__()
        self.name = name
        self.block_time = block_time
        self.queue = queue.Queue(maxsize=max_size)

    def get(self, block: bool = False) -> object:
        return self.queue.get(block, self.block_time)

    def put(self, item: object, block: bool = False) -> None:
        self.queue.put(item, block, self.block_time)

    def size(self) -> int:
        return self.queue.qsize()

    def is_empty(self) -> bool:
        return self.queue.empty()

    def is_full(self) -> bool:
        return self.queue.full()
