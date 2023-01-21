import logging
import uuid

from flask import Flask, request

import settings
from db.job import JobDBManager
from db.job_result import JobFailedResult, JobResultDBManager
from infra.AnaplanQueue import InMemoryAnaplanQueueManager
from scraper.url_scraper import UrlScraper
from utils.constants import (
    DEPTH_REQUEST_PARAM,
    JOB_ID_REQUEST_PARAM,
    URL_MAPPER_QUEUE,
    URL_REQUEST_PARAM,
)
from web.response import (
    GeneralError,
    InvalidRequest,
    JobCompletedSuccessfully,
    JobFailed,
    JobInProgress,
    NonJsonRequestRequest,
    NotFound,
    ParseResponse,
)

import utils.logging_config  # isort:skip

logger = logging.getLogger(__name__)

app = Flask(__name__)

queue_manager = InMemoryAnaplanQueueManager()
job_result_db_factory = JobResultDBManager()
job_db_factory = JobDBManager()


@app.route("/api/v1/jobs", methods=["POST"])
def create_scraping_job():
    url_request_data = request.get_json()
    logger.info("Creating new url scraping request %s", url_request_data)

    # validate required params exist
    if not _validate_parse_request(url_request_data):
        logger.warning("Request %s is invalid", url_request_data)
        ir_response = InvalidRequest()
        return ir_response.data, ir_response.status

    job_id = uuid.uuid4().hex
    logger.info("Creating new job %s for scraping request %s", job_id, url_request_data)
    url_request_data[JOB_ID_REQUEST_PARAM] = job_id
    url_mapper_queue.put(url_request_data)

    pr_response = ParseResponse(job_id)
    return pr_response.data, pr_response.status


@app.route("/api/v1/jobs/<job_id>", methods=["GET"])
def job_status(job_id):
    logger.info("Checking job %s status", job_id)

    url_dal = job_result_db_factory.get_dal()
    jobs_dal = job_db_factory.get_dal()

    job_results = url_dal.get(job_id)

    if job_results:
        logger.info("Found scraping results for job %s", job_id)

        # handle failures by translating the job result to an error response
        if isinstance(job_results, JobFailedResult):
            failed_response = JobFailed()
            return failed_response.data, failed_response.status

        # job is successful - build a response from the scraping results
        jr_response = JobCompletedSuccessfully(
            job_id, job_results.url, job_results.scrape_results
        )
        return jr_response.data, jr_response.status

    elif jobs_dal.job_in_progress(job_id):
        logger.info("Job %s is still in progress", job_id)
        jip_response = JobInProgress(job_id)
        return jip_response.data, jip_response.status

    logger.warning("Couldn't find job %s", job_id)
    nf_response = NotFound(job_id)
    return nf_response.data, nf_response.status


# Global request preprocess - makes sure we accept only json requests
@app.before_request
def only_json():
    if not request.is_json:
        njr_response = NonJsonRequestRequest()
        return njr_response.data, njr_response.status


# Global general error handler - makes every 500 error formatted as json
@app.errorhandler(GeneralError.status)
def handle_invalid_usage(error):
    ge_response = GeneralError()
    return ge_response.data, ge_response.status


def _validate_parse_request(url_parse_request):
    """
    Validates that the given url parsing request content holds all relevant params (dpeth and url) and that the depth is
    a positive integer
    """
    try:
        return (
            URL_REQUEST_PARAM in url_parse_request
            and DEPTH_REQUEST_PARAM in url_parse_request
            and isinstance(url_parse_request[DEPTH_REQUEST_PARAM], int)
            and int(url_parse_request[DEPTH_REQUEST_PARAM]) > 0
        )
    except ValueError:
        return False


if __name__ == "__main__":
    url_mapper_queue = queue_manager.get_queue(URL_MAPPER_QUEUE)
    jobs_dal = job_db_factory.get_dal()
    job_results_dal = job_result_db_factory.get_dal()

    logger.info("Starting UrlMapper worker")
    url_mapper = UrlScraper(url_mapper_queue, jobs_dal, job_results_dal)
    url_mapper.start()

    # Runs the app with dev server, on prod this will run through some wsgi (e.g. waitress or gunicorn)
    app.run(port=settings.APP_PORT)
