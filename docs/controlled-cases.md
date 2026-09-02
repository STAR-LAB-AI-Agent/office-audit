# 受控缺陷样例与标签

fixtures/controlled-cases.json 是不含原始文档的期望标签清单，scripts/evaluate_controlled_cases.py 每次运行时在系统临时目录生成对应 .docx，调用真实审计器并比对标签。临时文件不写入仓库，也不联网。

## 覆盖的受控情况

| 样例 | 预期验证 |
| --- | --- |
| clean-general-document | 正常通用文档不产生 error/warning |
| heading-level-jump | 一级标题后直接出现三级标题，命中 structure.heading_level_jump |
| required-section-missing | 用户明确提供章节清单后，缺项命中 error |
| empty-placeholder-and-format | 空段落、空单元格、TODO 占位符和格式离群分别命中 |
| unsupported-drawing-object | 绘图对象单独出现在 unsupported_objects，而不是一句笼统提示 |

## 复现命令

    python scripts\evaluate_controlled_cases.py --format terminal
    python scripts\evaluate_controlled_cases.py --format json --output reports\controlled-cases.json

通过条件是所有样例的期望标签都命中、摘要约束满足且审计器没有结构化错误。该验收证明的是确定性规则和安全边界，不替代真实公开文档的人工 PII、许可证和再分发核验。
