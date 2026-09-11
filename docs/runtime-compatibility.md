# 智能体宿主兼容说明

## 统一设计

本项目只维护一个确定性审计内核：`scripts/audit_docx.py`。根目录 `SKILL.md` 和 `skills/office-audit/SKILL.md` 只负责告诉不同宿主何时、如何调用它；跨宿主启动器 `skills/office-audit/scripts/run_audit.py` 会向上查找项目根目录，因此不依赖智能体的当前工作目录。

## 接入方式与验收口径

| 宿主 | 接入方式 | 验收状态 |
| --- | --- | --- |
| Codex | 将仓库根目录安装或链接到 Codex Skills 目录，名称保持 `office-audit` | 2026-09-11 使用 Codex CLI 0.153.4 实测通过 |
| Nanobot | 将本仓库作为 workspace；Nanobot 扫描 `skills/office-audit/SKILL.md` | 由课程统一 Nanobot 环境实测 |
| Claude Code | 直接打开本仓库；项目入口位于 `.claude/skills/office-audit/SKILL.md` | 入口已配置，待 Claude Code 实机调用 |
| Antigravity | 将同一 Skill 映射到项目 `.agents/skills/office-audit/` | 尚未实测，不宣称通过 |

“脚本测试通过”“Skill 结构可发现”和“宿主真实调用通过”是三项不同证据。某个宿主只有在它确实识别 Skill、调用审计器、生成报告并保持原文不变后，才可标为实测通过。

## 最小验收场景

每个宿主至少执行以下四项：

1. 自然语言完整审计成功并输出报告；
2. 自然语言结构审计被正确路由为 `structure`；
3. 字段与格式审计被正确路由为 `fields_format`；
4. 输出路径等于输入路径时被拒绝，且输入文件哈希不变。

验收记录应保留宿主版本、日期、提示词、生成报告路径、返回结果和输入文件审计前后 SHA-256；不要把含个人信息的真实原文提交到 GitHub。

## Codex 实测记录（2026-09-11）

在新的 Codex CLI 0.153.4 进程中显式请求使用 `$office-audit`，宿主成功发现并读取根目录 `SKILL.md`。对无个人信息的合成演示文档完成以下检查：

| 用例 | 实际路由 | 退出码 | 结果 |
| --- | --- | --- | --- |
| “综合检查这份Word文档” | `full` | 0 | 通过 |
| “只检查标题层级和缺失章节” | `structure` | 0 | 通过 |
| “检查空字段、占位符和格式” | `fields_format` | 0 | 通过 |
| 报告路径与输入路径相同 | `full` | 2 | 按预期拒绝，错误码 `unsafe_output_path` |

输入文档在测试前后的 SHA-256 均为 `9A59A039FA0AACACF4AE502AE69696A38868853238D5D7E7D9F2B2847719B667`。测试输出位于被 Git 忽略的 `outputs/codex-runtime-test/`，不作为发布数据集提交。
