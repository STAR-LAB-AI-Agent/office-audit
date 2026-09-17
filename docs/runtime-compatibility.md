# 智能体宿主兼容说明

> 状态日期：2026-09-17。本文记录统一内核在不同智能体（Agent）宿主环境中的接入方式、验收口径与实测记录。

## 统一设计与架构优势

本项目只维护一个确定性审计内核：`scripts/audit_docx.py`。根目录 `SKILL.md`、`skills/office-audit/SKILL.md` 和 `.claude/skills/office-audit/SKILL.md` 只负责告诉不同宿主何时、如何调用它；跨宿主启动器 `skills/office-audit/scripts/run_audit.py` 会自动向上查找项目根目录，因此不依赖智能体的当前工作目录。

规则配置、规则开关和文件资源预检仍使用同一 CLI。结果中新增禁用规则等字段，接入方应允许附加字段；资源预检不是运行时沙箱。

## 接入方式与验收口径

统一证据等级：**A=当前验证**、**B=历史验证**、**C=未验证**。

| 宿主 | 接入方式 | 验收状态 | 证据级别 |
| --- | --- | --- | --- |
| **Codex** | 将仓库根目录安装或链接到 Codex Skills 目录，名称保持 `office-audit` | 2026-09-11 使用 Codex CLI 0.153.4 实测通过 | B（历史验证） |
| **Nanobot** | 将本仓库作为 workspace；Nanobot 自动扫描 `skills/office-audit/SKILL.md` | 2026-09-11 课程统一环境实测通过 | B（历史验证） |
| **Claude Code** | 直接打开本仓库；项目入口位于 `.claude/skills/office-audit/SKILL.md` | 2026-09-11 实测通过 | B（历史验证） |
| **Antigravity (CLI)** | 在 Antigravity 工作区中直接调用底层 CLI 脚本执行全流程审计 | 2026-09-17 实测通过，哈希一致，防覆写有效（详见 [docs/antigravity-verification.md](antigravity-verification.md)） | A（当前验证） |
| **Antigravity (Agent)** | 通过 Antigravity 原生 Agent Tool / Skill 机制由 LLM 自主触发与调度 | 尚未开展端到端 Agent 自主闭环验证 | C（未验证） |


“脚本测试通过”“Skill 结构可发现”和“宿主真实调用通过”是三项不同证据。某个宿主只有在它确实识别 Skill、调用审计器、生成报告并保持原文不变后，才可标为实测通过。

## 最小验收场景

每个宿主至少验证以下四项基本行为：

1. 自然语言完整审计成功并输出结构化报告；
2. 自然语言结构审计被正确路由为 `structure`；
3. 字段与格式审计被正确路由为 `fields_format`；
4. 输出路径等于输入路径时被拒绝，且输入文件哈希不变。

验收记录应保留宿主版本、日期、提示词、生成报告路径、返回结果和输入文件审计前后 SHA-256；严禁把含个人信息的真实原文提交到 GitHub。

## Codex 实测记录（2026-09-11）

在新的 Codex CLI 0.153.4 进程中显式请求使用 `$office-audit`，宿主成功发现并读取根目录 `SKILL.md`。对无个人信息的合成演示文档完成以下检查：

| 用例 | 实际路由 | 退出码 | 结果 |
| --- | --- | --- | --- |
| “综合检查这份Word文档” | `full` | 0 | 通过 |
| “只检查标题层级和缺失章节” | `structure` | 0 | 通过 |
| “检查空字段、占位符和格式” | `fields_format` | 0 | 通过 |
| 报告路径与输入路径相同 | `full` | 2 | 按预期拒绝，错误码 `unsafe_output_path` |

输入文档在测试前后的 SHA-256 均为 `9A59A039FA0AACACF4AE502AE69696A38868853238D5D7E7D9F2B2847719B667`。测试输出位于被 Git 忽略的 `outputs/codex-runtime-test/`，不作为发布数据集提交。

## Nanobot 与 Claude Code 实测记录（2026-09-11）

用户分别在 Nanobot 和 Claude Code 中调用 `office-audit`。两种宿主均生成3份可解析 JSON 报告，实际模式和统计完全一致：

| 用例 | 实际模式 | Nanobot | Claude Code |
| --- | --- | --- | --- |
| 合成演示文档完整审计 | `full` | 0 error，5 findings，1个未审计对象 | 0 error，5 findings，1个未审计对象 |
| 真实报告结构审计 | `structure` | 0 error，1 finding，4个未审计对象 | 0 error，1 finding，4个未审计对象 |
| 真实报告字段与格式审计 | `fields_format` | 0 error，23 findings，11个未审计对象 | 0 error，23 findings，11个未审计对象 |

两份真实报告测试副本与仓库外原文件的 SHA-256 一致。运行产物分别保存在被 Git 忽略的 `outputs/nanobot-test/` 和 `outputs/claude-test/`，原始个人文档保存在被 Git 忽略的 `data/external/personal-reports/`，均不进入公开仓库。

## Antigravity 开发环境中的 CLI 记录（2026-09-17 最新实测）

在 Antigravity 研发环境中，审计器作为原生 Python CLI 驱动执行，于 2026-09-17 完成了交付前最终全量复测。仓库内已沉淀公开、脱敏的验证凭据：[`docs/antigravity-verification.md`](antigravity-verification.md)；本地全量测试产物保存在被 Git 忽略的 `outputs/antigravity-final/verification.md`（该路径受 `.gitignore` 保护，不提交至 GitHub）：
- 全量 46 项单元测试 `python -m unittest discover -s tests -v` 耗时约 6.6 秒全部通过；
- 15 组受控缺陷样例评测 `scripts/evaluate_controlled_cases.py` 自动化生成、校验与指标计算顺利完成；
- 12 份真实外部文档基线对比保持 SHA-256 100% 不变，准确抓取 33 处未审计对象；
- 在 `outputs/antigravity-final/demo/demo-input.docx` 上实跑三模式审计，输入 SHA-256（`f23eb710...`）前后一致，输出路径冲突被安全拦截（退出码 1，`unsafe_output_path`）。

## 结论

Codex、Nanobot、Claude Code 拥有 2026-09-11 的端到端宿主调用历史记录（证据等级 B），当前 46 测试新版本建议在对应环境中参考复测提纲再次跑通。上述 Antigravity 记录仅证明在当前开发与运行环境中通过 CLI 成功执行审计、测试与安全拦截（证据等级 A，详见 [`docs/antigravity-verification.md`](antigravity-verification.md)），不能证明通过 Antigravity 原生 Skill 发现机制由大模型自主调度调用（证据等级 C），因此不将其列为已完成全链路自主验收的宿主。


