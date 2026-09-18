# AI Office 文档审计

[![Audit CI](https://github.com/STAR-LAB-AI-Agent/office-audit/actions/workflows/audit-ci.yml/badge.svg?branch=main)](https://github.com/STAR-LAB-AI-Agent/office-audit/actions/workflows/audit-ci.yml?query=branch%3Amain)

AI Office 文档审计是针对 Word (`.docx`) 文档的只读合规自检工具与智能体 Skill，对应选题 **#03 AI Office 文档审计**。

该项目用于在 Word 文档提交前检查标题层级、缺失章节、漏填内容、占位符以及字体排版格式离群，并逐项标明当前无法直接审计的对象。审计全过程严格只读，绝不修改源文件。

项目既可以作为独立的 Python 命令行（CLI）工具离线运行，也可以作为 Skill 接入 Codex、Nanobot、Claude Code 等智能体宿主环境。所有入口统一调用同一套 Python 确定性审计内核，确保规则一致、结果可复现。

## 三类审计意图

系统支持三种审计模式，可显式指定或由自然语言请求自动映射：

- `full`（完整审计）：结构、字段和排版格式全量检查；
- `structure`（结构审计）：检查标题层级连贯性（避免跨级跳级）及用户指定的必需章节（必需章节由用户提供，不默认强制特定模板）；
- `fields_format`（字段与格式审计）：检查正文及表格中的空白段落、空白单元格、常见占位符以及样式格式离群。

正文、表格、嵌套表格以及实际引用的页眉页脚均参与审计。图片、公式、文本框、形状、OLE 嵌入对象、批注等内容目前不能直接解析内部文字，程序会逐项输出未审计对象清单，记录其类型与结构化位置。

## 安装

安装运行依赖：

```powershell
python -m pip install -r requirements.txt
```

核心依赖为 `python-docx >=1.2,<2`（当前环境实测验证版本为 `1.2.0`），无需外部模型 API Key 即可本地离线执行。

## CLI 使用

核心脚本位于 `scripts/audit_docx.py`。

### 1. 基础审计执行
```powershell
python scripts/audit_docx.py `
  --input "path/to/document.docx" `
  --mode full `
  --format json `
  --output "reports/audit.json"
```

### 2. 自然语言请求映射
```powershell
python scripts/audit_docx.py `
  --input "path/to/document.docx" `
  --request "只检查标题层级和缺失章节" `
  --format markdown `
  --output "reports/structure.md"
```

### 3. 按指定章节清单检查
将必需章节按行保存在文本文件中，程序将比对是否存在对应标题：
```powershell
python scripts/audit_docx.py `
  --input "path/to/document.docx" `
  --mode structure `
  --required-sections "config/required-sections.txt" `
  --format terminal
```

当报告或日志输出路径与输入路径相同时，程序将立即报错并拒绝执行。

## Skill 接入

仓库提供了面向主流智能体环境的入口配置：

- `SKILL.md`：通用智能体 / Codex 接入入口；
- `skills/office-audit/SKILL.md`：工作区型智能体 / Nanobot 接入入口；
- `.claude/skills/office-audit/SKILL.md`：Claude Code 项目级接入入口；
- `skills/office-audit/scripts/run_audit.py`：跨宿主稳定启动器，自动向上探测并定位项目根目录，抹平工作路径差异。

各宿主通过上述配置即可发现 `office-audit` Skill 并调度底层 CLI 工具。

## 自定义审计规则

系统支持通过 `--rules` 传入 JSON 配置文件（示例见 `references/rules-example.json`），实现灵活定制：

```powershell
python scripts/audit_docx.py `
  --input "path/to/document.docx" `
  --rules "references/rules-example.json" `
  --format json
```

支持的规则配置项：
- `required_sections`：用户指定的必需章节名称列表；
- `placeholders`：自定义占位符词表（默认包含 `TODO`、`TBD`、`XXX` 等）；
- `placeholder_pattern`：自定义占位符正则表达式（优先级高于词表）；
- `severity_overrides`：重定义指定规则的严重级别（`info` / `warning` / `error`）；
- `disabled_rules`：显式禁用的规则 ID 清单；
- `rule_switches`：针对特定规则的启用开关（`{rule_id: true/false}`）；
- `limits`：文件与解析资源安全限制。

## 输出格式

支持三种输出格式（`--format json|markdown|terminal`），主数据格式为 JSON：

- **结构化位置与证据**：问题条目包含规则 ID、严重度、正文段落序号或表格行/列坐标，并附带用于人工核对的上下文前后文字与修改建议；
- **空白段落智能分组**：连续空段按组聚合定位，单个排版空行默认为 `info`，连续空行提升为待核对 `warning`；纯图片或含公式单元格不误判为空；
- **未审计对象清单**：对图片、公式、文本框、嵌入对象等显式记录位置与类型，杜绝隐式漏检；
- **禁用规则透明度**：被关闭的规则显式登记在 `disabled_rules` 中，避免“未执行检查”被误读为“文档合规”；
- **脱敏运行日志**：可选的 `--log` 参数仅记录执行模式、耗时、对象计数与错误码，严禁向日志写入正文文本或敏感信息。

## 46项单元测试和15组受控样例

项目内置了完备的自动化测试体系：

### 1. 单元测试套件（46 项）
覆盖规则匹配、CLI 路由、资源限制、硬链接冲突与异常拦截：
```powershell
python -m unittest discover -s tests -v
```
全量 46 项单元测试全部通过。

### 2. 受控缺陷样例评测（15 组）
在临时目录动态生成具有已知特征的合成文档进行端到端检验，测试完成后自动销毁：
```powershell
python scripts/evaluate_controlled_cases.py --format terminal
```
当前 15 组受控样例全部通过，指标为 TP=8, FP=0, FN=0, TN=27，Precision=100.0%, Recall=100.0%。

> 声明：受控合成样例指标仅反映系统对已知确定性规则集的覆盖能力，不代表复杂多样的现实文档整体准确率。

## Python 3.10/3.11/3.12 CI

项目通过 GitHub Actions（`.github/workflows/audit-ci.yml`）实现自动化持续集成。每次向 `main` 分支提交或发起 Pull Request 时，均在 Ubuntu 环境针对 **Python 3.10、3.11、3.12** 矩阵自动安装依赖、执行 46 项单元测试并运行 15 组受控样例评测，确保跨版本稳定运行。

## 性能与低上下文优化

- **零模型消耗**：审计内核在本地采用基于规则的离线确定性计算，`model_calls` 恒为 0，不产生任何 API Token 消耗；
- **低上下文摘要**：将数万字符的长篇文档解析并提炼为紧凑的结构化证据清单，摘要字符比通常维持在 0.4%~6% 之间，便于后续智能体以极少上下文开销进行解读；
- **性能基准测试**：
  ```powershell
  python scripts/benchmark_audit.py --sizes 50,200,800 --repeats 3
  ```
  在 50、200、800 段落的文档规模下均能保持毫秒至秒级的快速响应。

## Demo 演示生成

项目内置了自动化演示用例文档生成脚本：
```powershell
python scripts/demo_audit.py --output-dir outputs/demo --force
```
该脚本在被忽略的 `outputs/demo/` 目录下生成一份包含典型缺陷（标题跳级、占位符、空单元格、格式离群和绘图对象）的无敏感信息演示文档 `demo-input.docx`，并完成只读审计生成报告，供快速体验或演示录屏使用。

## 安全措施

- **只读保证**：输入文档全程保持只读，审计前后文件 SHA-256 哈希值严格保持不变；
- **输出覆盖防护**：严格校验输出路径，拦截输出等于输入的情况，并支持同文件硬链接与符号链接的物理实体重合拦截；
- **资源消耗预检**：前置预检文件大小（默认上限 50MB）、Zip 压缩条目数（默认上限 1000）及解压体积比（默认上限 100 倍），防范浅层畸形文件拒绝服务；
- **数据合规隔离**：不依赖外部网络连接，不上传文档原文，本地临时文件自动清理。

## 已知问题

- **排版样式继承**：复杂的层叠样式继承与单个段落内混合富文本字体的离群识别可能存在局限；
- **复杂嵌入对象**：文本框内部文字、嵌入式表格与复杂公式当前仅记录类型与所在位置，尚未支持深度内容文本解析；
- **合规边界**：本项目聚焦于排版格式与文档结构合规，不包含专门的 PII（个人隐私信息）合规审计与语义级逻辑校对。

## 许可证与依赖说明

- **依赖环境**：`python-docx >=1.2,<2`（验证版本为 `1.2.0`）；
- **开源许可证**：本项目采用 [MIT 许可证](LICENSE) 开源。
