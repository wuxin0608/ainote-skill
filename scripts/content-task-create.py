#!/usr/bin/env python3
"""content-task-create：创建全案文案任务（简化入参，脚本侧拼网页同款 body）"""

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


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    p = with_project_id(params)
    goal = str(p.get("goal") or p.get("topic") or "").strip()
    if not goal:
        raise ValueError("缺少 goal（推广方向）")

    use_ai = p.get("use_ai_topics")
    if use_ai is None:
        use_ai = p.get("useAiTopics")
    if use_ai is None:
        use_ai = True
    use_ai = bool(use_ai)

    raw_types = p.get("content_types") or p.get("contentTypes") or DEFAULT_CONTENT_TYPES
    if isinstance(raw_types, str):
        content_types = [x.strip() for x in raw_types.split(",") if x.strip()]
    elif isinstance(raw_types, list):
        content_types = [str(x).strip() for x in raw_types if str(x).strip()]
    else:
        content_types = list(DEFAULT_CONTENT_TYPES)

    selected = p.get("selected_topics") or p.get("selectedTopics") or []
    if not isinstance(selected, list):
        selected = []

    body: Dict[str, Any] = {
        "project_id": p["project_id"],
        "brief": {
            "goal": goal,
            "topic": goal,
            "audience": str(p.get("audience") or "").strip(),
            "actionId": "auto",
            "actionLabel": "AI 自动推荐",
        },
        "use_ai_topics": use_ai,
        "selected_topics": selected,
        "content_type_config": _build_content_type_config(content_types),
    }

    payload = request_api("POST", "/v1/project_task/create", body=body, timeout=120)
    info = payload.get("info") or payload.get("data", {}).get("info") or payload.get("data") or {}
    task_id = info.get("id") if isinstance(info, dict) else None
    result: Dict[str, Any] = {"info": info, "result": payload}
    if task_id is not None:
        result["taskId"] = int(task_id)
    return result


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python content-task-create.py \'{"goal":"推广方向","use_ai_topics":true,"content_types":["xiaohongshu"]}\'',
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
