from abc import ABCMeta, abstractmethod
from typing import Set

from utils.singleton import Singleton, SingletonMeta


class JobDBManager:
    __metaclass__ = SingletonMeta

    def get_dal(self):
        return InMemoryJobDB()


class JobDB:
    __metaclass__ = ABCMeta

    @abstractmethod
    def add_job(self, job_id: str) -> None:
        pass

    @abstractmethod
    def remove_job(self, job_id: str) -> None:
        pass

    @abstractmethod
    def job_in_progress(self, job_id: str) -> bool:
        pass


class InMemoryJobDB(JobDB, Singleton):
    def __init__(self):
        super().__init__()
        self.jobs: Set[str] = set()

    def add_job(self, job_id: str) -> None:
        self.jobs.add(job_id)

    def remove_job(self, job_id: str) -> None:
        self.jobs.remove(job_id)

    def job_in_progress(self, job_id: str) -> bool:
        return job_id in self.jobs
