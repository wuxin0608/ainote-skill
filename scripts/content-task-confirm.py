#!/usr/bin/env python3
"""content-task-confirm：确认选题并触发生成（topics/update + generate）"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from common import request_api


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    task_id = params.get("taskId") or params.get("id") or params.get("project_task_id")
    if task_id is None:
        raise ValueError("缺少 taskId")
    task_id = int(task_id)
    if task_id <= 0:
        raise ValueError("taskId 必须大于 0")

    topics = params.get("topics")
    updated = None
    if topics is not None:
        if not isinstance(topics, list):
            raise ValueError("topics 必须是数组")
        updated = request_api(
            "POST",
            "/v1/project_task_topics/update",
            body={"project_task_id": task_id, "topics": topics},
        )

    generated = request_api(
        "POST",
        "/v1/project_task/generate",
        body={"id": task_id},
        timeout=120,
    )
    return {
        "taskId": task_id,
        "topicsUpdated": updated is not None,
        "topicsResult": updated,
        "generateResult": generated,
    }


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(
            '用法: python content-task-confirm.py \'{"taskId":123,"topics":[{"id":1,"selected":true,"use_count":1}]}\'',
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
