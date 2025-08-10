import logging
import requests
from urllib.parse import urlparse, urljoin

logger = logging.getLogger()

class URLResolver:
    _cache = {}

    @classmethod
    def get_base_url(cls, url):
        if url not in cls._cache:
            parsed = urlparse(url)
            cls._cache[url] = f"{parsed.scheme}://{parsed.netloc}"
        return cls._cache[url]

def safe_get(url, timeout=30):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }
    
    try:
        resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
        return resp
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

def build_full_url(base_url, href):
    return urljoin(base_url, href)
