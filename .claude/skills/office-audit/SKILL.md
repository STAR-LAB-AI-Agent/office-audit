---
name: office-audit
description: "Audit general Word .docx documents in read-only mode for structure, user-defined required sections, empty fields, placeholders, basic formatting consistency, and unsupported objects. Use when the user asks Claude Code to inspect a Word document and generate an audit report."
---

# Office Audit

Read the repository-root `SKILL.md` for the complete workflow and safety boundaries. This project keeps one audit engine for every agent host; do not create a separate Claude-specific implementation.

Run the shared launcher from the repository workspace:

```powershell
python skills/office-audit/scripts/run_audit.py --input "path\to\document.docx" --mode full --format markdown --output "reports\audit.md"
```

Use `full`, `structure`, or `fields_format` according to the request, or pass a clear natural-language request with `--request`. Never overwrite the input document. Report unsupported objects individually, and do not describe the current rules as a PII or legal-compliance audit.
