# 当前验收状态

状态日期：2026年9月17日。本页区分实测证据、历史记录与待办事项，严格以可复现事实为准，不以“已完成”代指未经检验的断言。

## 一、验收分级定义

- **Level A（当前版本直接验证通过）**：在当前最新代码与环境下直接执行，具备第一手运行日志、哈希或 CI 记录。
- **Level B（历史版本验证证据）**：在早期历史提交中完成端到端测试，具备历史日志，但当前版本尚未重新独立跑通完整闭环。
- **Level C（当前未验证 / 需要人工完成）**：明确未做该项测试，或属于个人隐私、官方评定等人工专属事项。

---

## 二、当前验证事实清单

| 项目 | 分级 | 结果 | 证据与边界 |
| --- | --- | --- | --- |
| **本地单元测试** | Level A | 46 项全部通过（耗时约 6.6s） | 本地 Python 3.12.7 执行 `python -m unittest discover -s tests -v` 全量通过。 |
| **受控样例评测** | Level A | 15 组全部通过（TP=8, FP=0, FN=0, TN=27） | Precision=100.0%, Recall=100.0%。声明：仅代表预设规则集，不代表真实文档实际准确率。 |
| **真实文档回归** | Level A | 12 份样本解析无报错，输入哈希完全不变 | 捕获 33 处未审计对象。声明：缺乏人工逐点真值标签，不能断言未审计对象召回率 100%。 |
| **性能压力基线** | Level A | 50/200/800 段落测试实测完成 | 实测 p50 分别为 181.21ms, 674.98ms, 5988.48ms；离线内核 `model_calls=0`。 |
| **云端 CI 工作流** | Level A | Python 3.10 / 3.11 / 3.12 矩阵全绿通过 | [![Audit CI](https://github.com/STAR-LAB-AI-Agent/office-audit/actions/workflows/audit-ci.yml/badge.svg?branch=main)](https://github.com/STAR-LAB-AI-Agent/office-audit/actions/workflows/audit-ci.yml?query=branch%3Amain) 最新 main 分支云端矩阵构建全绿通过。 |
| **Antigravity CLI** | Level A | 端到端 CLI 冒烟、输入哈希保护及防覆写测试通过 | 公开凭据见 [`docs/antigravity-verification.md`](antigravity-verification.md)；本地生成物见 `outputs/antigravity-final/`（受 gitignore 保护不公开）；不代表原生 Agent Tool 自主闭环验证。 |

| **Codex 宿主** | Level B | 具备 2026-09-11 端到端调用记录 | 历史 3 模式调用通过，当前 46 测试新版尚未重新独立跑通宿主交互。 |
| **Nanobot 宿主** | Level B | 具备 2026-09-11 端到端调用记录 | 历史 3 模式调用通过，当前 46 测试新版尚未重新独立跑通宿主交互。 |
| **Claude Code 宿主**| Level B | 具备 2026-09-11 端到端调用记录 | 历史 3 模式调用通过，当前 46 测试新版尚未重新独立跑通宿主交互。 |
| **Antigravity 原生 Agent**| Level C | 当前未验证 | 仅完成 CLI 层面调用，未在 Antigravity 宿主内完成 LLM 自主触发与调度的闭环评测。 |
| **演示视频录制** | Level C | 待人工完成 | 按照 `docs/demo-script.md` 由学生本人录制 45-55 秒无敏演示视频。 |
| **手册个人信息与签名** | Level C | 待人工完成 | 保护学生隐私，封面个人信息、承诺书签名及教师评定栏严格留白。 |
| **手册回顾日期待核对** | Level C | 待人工完成 | 第 11 至 15 篇阶段回顾日期已标记为 `TODO（日期待核对）`，待学生核实。 |

---

## 三、公开资产与再分发边界

1. **外部真实样例**：12 份真实样本均位于本地开发目录，仅用于格式发现与回归测试，未在公开仓库中追踪或再分发；
2. **公开清单元数据**：`data/public-samples.manifest.json` 中明确记录公开候选的许可与校验哈希；
3. **敏感信息与密钥**：项目中绝不包含任何 API 密钥、个人文档正文片段或未授权个人数据。

---

## 四、历史提交关联

- **阶段 0 提交**：`2dcc5f3`
- **阶段 1 提交**：`d7b0ad5`
- **阶段 2/3 提交**：`2dfe296`（包含 46 项单元测试、15 组受控评测、资源限制与 CI 验证）
