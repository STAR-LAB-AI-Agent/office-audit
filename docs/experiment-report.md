# AI Office 文档审计：阶段性实验报告

> 状态：阶段性草稿（2026-09-02），用于持续验收和后续正式报告整理。文中明确区分已完成工作、实验事实和未完成事项，不把候选数据当作已通过样例。

## 1. 项目概况

- 课程题目：`#03 AI Office 文档审计`
- 项目形态：可独立运行的 Python CLI + `SKILL.md` Skill 说明
- 目标对象：课程报告、通知、会议纪要、制度文件、项目说明、申请材料和模板等通用 Word 文档
- 第一版核心格式：`.docx`
- 运行原则：离线、只读、可追溯；不自动修改原文，不执行文档中的宏、脚本或指令文字

## 2. 要解决的问题

人工检查 Word 文档时，标题层级、空段落、空表格项、占位符和格式离群容易被遗漏；复杂对象又可能被解析器静默忽略。本项目把审计拆成稳定的结构化规则，并对暂未覆盖的对象逐项说明位置、数量、原因、影响和建议，使用户能区分“发现了问题”和“这个对象尚未被审计”。

项目不把某一种学校报告模板当作通用标准。缺失章节只有在用户提供章节清单或规则时才报告；没有标准时输出“未指定标准”提示，并继续做可以由文档自身结构推断的检查。

## 3. 技术路线

```text
自然语言请求
    -> 离线关键词路由（full / structure / fields_format）
    -> Skill 参数整理与路径安全检查
    -> Python CLI
    -> python-docx 读取正文、表格、页眉页脚和样式
    -> 结构 / 字段 / 格式 / 未审计对象规则
    -> JSON 主结果 + Markdown/终端投影
```

自然语言路由当前是透明关键词实现，不依赖网络和模型。未来可以增加模型适配器，但模型只能负责把复杂请求转换为同一份结构化参数，不能改变规则证据、严重级别或只读边界。

## 4. 已实现功能

1. `full`：综合检查结构、字段/占位符和基础格式。
2. `structure`：检查标题层级跳级、用户指定的必需章节和未指定标准提示。
3. `fields_format`：检查空段落、空单元格、常见占位符、表格占位符和同类段落格式离群。
4. 覆盖正文、表格及嵌套单元格，以及文档中实际引用的页眉页脚。
5. 对图片/绘图、文本框/形状、OLE、SmartArt、批注和修订逐项生成 `unsupported_objects` 记录。
6. JSON 结果包含 `findings`、`unsupported_objects`、统计、运行指标和结构化错误；报告路径不能覆盖输入文件。
7. 可选 JSONL 日志只记录模式、统计、耗时、对象数、模型调用数和错误码，不记录正文、证据、自然语言请求或密钥。
8. `evaluate_manifest.py` 支持读取仓库外的候选 `.docx`，默认不联网、不下载、不修改 manifest，并只输出审计统计摘要。

## 5. 数据集和许可证边界

已对 Hugging Face `superdoc-dev/docx-corpus`、DocxCorp 官方下载入口和 DS3Lab/WordScape 做第一方来源核验，详细证据见[公开数据研究记录](public-dataset-research.md)。当前 `data/public-samples.manifest.json` 已按过滤条件登记 12 条 `pending` 候选元数据：置信度不低于 0.8、词数在 100–5000、语言为英语或中文，并排除高风险类别和主题。

此处的 `pending` 很重要：候选尚未完成文件级许可核对、人工 PII 抽查、本地下载时间/字节数/SHA-256 记录和正式审计，所以没有一条被标为 `verified`。元数据 ODC-BY 1.0 不等于每份 `.docx` 可以自由再分发；原始文档默认留在仓库外，清单只保存来源和核验状态。

## 6. 验证证据

使用课程绑定 Python 3.12.13（`python-docx` 1.2.0）完成：

