"""CloudFront のアクセスログ（v2 の JSON）を、日本時間の1日ごとの CSV にする。

日付を渡さないときは、前日の全体を書く。日付が当日のときは、実行時刻の1時間前までを書く。
CSV の列は、配信している v2 の項目と同じ名前、同じ順。
"""

import csv
import gzip
import io
import json
import os
from datetime import datetime, timedelta, timezone

import boto3

JST = timezone(timedelta(hours=9))
UTC = timezone.utc

BUCKET = os.environ["LOG_BUCKET"]
LOG_PREFIX = os.environ.get("LOG_PREFIX", "AWSLogs/868118155022/CloudFront/")
DISTRIBUTION_ID = os.environ.get("DISTRIBUTION_ID", "E1P47C37OV1I3G")
OUT_PREFIX = os.environ.get("OUT_PREFIX", "csv/")

FIELDS = [
    "date",
    "time",
    "x-edge-location",
    "sc-bytes",
    "c-ip",
    "cs-method",
    "cs(Host)",
    "cs-uri-stem",
    "sc-status",
    "cs(Referer)",
    "cs(User-Agent)",
    "cs-uri-query",
    "x-edge-result-type",
    "x-edge-request-id",
    "x-host-header",
    "cs-protocol",
    "cs-bytes",
    "time-taken",
    "x-forwarded-for",
    "ssl-protocol",
    "ssl-cipher",
    "x-edge-response-result-type",
    "cs-protocol-version",
    "fle-status",
    "fle-encrypted-fields",
    "c-port",
    "time-to-first-byte",
    "x-edge-detailed-result-type",
    "sc-content-type",
    "sc-content-len",
    "sc-range-start",
    "sc-range-end",
    "c-country",
    "asn",
]

s3 = boto3.client("s3")


def handler(event, context):
    event = event or {}
    now = datetime.now(JST)
    if event.get("date"):
        days = [datetime.fromisoformat(event["date"]).date()]
    else:
        days = [now.date() - timedelta(days=1)]
    return {"days": [export_day(day, now) for day in days]}


def export_day(day, now):
    start = datetime.combine(day, datetime.min.time(), tzinfo=JST)
    end = start + timedelta(days=1)
    today = now.astimezone(JST).date()
    if day > today:
        raise ValueError(f"date is in the future: {day.isoformat()}")
    if day == today:
        end = min(end, now.astimezone(JST) - timedelta(hours=1))

    rows = []
    files = 0
    if end > start:
        for key in log_keys(start, end):
            files += 1
            for record in records(key):
                stamp = record_time(record)
                if stamp is not None and start <= stamp < end:
                    rows.append(record)
    rows.sort(key=lambda row: (row.get("date", ""), row.get("time", ""), row.get("x-edge-request-id", "")))

    key = f"{OUT_PREFIX}{day.isoformat()}.csv"
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=to_csv(rows),
        ContentType="text/csv; charset=utf-8",
    )
    return {
        "date": day.isoformat(),
        "rows": len(rows),
        "files": files,
        "key": key,
        "from": start.isoformat(),
        "until": end.isoformat(),
    }


def log_keys(start, end):
    hour = start.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
    stop = end.astimezone(UTC)
    keys = []
    while hour < stop:
        prefix = f"{LOG_PREFIX}{DISTRIBUTION_ID}.{hour.strftime('%Y-%m-%d-%H')}."
        token = None
        while True:
            args = {"Bucket": BUCKET, "Prefix": prefix}
            if token:
                args["ContinuationToken"] = token
            page = s3.list_objects_v2(**args)
            for item in page.get("Contents", []):
                if item["Key"].endswith(".gz") and item["Size"] > 0:
                    keys.append(item["Key"])
            if not page.get("IsTruncated"):
                break
            token = page["NextContinuationToken"]
        hour += timedelta(hours=1)
    return keys


def records(key):
    body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
    with gzip.GzipFile(fileobj=io.BytesIO(body)) as raw:
        for line in raw.read().decode("utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def record_time(record):
    try:
        return datetime.strptime(
            f'{record["date"]} {record["time"]}', "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=UTC)
    except (KeyError, ValueError):
        return None


def to_csv(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({name: "" if row.get(name) is None else row.get(name, "") for name in FIELDS})
    return buf.getvalue().encode("utf-8")
