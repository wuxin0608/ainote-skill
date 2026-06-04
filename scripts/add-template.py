#!/usr/bin/env python3
"""add-template：导入笔记模板"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from common import request_skill, resolve_publish_key


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    publish_key = resolve_publish_key(params)
    title = str(params.get("title") or "").strip()
    text = str(params.get("text") or params.get("desc") or "").strip()
    imgs = params.get("imgs") or params.get("urls") or []
    if isinstance(imgs, str):
        imgs = [imgs]
    if not title or not text or not imgs:
        raise ValueError("缺少 title、text 或 imgs")

    body: Dict[str, Any] = {
        "publishKey": publish_key,
        "title": title,
        "text": text,
        "imgs": list(imgs),
    }
    tag = params.get("tag")
    if tag:
        body["tag"] = str(tag)
    original_id = params.get("originalId") or params.get("original_id")
    if original_id:
        body["originalId"] = str(original_id)

    payload = request_skill("/v/ainote/skill/add/template", body)
    return {"templateResult": payload}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add xhs template via ainote skill API.")
    parser.add_argument("--params", default=None, help="JSON 参数对象")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.params:
        print(
            '用法: python add-template.py \'{"title":"...","text":"...","imgs":["https://..."],"deviceName":"设备名"}\'',
            file=sys.stderr,
        )
        return 1
    try:
        params = json.loads(args.params)
        if not isinstance(params, dict):
            raise ValueError("--params 必须是 JSON 对象")
        result = run(params)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
