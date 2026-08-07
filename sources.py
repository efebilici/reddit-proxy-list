"""Free proxy list sources.

Each entry:
  name     - short identifier
  url      - raw text/JSON endpoint
  protocol - http / socks4 / socks5 / mixed (per-line when prefixed)
  fmt      - bare | prefixed | hostport_country | comments | json
  cap      - max proxies sampled from this source (None = no cap)
"""

import json
import random
import re

import requests

REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "reddit-proxy-list/1.0 (+https://github.com/efebilici/reddit-proxy-list)"}

SOURCES = [
    {
        "name": "thespeedx",
        "url": "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "protocol": "http",
        "fmt": "bare",
        "cap": 2500,
    },
    {
        "name": "ercindedeoglu-http",
        "url": "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
        "protocol": "http",
        "fmt": "bare",
        "cap": 3000,
    },
    {
        "name": "ercindedeoglu-socks5",
        "url": "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt",
        "protocol": "socks5",
        "fmt": "bare",
        "cap": 1500,
    },
    {
        "name": "proxifly",
        "url": "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
        "protocol": "mixed",
        "fmt": "prefixed",
        "cap": 2600,
    },
    {
        "name": "monosans",
        "url": "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "protocol": "http",
        "fmt": "bare",
        "cap": 400,
    },
    {
        "name": "r00tee",
        "url": "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt",
        "protocol": "http",
        "fmt": "bare",
        "cap": 3000,
    },
    {
        "name": "zloi",
        "url": "https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt",
        "protocol": "http",
        "fmt": "hostport_country",
        "cap": 2000,
    },
    {
        "name": "mzyui",
        "url": "https://raw.githubusercontent.com/mzyui/proxy-list/main/http.txt",
        "protocol": "http",
        "fmt": "bare",
        "cap": 4000,
    },
    {
        "name": "proxyscrape",
        "url": "https://raw.githubusercontent.com/ProxyScrape/free-proxy-list/main/proxies/all/data.txt",
        "protocol": "mixed",
        "fmt": "prefixed",
        "cap": 1800,
    },
    {
        "name": "iplocate",
        "url": "https://raw.githubusercontent.com/iplocate/free-proxy-list/main/all-proxies.txt",
        "protocol": "mixed",
        "fmt": "prefixed",
        "cap": 2100,
    },
    {
        "name": "hookzof",
        "url": "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "protocol": "socks5",
        "fmt": "bare",
        "cap": 300,
    },
    {
        "name": "roosterkid",
        "url": "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
        "protocol": "http",
        "fmt": "bare",
        "cap": 150,
    },
    {
        "name": "vpslab",
        "url": "https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_all.txt",
        "protocol": "http",
        "fmt": "comments",
        "cap": 800,
    },
    {
        "name": "geonode",
        "url": "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http",
        "protocol": "http",
        "fmt": "json",
        "cap": 500,
    },
]

IPPORT = re.compile(r"^\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})")
PREFIXED = re.compile(r"^\s*(\w+)://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})")


def _normalize_protocol(proto):
    return "http" if proto in ("http", "https") else proto


def _parse_line(line, fmt, default_protocol):
    if fmt in ("bare", "comments"):
        if fmt == "comments" and line.lstrip().startswith("#"):
            return None
        m = IPPORT.match(line)
        if not m:
            return None
        return (_normalize_protocol(default_protocol), f"{m.group(1)}:{m.group(2)}")
    if fmt == "prefixed":
        m = PREFIXED.match(line)
        if not m:
            return None
        return (_normalize_protocol(m.group(1)), f"{m.group(2)}:{m.group(3)}")
    if fmt == "hostport_country":
        parts = line.strip().split(":")
        if len(parts) < 2 or not IPPORT.match(f"{parts[0]}:{parts[1]}"):
            return None
        return (_normalize_protocol(default_protocol), f"{parts[0]}:{parts[1]}")
    return None


def _fetch_source(src):
    if src["fmt"] == "json":
        text = requests.get(src["url"], headers=HEADERS, timeout=REQUEST_TIMEOUT).text
        data = json.loads(text)
        items = [
            (_normalize_protocol(src["protocol"]), f"{i['ip']}:{i['port']}")
            for i in data.get("data", [])
        ]
    else:
        text = requests.get(src["url"], headers=HEADERS, timeout=REQUEST_TIMEOUT).text
        items = []
        for line in text.splitlines():
            parsed = _parse_line(line, src["fmt"], src["protocol"])
            if parsed:
                items.append(parsed)
    if src["cap"] and len(items) > src["cap"]:
        items = random.sample(items, src["cap"])
    return items


def fetch_all_proxies():
    """Return {host:port: protocol} merged across all sources."""
    proxies = {}
    for src in SOURCES:
        try:
            items = _fetch_source(src)
        except (requests.RequestException, ValueError) as e:
            print(f"  {src['name']}: FAILED ({e})")
            continue
        for protocol, proxy in items:
            proxies.setdefault(proxy, protocol)
        print(f"  {src['name']}: {len(items)} collected")
    return proxies
