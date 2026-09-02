"""Generate temporary controlled .docx cases and verify expected audit labels."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from docx import Document
from docx.oxml import OxmlElement

try:
    from .audit_docx import audit_document
except ImportError:  # direct execution from the repository root
    from audit_docx import audit_document


Builder = Callable[[Document], None]


def _clean_general_document(document: Document) -> None:
    document.add_heading("项目说明", level=1)
    document.add_paragraph("这是一份用于规则基线的通用项目说明。")
    document.add_paragraph("正文内容完整，便于验证正常文档不会产生警告。")
    table = document.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "字段"
    table.cell(0, 1).text = "值"
    table.cell(1, 0).text = "状态"
    table.cell(1, 1).text = "已完成"


def _heading_level_jump(document: Document) -> None:
    document.add_heading("项目说明", level=1)
    document.add_heading("实现细节直接使用三级标题", level=3)
    document.add_paragraph("这里仅用于验证结构规则。")


def _required_section_missing(document: Document) -> None:
    document.add_heading("项目说明", level=1)
    document.add_paragraph("用户要求的风险章节没有出现在该文档中。")


def _empty_placeholder_and_format(document: Document) -> None:
    document.add_heading("字段与格式", level=1)
    document.add_paragraph("同类正文一")
    document.add_paragraph("同类正文二")
    outlier = document.add_paragraph("同类正文格式离群")
    outlier.runs[0].bold = True
    document.add_paragraph("")
    document.add_paragraph("TODO：提交前补充本字段。")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "字段"
    table.cell(0, 1).text = ""


def _unsupported_drawing_object(document: Document) -> None:
    document.add_heading("对象检查", level=1)
    document.add_paragraph("正文仍可读取，但绘图对象内部文字不纳入第一版语义审计。")
    paragraph = document.add_paragraph()
    run = paragraph.add_run()
    run._r.append(OxmlElement("w:drawing"))


BUILDERS: dict[str, Builder] = {
    "clean_general_document": _clean_general_document,
    "heading_level_jump": _heading_level_jump,
    "required_section_missing": _required_section_missing,
    "empty_placeholder_and_format": _empty_placeholder_and_format,
    "unsupported_drawing_object": _unsupported_drawing_object,
}


def _load_manifest(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping) or not isinstance(value.get("cases"), list):
        raise ValueError("受控样例清单必须是包含 cases 数组的 JSON 对象")
    return value


def _check_case(case: Mapping[str, Any], root: Path) -> dict[str, Any]:
    case_id = str(case.get("id", ""))
    builder_name = str(case.get("builder", ""))
    builder = BUILDERS.get(builder_name)
    if not case_id or builder is None:
        return {
            "id": case_id or builder_name or "<unknown>",
            "passed": False,
            "errors": ["缺少有效 id 或未知 builder"],
        }

    input_path = root / f"{case_id}.docx"
    document = Document()
    builder(document)
    document.save(input_path)
    result = audit_document(
        input_path,
        mode=str(case.get("mode", "full")),
        required_sections=case.get("required_sections"),
    )

    errors: list[str] = []
    if result.get("errors"):
        errors.append(f"审计返回 errors={result['errors']!r}")

    findings = result.get("findings", [])
    for expected in case.get("expected_findings", []):
        if not isinstance(expected, Mapping):
            errors.append(f"无效 expected_findings 项：{expected!r}")
            continue
        matches = [item for item in findings if item.get("rule_id") == expected.get("rule_id")]
        if not matches:
            errors.append(f"未命中 finding 规则：{expected.get('rule_id')}")
            continue
        expected_severity = expected.get("severity")
        if expected_severity and not any(item.get("severity") == expected_severity for item in matches):
            errors.append(
                f"finding 规则 {expected.get('rule_id')} 未出现期望级别 {expected_severity}"
            )

    unsupported = result.get("unsupported_objects", [])
    unsupported_types = {item.get("object_type") for item in unsupported}
    for expected_type in case.get("expected_unsupported", []):
        if expected_type not in unsupported_types:
            errors.append(f"未命中 unsupported object 类型：{expected_type}")

    for severity, expected_count in dict(case.get("expected_summary", {})).items():
        actual_count = result.get("summary", {}).get(severity)
        if actual_count != expected_count:
            errors.append(f"summary.{severity} 期望 {expected_count}，实际 {actual_count}")

    return {
        "id": case_id,
        "description": str(case.get("description", "")),
        "passed": not errors,
        "summary": result.get("summary", {}),
        "findings": sorted({item.get("rule_id") for item in findings}),
        "unsupported": sorted(unsupported_types),
        "errors": errors,
    }


def evaluate(manifest_path: Path) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    with tempfile.TemporaryDirectory(prefix="ai-office-controlled-") as temp:
        root = Path(temp)
        cases = [_check_case(case, root) for case in manifest["cases"] if isinstance(case, Mapping)]
    passed = all(bool(item.get("passed")) for item in cases) and len(cases) == len(manifest["cases"])
    return {
        "schema_version": "1.0",
        "manifest": str(manifest_path),
        "case_count": len(cases),
        "passed_count": sum(bool(item.get("passed")) for item in cases),
        "failed_count": sum(not bool(item.get("passed")) for item in cases),
        "raw_documents_retained": False,
        "network_used": False,
        "passed": passed,
        "cases": cases,
    }


def render_report(report: Mapping[str, Any], format_name: str) -> str:
    if format_name == "json":
        return json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    lines = [
        "# 受控 Word 缺陷样例验收",
        "",
        f"- 结果：{'通过' if report.get('passed') else '失败'}",
        f"- 样例：{report.get('case_count', 0)}，通过：{report.get('passed_count', 0)}，失败：{report.get('failed_count', 0)}",
        "- 网络：禁用；原始变体：临时生成且不保留",
        "",
        "| 样例 | 结果 | 命中规则 | 未审计对象 | 错误 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for case in report.get("cases", []):
        lines.append(
            "| {id} | {status} | {findings} | {unsupported} | {errors} |".format(
                id=case.get("id", ""),
                status="通过" if case.get("passed") else "失败",
                findings=", ".join(case.get("findings", [])) or "无",
                unsupported=", ".join(case.get("unsupported", [])) or "无",
                errors="；".join(case.get("errors", [])) or "无",
            )
        )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate temporary controlled .docx cases and verify labels."
    )
    parser.add_argument(
        "--manifest",
        default="fixtures/controlled-cases.json",
        help="controlled case manifest",
    )
    parser.add_argument("--format", choices=("json", "markdown", "terminal"), default="terminal")
    parser.add_argument("--output", help="optional report path; never stores generated .docx cases")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest_path = Path(args.manifest).expanduser().resolve(strict=False)
    try:
        report = evaluate(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report = {
            "schema_version": "1.0",
            "passed": False,
            "case_count": 0,
            "passed_count": 0,
            "failed_count": 1,
            "errors": [str(exc)],
        }
        rendered = render_report(report, "json" if args.format == "json" else "markdown")
        print(rendered, end="")
        return 2

    rendered = render_report(report, "markdown" if args.format in {"markdown", "terminal"} else "json")
    if args.output:
        output_path = Path(args.output).expanduser().resolve(strict=False)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["BUILDERS", "build_parser", "evaluate", "main", "render_report"]
