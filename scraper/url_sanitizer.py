import logging
from typing import Optional
from urllib.parse import urljoin, urlparse

import utils.logging_config  # isort:skip

logger = logging.getLogger(__name__)


class URLSanitizer:
    def get_hostname(self, url: str) -> str:
        try:
            result = urlparse(url)
            return result.scheme + "://" + result.hostname
        except:
            logger.error(f"Unable to extracte host from URL: {url}")
            return False

    def sanitize_url(self, hostname: str, url: str) -> Optional[str]:
        try:
            result = urlparse(url)
            if not result.scheme or not result.netloc:
                res = hostname
                if result.path:
                    res = (
                        f"{res}/{result.path}"
                        if not result.path.startswith("/")
                        else f"{res}{result.path}"
                    )
                if result.params:
                    res = f"{res};{result.params}"
                if result.query:
                    res = f"{res}?{result.query}"
                if result.fragment:
                    res = f"{res}?{result.fragment}"
                return urljoin(res, ".")
            return urljoin(url, ".")
        except:
            logger.warning(f"URL {url} is not valid")
            return None
