"""Evaluate locally staged .docx candidates from a metadata-only manifest.

The evaluator deliberately does not download files, update the manifest, or
write document findings into the public metadata directory.  It is a safe
bridge between a public candidate list and raw files kept outside the Git
repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .audit_docx import SUPPORTED_MODES, audit_document
except ImportError:  # direct ``python scripts/evaluate_manifest.py`` execution
    from audit_docx import SUPPORTED_MODES, audit_document


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "data" / "public-samples.manifest.json"
SAMPLE_ID_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ManifestError(Exception):
    """An expected manifest or evaluator input error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _resolved_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve(strict=False)


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        raise ManifestError("manifest_not_found", f"manifest 文件不存在：{path}") from None
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError("invalid_manifest", f"manifest 不是可解析的 JSON：{type(exc).__name__}") from None
    if not isinstance(value, dict):
        raise ManifestError("invalid_manifest", "manifest 顶层必须是 JSON 对象")
    candidates = value.get("candidates", {})
    records = candidates.get("records", []) if isinstance(candidates, Mapping) else None
    if not isinstance(records, list):
        raise ManifestError("invalid_manifest", "manifest.candidates.records 必须是数组")
    return value


def _candidate_path(record: Mapping[str, Any], sample_root: Path) -> Path:
    candidate_id = str(record.get("id", ""))
    if not SAMPLE_ID_PATTERN.fullmatch(candidate_id):
        raise ManifestError("invalid_candidate_id", "候选记录 id 必须是 64 位小写十六进制字符串")
    configured = record.get("local_path_outside_git")
    if configured:
        raw = Path(str(configured)).expanduser()
        return _resolved_path(raw if raw.is_absolute() else sample_root / raw)
    # Never use the untrusted source filename to construct a local path.
    return _resolved_path(sample_root / f"{candidate_id}.docx")


