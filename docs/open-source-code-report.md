# AI Office 文档审计开源代码报告

专业实习课题 #03　作者署名 Wh1t3zZ114　2026年9月15日

## 一 项目任务

本项目面向通用 Word 文档，检查标题层级、用户指定的缺失章节、空白字段、占位内容与基础格式差异，并生成可定位的问题清单。成品由一套Python审计内核和多个Skill入口组成，可通过命令行独立运行，也可由Codex、Nanobot或Claude Code调用。

项目选择以DOCX作为第一版输入格式，是为了把解析、定位和只读边界做清楚，而不是把“通用文档”理解为必须支持所有Office格式。通用性体现在不固定学校模板、用户可配置章节清单，以及对报告、通知、会议纪要、申请材料等文档使用相同接口。

## 二 架构与职责

| 文件或目录 | 职责 |
| --- | --- |
| SKILL.md | 通用宿主入口和任务边界 |
| skills/office-audit/ | 工作区型宿主入口与跨宿主启动器 |
| .claude/skills/office-audit/ | Claude Code项目入口 |
| agents/openai.yaml | Codex展示元数据 |
| scripts/audit_docx.py | 解析、规则、结果渲染与CLI |
| scripts/evaluate_controlled_cases.py | 临时生成受控文档并核对标签 |
| fixtures/controlled-cases.json | 受控样例标签，不包含真实原文 |
| tests/ | 正例、反例、异常和安全边界测试 |
| references/rules-example.json | 自定义规则示例 |
| docs/ | 设计、验证、使用说明与报告 |

宿主将用户要求整理成参数，审计内核调用python-docx遍历正文、表格和页眉页脚，再执行确定性检查。JSON是主结果；Markdown和终端摘要使用同一份结构化数据。三种宿主不维护独立规则，避免不同入口出现不同审计语义。

问题条目包括rule_id、severity、location、locator、evidence及suggestion。空白段落按连续组报告前后文字和paragraph_indices。未审计对象逐个记录，不将“没有告警”描述为全文合规。关闭的规则也明确列入disabled_rules。

## 三 开发过程与关键修改

初期先固定只读输入、独立输出、无固定模板和结构化错误等约束，再实现最小CLI。真实样例暴露了两个问题：Word中的可见编号不等于OOXML段落序号，格式差异也不一定是错误。随后增加文字锚点、空段分组和同类段落比较，降低人工核对成本。

后续扩展到15组受控样例，评测器同时检查应该出现与不该出现的规则。配置层增加规则开关、严重级别覆盖与资源预检。9月15日交付审查发现并修复了资源参数接受NaN、样例编号可越出临时目录、硬链接路径绕过只读保护，以及公式未单独标注等边界。

这些修改基于具体问题和回归测试，不代表系统能抵御所有恶意输入。项目保留格式继承、特殊文体、正则回溯和未审计复杂内容等限制，供使用者判断是否适合当前任务。

## 四 安装与使用

直接依赖为python-docx，版本范围为>=1.2,<2。该范围不是精确锁定文件；上游还会安装其传递依赖，例如lxml。项目代码与文档采用MIT许可证，作者署名为Wh1t3zZ114。依赖许可证以安装包及上游声明为准，不用本项目许可证覆盖第三方资产。

```powershell
python -m pip install -r requirements.txt
python scripts/demo_audit.py --output-dir outputs/demo
python scripts/audit_docx.py --input outputs/demo/demo-input.docx --mode full --format json --output outputs/demo/audit.json
```

已有演示输出时，可换一个新目录；只有确认需要重新生成演示文件时再使用demo脚本的--force。

结构审计可传入--required-sections，字段与格式审计使用--mode fields_format，也可以通过--request传入自然语言。三类请求分别为“完整检查这份文档”“只检查标题层级和缺失章节”“检查空字段、占位符和格式”。未指定章节标准时，程序明确提示未指定，而不是默认要求某些固定章节。

--rules接受JSON配置，支持严重级别覆盖、禁用规则与资源限制。placeholders是替换默认词表，placeholder_pattern优先于词表；自定义正则仅用于可信配置，语法检查不能保证执行时间。报告路径及日志路径不得覆盖输入文件或彼此覆盖。

## 五 测试与结果

9月15日在Python 3.9.0和3.12.14分别完成46项单元测试，均通过；15组受控评测全部通过。文档—规则级指标为TP=8、FP=0、FN=0、TN=27，精确率和召回率均为100%。指标仅适用于预先定义的合成样例，不能用作真实文档准确率或安全保障承诺。

12份仓库外真实文档本轮回归均无解析错误，输入哈希保持不变，已识别未审计对象仍为33个。9月11日保留了Codex、Nanobot、Claude Code宿主运行记录；之后的修改须另行复测。GitHub Actions工作流已经配置，但云端执行结果须查看实际运行记录。

```powershell
python -m unittest discover -s tests -v
python scripts/evaluate_controlled_cases.py --format terminal
```

完整实验条件、逐份计数、性能数据和已知不足见实验报告。测试计数发生变化时，应先更新验证证据，再修改报告。

## 六 安全与开源边界

审计内核本地运行且不调用模型或网络API，但宿主本身可能使用在线模型。真实文件进入宿主测试前，需要确认其数据处理方式符合使用者要求。结果中的证据片段也可能带有个人信息，因此报告同样不能随意公开。

代码仓库保留样例元数据和合成构造方法，不提交真实原文、个人实习手册、密钥或私人审计报告。外部样例的发布状态与本地检测能力分开管理。Git忽略规则能防止误添加，但不自动清除曾经提交的历史内容。

默认资源预检包括文件体积、ZIP条目、声明解压总量和条件性的压缩比检查。这些是有限预检，不是进程级内存或CPU隔离。只读路径保护和哈希回归有助于防止误覆盖，也不能替代操作系统权限和可信运行环境。

## 七 项目总结

目前版本适合用于课程展示和辅助人工检查：输入输出明确，结果可以追溯到规则与位置，核心可独立测试。它还不能替代最终排版审阅、专业内容审核或安全查杀。后续改进应优先完善格式继承与真实样例标签，不急于增加OCR或自动修复等新功能。

开源仓库：[STAR-LAB-AI-Agent/office-audit](https://github.com/STAR-LAB-AI-Agent/office-audit)。项目许可证见根目录LICENSE；依赖上游见[python-docx](https://github.com/python-openxml/python-docx)；当前验证状态见docs/validation-status.md。最终提交版本由实际Git提交号与测试记录共同标识。
