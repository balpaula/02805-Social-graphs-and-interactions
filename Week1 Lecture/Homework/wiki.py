"""Thin Wikipedia API client for the week-1 checks, with an on-disk cache.

Two things the course flags and this module handles once:
  * Wikipedia answers 403 unless the request carries a User-Agent naming the client.
  * It answers 429 if you go too fast, so every call backs off and retries.

Results are cached in data/wiki_cache.json, so the figures can be rebuilt offline
and we are not hammering the API on every run.
"""

import json
import os
import re
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))


def _data_dir():
    here = HERE
    for _ in range(5):
        for name in ("data", "Data"):
            path = os.path.join(here, name)
            if os.path.isdir(path):
                return path
        here = os.path.dirname(here)
    return os.path.join(HERE, "data")


CACHE_PATH = os.path.join(_data_dir(), "wiki_cache.json")
API = "https://en.wikipedia.org/w/api.php"

USER_AGENT = ("02805-varmel-week1/0.1 (DTU 02805 Social Graphs course project; "
              "educational use; contact via github.com/balpaula)")

_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT})


def _load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, indent=1, sort_keys=True)


def get(params):
    """One API call, retrying on 429 / transient failures."""
    for attempt in range(6):
        r = _session.get(API, params=params, timeout=30)
        if r.status_code == 200:
            return r.json()
        time.sleep(3 * (attempt + 1))
    r.raise_for_status()


def _resolve(d, requested):
    """Map a requested title through normalisation and redirects to the final one."""
    hop = {}
    for key in ("normalized", "redirects"):
        for e in d.get(key, []):
            hop[e["from"]] = e["to"]
    title = requested
    for _ in range(5):
        if title not in hop:
            break
        title = hop[title]
    return title


def article_bytes(node_ids, refresh=False):
    """Byte size of every article, 50 titles per request (prop=info)."""
    cache = _load_cache()
    store = cache.setdefault("bytes", {})
    todo = [n for n in node_ids if refresh or n not in store]

    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        d = get({"action": "query", "format": "json", "formatversion": 2,
                 "redirects": 1, "prop": "info",
                 "titles": "|".join(t.replace("_", " ") for t in batch)})["query"]
        pages = {p["title"]: p for p in d["pages"]}
        for nid in batch:
            title = _resolve(d, nid.replace("_", " "))
            if title in pages:
                store[nid] = pages[title].get("length")
        time.sleep(0.6)

    if todo:
        _save_cache(cache)
    return {n: store[n] for n in node_ids if n in store}


def wikitext(node_id, refresh=False):
    """Raw wiki-source of one article - where the [[links]] actually live."""
    cache = _load_cache()
    store = cache.setdefault("wikitext", {})
    if refresh or node_id not in store:
        d = get({"action": "query", "format": "json", "formatversion": 2,
                 "redirects": 1, "prop": "revisions", "rvprop": "content",
                 "rvslots": "main", "titles": node_id.replace("_", " ")})
        store[node_id] = d["query"]["pages"][0]["revisions"][0]["slots"]["main"]["content"]
        _save_cache(cache)
        time.sleep(1.0)
    return store[node_id]


LINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:\|[^\]]*)?\]\]")


def outlinks(node_id, refresh=False):
    """Every [[Page name]] in the wiki-source, article namespace only.

    This is exactly how the course harvested the edges, so re-running it is how we
    check the snapshot rather than trusting it.
    """
    raw = LINK_RE.findall(wikitext(node_id, refresh=refresh))
    titles = [t.strip().replace(" ", "_") for t in raw if ":" not in t]
    return raw, titles
