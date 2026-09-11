# AI Office 文档审计：开源代码报告（证据版草稿）

> 状态：阶段性草稿（更新至 2026-09-11），不代表最终开源代码报告或公开发布验收已经完成。当前数量和完成状态见[当前验收状态](validation-status.md)。

## 1. 项目说明

项目名称：AI Office 文档审计 Skill。

项目目标：针对通用 Word 文档提供离线、只读、可追溯的结构、字段和基础格式审计。核心格式为 .docx，输出结构化 JSON，并提供 Markdown/终端投影。

适用文档：课程报告、通知、会议纪要、制度文件、项目方案、申请材料和模板等。系统不把任何单一学校模板硬编码为通用标准。

## 2. 目录与职责

| 路径 | 职责 |
| --- | --- |
| scripts/audit_docx.py | 核心 .docx 解析、三类模式、规则引擎、CLI 和结果投影 |
| scripts/evaluate_manifest.py | 读取仓库外真实候选，只输出脱敏统计，不下载、不改 manifest |
| scripts/evaluate_controlled_cases.py | 生成临时受控变体并核对期望标签 |
| scripts/demo_audit.py | 生成无个人信息的端到端演示文档 |
| tests/test_audit_docx.py | 核心审计与安全回归用例；当前总数见[验收状态](validation-status.md) |
| tests/test_skill_layout.py | 多宿主 Skill 目录与启动器回归用例；当前总数见[验收状态](validation-status.md) |
| fixtures/controlled-cases.json | 受控样例标签，不含原始文档 |
| data/public-samples.manifest.json | 公开样例元数据和许可证/PII 核验状态 |
| SKILL.md | Skill 触发条件、边界、调用方式和结果约束 |
| docs/ | 设计、研究、性能、演示和交付证据 |

## 3. 运行方式

安装依赖：

    python -m pip install -r requirements.txt

完整审计：

    python scripts/audit_docx.py --input path\to\document.docx --mode full --format json --output reports\audit.json

自然语言路由：

    python scripts/audit_docx.py --input path\to\document.docx --request "全面检查这份 Word 文档" --format json

规则和安全验收：

    python scripts/evaluate_controlled_cases.py --format terminal
    python -m unittest discover -s tests -v

## 4. 依赖与许可证记录

- Python：2026-09-11 本轮验收环境为 3.9.0；该值是本轮环境记录，不是项目锁定版本。
- python-docx：`requirements.txt` 约束 `>=1.2,<2`，用于读取和遍历 `.docx`；本轮实际导入 1.2.0，但项目不宣称固定安装该版本。官方项目见 [python-openxml/python-docx](https://github.com/python-openxml/python-docx)，许可证为 [MIT](https://github.com/python-openxml/python-docx/blob/master/LICENSE)。
- 项目代码：仓库根目录已提供 [MIT LICENSE](../LICENSE)。该许可证不改变第三方文档本体的版权与再分发边界。
- 公开数据：当前只提交元数据 manifest。docx-corpus 的元数据许可、文档本体版权和文件级再分发权分开记录，文件级许可未确认前不提交原文。

## 5. 当前验收证据

1. 2026-09-11 本轮 16/16 unittest 通过，输入文档保护、输出隔离和日志最小化由对应回归用例覆盖。
2. 2026-09-11 本轮受控标签验收 5/5 通过。
3. Codex、Nanobot 和 Claude Code 已有端到端记录；Antigravity 未验证。
4. 公开候选已有仓库外下载和 12/12 离线解析的历史工程记录，但当前仍是 12/12 `pending`、PII 12/12 `not_started`、文件级再分发 12/12 `UNVERIFIED`。
5. 本轮只读核验确认当前分支为 `main`，远程 HEAD 也指向 `main`，`origin` 为 <https://github.com/STAR-LAB-AI-Agent/office-audit.git>，根目录已有 MIT `LICENSE`。
6. 其余已运行证据和不能外推的边界见[当前验收状态](validation-status.md)；历史编译、Skill 校验和敏感信息扫描记录不等于本轮重新执行。

## 6. 发布前清单

- [ ] 根据老师最终要求补齐正式实验报告、AI 安全案例报告和实习总结。
- [ ] 完成 15 天实习手册记录，每日不少于 400 字，并检查页面排版。
- [ ] 完成 1 分钟内演示视频，展示自然语言路由、JSON 结果和逐项未审计对象。
- [ ] 对公开候选逐份完成 PII 抽查和再分发许可核对；未通过的只保留 metadata/pending 或 rejected。
- [x] 仓库根目录提供 MIT `LICENSE`，README 记录 `python-docx` 名称、版本范围、许可证和实际用途。
- [x] GitHub `origin` 已配置为 <https://github.com/STAR-LAB-AI-Agent/office-audit.git>。
- [ ] 最后执行密钥、个人信息、原文、临时文件、Git 历史和报告链接检查。
- [ ] 核对远程仓库可见性、默认分支、最终提交内容和发布说明；不得仅凭已配置 `origin` 宣称公开交付完成。
