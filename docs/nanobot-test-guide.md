# Nanobot 测试指南

1. 将整个 `office-audit` 仓库作为 Nanobot 的 workspace，确认其中存在 `skills/office-audit/SKILL.md`。
2. 安装依赖：`python -m pip install -r requirements.txt`。
3. 准备一份测试 `.docx`。建议先用 `python scripts/demo_audit.py --output-dir outputs/nanobot-test --force` 生成无个人信息的演示文档。
4. 在 Nanobot 中发送：

   > 使用 office-audit 审计 outputs/nanobot-test/demo-input.docx，进行完整审计，把 JSON 报告保存到 outputs/nanobot-test/nanobot-full.json，不要修改原文。

5. 再测试一句“只检查标题层级和缺失章节”，确认报告中的 `mode` 为 `structure`；测试一句“检查空字段、占位符和格式”，确认 `mode` 为 `fields_format`。
6. 截图保留 Nanobot 识别 Skill、调用命令和生成结果的界面。记录 Nanobot 版本、日期和异常；不要把含个人信息的真实文档提交到 GitHub。

通过标准：Nanobot 能发现 `office-audit`，三类模式路由正确，报告成功生成，输入文档没有被修改。若无法发现，优先检查 Nanobot 当前 workspace 是否就是仓库根目录，以及 Skill 文件夹名与 frontmatter 的 `name: office-audit` 是否一致。
