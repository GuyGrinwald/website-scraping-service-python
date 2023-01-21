import logging
import threading

import bs4
import requests

from db.job import JobDB
from db.job_result import JobFailedResult, JobResultDB, JobSuccessResult
from infra.AnaplanQueue import AnaplanQueue
from utils.constants import DEPTH_REQUEST_PARAM, JOB_ID_REQUEST_PARAM, URL_REQUEST_PARAM


class UrlScraper(threading.Thread):
    def __init__(
        self, in_queue: AnaplanQueue, job_dal: JobDB, job_result_dal: JobResultDB
    ):
        super().__init__()
        self.in_queue = in_queue
        self.job_dal = job_dal
        self.job_result_dal = job_result_dal

    def scrape_url(self, url: str, depth: int):

        #####
        # Your code here - add logic that does the actual scraping. You can add additional functions as needed.
        ####

        return {}

    def run(self) -> None:
        while True:
            msg = self.in_queue.get()
            url = msg[URL_REQUEST_PARAM]
            job_id = msg[JOB_ID_REQUEST_PARAM]
            depth = msg[DEPTH_REQUEST_PARAM]

            try:
                self.job_dal.add_job(job_id)
                logging.info("Starting job %s on %s", job_id, msg)

                scrape_results = self.scrape_url(url, depth)
                logging.info("Parsing job %s completed", job_id)

                self.job_result_dal.put(job_id, JobSuccessResult(url, scrape_results))

            except Exception:
                logging.exception("Job %s failed", job_id)
                self.job_result_dal.put(job_id, JobFailedResult(url))

            finally:
                self.job_dal.remove_job(job_id)
