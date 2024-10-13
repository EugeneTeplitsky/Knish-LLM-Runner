from asyncio import Queue
from typing import Any, Callable, Coroutine


class QueueService:
    def __init__(self):
        self.queue = Queue()
        self.current_position = 0
        self.task_positions = {}

    async def enqueue(self, task: Callable[[], Coroutine[Any, Any, Any]]) -> Any:
        position = self.current_position
        await self.queue.put((position, task))
        self.task_positions[position] = True
        self.current_position += 1
        return await self.dequeue()  # Wait for the task to be executed

    async def dequeue(self) -> Any:
        position, task = await self.queue.get()
        try:
            result = await task()
            return result
        finally:
            self.queue.task_done()
            del self.task_positions[position]

    def get_queue_position(self, task_position: int) -> int:
        return sum(1 for pos in self.task_positions if pos < task_position)

    async def run_queue(self):
        while True:
            await self.dequeue()

    def queue_size(self) -> int:
        return self.queue.qsize()


# Create a global instance of QueueService
queue_service = QueueService()
