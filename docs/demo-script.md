# 1 分钟内演示脚本

目标时长：约 45–55 秒。演示只使用 `scripts/demo_audit.py` 生成的合成文档，不使用个人文档或许可证不明的原始数据。

录制前应先核对[当前验收状态](validation-status.md)，避免在口播中沿用旧的测试数量或发布状态。

## 录制前准备

```powershell
python scripts\demo_audit.py --output-dir outputs\demo --force
```

命令会在被 `.gitignore` 排除的 `outputs/demo` 下生成 `demo-input.docx`、`demo-result.json` 和 `demo-result.md`。生成文档包含标题跳级、`TODO` 占位符、空单元格、格式离群和绘图对象，便于在一次演示中展示不同结果类型。

## 分镜和口播

| 时间 | 屏幕内容 | 口播要点 |
| --- | --- | --- |
| 0–6 秒 | 打开项目根目录和 `SKILL.md` | “这是一个面向通用 Word 文档的只读审计 Skill，输入文档不会被修改。” |
| 6–16 秒 | 展示 `demo_audit.py` 命令和终端摘要 | “脚本先生成安全的演示文档，再把自然语言请求映射为完整审计模式。” |
| 16–30 秒 | 打开 `demo-result.md` 的审计问题部分 | “这里能看到标题层级跳级、占位符、空单元格和格式问题，每条都有规则、位置、证据和建议。” |
| 30–41 秒 | 滚动到“未审计对象”部分 | “绘图对象不会被静默忽略，而是单独说明数量、原因、影响和人工检查建议。” |
| 41–50 秒 | 打开 `demo-result.json` 的 `summary`、`metrics` | “JSON 是主结果，当前离线运行模型调用数为零，审计过程只读且不上传文档。” |
| 50–55 秒 | 显示 README 的测试命令 | “当前25个单元测试和5组受控样例通过，详细结果见验收状态页。” |

## 演示注意事项

- 如果需要展示自然语言路由，可额外运行：

  ```powershell
  python scripts\audit_docx.py --input outputs\demo\demo-input.docx --request "只看标题层级和缺失章节" --format json
  ```

- 不要在镜头中展示 `data` 候选文档的正文，因为它们尚未完成文件级许可证和 PII 核验。
- 不要把临时生成的 `.docx`、JSON 报告或 Markdown 报告误加入 Git；`outputs/` 已被忽略。
