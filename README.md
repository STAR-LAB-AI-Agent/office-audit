# AI Office 文档审计

AI Office 文档审计是“智能体开发实战”课程中的 Word 文档审计 Skill，对应选题 `#03 AI Office 文档审计`。

该项目用于在 Word 文档提交前检查标题层级、漏填内容、占位符和明显的格式异常，并逐项列出目前无法直接审计的对象。当前版本专注 `.docx`，审计过程只读，不会修改原文。

项目可以直接当 Python CLI 使用，也可以接入 Codex、Nanobot 和 Claude Code。三个入口共用同一套审计代码，避免不同智能体跑出不同规则。

截至 2026-09-11，当前分支为 `main`，已配置 GitHub `origin` <https://github.com/STAR-LAB-AI-Agent/office-audit.git>，仓库根目录已提供 MIT `LICENSE`。测试、宿主兼容、公开候选和发布边界汇总在 [`docs/validation-status.md`](docs/validation-status.md)，其他报告保留实验过程和分析；最终公开交付尚未完成。

## 能检查什么

目前有三种模式：

- `full`：结构、字段和基础格式一起检查；
- `structure`：检查标题层级、章节顺序和用户指定的必需章节；
- `fields_format`：检查空段落、空单元格、常见占位符和格式离群。

必需章节由用户提供，程序不会默认所有文档都要有“摘要、正文、参考文献”之类的固定结构。没有章节清单时，报告会注明“未指定标准”，然后继续完成其他检查。

正文、表格、嵌套表格以及实际使用的页眉页脚会参与审计。图片、文本框、形状、OLE、SmartArt、批注和修订目前还不能直接解析，但程序会逐个记录它们的位置、数量和可能漏检的内容，不会用一句“存在未审计对象”带过。

## 快速开始

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

`requirements.txt` 当前只声明一项直接第三方运行依赖：

