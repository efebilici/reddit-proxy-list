"""Scrape free proxy lists, validate against Reddit, publish the usable ones."""

import json
import time
from datetime import datetime, timezone

from checker import REDDIT_URL, check_all
from sources import SOURCES, fetch_all_proxies

TXT_CAP = 200
JSON_CAP = 1000


def _write_proxies(path, results):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(r["proxy"] for r in results))
        if results:
            f.write("\n")


def main():
    start = time.time()
    print(f"[1/3] Collecting proxies from {len(SOURCES)} sources...")
    proxies = fetch_all_proxies()
    print(f"  total unique: {len(proxies)}")

    print("[2/3] Validating against Reddit...")
    results = check_all(proxies)
    print(f"  passed: {len(results)}")

    print("[3/3] Writing output...")
    results.sort(key=lambda r: r["latency_ms"])
    http_results = [r for r in results if r["protocol"] == "http"]
    socks_results = [r for r in results if r["protocol"] != "http"]

    _write_proxies("reddit_proxies.txt", http_results[:TXT_CAP])
    _write_proxies("reddit_proxies_socks.txt", socks_results[:TXT_CAP])
    payload = {
        "count": len(results),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "target": REDDIT_URL,
        "proxies": results[:JSON_CAP],
    }
    with open("reddit_proxies.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    elapsed = int(time.time() - start)
    print(f"done in {elapsed}s — http: {len(http_results)}, socks: {len(socks_results)}")


if __name__ == "__main__":
    main()
