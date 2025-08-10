import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import feedparser

from utils import safe_get, URLResolver, build_full_url
import re

logger = logging.getLogger()

# Updated CSS selectors per forum snippet
THREAD_LIST_ITEM_SELECTOR = "li.topic"               # Thread container selector
THREAD_TITLE_SELECTOR = "a.thread_title_link"         # Thread URL link inside thread container
THREAD_UNIQUE_ID_ATTR = "data-thread-id"             # Thread unique ID attribute on <li>
POST_CONTAINER_SELECTOR = "div.message-inner"        # Each post container inside threads
POST_BODY_SELECTOR = "div.bbWrapper"                  # Post content wrapper
NEXT_PAGE_SELECTOR = "a.pageNav-jump--next"          # Selector for pagination next page

def parse_post_date(post_soup):
    time_tag = post_soup.find("time")
    if time_tag and time_tag.has_attr("datetime"):
        dt_str = time_tag["datetime"]
        try:
            return datetime.fromisoformat(dt_str.rstrip('Z'))
        except Exception as e:
            logger.debug(f"Failed to parse datetime {dt_str}: {e}")
    return None

def scan_simple_page(url, keywords, seen):
    hits = []
    base_url = URLResolver.get_base_url(url)
    logger.info(f"Scanning simple page: {url}")
    resp = safe_get(url)
    if resp is None:
        logger.warning(f"Failed to fetch page: {url}")
        return hits

    soup = BeautifulSoup(resp.content, "html.parser")
    for post in soup.find_all("a", href=True, text=True):
        href = post["href"]
        if href in seen:
            logger.debug(f"Already seen link: {href}")
            continue
        text = post.get_text().lower()
        for keyword in keywords:
            if keyword.lower() in text:
                full_url = build_full_url(base_url, href)
                hit_msg = f"Found '{keyword}' at [{full_url}]({full_url})"
                logger.info(f"Keyword match: {hit_msg}")
                hits.append(hit_msg)
                seen.add(href)
                break
    logger.info(f"Finished scanning simple page: {url}, found {len(hits)} hits")
    return hits

def fetch_posts_from_thread(thread_url, keywords, seen, max_thread_pages=5, css_params={}):
    hits = []
    page_url = thread_url
    pages_crawled = 0

    logger.info(f"Fetching posts from thread: {thread_url}")
    # while page_url and pages_crawled < max_thread_pages:
    logger.debug(f"Fetching thread page: {page_url} (page {pages_crawled+1})")
    resp = safe_get(page_url)
    if resp is None:
        logger.warning(f"Failed to fetch thread page: {page_url}")
        return hits #break
    soup = BeautifulSoup(resp.content, "html.parser")

    posts = soup.select(css_params["POST_CONTAINER_SELECTOR"])
    logger.debug(f"Found {len(posts)} posts on page {page_url}")
    # if posts:
    #     post = posts[0]
    for post in posts:
        unique_id = post.select_one("div.post_content").get("id")[len("post_content"):]
        unique_url = build_full_url(page_url,"#p"+unique_id)
        logger.debug(f"Processing post with unique ID: {unique_id}")
        if not unique_url or unique_url in seen:
            logger.debug(f"Skipping post with id {unique_id} (already seen or missing)")
            # continue

        post_body_el = post.select_one(css_params["POST_BODY_SELECTOR"])
        logger.debug(f"Post body element found: {post_body_el is not None}")
        if not post_body_el:
            logger.debug(f"No post body found for post id {unique_id}")
            # continue

        text = post_body_el.get_text(separator=" ", strip=True).lower()
        # Split on any non-word character (punctuation, slashes, etc.)
        words = re.split(r"[^\w]+", text)
        logger.debug(f"post text: {text[:100]}... (truncated for debug)")
        for keyword in keywords:
            if keyword.lower() in words:
                hit_msg = f"Found '{keyword}' in post {unique_url}"
                logger.info(f"Keyword match: {hit_msg}")
                hits.append(hit_msg)
                seen.add(unique_url)
                break

        # next_link = soup.select_one(css_params["NEXT_PAGE_SELECTOR"])
        # if next_link and "href" in next_link.attrs:
        #     page_url = build_full_url(page_url, next_link["href"])
        #     pages_crawled += 1
        #     logger.debug(f"Moving to next thread page: {page_url}")
        # else:
        #     page_url = None

    logger.info(f"Finished fetching thread: {thread_url}, found {len(hits)} hits")
    return hits

