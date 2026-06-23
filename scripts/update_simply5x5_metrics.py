#!/usr/bin/env python3
"""Update Simply5x5 public metrics from App Store Connect Analytics reports.

The script keeps a small public aggregate in data/simply5x5_metrics.json and
updates marked spans in the static HTML pages. It is intentionally conservative:
raw App Store Connect reports are never written to the repository.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_BASE = "https://api.appstoreconnect.apple.com"
DATA_FILE = Path("data/simply5x5_metrics.json")
HTML_FILES = [Path("index.html"), Path("projects/simply5x5.html")]


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def env_list(name: str, default: str) -> list[str]:
    return [item.strip() for item in env(name, default).split(",") if item.strip()]


def parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value[:10])


def default_as_of() -> dt.date:
    # Apple considers Analytics Reports data complete two days after the report date.
    return dt.datetime.now(dt.UTC).date() - dt.timedelta(days=2)


def compact_number(value: float | int) -> str:
    number = float(value)
    sign = "-" if number < 0 else ""
    number = abs(number)
    if number >= 1_000_000:
        text = f"{number / 1_000_000:.2f}".rstrip("0").rstrip(".")
        return f"{sign}{text}M"
    if number >= 1_000:
        text = f"{number / 1_000:.2f}".rstrip("0").rstrip(".")
        return f"{sign}{text}K"
    if number.is_integer():
        return f"{sign}{int(number)}"
    return f"{sign}{number:.1f}".rstrip("0").rstrip(".")


def month_year(value: str | dt.date) -> str:
    date = parse_date(value) if isinstance(value, str) else value
    return date.strftime("%B %Y")


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def update_html(metrics: dict[str, Any]) -> int:
    replacements = {
        "simply5x5-as-of": month_year(metrics["as_of"]),
        "simply5x5-downloads": compact_number(metrics["downloads_total"]),
        "simply5x5-sessions": compact_number(metrics["sessions_total"]),
        "simply5x5-active-average": compact_number(metrics["active_average_30d"]),
    }
    changed_files = 0
    for path in HTML_FILES:
        text = path.read_text(encoding="utf-8")
        original = text
        for key, value in replacements.items():
            pattern = re.compile(rf'(<span\s+data-metric="{re.escape(key)}"[^>]*>)(.*?)(</span>)', re.S)
            text, count = pattern.subn(rf"\g<1>{value}\g<3>", text)
            if count == 0:
                raise RuntimeError(f"{path} is missing data-metric={key!r}")
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed_files += 1
    return changed_files


def number_from_cell(value: str | None) -> float:
    if value is None:
        return 0.0
    cleaned = value.strip().replace(",", "")
    if not cleaned or cleaned in {"-", "--"}:
        return 0.0
    return float(cleaned)


def parse_metric_value(value: str) -> float:
    cleaned = value.strip().replace(",", "")
    if not cleaned:
        raise ValueError("metric value cannot be empty")
    suffix = cleaned[-1:].lower()
    multiplier = 1.0
    if suffix in {"k", "m"}:
        cleaned = cleaned[:-1]
        multiplier = 1_000.0 if suffix == "k" else 1_000_000.0
    return float(cleaned) * multiplier


def pick_column(row: dict[str, str], candidates: list[str]) -> str | None:
    by_normalized = {normalized(key): key for key in row}
    for candidate in candidates:
        key = by_normalized.get(normalized(candidate))
        if key is not None:
            return key
    return None


def row_date(row: dict[str, str], candidates: list[str]) -> dt.date | None:
    key = pick_column(row, candidates)
    if not key:
        return None
    value = (row.get(key) or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return dt.datetime.strptime(value[:10], fmt).date()
        except ValueError:
            pass
    return None


def parse_rows(payload: bytes) -> list[dict[str, str]]:
    if payload[:2] == b"\x1f\x8b":
        payload = gzip.decompress(payload)
    text = payload.decode("utf-8-sig", errors="replace")
    first_line = text.splitlines()[0] if text.splitlines() else ""
    delimiter = "\t" if first_line.count("\t") >= first_line.count(",") else ","
    return list(csv.DictReader(io.StringIO(text), delimiter=delimiter))


class AppStoreConnect:
    def __init__(self) -> None:
        self.issuer_id = env("ASC_ISSUER_ID")
        self.key_id = env("ASC_KEY_ID")
        self.private_key = env("ASC_PRIVATE_KEY").replace("\\n", "\n")
        self.app_id = env("SIMPLY5X5_APP_ID")
        missing = [
            name
            for name, value in {
                "ASC_ISSUER_ID": self.issuer_id,
                "ASC_KEY_ID": self.key_id,
                "ASC_PRIVATE_KEY": self.private_key,
                "SIMPLY5X5_APP_ID": self.app_id,
            }.items()
            if not value
        ]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    def token(self) -> str:
        try:
            import jwt
        except ImportError as exc:
            raise RuntimeError("Install PyJWT with crypto support: pip install 'PyJWT[crypto]'") from exc
        now = int(time.time())
        token = jwt.encode(
            {"iss": self.issuer_id, "iat": now, "exp": now + 20 * 60, "aud": "appstoreconnect-v1"},
            self.private_key,
            algorithm="ES256",
            headers={"kid": self.key_id, "typ": "JWT"},
        )
        return token.decode("utf-8") if isinstance(token, bytes) else token

    def request(
        self,
        method: str,
        path_or_url: str,
        *,
        params: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        authorized: bool = True,
    ) -> bytes:
        url = path_or_url if path_or_url.startswith("http") else f"{API_BASE}{path_or_url}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        data = None
        headers = {"Accept": "application/json"}
        if authorized:
            headers["Authorization"] = f"Bearer {self.token()}"
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{method} {url} failed with HTTP {error.code}: {detail}") from error

    def json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        payload = self.request(method, path, **kwargs)
        return json.loads(payload.decode("utf-8")) if payload else {}

    def paged(self, path: str, params: dict[str, str] | None = None) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        next_url: str | None = None
        while True:
            if next_url:
                response = self.json("GET", next_url)
            else:
                response = self.json("GET", path, params=params)
            items.extend(response.get("data", []))
            next_url = response.get("links", {}).get("next")
            if not next_url:
                return items

    def ensure_report_request(self) -> None:
        if env("ASC_CREATE_ANALYTICS_REQUEST", "false").lower() not in {"1", "true", "yes"}:
            return
        body = {
            "data": {
                "type": "analyticsReportRequests",
                "attributes": {"accessType": "ONGOING"},
                "relationships": {"app": {"data": {"type": "apps", "id": self.app_id}}},
            }
        }
        self.json("POST", "/v1/analyticsReportRequests", body=body)
        raise RuntimeError(
            "Created an ONGOING analytics report request. Apple usually needs 24-48 hours "
            "before the first report is available; rerun this workflow later."
        )

    def reports(self) -> list[dict[str, Any]]:
        requests = self.paged(
            f"/v1/apps/{self.app_id}/analyticsReportRequests",
            {
                "limit": "200",
                "fields[analyticsReportRequests]": "accessType,stoppedDueToInactivity,reports",
                "fields[analyticsReports]": "name,category,instances",
            },
        )
        if not requests:
            self.ensure_report_request()
            raise RuntimeError(
                "No Analytics Report request exists for this app. Set ASC_CREATE_ANALYTICS_REQUEST=true "
                "once, or create an ONGOING request in App Store Connect."
            )
        reports: list[dict[str, Any]] = []
        for request in requests:
            reports.extend(
                self.paged(
                    f"/v1/analyticsReportRequests/{request['id']}/reports",
                    {"limit": "200", "fields[analyticsReports]": "name,category,instances"},
                )
            )
        return reports

    def report_rows(self, report_names: list[str]) -> list[dict[str, str]]:
        report = find_report(self.reports(), report_names)
        instances = self.paged(f"/v1/analyticsReports/{report['id']}/instances", {"limit": "200"})
        if not instances:
            raise RuntimeError(f"Report {report_name(report)!r} has no available instances yet.")
        rows: list[dict[str, str]] = []
        for instance in instances:
            segments = self.paged(
                f"/v1/analyticsReportInstances/{instance['id']}/segments",
                {"limit": "200", "fields[analyticsReportSegments]": "url"},
            )
            for segment in segments:
                url = segment.get("attributes", {}).get("url")
                if not url:
                    continue
                rows.extend(parse_rows(self.request("GET", url, authorized=False)))
        if not rows:
            raise RuntimeError(f"Report {report_name(report)!r} did not contain downloadable rows.")
        return rows


def report_name(report: dict[str, Any]) -> str:
    return report.get("attributes", {}).get("name") or report.get("id", "")


def find_report(reports: list[dict[str, Any]], candidates: list[str]) -> dict[str, Any]:
    normalized_candidates = [normalized(candidate) for candidate in candidates]
    for report in reports:
        name = report_name(report)
        normalized_name = normalized(name)
        if normalized_name in normalized_candidates:
            return report
    for report in reports:
        name = report_name(report)
        normalized_name = normalized(name)
        if any(candidate and candidate in normalized_name for candidate in normalized_candidates):
            return report
    available = ", ".join(sorted(report_name(report) for report in reports))
    raise RuntimeError(f"Could not find report matching {candidates}. Available reports: {available}")


def sum_metric_after(
    rows: list[dict[str, str]],
    metric_columns: list[str],
    date_columns: list[str],
    after: dt.date,
    through: dt.date,
) -> tuple[float, dt.date]:
    total = 0.0
    latest = after
    for row in rows:
        date = row_date(row, date_columns)
        if date is None or date <= after or date > through:
            continue
        metric_key = pick_column(row, metric_columns)
        if metric_key is None:
            continue
        total += number_from_cell(row.get(metric_key))
        latest = max(latest, date)
    return total, latest


def active_history_after(
    rows: list[dict[str, str]],
    metric_columns: list[str],
    date_columns: list[str],
    after: dt.date,
    through: dt.date,
) -> dict[str, float]:
    grouped: dict[str, float] = {}
    for row in rows:
        date = row_date(row, date_columns)
        if date is None or date <= after or date > through:
            continue
        metric_key = pick_column(row, metric_columns)
        if metric_key is None:
            continue
        key = date.isoformat()
        grouped[key] = grouped.get(key, 0.0) + number_from_cell(row.get(metric_key))
    return grouped


def average_last_30_days(history: dict[str, float], through: dt.date, fallback: float) -> float:
    start = through - dt.timedelta(days=29)
    values = [
        value
        for date_text, value in history.items()
        if start <= parse_date(date_text) <= through
    ]
    if not values:
        return fallback
    return round(sum(values) / len(values))


def fetch_from_app_store(state: dict[str, Any], as_of: dt.date) -> dict[str, Any]:
    client = AppStoreConnect()
    date_columns = env_list("SIMPLY5X5_DATE_COLUMNS", "Date,Report Date,Event Date,Start Date,End Date")

    downloads_rows = client.report_rows(
        env_list("SIMPLY5X5_DOWNLOAD_REPORT_NAMES", "App Store Downloads,Downloads")
    )
    sessions_rows = client.report_rows(
        env_list("SIMPLY5X5_SESSIONS_REPORT_NAMES", "App Sessions,Sessions,App Usage")
    )

    downloads_delta, downloads_through = sum_metric_after(
        downloads_rows,
        env_list("SIMPLY5X5_DOWNLOAD_COLUMNS", "Total Downloads,Downloads,First Time Downloads,First-Time Downloads"),
        date_columns,
        parse_date(state["processed_through"]["downloads"]),
        as_of,
    )
    sessions_delta, sessions_through = sum_metric_after(
        sessions_rows,
        env_list("SIMPLY5X5_SESSIONS_COLUMNS", "Sessions,App Sessions"),
        date_columns,
        parse_date(state["processed_through"]["sessions"]),
        as_of,
    )
    active_history = {
        str(item["date"]): float(item["value"])
        for item in state.get("active_devices_daily", [])
        if "date" in item and "value" in item
    }
    active_history.update(
        active_history_after(
            sessions_rows,
            env_list("SIMPLY5X5_ACTIVE_COLUMNS", "Active Devices,Active in Last 30 Days,Active Devices Last 30 Days"),
            date_columns,
            parse_date(state["processed_through"]["active_devices"]),
            as_of,
        )
    )

    state["downloads_total"] = int(round(float(state["downloads_total"]) + downloads_delta))
    state["sessions_total"] = int(round(float(state["sessions_total"]) + sessions_delta))
    state["processed_through"]["downloads"] = downloads_through.isoformat()
    state["processed_through"]["sessions"] = sessions_through.isoformat()
    if active_history:
        latest_active = max(parse_date(date_text) for date_text in active_history)
        state["processed_through"]["active_devices"] = max(
            parse_date(state["processed_through"]["active_devices"]), latest_active
        ).isoformat()
    state["active_devices_daily"] = [
        {"date": date_text, "value": active_history[date_text]}
        for date_text in sorted(active_history)
        if parse_date(date_text) >= as_of - dt.timedelta(days=90)
    ]
    state["active_average_30d"] = average_last_30_days(
        active_history, as_of, float(state["active_average_30d"])
    )
    state["as_of"] = as_of.isoformat()
    return state


def apply_manual_metrics(
    state: dict[str, Any],
    *,
    downloads_total: str,
    sessions_total: str,
    active_average_30d: str,
    as_of: dt.date,
) -> dict[str, Any]:
    missing = [
        name
        for name, value in {
            "--set-downloads": downloads_total,
            "--set-sessions": sessions_total,
            "--set-active-average": active_average_30d,
        }.items()
        if not value.strip()
    ]
    if missing:
        raise RuntimeError(f"Manual updates require all metric values: {', '.join(missing)}")

    state["downloads_total"] = int(round(parse_metric_value(downloads_total)))
    state["sessions_total"] = int(round(parse_metric_value(sessions_total)))
    state["active_average_30d"] = int(round(parse_metric_value(active_average_30d)))
    state["as_of"] = as_of.isoformat()
    state["processed_through"] = {
        "downloads": as_of.isoformat(),
        "sessions": as_of.isoformat(),
        "active_devices": as_of.isoformat(),
    }
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-file", default=str(DATA_FILE))
    parser.add_argument("--as-of-date", default="")
    parser.add_argument("--metrics-json", default="", help="Use a prepared metrics JSON instead of the API.")
    parser.add_argument("--set-downloads", default="", help="Set total downloads manually, e.g. 1090 or 1.09K.")
    parser.add_argument("--set-sessions", default="", help="Set total app sessions manually, e.g. 7370 or 7.37K.")
    parser.add_argument("--set-active-average", default="", help="Set 30-day average active users manually.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data_path = Path(args.data_file)
    state = read_json(Path(args.metrics_json)) if args.metrics_json else read_json(data_path)
    as_of = parse_date(args.as_of_date) if args.as_of_date else default_as_of()
    has_manual_metrics = any(
        [args.set_downloads.strip(), args.set_sessions.strip(), args.set_active_average.strip()]
    )

    if has_manual_metrics:
        state = apply_manual_metrics(
            state,
            downloads_total=args.set_downloads,
            sessions_total=args.set_sessions,
            active_average_30d=args.set_active_average,
            as_of=as_of,
        )
    elif not args.metrics_json:
        state = fetch_from_app_store(state, as_of)

    if args.dry_run:
        print(json.dumps(state, indent=2))
        return 0

    write_json(data_path, state)
    update_html(state)
    print(
        "Updated Simply5x5 metrics: "
        f"{compact_number(state['downloads_total'])} downloads, "
        f"{compact_number(state['sessions_total'])} sessions, "
        f"{compact_number(state['active_average_30d'])} avg active devices, "
        f"as of {month_year(state['as_of'])}."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
