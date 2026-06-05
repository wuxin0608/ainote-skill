#!/usr/bin/env python3
"""Shared helpers for ainote noteshare skill scripts."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
CACHE_DIR = os.path.join(SKILL_ROOT, ".cache")
DEVICES_CACHE = os.path.join(CACHE_DIR, "devices.json")

API_BASE = "https://ainote.com.cn/api/web"
API_KEY_HEADER = "X-AINOTE-API-KEY"
SUCCESS_CODE = 20000


def get_api_key() -> str:
    key = os.environ.get("AINOTE_API_KEY", "").strip()
    if not key:
        raise ValueError("缺少 AINOTE_API_KEY，请设置环境变量 AINOTE_API_KEY")
    return key


def request_skill(path: str, body: Optional[Dict[str, Any]] = None) -> Any:
    api_key = get_api_key()
    url = f"{API_BASE}{path}"
    response = requests.post(
        url,
        json=body or {},
        headers={API_KEY_HEADER: api_key},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json() if response.text else {}
    code = payload.get("code")
    if code is not None and code != SUCCESS_CODE:
        message = payload.get("message") or str(payload)
        raise ValueError(f"API 错误: code={code}, message={message}")
    return payload


def ensure_cache_dir() -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)


def load_devices() -> List[Dict[str, Any]]:
    if not os.path.isfile(DEVICES_CACHE):
        return []
    with open(DEVICES_CACHE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict):
            name = str(item.get("name") or "").strip()
            device_id = item.get("deviceId")
            url = str(item.get("url") or "").strip()
            if name and device_id is not None:
                out.append({"name": name, "deviceId": device_id, "url": url})
    return out


def save_devices(devices: List[Dict[str, Any]]) -> None:
    ensure_cache_dir()
    with open(DEVICES_CACHE, "w", encoding="utf-8") as f:
        json.dump(devices, f, ensure_ascii=False, indent=2)


def resolve_device_id(params: Optional[Dict[str, Any]] = None) -> int:
    params = params or {}
    raw_id = params.get("deviceId")
    if raw_id is not None:
        device_id = int(raw_id)
        if device_id > 0:
            return device_id
        raise ValueError("deviceId 必须大于 0")

    device_name = str(params.get("deviceName") or params.get("name") or "").strip()
    devices = load_devices()
    if device_name:
        for item in devices:
            if item.get("name") == device_name:
                return int(item["deviceId"])
        raise ValueError(f"devices.json 中不存在设备: {device_name}")

    if len(devices) == 1:
        return int(devices[0]["deviceId"])
    if not devices:
        raise ValueError("缺少 deviceId，请先运行 device-list.py 生成 .cache/devices.json")
    names = ", ".join(item["name"] for item in devices)
    raise ValueError(f"存在多个设备，请指定 deviceName 或 deviceId。可选: {names}")


def resolve_publish_key(params: Optional[Dict[str, Any]] = None) -> str:
    params = params or {}
    for key in ("publishKey", "deviceUrl", "url"):
        value = params.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    device_name = str(params.get("deviceName") or params.get("name") or "").strip()
    devices = load_devices()
    if device_name:
        for item in devices:
            if item.get("name") == device_name and item.get("url"):
                return str(item["url"])
        raise ValueError(f"devices.json 中不存在设备: {device_name}")

    if len(devices) == 1 and devices[0].get("url"):
        return str(devices[0]["url"])
    if not devices:
        raise ValueError("缺少 publishKey，请先运行 device-list.py 生成 .cache/devices.json")
    names = ", ".join(item["name"] for item in devices)
    raise ValueError(f"存在多个设备，请指定 deviceName。可选: {names}")


def parse_publish_key(publish_key: str) -> Dict[str, str]:
    parsed = urlparse(publish_key.strip())
    query = parsed.query
    values = {}
    for part in query.split("&"):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        values[k] = v
    app_key = values.get("appkey", "").strip()
    tag = values.get("tag", "").strip()
    if not app_key:
        raise ValueError("publishKey URL 缺少 appkey 参数")
    return {"appkey": app_key, "tag": tag}
