from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Dict, Optional

from utils.singleton import Singleton, SingletonMeta


class JobResultDBManager:
    __metaclass__ = SingletonMeta

    def get_dal(self):
        return InMemoryJobResultDB()


class JobResult:
    __metaclass__ = ABCMeta

    """
    A data container that holds the results of a scraping job: scraped url, and whether or not the job was successful
    """

    def __init__(self, url: str, success: bool):
        self.url = url
        self.success = success


class JobSuccessResult(JobResult):
    """
    A successful scraping job result. Also holds the scrape results tree
    """

    def __init__(self, url: str, scrape_results: Dict[str]):
        super().__init__(url=url, success=True)
        self.scrape_results = scrape_results


class JobFailedResult(JobResult):
    """
    A failed job result.
    """

    def __init__(self, url: str):
        super().__init__(url=url, success=False)


class JobResultDB:
    __metaclass__ = ABCMeta

    @abstractmethod
    def put(self, job_id: str, job_result: JobResult):
        pass

    @abstractmethod
    def get(self, job_id: str) -> Optional[JobResult]:
        pass


class InMemoryJobResultDB(JobResultDB, Singleton):
    def __init__(self):
        super().__init__()
        self.job_results = {}

    def put(self, job_id: str, job_result: JobResult) -> None:
        self.job_results[job_id] = job_result

    def get(self, job_id: str) -> Optional[JobResult]:
        if job_id not in self.job_results:
            return None

        return self.job_results[job_id]