```powershell
python -m py_compile scripts\audit_docx.py scripts\benchmark_audit.py scripts\evaluate_manifest.py tests\test_audit_docx.py
python -m unittest discover -s tests -v
```

结果：10 个回归用例全部通过；输入文档字节在审计前后保持不变。使用 Skill 官方校验脚本得到 `Skill is valid!`。manifest 结构检查得到 12 条候选、每条必填字段齐全、`raw_docx=0`。官方 rows API 回读后，12 条记录的 ID、URL、类型、主题、语言、词数和置信度全部与清单一致。

性能基线见[性能记录](performance-baseline.md)。50、200、800 段受控文档的摘要字符比例分别为 6.17%、1.55%、0.38%，当前 `model_calls=0`；两次同日运行的墙钟耗时有明显波动，因此这些数据只说明“先本地解析和压缩”的方向，不是跨机器性能保证，也不是模型 token 统计。

### 6.1 真实公开样例的仓库外预检

2026-09-02 按 manifest 前 3 条候选做了小批量下载、SHA-256 自算和 `full` 模式审计预检。12 条候选中 3 条实际审计、9 条因未下载保持 `pending_local_input`；3 条均可解析，`audit_error=0`、`invalid=0`、`model_calls=0`。三份本地 SHA-256 均不等于数据源行 id，这个实测结果已写入 `data/public-samples.manifest.json` 的 `evidence.external_preflight`，说明后续必须使用本地自算哈希。

这只是工程链路预检，不是数据集许可结论：3 份原始文件位于系统临时目录，没有原文、提取全文或本地路径进入 Git；主动清理动作被桌面安全策略阻止，临时文件仍在仓库外。当前 3 条的文件级再分发许可仍为 `UNVERIFIED`，PII 抽查仍为 `not_started`，因此所有候选仍保持 `pending`。正式评估前还需先人工查看 `extracted/{id}.txt`，完成 PII 抽查和逐份再分发许可核对。

演示脚本 `scripts/demo_audit.py` 可生成不含个人信息的临时缺陷文档，复现标题跳级、占位符、空单元格、格式离群和未审计绘图对象，并输出 JSON/Markdown 结果。该临时文档不进入仓库。

## 7. 当前限制

- 尚未完成 12 条候选的人工 PII 抽查和逐份文件级再分发许可核对，因此不能宣称拥有可公开分发的真实 `.docx` 测试集。
- 尚未接入在线模型；当前低 token 结论只基于确定性摘要字符代理。
- `.doc`、扫描 PDF、图片文字、文本框内部语义、嵌入式 Office 对象、批注内容和修订语义不在第一版直接审计范围。
- 当前回归样例主要是临时可控文档；真实公开样例已完成 3/12 的仓库外工程预检，但因 PII 和文件级许可尚未核验，不能称为正式公开数据集评估。
- GitHub 远程仓库尚未创建或公开；当前本地仓库是唯一提交边界。

## 8. 后续计划

1. 逐条预览候选文本、人工抽查 PII，并记录拒绝原因而不是删除证据。
2. 对允许本地研究的样例下载到仓库外，补齐 UTC 时间、字节数和本地 SHA-256，再运行外部样例评估器。
3. 用真实文档生成少量受控缺陷变体和期望标签，同时保留原文不入 Git 的边界。
4. 录制不超过 1 分钟的端到端演示，展示自然语言路由、结构化结果和未审计对象告警。
5. 完善正式人工智能安全案例报告、开源代码报告和实习总结，最后再做密钥、个人信息、许可证和 Git 历史检查。

## 9. 复现入口

```powershell
python scripts\demo_audit.py --output-dir outputs\demo --force
python scripts\evaluate_manifest.py --format markdown --limit 3
python scripts\audit_docx.py --input "path\to\document.docx" --request "全面检查这份 Word 文档" --format json
```

上述命令不要求 API 密钥；外部真实样例必须由使用者自行放在仓库外，并在确认许可和隐私条件后再进行下一步处理。
