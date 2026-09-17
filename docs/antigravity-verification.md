# Antigravity 宿主 CLI 验证记录

- 验证日期：2026年9月17日
- 宿主环境：Antigravity IDE / Agent Execution Environment (Windows PowerShell, Python 3.12.7)
- 入口形式：CLI 脚本执行 (`python scripts/audit_docx.py`)
- 证据定性：**Level A（当前版本直接验证）**
- 存储说明：本地全量运行生成物（含测试 docx 与三模式 JSON 报告）位于本地 `outputs/antigravity-final/`，受仓库 `.gitignore` 保护不上传 GitHub；本文件为仓库内公开可追溯的脱敏验证凭据。

---

## 一、定性声明与边界

本次验证为在当前 Antigravity 运行环境中通过命令行终端进行端到端 CLI 审计与规则调用，证明 Python 审计内核、CLI 接口、输入只读哈希保护及输出路径防覆写在当前运行环境完全正常工作。

**明确边界**：本验证仅证明 CLI 命令行执行能力，不代表在 Antigravity 宿主内通过原生自主 Agent Tool/Skill 机制被 LLM 自主触发与调度的端到端交互已完成。

---

## 二、实测结果

### 1. 输入文件哈希保护测试
- 测试文件：合成无敏演示文档 `demo-input.docx`
- 审计前 SHA-256：`f23eb7108a0361f5291ddb16d45162d156c97e7a130a362be243e3810ba200d1`
- 审计后 SHA-256：`f23eb7108a0361f5291ddb16d45162d156c97e7a130a362be243e3810ba200d1`
- 结果：**哈希严格一致**，证明审计执行全过程仅执行只读解析，绝不篡改输入源文件。

### 2. 输出覆盖防护测试
- 测试命令：
  ```powershell
  python scripts/audit_docx.py --input outputs/antigravity-final/demo/demo-input.docx --output outputs/antigravity-final/demo/demo-input.docx
  ```
- 返回码：`1`
- 错误信息：结构化拦截错误 `unsafe_output_path`（“报告或日志路径不能覆盖输入文档或彼此覆盖”）。
- 结果：**成功拦截**，有效杜绝覆盖风险。

### 3. 三模式调用与审计统计
对同一份合成文档分别运行三种审计模式，实际执行结果如下：

| 模式 | 退出码 | 发现项数量 (Findings) | 严重度统计 (Summary) | 未审计对象 |
| --- | :---: | :---: | :---: | :---: |
| `full` | 0 | 4 | `{"error": 0, "warning": 3, "info": 1}` | 1 (`image_or_drawing`) |
| `structure` | 0 | 2 | `{"error": 0, "warning": 1, "info": 1}` | 1 (`image_or_drawing`) |
| `fields_format` | 0 | 2 | `{"error": 0, "warning": 2, "info": 0}` | 1 (`image_or_drawing`) |

---

## 三、结论

Antigravity 环境下的底层 CLI 工具调用、只读安全屏障与多模式路由均工作正常，评测结果与预期设计严格吻合。
