# AI Office 文档审计

这是“智能体开发实战”课程实习的 AI Office 文档审计 Skill。项目对应课程任务书中的 `#03 AI Office 文档审计`，当前已完成可独立运行的 `.docx` 只读审计 CLI、离线自然语言意图路由、性能基线和公开数据元数据清单。项目采用“单一审计内核 + 多宿主 Skill 入口”，不绑定 Codex、Nanobot 或其他某一种智能体。

## 项目定位

项目面向学生、教师以及需要检查日常办公文档的用户，适用对象包括课程报告、通知、会议纪要、制度文件、项目说明、申请材料和模板等通用文档，不把“实习报告”当作唯一模板。当前主格式是 `.docx`；旧式 `.doc`、扫描件、图片文字和复杂嵌入对象不在第一版的直接解析范围内，遇到这些对象时输出明确的未审计对象说明。

审计是只读的：程序读取文档并生成问题清单，不自动修改、覆盖、移动或删除原文。用户可以选择结构化 JSON 作为主结果，也可以同时生成便于阅读的 Markdown 或终端摘要。

## 三类审计模式

1. **完整审计**：综合检查文档结构、空字段/占位内容和基础格式一致性。
2. **结构审计**：检查标题层级、章节顺序、缺失章节以及用户明确提供的必需章节列表。
3. **字段与格式审计**：检查空段落、常见占位符、表格空单元格和文档内部的主导格式异常。

必需章节不会被写死成某一种报告模板。用户提供要求清单时，审计器按清单核对；没有行业或课程标准时，结果明确标记为“未指定标准”，而不是假定所有文档都必须包含同一组章节。

## 当前调用链

```text
自然语言请求 → Agent 意图识别 → Skill 参数整理 → Python CLI
→ python-docx 解析 .docx → 规则审计 → JSON / Markdown / 终端结果
```

当前自然语言层采用透明的关键词路由，不联网、不调用模型；模型适配器可以作为后续增强，但不能绕过只读和确认边界。核心脚本可独立运行，并提供输入路径、自然语言请求、审计模式、必需章节、规则配置和输出格式等参数。

## 通用 Skill 结构

```text
SKILL.md                              # 通用/Codex Skill 入口
agents/openai.yaml                    # Codex 展示与默认提示
skills/office-audit/SKILL.md          # Nanobot 工作区扫描入口
skills/office-audit/scripts/run_audit.py  # 跨宿主薄启动器
scripts/audit_docx.py                 # 唯一审计内核
```

各入口共享同一个审计器和结果协议，不维护多套规则。Nanobot 将本仓库作为 workspace 时会发现 `skills/office-audit/`；Codex 可将仓库根目录安装/链接为名为 `office-audit` 的 Skill。Claude Code、Antigravity 等支持目录型 Skill 的宿主也可映射同一仓库。具体路径和已验证状态见 [`docs/runtime-compatibility.md`](docs/runtime-compatibility.md)，课程环境的操作步骤见 [`docs/nanobot-test-guide.md`](docs/nanobot-test-guide.md)。

## 已实现的 CLI

当前已完成确定性 `.docx` 审计 CLI、结构化结果模型、基础规则、未审计对象逐项告警、独立报告输出、离线自然语言路由、脱敏 JSONL 日志和性能基线。公开数据研究已形成第一方来源核验文档，并在 `data/public-samples.manifest.json` 中登记 12 条候选；原始文档因许可和隐私边界不进入代码仓库。

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

完整审计并生成 JSON 报告：

```powershell
python scripts/audit_docx.py `
  --input "path\to\document.docx" `
  --mode full `
  --format json `
  --output "reports\audit.json" `
  --log "logs\audit.jsonl"
```

也可以直接用自然语言请求推断审计模式；关键词路由会把综合检查、标题/章节检查、空字段/格式检查分别映射到 `full`、`structure`、`fields_format`。范围冲突或无法识别的请求会返回结构化错误，不会擅自选择模式。

```powershell
python scripts/audit_docx.py `
  --input "path\to\document.docx" `
  --request "只看标题层级和缺失章节" `
  --format json
```

结构审计可以通过文本文件提供必需章节，每行一个章节名称；规则文件是 JSON 对象，可配置 `required_sections`、`placeholders` 和 `severity_overrides`。

