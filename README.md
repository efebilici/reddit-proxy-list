# Reddit Proxy List

Automatically scraped free proxies, validated against Reddit, published every hour via GitHub Actions.

[![Last update](https://img.shields.io/github/last-commit/efebilici/reddit-proxy-list)](https://github.com/efebilici/reddit-proxy-list/actions)
[![Reddit-usable proxies](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fefebilici%2Freddit-proxy-list%2Fmain%2Freddit_proxies.json&query=count&label=reddit-usable%20proxies&color=green)](https://github.com/efebilici/reddit-proxy-list/blob/main/reddit_proxies.json)

## Files

| File | Contents |
|---|---|
| `reddit_proxies.txt` | HTTP/HTTPS proxies that returned HTTP 200 from Reddit, fastest first |
| `reddit_proxies_socks.txt` | SOCKS4/SOCKS5 proxies that passed the same check |
| `reddit_proxies.json` | Full metadata: latency, protocol, check time |

## Usage

```bash
# plain list
curl -O https://raw.githubusercontent.com/efebilici/reddit-proxy-list/main/reddit_proxies.txt

# use the first proxy with curl
PROXY=$(head -1 reddit_proxies.txt)
curl -x "http://$PROXY" https://www.reddit.com/r/all/hot.json
```

### With [YARS](https://github.com/salahar9/YARS)

```python
from yars.yars import YARS

miner = YARS(proxy="http://1.2.3.4:8080")   # paste a proxy from reddit_proxies.txt
```

## How it works

1. **Scrape** — hourly (GitHub Actions cron), proxy lists are pulled from the free sources listed below and deduplicated.
2. **Validate** — every proxy is tested with a `GET https://www.reddit.com/r/all/hot.json` (8s timeout, 50 workers, random browser UA). Only HTTP 200 passes — Reddit's 403/429 blocks are filtered out.
3. **Publish** — the top ~200 fastest proxies are committed to this repo (only when the list changes).

## Sources

| Source | Protocols |
|---|---|
| [TheSpeedX/PROXY-List](https://github.com/TheSpeedX/PROXY-List) | http, socks4, socks5 |
| [ErcinDedeoglu/proxies](https://github.com/ErcinDedeoglu/proxies) | http, https, socks4, socks5 |
| [proxifly/free-proxy-list](https://github.com/proxifly/free-proxy-list) | http, https, socks4, socks5 |
| [monosans/proxy-list](https://github.com/monosans/proxy-list) | http, socks4, socks5 |
| [r00tee/Proxy-List](https://github.com/r00tee/Proxy-List) | http, socks4, socks5 |
| [zloi-user/hideip.me](https://github.com/zloi-user/hideip.me) | http, https, socks4, socks5 |
| [mzyui/proxy-list](https://github.com/mzyui/proxy-list) | http, socks4, socks5 |
| [ProxyScrape/free-proxy-list](https://github.com/ProxyScrape/free-proxy-list) | http, https, socks4, socks5 |
| [iplocate/free-proxy-list](https://github.com/iplocate/free-proxy-list) | http, https, socks4, socks5 |
| [hookzof/socks5_list](https://github.com/hookzof/socks5_list) | socks5 |
| [roosterkid/openproxylist](https://github.com/roosterkid/openproxylist) | http, socks4, socks5 |
| [VPSLabCloud/VPSLab-Free-Proxy-List](https://github.com/VPSLabCloud/VPSLab-Free-Proxy-List) | http, socks4, socks5 |
| [geonode](https://proxylist.geonode.com) | http |

## Disclaimer

- Free proxies are **unreliable** — most are dead or short-lived. The list can be empty on any given run; that is expected.
- Reddit's Terms of Service prohibit automated access. This project is for **educational and research purposes**; use at your own risk.
- The proxy IPs in this list belong to third parties. Do not send abusive traffic through them.