def _sha256_and_size(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def _audit_projection(result: Mapping[str, Any]) -> dict[str, Any]:
    errors = result.get("errors", [])
    error_codes = [str(item.get("code", "error")) for item in errors if isinstance(item, Mapping)]
    return {
        "summary": dict(result.get("summary", {})),
        "metrics": dict(result.get("metrics", {})),
        "finding_count": len(result.get("findings", [])),
        "unsupported_object_count": len(result.get("unsupported_objects", [])),
        "error_codes": error_codes,
    }


def _evaluate_record(record: Mapping[str, Any], sample_root: Path | None, mode: str) -> dict[str, Any]:
    candidate_id = str(record.get("id", ""))
    item: dict[str, Any] = {
        "id": candidate_id,
        "manifest_status": record.get("status"),
        "metadata_status": record.get("metadata_status"),
        "local_status": "pending_local_input",
        "audit": None,
        "observed_byte_size": None,
        "observed_sha256": None,
        "error_codes": [],
        "note": "未提供本地样例；评估器不会联网下载文档",
    }
    if sample_root is None:
        return item

    try:
        path = _candidate_path(record, sample_root)
    except ManifestError as exc:
        item["local_status"] = "invalid_metadata"
        item["error_codes"] = [exc.code]
        item["note"] = exc.message
        return item
    if not path.exists():
        return item
    if not path.is_file():
        item["local_status"] = "invalid_local_input"
        item["error_codes"] = ["local_input_not_file"]
        item["note"] = "候选路径不是文件"
        return item
    if path.suffix.casefold() != ".docx":
        item["local_status"] = "invalid_local_input"
        item["error_codes"] = ["unsupported_local_format"]
        item["note"] = "外部样例必须是 .docx"
        return item

    byte_size, observed_sha256 = _sha256_and_size(path)
    item["observed_byte_size"] = byte_size
    item["observed_sha256"] = observed_sha256
    expected_sha256 = record.get("local_sha256")
    if expected_sha256 is not None:
        expected_text = str(expected_sha256).casefold()
        if not SHA256_PATTERN.fullmatch(expected_text):
            item["local_status"] = "invalid_metadata"
            item["error_codes"] = ["invalid_manifest_sha256"]
            item["note"] = "manifest.local_sha256 必须是 64 位小写十六进制字符串"
            return item
        if expected_text != observed_sha256:
            item["local_status"] = "hash_mismatch"
            item["error_codes"] = ["local_sha256_mismatch"]
            item["note"] = "本地样例哈希与 manifest 不一致；未继续审计"
            return item

    result = audit_document(path, mode=mode)
    projection = _audit_projection(result)
    item["local_status"] = "audited" if not projection["error_codes"] else "audit_error"
    item["audit"] = projection
    item["error_codes"] = projection["error_codes"]
    item["note"] = "仅保留审计统计；正文证据不会被该评估器写入 manifest"
    return item


def _summarize(items: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    statuses = [str(item.get("local_status", "unknown")) for item in items]
    return {
        "selected": len(items),
        "audited": statuses.count("audited"),
        "pending_local_input": statuses.count("pending_local_input"),
        "hash_mismatch": statuses.count("hash_mismatch"),
        "audit_error": statuses.count("audit_error"),
        "invalid_input_or_metadata": sum(
            status in {"invalid_metadata", "invalid_local_input"} for status in statuses
        ),
    }


def evaluate_manifest(
    manifest_path: str | Path = DEFAULT_MANIFEST,
    *,
    sample_root: str | Path | None = None,
    mode: str = "full",
    limit: int | None = None,
) -> dict[str, Any]:
    """Evaluate candidate files that already exist in a caller-supplied directory."""

    if mode not in SUPPORTED_MODES:
        raise ManifestError("invalid_mode", f"不支持的审计模式：{mode}")
    if limit is not None and limit <= 0:
        raise ManifestError("invalid_limit", "limit 必须是正整数")
    path = _resolved_path(manifest_path)
    manifest = _load_manifest(path)
    records = manifest["candidates"]["records"]
    selected_records = records[:limit] if limit is not None else records
    root = _resolved_path(sample_root) if sample_root is not None else None
    errors: list[dict[str, str]] = []
    if root is not None and not root.is_dir():
        errors.append({"code": "sample_root_not_found", "message": f"本地样例目录不存在：{root}"})
        root = None

    items = [
        _evaluate_record(record, root, mode)
        for record in selected_records
        if isinstance(record, Mapping)
    ]
    return {
        "schema_version": "1.0",
        "manifest": {
            "path": str(path),
            "candidate_status": manifest["candidates"].get("status"),
            "candidate_total": len(records),
            "evaluated_selection": len(selected_records),
        },
        "mode": mode,
        "network_access": False,
        "writes_to_manifest": False,
        "raw_documents_in_report": False,
        "summary": _summarize(items),
        "errors": errors,
        "samples": items,
    }


def render_evaluation(result: Mapping[str, Any], format_name: str = "json") -> str:
    if format_name == "json":
        return json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if format_name not in {"markdown", "terminal"}:
        raise ValueError(f"unsupported output format: {format_name}")
    summary = result.get("summary", {})
    lines = [
        "# 公开文档候选评估",
        f"- 模式：{result.get('mode', '')}",
        f"- 候选：{summary.get('selected', 0)}，已审计：{summary.get('audited', 0)}，待本地样例：{summary.get('pending_local_input', 0)}",
        f"- 哈希不匹配：{summary.get('hash_mismatch', 0)}，评估错误：{summary.get('audit_error', 0)}",
        "- 网络下载：禁用；manifest 写入：禁用；报告不保留正文证据",
        "",
        "## 样例状态",
    ]
    for item in result.get("samples", []):
        audit = item.get("audit") or {}
        audit_summary = audit.get("summary", {})
        lines.append(
            f"- `{item.get('id', '')}`：{item.get('local_status', '')}；"
            f"error={audit_summary.get('error', 0)}，warning={audit_summary.get('warning', 0)}，"
            f"info={audit_summary.get('info', 0)}；{item.get('note', '')}"
        )
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate metadata-manifest .docx candidates without network downloads or manifest writes."
    )
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="metadata-only manifest path")
    parser.add_argument("--sample-root", help="directory containing external files named <candidate-id>.docx")
    parser.add_argument("--mode", choices=SUPPORTED_MODES, default="full")
    parser.add_argument("--limit", type=int, help="evaluate only the first N manifest records")
    parser.add_argument("--format", choices=("json", "markdown", "terminal"), default="json")
    parser.add_argument("--output", help="write a separate evaluation report")
    return parser


def _write_output(path_value: str, content: str, manifest_path: Path) -> None:
    output_path = _resolved_path(path_value)
    if output_path == manifest_path:
        raise ManifestError("unsafe_output_path", "评估报告不能覆盖 manifest")
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise ManifestError("output_write_failed", f"评估报告写入失败：{type(exc).__name__}") from None


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = evaluate_manifest(
            args.manifest,
            sample_root=args.sample_root,
            mode=args.mode,
            limit=args.limit,
        )
        rendered = render_evaluation(result, args.format)
        if args.output:
            _write_output(args.output, rendered, _resolved_path(args.manifest))
        else:
            sys.stdout.write(rendered)
    except ManifestError as exc:
        result = {
            "schema_version": "1.0",
            "mode": getattr(args, "mode", "full"),
            "summary": {},
            "errors": [{"code": exc.code, "message": exc.message}],
            "samples": [],
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        return 2
    return 2 if result.get("errors") or result.get("summary", {}).get("hash_mismatch", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["build_parser", "evaluate_manifest", "main", "render_evaluation"]
