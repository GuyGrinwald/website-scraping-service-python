import asyncio
import logging
import threading

import aiohttp
from bs4 import BeautifulSoup

from db.job import JobDB
from db.job_result import JobFailedResult, JobResultDB, JobSuccessResult
from infra.AnaplanQueue import AnaplanQueue
from scraper.node import Node
from scraper.url_cache import URLCache
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
        self.url_sanitizer = URLSanitizer()
        self.url_cache = URLCache(URLCache.DEFAULT_CAPACITY)

    async def scrape_url(self, url: str):
        """
        Attempts to scrape the given URL and return a list of children URLs, uses an in-memory cache for optimization
        """
        try:
            children = self.url_cache.get(url)

            if children is not None:
                return children

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.read()
                    soup = BeautifulSoup(html, "html.parser")
                    children = [
                        a.get("href", None) for a in soup.find_all("a", href=True)
                    ]
                    self.url_cache.put(url, children)
                    return children
        except:
            logger.warning(f"Unable to scrape URL: {url}")
            self.url_cache.put(
                url, []
            )  # cache bad result as well to minimize bad searches
            return []

    async def traverse_url(self, url: str, depth: int):
        # Validate that the input URL is valid
        host = self.url_sanitizer.get_hostname(url)
        if not host:
            return {"url": url, "urls": []}

        root = Node(url)
        task = asyncio.create_task(self.scrape_url(root.url))
        stack = [(root, task, 0)]

        while stack:
            current_node, scrape_task, node_depth = stack.pop()
            if node_depth != depth:
                try:
                    child_urls = await scrape_task
                    for child_url in child_urls:
                        child_url = self.url_sanitizer.sanitize_url(host, child_url)
                        if child_url:
                            child_node = Node(child_url)
                            current_node.urls.append(child_node)
                            task = asyncio.create_task(self.scrape_url(child_url))
                            stack.append((child_node, task, node_depth + 1))
                except:
                    logger.warning(f"Unable to process URL: {child_url}")

        return root.urls

    def run(self) -> None:
        loop = asyncio.new_event_loop()

        while True:
            msg = self.in_queue.get(block=True)
            url = msg[URL_REQUEST_PARAM]
            job_id = msg[JOB_ID_REQUEST_PARAM]
            depth = msg[DEPTH_REQUEST_PARAM]

            try:
                self.job_dal.add_job(job_id)
                logger.info("Starting job %s on %s", job_id, msg)

                scrape_results = loop.run_until_complete(self.traverse_url(url, depth))
                logger.info("Parsing job %s completed", job_id)

                self.job_result_dal.put(job_id, JobSuccessResult(url, scrape_results))

            except Exception:
                logger.exception("Job %s failed", job_id)
                self.job_result_dal.put(job_id, JobFailedResult(url))

            finally:
                self.job_dal.remove_job(job_id)