```powershell
python scripts/audit_docx.py `
  --input "path\to\document.docx" `
  --mode structure `
  --required-sections "config\required-sections.txt" `
  --format markdown `
  --output "reports\structure.md"
```

程序不会保存或改写输入文档；报告输出路径与输入路径相同会被拒绝。非法路径、扩展名、规则文件和不可解析文档会以结构化 `errors` 返回，并使用非零退出码。

本项目不会把真实 API 密钥、密码、私人文档或许可证不明的原始数据提交到 Git。公开文档只在确认许可和再分发条件后作为固定测试样例；其他资料保留来源、下载日期、哈希和许可信息，原文件默认不进入仓库。

## 公开数据与本地评估

公开数据来源和许可边界见 [`docs/public-dataset-research.md`](docs/public-dataset-research.md)，机器可读清单见 [`data/public-samples.manifest.json`](data/public-samples.manifest.json)。当前清单只保留来源元数据和 12 条待核验候选，不携带原始 `.docx`；文件级再分发许可和 PII 抽查完成前，候选不得标为 `verified`。

对存放在仓库外、且按 `<candidate-id>.docx` 命名的本地样例，可以运行只读评估器：

```powershell
python scripts/evaluate_manifest.py `
  --manifest "data\public-samples.manifest.json" `
  --sample-root "E:\path\outside\repository\docx-samples" `
  --mode full `
  --format markdown `
  --output "reports\external-evaluation.md"
```

评估器不会联网下载、不会修改 manifest 或原文，也不会把正文证据写入评估摘要；未提供本地样例时，每条候选会明确显示为 `pending_local_input`。

## 演示与阶段报告

可以用无个人信息的合成文档录制端到端演示：

```powershell
python scripts\demo_audit.py --output-dir outputs\demo --force
```

演示分镜见 [`docs/demo-script.md`](docs/demo-script.md)，当前阶段性实验报告见 [`docs/experiment-report.md`](docs/experiment-report.md)。二者都明确区分已完成证据与待核验事项，不能替代最终课程报告。

受控缺陷标签验收见 docs/controlled-cases.md。脚本每次在临时目录生成无个人信息的 .docx 变体，验证标题跳级、缺章节、空字段、占位符、格式离群和未审计对象；变体不进入仓库：

    python scripts\evaluate_controlled_cases.py --format terminal

课程交付材料草稿见 docs/ai-safety-case-report.md 和 docs/open-source-code-report.md，二者保留当前证据与未完成清单，不替代最终提交版。

## 结果和覆盖范围

审计结果包含目标文件、审计范围、统计摘要、问题列表、未审计对象列表和运行指标。每条问题记录唯一编号、严重级别、规则编号、结构化位置、证据、问题说明和修复建议；Markdown 报告对非空段落给出文字锚点，对空白段落给出前后可见文字、连续空白总数和组内次序，格式离群还列出具体属性差异。OOXML 零基段落索引仅作为技术定位，不冒充页面上的编号或自然段序号。每个未审计对象也单独记录类型、位置、数量、未审计原因、影响和建议，不能只输出一句笼统的“存在未审计对象”。

当前确定性检查包括：标题样式跳级、用户指定的缺失章节、未指定标准提示、空段落、空表格单元格、常见占位符、表格占位符和同类段落的基础格式离群。正文、表格/嵌套表格以及文档中实际引用的页眉页脚会被读取；图片/绘图、文本框/形状、OLE、SmartArt、批注和修订等对象会逐项登记为未审计对象。

## 测试

测试使用标准库 `unittest`，不要求在线服务或模型密钥：

```powershell
python -m unittest discover -s tests -v
```

回归集覆盖审计规则、路径安全、输入文档字节不变和通用 Skill 布局；具体用例数以命令实际输出为准。

可用临时可控文档进行本地性能/压缩对照（不会保存测试文档）：

```powershell
python scripts/benchmark_audit.py --sizes 50,200,800 --repeats 3
```

报告中的 `summary_char_ratio` 是“规则证据摘要字符数 / 输入字符数”的本地压缩代理，不等同于模型 token；`model_calls` 在当前离线实现中应为 0。

## 本地开发

当前开发使用 Python 3.10–3.12 和 `python-docx`。公开提交前仍需完成 Nanobot 实机记录、许可证确认、敏感内容与 Git 历史复核。
