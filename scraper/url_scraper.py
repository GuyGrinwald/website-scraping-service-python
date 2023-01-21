import logging
import threading
from functools import cache

import requests
from bs4 import BeautifulSoup

from db.job import JobDB
from db.job_result import JobFailedResult, JobResultDB, JobSuccessResult
from infra.AnaplanQueue import AnaplanQueue
from scraper.node import Node
from scraper.url_sanitizer import URLSanitizer
from utils.constants import DEPTH_REQUEST_PARAM, JOB_ID_REQUEST_PARAM, URL_REQUEST_PARAM

import utils.logging_config  # isort:skip

logger = logging.getLogger(__name__)


class UrlScraper(threading.Thread):
    def __init__(
        self, in_queue: AnaplanQueue, job_dal: JobDB, job_result_dal: JobResultDB
    ):
        super().__init__()
        self.in_queue = in_queue
        self.job_dal = job_dal
        self.job_result_dal = job_result_dal

    @cache
    def scrape_url(self, url: str):
        """
        Attempts to scrape the given URL and return a list of children URLs, uses an in-memory cache for optimization
        """
        try:
            req = requests.get(url, timeout=5)
            soup = BeautifulSoup(req.content, "html.parser")
            return [a.get("href", None) for a in soup.find_all("a", href=True)]
        except:
            logger.warning(f"Unable to scrape URL: {url}")
            return []

    def build_res_tree(self, root: Node) -> dict:
        """
        Recursively iterate over a Node tree and collect the URLs in it to a dictionary
        """
        res = {"url": root.url, "urls": []}

        if not root.children:
            return res

        for child in root.children:
            res["urls"].append(self.build_res_tree(child))

        return res

    def traverse_url(self, url: str, depth: int):
        url_sanitizer = URLSanitizer()

        # Validate that the input URL is valid
        host = url_sanitizer.get_hostname(url)
        if not host:
            return {"url": url, "urls": []}

        root = Node(url)
        stack = [(root, 0)]

        while stack:
            current_node, url_depth = stack.pop()
            if url_depth != depth:
                try:
                    children = self.scrape_url(current_node.url)
                    for child in children:
                        child = url_sanitizer.sanitize_url(host, child)
                        if child:
                            child_node = Node(child)
                            current_node.children.append(child_node)
                            stack.append((child_node, url_depth + 1))
                except:
                    logger.exception(f"Unable to scrape URL: {url}")

        return self.build_res_tree(root)

    def run(self) -> None:
        while True:
            msg = self.in_queue.get(block=True)
            url = msg[URL_REQUEST_PARAM]
            job_id = msg[JOB_ID_REQUEST_PARAM]
            depth = msg[DEPTH_REQUEST_PARAM]

            try:
                self.job_dal.add_job(job_id)
                logger.info("Starting job %s on %s", job_id, msg)

                scrape_results = self.traverse_url(url, depth)
                logger.info("Parsing job %s completed", job_id)

                self.job_result_dal.put(job_id, JobSuccessResult(url, scrape_results))

            except Exception:
                logger.exception("Job %s failed", job_id)
                self.job_result_dal.put(job_id, JobFailedResult(url))

            finally:
                self.job_dal.remove_job(job_id)
