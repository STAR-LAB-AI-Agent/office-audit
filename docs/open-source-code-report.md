# AI Office 文档审计：开源代码报告（证据版草稿）

> 状态：阶段性草稿（2026-09-02）。本地仓库已可复现；GitHub 远程仓库尚未创建。

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
| tests/test_audit_docx.py | 10 个 unittest 回归用例 |
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

- Python：开发与验收使用 3.12.13。
- python-docx：1.2.0，读取和遍历 .docx。
- 项目代码：当前尚未声明独立开源许可证；公开 GitHub 前应补充 LICENSE，并在 README 中说明课程项目属性。
- 公开数据：当前只提交元数据 manifest。docx-corpus 的元数据许可、文档本体版权和文件级再分发权分开记录，文件级许可未确认前不提交原文。

## 5. 当前验收证据

1. Python 编译通过。
2. 10/10 unittest 通过，输入文档字节在审计前后不变。
3. Skill 官方校验返回 Skill is valid。
4. 受控标签验收 5/5 通过。
5. 公开候选仓库外预检 3 条可解析、9 条明确显示 pending_local_input；没有原始文档进入 Git。
6. 仓库敏感信息扫描无 API key、密码模式命中；仓库内 .docx 数量为 0。

## 6. 发布前清单

- [ ] 根据老师最终要求补齐正式实验报告、AI 安全案例报告和实习总结。
- [ ] 完成 15 天实习手册记录，每日不少于 400 字，并检查页面排版。
- [ ] 完成 1 分钟内演示视频，展示自然语言路由、JSON 结果和逐项未审计对象。
- [ ] 对公开候选逐份完成 PII 抽查和再分发许可核对；未通过的只保留 metadata/pending 或 rejected。
- [ ] 为代码补充最终开源许可证、贡献/使用说明和固定版本信息。
- [ ] 最后执行密钥、个人信息、原文、临时文件、Git 历史和报告链接检查。
- [ ] 验收完成后再创建 GitHub 仓库；可先 private，确认无敏感材料后再公开。