def crawl_and_search_threads(forum_section_url, keywords, seen, visited_threads, max_forum_pages=3, max_thread_pages=5, css_params={}):
    hits = []
    current_page_url = forum_section_url
    pages_checked = 0

    logger.info(f"Starting crawl of forum section: {forum_section_url}")
    while current_page_url and pages_checked < max_forum_pages:
        logger.debug(f"Fetching forum page: {current_page_url} (page {pages_checked+1})")
        resp = safe_get(current_page_url)
        if resp is None:
            logger.warning(f"Failed to fetch forum page: {current_page_url}")
            break
        soup = BeautifulSoup(resp.content, "html.parser")

        threads = soup.select(css_params["THREAD_LIST_ITEM_SELECTOR"])
        logger.debug(f"Found {len(threads)} threads on forum page {current_page_url}")
        for thread in threads:
            thread_soup = BeautifulSoup(str(thread), "html.parser")
            logger.debug(f"Processing thread: {thread_soup}")
            # thread_id = thread.get(css_params["THREAD_UNIQUE_ID_ATTR"])
            thread_id = thread.get('href','').rstrip('/')[-7:]
            # thread_link = thread.select_one(css_params["THREAD_TITLE_SELECTOR"])
            thread_link = thread.get('href','')
            logger.debug(f"thread_id: {thread_id}")
            logger.debug(f"thread_link: {thread_link}")

            if not thread_link or not thread_id:
                logger.debug("Skipping thread with missing link or id")
                continue

            thread_url = build_full_url(current_page_url, thread_link)
            logger.debug(f"Thread URL: {thread_url}")

            if thread_url in visited_threads:
                logger.debug(f"Skipping already visited thread ID: {thread_id}")
                continue

            logger.info(f"Scanning thread: {thread_url} (ID: {thread_id})")
            hits.extend(fetch_posts_from_thread(thread_url, keywords, seen, max_thread_pages, css_params))
            # hits.extend(scan_simple_page(thread_url, keywords, seen))
            visited_threads.add(thread_url)

        logger.debug(f"NEXT_PAGE_SELECTOR: {css_params['NEXT_PAGE_SELECTOR']}")
        next_forum_page_link = soup.select_one(css_params["NEXT_PAGE_SELECTOR"])
        logging.debug(f"Next forum page link: {next_forum_page_link}")
        if not next_forum_page_link:
            logger.debug("No next page link found, stopping forum crawl")
            # print page number
            logger.debug(f"current page: " + str(pages_checked + 1))
            #logger.debug(print(soup.prettify()))
            break
        if next_forum_page_link and next_forum_page_link.has_attr("href"):
            current_page_url = build_full_url(current_page_url, next_forum_page_link["href"])
            pages_checked += 1
            logger.debug(f"Moving to next forum page: {current_page_url}")
        else:
            current_page_url = None

        # next_forum_page_link = urljoin(forum_section_url, f"{pages_checked+2}")
        # current_page_url = next_forum_page_link
        # logger.debug(f"Next forum page link: {next_forum_page_link}")
        # logger.debug(f"Current forum page link: {current_page_url}")
        # pages_checked += 1


    logger.info(f"Finished crawling forum section: {forum_section_url}, found {len(hits)} hits")
    return hits

def check_html_feed(url, watch_cfg, seen, visited_threads):
    search_body = watch_cfg.get("search_body", False)
    max_forum_pages = watch_cfg.get("max_forum_pages", 1)
    max_thread_pages = watch_cfg.get("max_thread_pages", 3)
    css_params = watch_cfg.get("css_params", {})

    if search_body:
        logger.debug(f"Searching forum section {url} with post body scanning enabled...")
        return crawl_and_search_threads(url, watch_cfg["keywords"], seen, visited_threads, max_forum_pages, max_thread_pages, css_params)
    else:
        logger.debug(f"Scanning simple page {url} for link text only (no body search)")
        return scan_simple_page(url, watch_cfg["keywords"], seen)

def check_rss_feed(url, keywords, seen):
    hits = []
    logger.debug(f"Fetching RSS feed from {url}")
    feed = feedparser.parse(url)
    logger.debug(f"Fetched {len(feed.entries)} entries from RSS feed")
    for entry in feed.entries:
        unique_id = getattr(entry, "id", None) or getattr(entry, "link", None)
        if not unique_id or unique_id in seen:
            logger.debug(f"Skipping RSS entry with id/link {unique_id} (already seen or missing)")
            continue
        text = (entry.title + " " + getattr(entry, "summary", "")).lower()
        for keyword in keywords:
            if keyword.lower() in text:
                hit_msg = f"Found '{keyword}' in: [{entry.title}]({unique_id})"
                logger.info(f"Keyword match: {hit_msg}")
                hits.append(hit_msg)
                seen.add(unique_id)
                break
    logger.info(f"Finished checking RSS feed: {url}, found {len(hits)} hits")
    return hits

def check_for_keywords(config, seen, visited_threads):
    all_hits = []
    logger.info("Starting keyword checks for all watch configs")
    for watch in config["watch"]:
        source_type = watch.get("type", "html").lower()
        url = watch["url"]
        logger.info(f"Checking source: {url} (type: {source_type})")
        if source_type == "rss":
            hits = check_rss_feed(url, watch["keywords"], seen)
        elif source_type == "html":
            hits = check_html_feed(url, watch, seen, visited_threads)
        else:
            logger.error(f"Unknown watch type '{source_type}' for URL {url}")
            hits = []
        all_hits.extend(hits)
    logger.info(f"Finished all keyword checks, total hits: {len(all_hits)}")
    return all_hits
