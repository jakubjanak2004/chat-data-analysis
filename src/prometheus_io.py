"""Load time series from Prometheus HTTP API into pandas."""

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional

import pandas as pd
import requests

# Override: export PROMETHEUS_URL=http://host:9090
DEFAULT_PROMETHEUS = "http://178.104.69.73:9090"
PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", DEFAULT_PROMETHEUS).rstrip("/")


def prom_query_range(
    query: str,
    start: datetime,
    end: datetime,
    step: str = "15s",
    base_url: Optional[str] = None,
) -> pd.DataFrame:
    """
    /api/v1/query_range → wide DataFrame (timestamp index, one column per series).
    """
    base = (base_url or PROMETHEUS_URL).rstrip("/")
    r = requests.get(
        f"{base}/api/v1/query_range",
        params={
            "query": query,
            "start": start.timestamp(),
            "end": end.timestamp(),
            "step": step,
        },
        timeout=120,
    )
    r.raise_for_status()
    payload = r.json()
    if payload.get("status") != "success":
        raise RuntimeError(payload)

    results = payload["data"]["result"]
    if not results:
        return pd.DataFrame()

    frames: List[pd.Series] = []
    for i, series in enumerate(results):
        metric = series.get("metric", {})
        name = metric.get("__name__", f"series_{i}")
        values = series["values"]
        idx = pd.to_datetime([float(t) for t, _ in values], unit="s", utc=True)
        vals = [float(v) for _, v in values]
        label_bits = {k: v for k, v in metric.items() if k != "__name__"}
        col = f"{name} {label_bits}".strip()
        frames.append(pd.Series(vals, index=idx, name=col[:200]))

    return pd.concat(frames, axis=1)


def prom_query_instant(
    query: str,
    at: Optional[datetime] = None,
    base_url: Optional[str] = None,
) -> list:
    """Instant query → raw Prometheus result list."""
    base = (base_url or PROMETHEUS_URL).rstrip("/")
    params: dict = {"query": query}
    if at is not None:
        params["time"] = at.timestamp()
    r = requests.get(f"{base}/api/v1/query", params=params, timeout=60)
    r.raise_for_status()
    payload = r.json()
    if payload.get("status") != "success":
        raise RuntimeError(payload)
    return payload["data"]["result"]


def test_connection(base_url: Optional[str] = None) -> bool:
    """GET /-/healthy or /api/v1/query?query=up"""
    base = (base_url or PROMETHEUS_URL).rstrip("/")
    try:
        r = requests.get(f"{base}/api/v1/query", params={"query": "1"}, timeout=10)
        return r.status_code == 200 and r.json().get("status") == "success"
    except OSError:
        return False
