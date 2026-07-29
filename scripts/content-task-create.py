#!/usr/bin/env python3
"""content-task-create：创建全案任务 + 用户已确认选题（skip_ai，不触发后端模型）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api, with_project_id

DEFAULT_CONTENT_TYPES = ["xiaohongshu"]


def _build_content_type_config(content_types: List[str]) -> List[Dict[str, Any]]:
    cfg: List[Dict[str, Any]] = []
    for t in content_types:
        t = str(t).strip()
        if not t:
            continue
        cfg.append(
            {
                "type": t,
                "enabled": True,
                "project_template_ids": [],
                "reference_dirs": [],
                "article_length": "1500",
                "tone": "consultant",
                "project_device_id": None,
            }
        )
    if not cfg:
        return _build_content_type_config(DEFAULT_CONTENT_TYPES)
    return cfg


def _normalize_topics(raw: Any) -> List[Dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        if not title:
            continue
        row: Dict[str, Any] = {
            "title": title,
            "angle": str(item.get("angle") or "").strip(),
            "audience": str(item.get("audience") or "").strip(),
            "use_count": int(item.get("use_count") or item.get("useCount") or 1),
        }
        tid = item.get("project_topic_id") or item.get("projectTopicId")
        if tid is not None:
            row["project_topic_id"] = int(tid)
        out.append(row)
    return out


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    goal = str(p.get("goal") or p.get("topic") or "").strip()
    if not goal:
        raise ValueError("缺少 goal（推广方向）")

    selected = _normalize_topics(p.get("selected_topics") or p.get("selectedTopics") or [])
    if not selected:
        raise ValueError(
            "缺少 selected_topics：请先由 Agent 起草选题并经用户确认后再创建任务"
        )

    raw_types = p.get("content_types") or p.get("contentTypes") or DEFAULT_CONTENT_TYPES
    if isinstance(raw_types, str):
        content_types = [x.strip() for x in raw_types.split(",") if x.strip()]
    elif isinstance(raw_types, list):
        content_types = [str(x).strip() for x in raw_types if str(x).strip()]
    else:
        content_types = list(DEFAULT_CONTENT_TYPES)

    body: Dict[str, Any] = {
        "project_id": p["project_id"],
        "source": "agent",
        "skip_ai": True,
        "brief": {
            "goal": goal,
            "topic": goal,
            "audience": str(p.get("audience") or "").strip(),
            "source": "agent",
            "actionId": "agent",
            "actionLabel": "Agent 选题落库",
        },
        "use_ai_topics": False,
        "selected_topics": selected,
        "content_type_config": _build_content_type_config(content_types),
    }

    payload = request_api("POST", "/v1/project_task/create", body=body, timeout=60)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    result: Dict[str, Any] = {"info": info, "result": payload}
    if isinstance(info, dict) and info.get("id") is not None:
        result["taskId"] = int(info["id"])
        result["topics"] = info.get("topics") or []
    return result


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python content-task-create.py \'{"goal":"推广方向","selected_topics":[{"title":"选题A","angle":"..."}]}\'',
            file=sys.stderr,
        )
        return 1
    try:
        params = json.loads(argv[0])
        if not isinstance(params, dict):
            raise ValueError("参数必须是 JSON 对象")
        print(json.dumps(run(params), ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
