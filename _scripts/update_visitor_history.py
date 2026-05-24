#!/usr/bin/env python3
"""Scrape the SmallCounter visitor map and merge results into _data/visitor_history.json.

SmallCounter's free map endpoint only exposes the last ~100 visitors. This script
runs on a schedule, parses the markers SmallCounter currently shows, and merges
them with previously seen markers so the rendered map reflects all visitors ever
captured (not just the most recent 100).

Per-location merge rule: keep the maximum visit count we have ever observed for a
location, and the most recent last-visit timestamp. Locations are keyed by
(lat, lng) rounded to 4 decimal places.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

DEFAULT_COUNTER_ID = "1777584151"
DEFAULT_URL_TEMPLATE = "https://smallcounter.com/vmap/{counter_id}/"
DEFAULT_OUTPUT = pathlib.Path("_data/visitor_history.json")

MARKER_RE = re.compile(
    r"var\s+point\s*=\s*new\s+GLatLng\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\);"
    r"\s*var\s+marker\s*=\s*createMarker\(\s*point\s*,\s*\"[^\"]*\"\s*,"
    r'\s*"((?:\\.|[^"\\])*)"'
)
TAG_RE = re.compile(r"<[^>]+>")
TOTAL_RE = re.compile(r"Total\s*:\s*([\d,]+)", re.IGNORECASE)
LAST_VISIT_RE = re.compile(r"Last visit\s*:\s*(.+)$", re.IGNORECASE)

USER_AGENT = (
    "Mozilla/5.0 (compatible; visitor-history-updater/1.0; "
    "+https://github.com/DarthUtopian/DarthUtopian.github.io)"
)


def fetch(url: str, timeout: float = 20.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def _decode_marker(value: str) -> str:
    return value.replace(r"\/", "/").replace(r"\"", '"')


def _strip_html(value: str) -> str:
    text = TAG_RE.sub("\n", value)
    return re.sub(r"\s+", " ", text).strip()


def parse_markers(html: str) -> list[dict]:
    entries: list[dict] = []
    for match in MARKER_RE.finditer(html):
        lat = float(match.group(1))
        lng = float(match.group(2))
        raw_marker = _decode_marker(match.group(3))
        text = _strip_html(raw_marker)
        total_match = TOTAL_RE.search(text)
        visits = int(total_match.group(1).replace(",", "")) if total_match else 1
        last_visit_match = LAST_VISIT_RE.search(text)
        last_visit = last_visit_match.group(1).strip() if last_visit_match else ""
        label = re.sub(r"\s*Total\s*:.*$", "", text, flags=re.IGNORECASE).strip()
        entries.append(
            {
                "lat": lat,
                "lng": lng,
                "label": label,
                "visits": visits,
                "last_visit": last_visit,
            }
        )
    return entries


def project_longitude(lng: float) -> float:
    return max(0.0, min(100.0, ((lng + 180.0) / 360.0) * 100.0))


def project_latitude(lat: float) -> float:
    return max(0.0, min(100.0, ((90.0 - lat) / 180.0) * 100.0))


def dot_size(visits: int) -> float:
    return max(8.0, min(18.0, 7.0 + math.sqrt(max(visits, 1)) * 1.6))


def location_key(lat: float, lng: float) -> str:
    return f"{round(lat, 4):.4f},{round(lng, 4):.4f}"


def load_existing(path: pathlib.Path) -> dict:
    if not path.exists():
        return {"updated_at": None, "total_visits": 0, "locations": []}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {"updated_at": None, "total_visits": 0, "locations": []}
    data.setdefault("locations", [])
    data.setdefault("total_visits", 0)
    data.setdefault("updated_at", None)
    return data


def _parse_last_visit(value: str) -> dt.datetime | None:
    if not value:
        return None
    for fmt in ("%d-%b-%Y %H:%M:%S", "%d-%b-%Y %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return dt.datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _dedupe_fresh(fresh: list[dict]) -> list[dict]:
    by_key: dict[str, dict] = {}
    for entry in fresh:
        key = location_key(entry["lat"], entry["lng"])
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = dict(entry)
            continue
        existing["visits"] = max(int(existing["visits"]), int(entry["visits"]))
        existing_dt = _parse_last_visit(existing.get("last_visit", ""))
        new_dt = _parse_last_visit(entry.get("last_visit", ""))
        if new_dt and (existing_dt is None or new_dt > existing_dt):
            existing["last_visit"] = entry["last_visit"]
        elif not existing.get("last_visit") and entry.get("last_visit"):
            existing["last_visit"] = entry["last_visit"]
    return list(by_key.values())


def merge(existing: dict, fresh: list[dict]) -> tuple[dict, bool]:
    fresh = _dedupe_fresh(fresh)
    by_key: dict[str, dict] = {}
    for loc in existing.get("locations", []):
        key = location_key(loc["lat"], loc["lng"])
        by_key[key] = dict(loc)

    changed = False
    for entry in fresh:
        key = location_key(entry["lat"], entry["lng"])
        if key in by_key:
            stored = by_key[key]
            new_visits = max(int(stored.get("visits", 0)), int(entry["visits"]))
            if new_visits != stored.get("visits"):
                stored["visits"] = new_visits
                changed = True
            stored_dt = _parse_last_visit(stored.get("last_visit", ""))
            entry_dt = _parse_last_visit(entry.get("last_visit", ""))
            if entry["last_visit"] and (
                stored_dt is None or (entry_dt is not None and entry_dt > stored_dt)
            ) and entry["last_visit"] != stored.get("last_visit"):
                stored["last_visit"] = entry["last_visit"]
                changed = True
            if entry["label"] and entry["label"] != stored.get("label"):
                stored["label"] = entry["label"]
                changed = True
        else:
            by_key[key] = {
                "lat": entry["lat"],
                "lng": entry["lng"],
                "label": entry["label"],
                "visits": int(entry["visits"]),
                "last_visit": entry["last_visit"],
            }
            changed = True

    locations = []
    for loc in by_key.values():
        loc["x"] = round(project_longitude(loc["lng"]), 3)
        loc["y"] = round(project_latitude(loc["lat"]), 3)
        loc["size"] = round(dot_size(int(loc["visits"])), 2)
        locations.append(loc)

    locations.sort(key=lambda l: (-int(l["visits"]), l["label"]))
    total_visits = sum(int(l["visits"]) for l in locations)

    merged = {
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "total_visits": total_visits,
        "location_count": len(locations),
        "locations": locations,
    }
    if total_visits != int(existing.get("total_visits", 0)):
        changed = True
    if len(locations) != len(existing.get("locations", [])):
        changed = True
    return merged, changed


def write_if_changed(path: pathlib.Path, data: dict, changed: bool) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if path.exists():
        current = path.read_text(encoding="utf-8")
        if current == payload and not changed:
            return False
    path.write_text(payload, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--counter-id",
        default=os.environ.get("SMALLCOUNTER_ID", DEFAULT_COUNTER_ID),
        help="SmallCounter counter id (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=DEFAULT_OUTPUT,
        help="Path to the JSON history file (default: %(default)s)",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Override the source URL entirely (useful for tests)",
    )
    args = parser.parse_args(argv)

    url = args.url or DEFAULT_URL_TEMPLATE.format(counter_id=args.counter_id)
    print(f"Fetching {url}", file=sys.stderr)
    try:
        html = fetch(url)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"ERROR fetching SmallCounter: {exc}", file=sys.stderr)
        return 1

    fresh = parse_markers(html)
    print(f"Parsed {len(fresh)} markers from SmallCounter", file=sys.stderr)
    if not fresh:
        print("No markers parsed; leaving existing history untouched", file=sys.stderr)
        return 0

    existing = load_existing(args.output)
    merged, changed = merge(existing, fresh)
    if not changed and args.output.exists():
        print("No visitor data changes; leaving file untouched", file=sys.stderr)
        return 0
    write_if_changed(args.output, merged, changed)
    print(
        f"Updated {args.output}: {merged['location_count']} locations, "
        f"{merged['total_visits']} total visits",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
