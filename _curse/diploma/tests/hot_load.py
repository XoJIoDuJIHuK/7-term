import asyncio
import datetime
import logging
import multiprocessing
import random
import statistics
import time
from collections import defaultdict
from functools import wraps

import httpx


logger = logging.getLogger(__name__)


class HotLoad:
    def __init__(
            self,
            duration: datetime.timedelta,
            processes_number: int = 1,
            workers_number: int = 1,
    ):
        self.duration = duration
        self.deadline = datetime.datetime.now() + duration
        self.processes_number = processes_number
        self.workers_number = workers_number

        self.headers = {}
        self.tasks = []
        self.errors = 0  # find usage
        self.on_startup_callable = None
        self.on_teardown_callable = None

    def task(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        self.tasks.append(wrapper)
        return wrapper

    def on_startup(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        self.on_startup_callable = wrapper
        return wrapper

    def on_teardown(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        self.on_teardown_callable = wrapper
        return wrapper

    @staticmethod
    def get_median(results) -> float:
        return statistics.median(results) if results else 0

    @staticmethod
    def get_timestamp_now():
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    async def run_worker(
            self,
            worker_id: int
    ) -> int:
        logger.info('Running worker %s', worker_id)

        stats = defaultdict(list)
        total_requests = 0

        async with httpx.AsyncClient(headers=self.headers) as client:
            while self.deadline > datetime.datetime.now():
                try:
                    start = time.time()
                    await self.tasks[
                        random.randint(0, len(self.tasks) - 1)
                    ](
                        client,
                        worker_id
                    )
                    end = time.time()
                    delta = end - start
                    current_timestamp = self.get_timestamp_now()
                    stats[current_timestamp].append(delta)
                except Exception as e:
                    logger.exception(e)
                    self.errors += 1
                total_requests += 1

        return total_requests

    async def run_workers(self, worker_start_id: int) -> int:
        results = await asyncio.gather(*[
            self.run_worker(worker_id=i + worker_start_id)
            for i in range(self.workers_number)
        ])
        return sum(results)

    def run_process(self, process_number: int, *args) -> int:
        worker_start_id = process_number * self.workers_number

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.run_workers(worker_start_id))
        return result

    async def run(self) -> float:
        if self.on_startup_callable:
            self.headers = await self.on_startup_callable()

        with multiprocessing.Pool(processes=self.processes_number) as pool:
            results = pool.map(self.run_process, range(self.processes_number))
        mean_rps = sum(results) / self.duration.total_seconds()

        if self.on_teardown_callable:
            await self.on_teardown_callable()

        return mean_rps
