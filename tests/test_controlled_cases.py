"""Unit tests for the controlled cases evaluator and metrics calculation."""

from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path

from scripts.evaluate_controlled_cases import evaluate, main, render_report

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / "fixtures" / "controlled-cases.json"


class ControlledCasesEvaluatorTests(unittest.TestCase):
    def test_default_manifest_evaluates_and_passes(self) -> None:
        report = evaluate(DEFAULT_MANIFEST)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 15)
        self.assertEqual(report["passed_count"], 15)
        self.assertEqual(report["failed_count"], 0)
        self.assertFalse(report["raw_documents_retained"])
        self.assertFalse(report["network_used"])

        metrics = report["metrics"]
        self.assertEqual(metrics["scope"], "warning_and_error_defects")
        self.assertEqual(metrics["fp"], 0)
        self.assertEqual(metrics["fn"], 0)
        self.assertGreater(metrics["tp"], 0)
        self.assertEqual(metrics["precision"], 1.0)
        self.assertEqual(metrics["recall"], 1.0)
        self.assertIn("不代表真实文档整体准确率", report["disclaimer"])

    def test_intentional_false_positive_triggers_failure(self) -> None:
        # table_cell_outlier generates format.dominant_style_outlier (warning)
        bad_manifest = {
            "cases": [
                {
                    "id": "fp-test",
                    "builder": "table_cell_outlier",
                    "mode": "fields_format",
                    "description": "测试故意声明不应出现但实际出现的误报",
                    "expected_findings": [],
                    "expected_absent_rules": ["format.dominant_style_outlier"],
                }
            ]
        }
        report = evaluate(bad_manifest)
        self.assertFalse(report["passed"])
        self.assertEqual(report["failed_count"], 1)
        self.assertGreater(report["metrics"]["fp"], 0)
        case_errors = report["cases"][0]["errors"]
        self.assertTrue(
            any("存在非预期的缺陷规则告警" in err or "命中了明确不应出现的规则" in err for err in case_errors)
        )

    def test_intentional_false_negative_triggers_failure(self) -> None:
        # clean_general_document does NOT have heading_level_jump
        bad_manifest = {
            "cases": [
                {
                    "id": "fn-test",
                    "builder": "clean_general_document",
                    "mode": "structure",
                    "description": "测试故意要求出现但实际未出现的漏报",
                    "expected_findings": [
                        {"rule_id": "structure.heading_level_jump", "severity": "warning"}
                    ],
                }
            ]
        }
        report = evaluate(bad_manifest)
        self.assertFalse(report["passed"])
        self.assertEqual(report["failed_count"], 1)
        self.assertGreater(report["metrics"]["fn"], 0)
        case_errors = report["cases"][0]["errors"]
        self.assertTrue(
            any("未命中 finding 规则" in err or "缺少预期的缺陷规则告警" in err for err in case_errors)
        )

    def test_zero_division_metrics_handled_cleanly(self) -> None:
        clean_only_manifest = {
            "cases": [
                {
                    "id": "clean-test",
                    "builder": "clean_rich_layout",
                    "mode": "full",
                    "required_sections": ["第一章 总体概述"],
                    "expected_findings": [],
                    "expected_absent_rules": [],
                }
            ]
        }
        report = evaluate(clean_only_manifest)
        self.assertTrue(report["passed"])
        metrics = report["metrics"]
        self.assertIsNone(metrics["precision"])
        self.assertIsNone(metrics["recall"])

        rendered = render_report(report, "terminal")
        self.assertIn("精确率 (Precision)：不适用 (N/A)", rendered)
        self.assertIn("召回率 (Recall)：不适用 (N/A)", rendered)

    def test_cli_exit_codes(self) -> None:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(main(["--manifest", str(DEFAULT_MANIFEST), "--format", "json"]), 0)
            self.assertEqual(main(["--manifest", "non_existent_path.json"]), 2)


if __name__ == "__main__":
    unittest.main()
