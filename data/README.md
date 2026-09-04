# data/ 目录说明：公开文档样例清单（仅元数据）

本目录是 `ai-office-document-audit-skill` 的公开样例元数据区。唯一权威清单是
[public-samples.manifest.json](./public-samples.manifest.json)——它只记录元数据和核验结论，
**不包含、也不允许包含任何原始文档内容**。核验依据见 [docs/public-dataset-research.md](../docs/public-dataset-research.md)（2026-09-02，第一方来源核验）。

## 1. 原始 .docx 不进 Git

- `.gitignore` 已排除 `data/raw/`、`data/external/`、`data/downloads/`、`data/cache/`。原始文档只能存放在
  这些被忽略目录或仓库外，任何情况下都不得把 .docx 原文、`extracted/*.txt` 全文提交进 Git。
- manifest 中的 `local_path_outside_git` 字段只记录仓库外本地路径，作为取用索引，不代表文件进入仓库。
- 本仓库当前有 12 条 `pending` 候选元数据记录（`candidates.records`），没有把任何原始文档提交到仓库；候选记录不等于已通过许可或 PII 审查。2026-09-02 曾对前 3 条候选做仓库外临时预检；2026-09-04 已将 12 条候选全部下载到仓库外的 `E:\大学\专业实习\external-samples`，并记录下载报告和离线评估报告。原始文档仍不进入仓库。

## 2. 元数据/代码与文档版权边界

清单按三种对象分别记录许可状态（沿用 VERIFIED / INFERENCE / UNVERIFIED 标注）：

| 对象 | superdoc-dev/docx-corpus + docxcorp.us | DS3Lab/WordScape |
| --- | --- | --- |
| 数据集元数据（含 url 列） | ODC-BY 1.0（官方声明 VERIFIED，四处第一方位置一致；可署名再分发） | 无独立许可声明（UNVERIFIED），列表文件不得入 Git |
| 管道/源码 | MIT（VERIFIED，LICENSE 落款 Harbour Enterprises Inc） | Apache-2.0（VERIFIED） |
| .docx 文档本体 | 版权归原作者（官方声明 VERIFIED）；文件级再分发许可 UNVERIFIED | 不重分发文档（VERIFIED），从原站下载逐站点判定（UNVERIFIED） |

关键红线：**不能因为元数据是 ODC-BY 1.0 就推断可以自由再分发某份文档原文**。公开仓库只进
“逐份核对许可/再分发完成、人工 PII 抽查通过”的少量样例；否则原文留在仓库外，manifest 记录其元数据。

## 3. PII 抽查状态

当前状态：`pii_spot_check.status = "not_started"`，12 条候选记录均为 `pending`，**本清单不含任何 PII 通过结论**。全量下载和离线解析只验证工程链路，不改变这一状态。
后续流程固定为：人工查看预览文本和已下载原文 → 检查正文、复杂文档部件和文件级许可 →
在记录里填写抽查结论 → 全部满足后才允许提升为 `verified`。未抽查的记录一律保持 `pending`，
不得填“通过”。

首轮文本筛查记录在 manifest 的 evidence.preliminary_text_review 中：9 条被标记为需要人工跟进，3 条仅在预览中未发现显式信号；这不是 PII 清除结论，也没有改变任何候选状态。

## 4. 如何补填下载时间 / 字节数 / 本地 SHA-256

候选记录（`pending`）被选中后，逐条补填以下三个字段，**缺一不可**：

- `downloaded_at_utc`：下载时间，UTC、ISO 8601（如 `2026-09-02T12:00:00Z`）。
- `byte_size`：下载文件字节数。
- `local_sha256`：本地自算 SHA-256（小写十六进制）。

⚠️ 实测警示（VERIFIED，2026-09-02）：docxcorp.us 下载的 3 个样本本地 SHA-256 **均不等于**数据源行 id，
与官方“id 即文件 SHA-256”的声明不符。因此 manifest 一律自算，**不得把行 id 当作校验值**。示例命令：

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath "path\to\sample.docx"
```

`local_sha256` 未补填的记录不允许标为 `verified`。

## 5. 候选与已核验样例的状态

每条样例记录的状态枚举：

- `pending`：已从元数据挑选，但 PII、复杂部件或文件级许可核验尚未全部完成；即使下载和哈希字段已经齐备，也必须保持该状态。
- `verified`：逐份许可与再分发核对完成、`downloaded_at_utc`/`byte_size`/`local_sha256` 齐备、
  人工 PII 抽查通过且不含可识别个人信息，才可提升。
- `rejected`：抽查发现 PII、许可不满足或来源不可用，附原因。

当前 12 条候选记录均为 `pending` 是**有意为之**：决策依据（选择标准、过滤条件、必填字段）都写在
`selection_plan` 和 `per_record_required_fields` 里，已先定标准再选元数据；虽然下载和哈希字段已经补齐，许可和 PII 核验尚未完成，不能伪造“已通过”记录。

## 6. 校验方式

```powershell
python -m json.tool data\public-samples.manifest.json > $null
```

## 7. 修改纪律

本仓库是多子任务共享仓库：只追加/更新本 manifest 与 README，不修改或回滚其他任务的改动
（根 README、SKILL.md、phase1-design.md、performance-baseline.md、benchmark_audit.py 等均属他人分区）。
不提交任何原始文档；清单不同时保留同一条记录的两个互相矛盾的许可/哈希结论。仓库外审查目录的文件不得因本地存在就被复制进 Git。
