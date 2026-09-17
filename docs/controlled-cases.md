# 受控缺陷样例与评测体系（阶段2）

- 更新日期：2026-09-15
- 标签清单：`fixtures/controlled-cases.json`（版本 1.1）
- 评测脚本：`scripts/evaluate_controlled_cases.py`
- 运行机制：每次运行时在系统临时目录生成对应 `.docx`，调用真实确定性审计内核并比对标签。运行完毕后临时目录自动销毁，不向仓库写入文档变体，完全离线运行。

## 一、覆盖的受控情况（15组）

| 样例 ID | 审计模式 | 核心验证目标与边界 | 预期命中规则 | 明确不应命中规则 |
| :--- | :--- | :--- | :--- | :--- |
| `clean-general-document` | `full` | 正常通用文档基线，无 warning/error | `structure.required_sections_not_specified` (info) | `format.dominant_style_outlier`, `structure.heading_level_jump`, `fields.empty_paragraph`, `fields.empty_cell`, `fields.placeholder` |
| `heading-level-jump` | `structure` | 标题层级跳级（H1后直接出现H3） | `structure.heading_level_jump` (warning) | `structure.required_section_missing` |
| `required-section-missing` | `structure` | 显式要求章节缺失 | `structure.required_section_missing` (error) | `structure.heading_level_jump` |
| `empty-placeholder-and-format` | `fields_format` | 综合缺陷：空段落(info)、空单元格、TODO占位符、正文格式离群 | `fields.empty_paragraph`, `fields.empty_cell`, `fields.placeholder`, `format.dominant_style_outlier` | 无 |
| `unsupported-drawing-object` | `full` | 绘图XML对象，验证逐项未审计登记 | `structure.required_sections_not_specified` (info)；未审计对象包含 `image_or_drawing` | `format.dominant_style_outlier`, `fields.empty_paragraph` |
| `clean-rich-layout` | `full` | 富文本正常排版（合法标题、列表、块引用、规整表格）不产生任何误报 | 无缺陷与提示（提供必需章节） | `format.dominant_style_outlier`, `structure.heading_level_jump`, `structure.required_section_missing`, `fields.empty_paragraph`, `fields.empty_cell`, `fields.placeholder` |
| `single-empty-paragraph` | `fields_format` | 段落间单个空段降级为 info 提示而非 warning | `fields.empty_paragraph` (info) | `format.dominant_style_outlier` |
| `consecutive-empty-paragraphs` | `fields_format` | 连续3个空段合并报告为 warning 且保留完整索引 | `fields.empty_paragraph` (warning) | `format.dominant_style_outlier` |
| `table-boundary-blanks` | `fields_format` | 表格前后空段不跨表格合并，分别独立报告为 info | `fields.empty_paragraph` (info, 2条) | `format.dominant_style_outlier` |
| `content-carrier-paragraphs` | `full` | 段落含绘图、公式或分页符，不误判为空白段落 | `structure.required_sections_not_specified` (info)；未审计对象包含 `image_or_drawing`、`equation` | `fields.empty_paragraph`, `format.dominant_style_outlier` |
| `visual-title-candidate` | `structure` | 视觉标题候选提示 (info)，且不能直接抵扣必需章节要求 (error) | `structure.title_candidate` (info), `structure.required_section_missing` (error), `structure.no_headings` (info) | `structure.heading_level_jump` |
| `table-column-baselines` | `fields_format` | 表格列独立格式基线，表头与各数据列合法样式差异不报离群 | 无 | `format.dominant_style_outlier`, `fields.empty_cell` |
| `table-cell-outlier` | `fields_format` | 表格同列中单格字体样式突变，精准命中离群警告 | `format.dominant_style_outlier` (warning) | `fields.empty_cell` |
| `no-majority-format` | `fields_format` | 多种格式各异且无任何格式严格过半，保守原则不报离群 | 无 | `format.dominant_style_outlier` |
| `unsupported-mixed-objects` | `full` | 复合未审计对象（批注、文本框、OLE对象）逐项分类登记 | `structure.required_sections_not_specified` (info)；未审计对象包含 `comment`, `text_box`, `ole_object` | `format.dominant_style_outlier`, `fields.empty_paragraph` |

---

## 二、指标定义与统计口径

为杜绝“只验证应该出现的出现了”导致的漏测，评测体系引入正反双向声明：

1. **评价范围**：仅针对缺陷规则（`warning` 与 `error` 级别）；信息提示（`info`）、未审计对象（`unsupported_objects`）和运行错误独立核查，不混入缺陷混淆矩阵。
2. **文档-规则级混淆矩阵**：
   - **真正例 (TP)**：预期命中且实际命中的缺陷规则；
   - **假正例 (FP)**：非预期触发或命中 `expected_absent_rules` 的缺陷告警（误报）；
   - **假反例 (FN)**：预期命中但实际未触发的缺陷告警（漏报）；
   - **真反例 (TN)**：明确声明不应出现且实际未出现的规则。
3. **指标公式**：
   - $	ext{Precision} = rac{	ext{TP}}{	ext{TP} + 	ext{FP}}$（分母为0时显示为“不适用 (N/A)”）；
   - $	ext{Recall} = rac{	ext{TP}}{	ext{TP} + 	ext{FN}}$（分母为0时显示为“不适用 (N/A)”）。
4. **指标边界声明**：受控合成样例指标仅反映预设测试集对已知确定性规则的覆盖能力，**不代表真实复杂文档的整体准确率**。真实文档准确性以人工页面复核为准（详见 [真实文档重点复核记录](real-samples-review.md)）。

---

## 三、复现与验证命令

```powershell
# 终端格式（含指标汇总与逐例明细）
python scripts/evaluate_controlled_cases.py --format terminal

# JSON 格式输出到文件
python scripts/evaluate_controlled_cases.py --format json --output reports/controlled-cases.json

# 评测框架自身回归单测（含故意误报与故意漏报检测）
python -m unittest tests/test_controlled_cases.py -v
```
