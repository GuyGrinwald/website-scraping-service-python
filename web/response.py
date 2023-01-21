class ParseResponse(object):
    STATUS_MESSAGE = "Job created"
    status = 200

    def __init__(self, job_id):
        self.job_id = job_id
        self.data = {"job_id": job_id, "status_message": ParseResponse.STATUS_MESSAGE}


class JobCompletedSuccessfully(object):
    STATUS_MESSAGE = "Job done"
    status = 200

    def __init__(self, job_id, url, scrape_results):
        self.job_id = job_id
        self.results = {"url": url, "urls": scrape_results}
        self.data = {
            "job_id": self.job_id,
            "results": self.results,
            "status_message": JobCompletedSuccessfully.STATUS_MESSAGE,
        }


class JobInProgress(object):
    STATUS_MESSAGE = "Job in Progress"
    status = 206

    def __init__(self, job_id):
        self.job_id = job_id
        self.data = {
            "job_id": self.job_id,
            "status_message": JobInProgress.STATUS_MESSAGE,
        }


class InvalidRequest(object):
    ERROR = "Invalid request"
    status = 400

    def __init__(self):
        self.data = {"error": InvalidRequest.ERROR}


class NonJsonRequestRequest(InvalidRequest):
    ERROR = "The server only accepts application/json content typed requests"

    def __init__(self):
        super().__init__()
        self.data = {"error": NonJsonRequestRequest.ERROR}


class NotFound(object):
    ERROR = "Job not found"
    status = 404

    def __init__(self, job_id):
        self.job_id = job_id
        self.data = {"error": NotFound.ERROR, "job_id": job_id}


class GeneralError(object):
    ERROR = "An error has occurred"
    status = 500

    def __init__(self):
        self.data = {"error": GeneralError.ERROR}


class JobFailed(GeneralError):
    ERROR = "Scraping job has failed"

    def __init__(self):
        super().__init__()
        self.data = {"error": JobFailed.ERROR}