| 依赖 | 版本约束 | 许可证 | 官方来源 | 在项目中的用途 |
| --- | --- | --- | --- | --- |
| `python-docx` | `>=1.2,<2` | MIT | [python-docx 官方仓库](https://github.com/python-openxml/python-docx) | 读取并遍历 `.docx` 的正文、表格、嵌套表格、页眉页脚、样式和相关 OOXML 结构 |

版本范围直接来自 [`requirements.txt`](requirements.txt)，表示兼容区间，并未锁定某个精确安装版本。许可证和来源与当前安装包元数据及项目内[开源代码报告](docs/open-source-code-report.md)的记录一致；上游许可证原文见 [python-docx LICENSE](https://github.com/python-openxml/python-docx/blob/master/LICENSE)。当前环境的实际安装版本记录在[验收状态](docs/validation-status.md)。

跑一次完整审计：

```powershell
python scripts/audit_docx.py `
  --input "path\to\document.docx" `
  --mode full `
  --format json `
  --output "reports\audit.json"
```

也可以直接传自然语言请求：

```powershell
python scripts/audit_docx.py `
  --input "path\to\document.docx" `
  --request "只检查标题层级和缺失章节" `
  --format markdown `
  --output "reports\structure.md"
```

需要按指定目录检查时，把章节名称逐行写进文本文件：

```powershell
python scripts/audit_docx.py `
  --input "path\to\document.docx" `
  --mode structure `
  --required-sections "config\required-sections.txt" `
  --format markdown `
  --output "reports\structure.md"
```

输出路径和输入路径相同时，程序会拒绝执行。非法文件、错误规则和无法解析的文档会返回结构化错误，并使用非零退出码。

## 在智能体里使用

仓库里保留了三个 Skill 入口：

```text
SKILL.md                              Codex 入口
skills/office-audit/SKILL.md          Nanobot 入口
.claude/skills/office-audit/SKILL.md  Claude Code 入口
scripts/audit_docx.py                 审计核心
```

Nanobot 和 Claude Code 都可以直接把本仓库设为 workspace。Codex 可以把仓库链接或安装为名为 `office-audit` 的 Skill。需要绕过当前工作目录差异时，可以使用统一启动器：

```powershell
python skills/office-audit/scripts/run_audit.py `
  --input "path\to\document.docx" `
  --mode full `
  --format json
```

Codex、Nanobot 和 Claude Code 都已经跑过完整审计、结构审计和字段格式审计。具体记录放在 [`docs/runtime-compatibility.md`](docs/runtime-compatibility.md)，Nanobot 的简要操作见 [`docs/nanobot-test-guide.md`](docs/nanobot-test-guide.md)。

## 报告内容

JSON 是主输出格式，另外提供 Markdown 和终端摘要。每条问题都会给出：

- 严重级别和规则编号；
- 正文、表格或页眉页脚中的位置；
- 用于人工核对的附近文字；
- 问题说明和修改建议。

连续空白段落按组报告，给出前后文字、数量和所有技术索引。单个空段默认是 `info`，连续多个是待核对的 `warning`；承载图片、公式或分隔符的段落不作为空段告警。格式离群按角色、样式及表格列分别比较，并列出具体差异。标题候选只提供定位提示，不代表已经确认章节存在或页面排版正确。

可选的 JSONL 日志只记录模式、耗时、对象数量、统计和错误码，不写入正文、证据片段、自然语言请求或密钥。

## 测试

Codex、Nanobot 和 Claude Code 已有端到端验收记录；Antigravity 尚未验证。证据边界见 [`docs/validation-status.md`](docs/validation-status.md) 和 [`docs/runtime-compatibility.md`](docs/runtime-compatibility.md)。单元测试不需要网络或模型密钥：

```powershell
python -m unittest discover -s tests -v
```

2026-09-12 当前验收为 25/25 个 unittest 通过，包含原有16项测试和9项排版正反例测试；后续数量与结果以状态页为准。

受控缺陷样例会在临时目录生成，不会留下测试文档：

```powershell
python scripts/evaluate_controlled_cases.py --format terminal
```

2026-09-11 当前验收为 5/5 组受控样例通过。该结果只覆盖合成的确定性规则样例，不替代公开候选的 PII 和再分发核验。性能测试可以这样运行：

```powershell
python scripts/benchmark_audit.py --sizes 50,200,800 --repeats 3
```

这里的 `summary_char_ratio` 只是证据摘要字符数与输入字符数的比值，不是模型 token 统计。审计核心离线运行，所以 `model_calls` 应为 0。

## 样例和数据

仓库不提交私人文档，也不收录许可证不清楚的公开文件。公开数据候选只在 [`data/public-samples.manifest.json`](data/public-samples.manifest.json) 保存来源、状态和校验信息，相关调查见 [`docs/public-dataset-research.md`](docs/public-dataset-research.md)。

如果已经在仓库外准备好候选文档，可以批量生成不含正文证据的统计摘要：

```powershell
python scripts/evaluate_manifest.py `
  --manifest "data\public-samples.manifest.json" `
  --sample-root "E:\path\outside\repository\docx-samples" `
  --mode full `
  --format markdown `
  --output "reports\external-evaluation.md"
```

想快速看看效果，可以生成一份不含个人信息的演示文档：

```powershell
python scripts/demo_audit.py --output-dir outputs/demo --force
```

## 已知问题

格式比较已按段落角色和表格列分组；同组不足3段或没有过半主导格式时不报告离群。因此小样本组中的异常可能漏检。角色识别依赖样式及有限文本特征，仍不能可靠识别所有手工排版、字体继承和段内混合格式。空白段落是否有意保留仍需结合页面判断。改进前后数据见[阶段1评估](docs/phase1-rule-evaluation.md)。

另外，`.doc`、扫描件和图片内文字暂不支持；文本框、SmartArt、嵌入对象、批注和修订只能识别对象，不能审计其中的内容。项目也没有专门的 PII 检测规则，因此文档质量报告不能当作隐私合规结论。

## 其他文档

- [`docs/validation-status.md`](docs/validation-status.md)：当前验收事实与证据边界；
- [`docs/controlled-cases.md`](docs/controlled-cases.md)：受控样例和期望标签；
- [`docs/performance-baseline.md`](docs/performance-baseline.md)：性能基线；
- [`docs/demo-script.md`](docs/demo-script.md)：演示录制步骤；
- [`docs/experiment-report.md`](docs/experiment-report.md)：阶段实验记录；
- [`docs/ai-safety-case-report.md`](docs/ai-safety-case-report.md)：安全边界说明。

## License

[MIT](LICENSE) © 2026 Wh1t3zZ114
