"""Validate proxies against Reddit (HTTP 200 on the .json listing endpoint)."""

import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

REDDIT_URL = "https://www.reddit.com/r/all/hot.json"
TIMEOUT = 8
MAX_WORKERS = 50

USER_AGENTS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
)


def _check(proxy, protocol):
    scheme = "socks5" if protocol in ("socks4", "socks5") else "http"
    proxies = {"http": f"{scheme}://{proxy}", "https": f"{scheme}://{proxy}"}
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    start = time.monotonic()
    try:
        response = requests.get(
            REDDIT_URL, headers=headers, proxies=proxies, timeout=TIMEOUT
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        if response.status_code == 200:
            return {"proxy": proxy, "protocol": protocol, "latency_ms": latency_ms}
    except requests.RequestException:
        pass
    return None


def check_all(proxies, max_workers=MAX_WORKERS):
    """Check {proxy: protocol}; return list of passing {proxy, protocol, latency_ms}."""
    results = []
    total = len(proxies)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_check, proxy, proto): proxy for proxy, proto in proxies.items()}
        done = 0
        for future in as_completed(futures):
            done += 1
            if done % 1000 == 0:
                print(f"  checked {done}/{total}")
            result = future.result()
            if result:
                results.append(result)
                print(f"  PASS {result['proxy']} ({result['latency_ms']}ms)")
    return results
