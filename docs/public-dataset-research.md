# 公开文档数据集研究：候选入口核验（阶段一 §7 配套）

- 编写日期：2026-09-02（UTC+8）
- 用途：为 `ai-office-document-audit-skill` 阶段一设计（[phase1-design.md](./phase1-design.md) §7）核验三个公开数据候选入口：来源归属、数据集组成/用途、许可证、再分发、个人信息风险、下载/版本/哈希记录方式，以及本项目的最小公开样例策略。
- 方法与范围：只使用第一方来源——Hugging Face 官方数据集卡片及官方 API、GitHub 仓库内 LICENSE/README/官方内容页、DocxCorp 官方站点及 API，并做了少量下载实测。不引用博客、搜索摘要或二手转述。页面无法访问或许可缺失之处一律标注，不猜测。
- 标注约定：
  - **VERIFIED**：本文直接在第一方页面/API/仓库文件中读到，或对线上端点实测得到（含时间点）。
  - **INFERENCE**：基于上述 VERIFIED 事实的合理推断，可能不成立；关键结论已说明为何是推断。
  - **UNVERIFIED**：无法从第一方来源确认的事实，或第一方声明互相矛盾/缺失。

---

## 0. 结论速览

1. **推荐主用 `superdoc-dev/docx-corpus`（Hugging Face）+ DocxCorp 官方下载入口（docxcorp.us）**：元数据与文件下载都清晰、许可有官方声明（元数据 ODC-BY 1.0、源码 MIT、文档版权归原作者）、有内容寻址 id、单文件下载 URL、提取文本端点和 takedown 通道，最小样例可以小批量、可审计地完成。
2. **WordScape 仅作为备选/后续增强**：它发布的是 9.4M 条 URL 列表（含 SHA-256 校验和）与管道代码，不重分发文档本体；接入需要自建下载+解析管道，工程量明显大于本项目需要，且 URL 列表本身的再分发许可在第一方资料中**没有声明**（UNVERIFIED）。
3. **实测警示（VERIFIED，2026-09-02）**：从 docxcorp.us 下载的 3 个 .docx 样本，其本地 SHA-256 **均不等于** 数据集行 id，与官方“id 即文件 SHA-256”的声明不符。因此项目 manifest 必须**自行计算并记录每个文件的本地 SHA-256**，不能把行 id 当完整性校验值。
4. **不能做**：不把 .docx 原文或提取文本重新发布到公开仓库（许可不覆盖文档本体）；不放入含个人信息的高风险样本（healthcare/forms/government 等类别）；不全量下载/镜像 CDN 或 URL 列表；不在未记录版本与哈希的情况下复现实验；不把“id=文件哈希”“76/46 语言”等声明当作已验证事实直接引用。

---

## 1. Hugging Face：superdoc-dev/docx-corpus

### 1.1 来源归属（VERIFIED）

- 数据集页面：[superdoc-dev/docx-corpus](https://huggingface.co/datasets/superdoc-dev/docx-corpus)；卡片正文与 YAML 元数据见[卡片原文](https://huggingface.co/datasets/superdoc-dev/docx-corpus/raw/main/README.md)。
- 官方 API 元数据（[api/datasets/superdoc-dev/docx-corpus](https://huggingface.co/api/datasets/superdoc-dev/docx-corpus)，2026-09-02 获取）：author=superdoc-dev，id=superdoc-dev/docx-corpus，private=false、gated=false，仓库 commit sha=86593bcc2041f2a134258574d7f368bedc694a02，HF 侧 createdAt=2026-03-09T19:43:52Z、lastModified=2026-03-09T19:46:50Z。
- 官方配套 GitHub 仓库：[superdoc-dev/docx-corpus](https://github.com/superdoc-dev/docx-corpus)（GitHub API：created_at=2026-01-09T11:10:21Z，pushed_at=2026-08-11T12:31:56Z，默认分支 main，仓库级 license=MIT）。该仓库不只是数据代码，还包括 [README](https://github.com/superdoc-dev/docx-corpus/blob/main/README.md)、[LICENSE](https://github.com/superdoc-dev/docx-corpus/blob/main/LICENSE)、官方站点内容源文件（[dataset.md](https://github.com/superdoc-dev/docx-corpus/blob/main/apps/site/content/dataset.md)、[quality.md](https://github.com/superdoc-dev/docx-corpus/blob/main/apps/site/content/quality.md)、[download.md](https://github.com/superdoc-dev/docx-corpus/blob/main/apps/site/content/download.md)）。
- 卡片与[docxcorp.us 首页 JSON-LD](https://docxcorp.us) 自称创建方为 SuperDoc（superdoc.dev）；代码 LICENSE 落款为 "Copyright (c) 2026 Harbour Enterprises Inc"（VERIFIED，见 [LICENSE 文件](https://github.com/superdoc-dev/docx-corpus/blob/main/LICENSE)）。

### 1.2 数据集组成与用途（VERIFIED）

- 卡片声明：736K+ 个来自公开网络的真实 .docx，已分类为 10 种文档类型、9 个主题、76 种语言，用途为文档分类/文档处理研究（[卡片](https://huggingface.co/datasets/superdoc-dev/docx-corpus/raw/main/README.md) YAML 含 task_categories: text-classification）。
- HF 仓库实际只含**元数据 parquet**（单文件 data/train-00000-of-00001.parquet，63,572,941 字节；见 [HF tree API](https://huggingface.co/api/datasets/superdoc-dev/docx-corpus/tree/main/data)），.docx 本体存放在 DocxCorp 的 Cloudflare R2（https://docxcorp.us/documents/{id}.docx）。
- 行级实测（HF datasets-server [rows API](https://datasets-server.huggingface.co/rows?dataset=superdoc-dev/docx-corpus&config=default&split=train&offset=0&length=3)，2026-09-02）：num_rows_total=736706；字段为 id, filename, type, topic, language, word_count, confidence, url。样本行如 filename="document.do"（fr/legal）、filename="content"（es/educational）、filename="index.php"（ru/administrative）——filename 只是源 URL 里的原始文件名，**不代表文件一定是规范命名的 .docx**（官方 schema 说明见 [dataset 页](https://docxcorp.us/dataset)）。
- 分类方法：两阶段（LLM 标注样例 + 微调 XLM-RoBERTa 分类器），[卡片](https://huggingface.co/datasets/superdoc-dev/docx-corpus/raw/main/README.md)、[quality 页](https://docxcorp.us/quality)（标签器提到 Claude Haiku 4.5）与 [GitHub README 管道说明](https://github.com/superdoc-dev/docx-corpus/blob/main/README.md)一致；置信度为 min(type_conf, topic_conf)，官方说明“不是校准概率、无人工标注测试集”（[quality 页](https://docxcorp.us/quality)）。
- 数据统计（官方 [dataset 页](https://docxcorp.us/dataset) 与 [llms.txt](https://docxcorp.us/llms.txt)，页面标注 lastVerified 2026-05-19）：已上传 1,101,537 / 已分类 736,242 / 待分类 267,539 / 待提取 93,440 / 空文本 4,316 / 重复 241,993 / 失败 117,862；word_count 中位数 566、平均 2,795、最大 15,811,488；语言 76 种，top5 = en 245,018 (33.3%)、ru、cs、pl、es；类型/主题计数与 736,242 总数自洽（[llms.txt](https://docxcorp.us/llms.txt)）。

### 1.3 许可证（声明 VERIFIED；注意适用范围）

- HF 卡片 YAML 与官方 API：license=odc-by（[卡片原文](https://huggingface.co/datasets/superdoc-dev/docx-corpus/raw/main/README.md)、[HF API](https://huggingface.co/api/datasets/superdoc-dev/docx-corpus)）。
- 官网四处一致声明“数据集**元数据**采用 ODC-BY 1.0；管道源码 MIT；**单个文档内容保留原作者版权**，语料是元数据索引+内容寻址镜像”（[dataset 页](https://docxcorp.us/dataset)、[download 页](https://docxcorp.us/download)、[quality 页已知局限 8](https://docxcorp.us/quality)、[首页 JSON-LD](https://docxcorp.us) 链接 [ODC-BY 1.0 文本](https://opendatacommons.org/licenses/by/1-0/)）。
- 结论：
  - **元数据行（含 url 列）**：官方声明 ODC-BY 1.0，即需署名来源并可再分发（VERIFIED 作为“官方声明”；具体义务以 [ODC-BY 1.0](https://opendatacommons.org/licenses/by/1-0/) 文本为准）。
  - **.docx 文件本身**：官方明确版权归原作者（VERIFIED 声明），ODC-BY 不覆盖它们——本项目能否再分发某份文档、以何条件分发，需逐份结合来源站点条款判断，**不能由数据集许可推断**（UNVERIFIED，除非官方补充文件级许可）。


### 1.4 个人信息风险（INFERENCE + 事实）

- 第一方资料中**没有找到脱敏/PII 过滤声明**（卡片、dataset/quality/download 页、GitHub README 均无）；官方有 takedown 通道：“如果发现属于你的文档需要移除，发邮件 help@docxcorp.us 并附哈希/URL/所有权证明，7 天内处理”（[GitHub README](https://github.com/superdoc-dev/docx-corpus/blob/main/README.md)、[dataset 页](https://docxcorp.us/dataset)、[llms.txt](https://docxcorp.us/llms.txt)）。
- 类目本身提示 PII 高发：forms（表单）、correspondence（信函）、government、healthcare 等类型均为真实网络文档（[llms.txt 类型分布](https://docxcorp.us/llms.txt)）。
- 判定：**数据集很可能含个人信息且无脱敏承诺；选用样本前必须人工抽查提取文本**（INFERENCE）。本项目只应把已人工核查、不含可识别个人信息的少量文档放入公开仓库。

### 1.5 下载/版本/哈希如何记录（VERIFIED + 实测）

- 版本锚点：HF 仓库 commit 86593bcc2041f2a134258574d7f368bedc694a02（[HF API](https://huggingface.co/api/datasets/superdoc-dev/docx-corpus)）；parquet 文件的 LFS SHA-256 4b01438bc3c56d1a7d652875fbc9782ca6b88a9b302be302d694fd814ac87b12、git blob oid 99a60c75cad9bca70ae19dc46bb72419c0acab85、Xet 哈希 d3ec5090…（[HF tree API](https://huggingface.co/api/datasets/superdoc-dev/docx-corpus/tree/main/data)）。注意：HF 侧 lastModified 为 2026-03-09，GitHub 仓库 2026-08-11 仍在更新——**以 HF 快照为准时记录上述哈希**（观察事实）。
- 官方下载方式：[download 页](https://docxcorp.us/download)——a) HF parquet（元数据）；b) manifest 端点 https://api.docxcorp.us/manifest?type=&topic=&lang=&min_confidence=，每次响应上限 2M 条 URL（官方页原文），全量约 736K URL；c) 单文件 https://docxcorp.us/documents/{id}.docx；d) 已提取文本 https://docxcorp.us/extracted/{id}.txt（实测 HEAD：HTTP 200、4,904 B、响应头 X-Robots-Tag: noindex，与 [download 页](https://docxcorp.us/download) 描述一致）。
- 实测（2026-09-02）：https://api.docxcorp.us/manifest?type=legal&lang=en 返回 HTTP 200（约 4.3 MB 文本，每行一个 documents/{id}.docx URL）。
- **实测哈希不符**（VERIFIED，重要）：按行 0/1/2 的 url 下载 3 个 .docx（40,085 B / 770,159 B / 24,880 B，均以 ZIP 魔数 PK\x03\x04 开头，样本 1 无 \r\n\r\n 尾字节），本地 SHA-256 分别 a67dcf9e…、3bfcb371…、9c6ef497…，**均不等于各自行 id**。官方多处声明 id 是文件字节的 SHA-256（[dataset 页](https://docxcorp.us/dataset)、[quality 页](https://docxcorp.us/quality)、[HF 卡片](https://huggingface.co/datasets/superdoc-dev/docx-corpus/raw/main/README.md)）。仓库 README 提到旧抓取可能带 4 字节 WARC 尾部（commit 477d1b9 前）并提供修复/重发布脚本（[README](https://github.com/superdoc-dev/docx-corpus/blob/main/README.md)），这可能解释差异，但**官方没有对“下载字节 ≠ id 哈希”给出说明**（原因 UNVERIFIED）。因此：**不在我们的 manifest 里把 id 当作校验值，一律自算 SHA-256**。

---

## 2. GitHub：DS3Lab/WordScape

### 2.1 来源归属（VERIFIED）

- 仓库：[DS3Lab/WordScape](https://github.com/DS3Lab/WordScape)（GitHub API，2026-09-02：repo id 721212829，组织 DS3Lab，public，默认分支 main，无 tags、无 releases、未归档）。
- 第一方说明：README 称其为“从 Web 爬取数据中提取多语言、视觉丰富的文档及版面标注的管道”，论文见 [OpenReview](https://openreview.net/pdf?id=xewwYquInO)，引用信息（NeurIPS 2023，作者列表）在 [README 的 Citation 段](https://github.com/DS3Lab/WordScape/blob/main/README.md)（VERIFIED 为仓库内自述，未核对外部出版物）。

### 2.2 组成与用途（VERIFIED）

- 仓库内容为**代码管道**：解析 Common Crawl → 提取 .doc/.docx URL → 下载 → 用 LibreOffice/PDF2Image 渲染页面图像、提取文本并生成语义实体（标题、表格等）的边界框标注（[README](https://github.com/DS3Lab/WordScape/blob/main/README.md)）。
- 发布物是 **URL 列表 + 校验和**：README 提供全部 9,418,228 条 URL（含关联文档 SHA-256 校验和）的下载，并按 Common Crawl 快照拆分：2013-48（57,150）、2016-50（309,734）、2020-40（959,098）、2021-43（1,424,709）、2023-06（3,009,335）、2023-14（3,658,202）（[README 表格](https://github.com/DS3Lab/WordScape/blob/main/README.md)）。
- 下载环节会保存元数据（HTTP 状态、OLE 信息、响应 SHA-256）用于完整性分析（[README](https://github.com/DS3Lab/WordScape/blob/main/README.md)）；[README_DOWNLOAD.md](https://github.com/DS3Lab/WordScape/blob/main/README_DOWNLOAD.md) 进一步说明每个 shard 对应 metadata parquet、“包含响应 bytehash 以防投毒”。
- 结论：**WordScape 不提供、也不镜像文档内容本身**；用户拿到 URL+校验和后自行从原始站点下载（VERIFIED，README 工作流如此描述）。这意味着若选它，需要自建下载+解析链路，且原始 URL 可达性无法保证。

### 2.3 许可证（VERIFIED 范围有限）

- 仓库 LICENSE 为 Apache License 2.0 全文（[LICENSE](https://github.com/DS3Lab/WordScape/blob/main/LICENSE)，11,357 B；GitHub API license 字段 apache-2.0 / SPDX Apache-2.0）。
- README “License” 段仅说：“贡献本仓库即同意按 LICENSE 文件许可你的工作”（[README](https://github.com/DS3Lab/WordScape/blob/main/README.md)）——**该许可只覆盖仓库代码**。
- 未发现针对“URL 列表数据集”的独立许可声明（仓库无其他 LICENSE 类文件，2026-09-02 通过 GitHub API 树核实）；Google Drive 分享链接可访问（下述 2.5），但**列表数据的再分发许可 = UNVERIFIED**。
- 文档正文：WordScape 不重分发文档，故“文档再分发”问题退化为“从原始站点下载是否允许”，逐站点不同，**UNVERIFIED**，本项目不深入。

### 2.4 个人信息风险（INFERENCE）

- 仓库内（README、LICENSE、README_DOWNLOAD）**没有** PII/脱敏相关声明；文档来自公共网络，类型上与 docx-corpus 类似，很可能含个人信息（INFERENCE）。下载环节唯一的安全相关说明是拒绝“潜在恶意特征”与过大文件（[README](https://github.com/DS3Lab/WordScape/blob/main/README.md)）。

### 2.5 下载/版本/哈希（VERIFIED / UNVERIFIED）

- 版本标识 = Common Crawl 快照号（CC-MAIN-2013-48 等），URL 列表自带每文档 SHA-256 校验和（[README](https://github.com/DS3Lab/WordScape/blob/main/README.md)）——这是该数据源推荐的完整性记录方式（VERIFIED 声明；未实测比对该列表与被下载文件）。
- 列表存放于 Google Drive（README 给出的 7 个分享链接）。2026-09-02 实测 7 个分享页均返回 HTTP 200（约 77–79 KB 的查看页 HTML）；**仅证明分享页可达，未验证文件本身可完整下载、大小/哈希**（UNVERIFIED）。
- 仓库无 tag/release，代码版本只能以 commit 记录（2026-09-02 实测 GitHub API 返回空 tags/releases）。


---

## 3. DocxCorp 官方 download 页面

### 3.1 页面与内容（VERIFIED，2026-09-02）

- 官方入口 [docxcorp.us/download](https://docxcorp.us/download)（HTTP 200）与配套 dataset（[docs 页](https://docxcorp.us/dataset)）、quality（[quality 页](https://docxcorp.us/quality)）、classification（[classification 页](https://docxcorp.us/classification)）、[llms.txt](https://docxcorp.us/llms.txt) 均可访问；站点内容源文件在官方仓库 apps/site/content/*.md（如 [dataset.md](https://github.com/superdoc-dev/docx-corpus/blob/main/apps/site/content/dataset.md)）。
- download 页（官方原文要点）：两种取数方式——Hugging Face 元数据 parquet；或 api.docxcorp.us/manifest（可按 type/topic/lang/min_confidence 过滤，wget -i manifest.txt 批量下载 R2 上的 .docx）；单文档 docxcorp.us/documents/{id}.docx；纯文本 docxcorp.us/extracted/{id}.txt；页面标注 **“License: ODC-BY 1.0. Cite as superdoc-dev/docx-corpus”**。
- 首页 JSON-LD（schema.org Dataset）：license 指向 https://opendatacommons.org/licenses/by/1-0/，creator=SuperDoc（[docxcorp.us](https://docxcorp.us)）。

### 3.2 许可是否可以确认（声明 VERIFIED / 边界 UNVERIFIED）

- 可以确认（作为官方声明）：**元数据层面** ODC-BY 1.0 在四处第一方位置一致出现——download 页、dataset 页、首页 JSON-LD、HF 卡片 YAML。
- 不能确认：**原始 .docx 文件层面**的再分发许可——官方明确“文档版权归原作者”（[dataset 页](https://docxcorp.us/dataset)、[quality 局限 8](https://docxcorp.us/quality)），未给出文件级许可；也未发现任何 PII/脱敏承诺。这两点按用户要求明确标记为 **UNVERIFIED**（官方网页可访问、但缺少相应声明，不猜测）。

---

## 4. 三来源对比

| 维度 | superdoc-dev/docx-corpus + docxcorp.us | DS3Lab/WordScape |
| --- | --- | --- |
| 来源归属 | SuperDoc（Harbour Enterprises Inc），HF+GitHub+官网一体（VERIFIED） | DS3Lab 组织，NeurIPS 2023 论文配套代码（VERIFIED） |
| 组成 | 元数据 parquet（73.6 万行）+ R2 上的 .docx 镜像 + 提取文本 | 管道代码 + 9.4M URL 列表（含 SHA-256 校验和），文档在原始站点 |
| 元数据/代码许可 | 元数据 ODC-BY 1.0；代码 MIT（官方声明 VERIFIED） | 代码 Apache-2.0（文件+API VERIFIED）；URL 列表许可未声明（UNVERIFIED） |
| 文档再分发 | 官方明示版权归原作者、许可不覆盖（声明 VERIFIED；逐份许可 UNVERIFIED） | 不重分发文档（VERIFIED） |
| PII 风险 | 无脱敏声明；类目含 forms/correspondence/healthcare（INFERENCE 高风险；有 takedown 通道） | 无脱敏声明（INFERENCE 高风险） |
| 下载/版本/哈希 | HF commit sha + parquet LFS SHA-256 可固化；单文件/清单下载可行（VERIFIED）；id ≠ 实测字节哈希（VERIFIED 实测） | 快照号 + 列表内 SHA-256（VERIFIED 声明）；Drive 文件内容未实测（UNVERIFIED） |
| 接入本项目成本 | 低：直接按 url 下载少量文件或摘取元数据行 | 高：需自建下载+解析（含原站依赖、可达性风险） |

---

## 5. 本项目最小公开样例策略（推荐）

结合阶段一设计 §7（“真实公开文档 + 可控缺陷变体 + 标签”、“manifest 记录 URL/获取时间/SHA-256/许可证/引用/本地位置”）：

1. **只取少量**：8–20 份，优先类型 reports/policies/educational/administrative/correspondence，**避开 healthcare、forms、government 做公开样例**（PII 概率高，INFERENCE）；如需领域代表性再选取并人工逐份核验。
2. **过滤条件**：confidence ≥ 0.8 且 word_count 在 100–5,000（官方说明置信度未校准、存在 15.8M 词巨型文档，[quality 页](https://docxcorp.us/quality)）；中英混合可选（language=en/zh，HF 卡片语言标签含 zh，[卡片](https://huggingface.co/datasets/superdoc-dev/docx-corpus/raw/main/README.md)）。
3. **获取方式**：从 HF parquet 挑行 → 用 url 列单文件下载（比 manifest 更可控），或先取 extracted/{id}.txt 预览文本，再决定是否下载原文（[download 页](https://docxcorp.us/download) 提供两种路径）。
4. **逐文件记录（manifest 每行）**：行 id、url、下载 UTC 时间、字节数、**本地自算 SHA-256**（不可依赖 id，见 1.5 实测）、HF 版本锚点（commit 86593bcc… + parquet LFS SHA-256 4b01438b…，取自 [HF API/tree](https://huggingface.co/api/datasets/superdoc-dev/docx-corpus/tree/main/data)）、许可声明（元数据 ODC-BY 1.0 / 文档版权归原作者）、引用（"docx-corpus (2026), https://docxcorp.us"）、人工 PII 抽查结论、本地存放路径（仓库外）。
5. **仓库只提交元数据与期望标签**：.docx 原文放仓库外目录并由 .gitignore 排除；公开样例仅限“人工核验无 PII、结构有代表性”的少量文件，并附 manifest（对齐阶段一 §7）。
6. **测试回归不依赖外部**：基线回归继续用“许可明确的基准文档 + 可控缺陷变体”（阶段一 §7 已有设计）；公开文件只作外部评估语料。
7. **WordScape 的用途**：仅当需要“带版面/布局标注”或更大规模时才考虑；届时用其快照 URL 列表 + SHA-256 校验和做小批量抽验，先验证原站可达性，再谈接入（UNVERIFIED 项未解决前不投入）。

**不能做的事情**（阶段一 §7 的硬边界，结合本次核验）：

- 不把 .docx 原文或 extracted/*.txt 全文重新发布到公开仓库（许可只覆盖元数据）。
- 不把未经人工核验的 healthcare/forms/government/含个人信息文档放进仓库或演示材料。
- 不全量下载/镜像 docxcorp R2 或 WordScape 的 9.4M URL（超出最小样例边界，也尊重上游带宽）。
- 不把行 id 当作文件哈希写入 manifest（实测不符）。
- 不在没有记录 HF commit/parquet SHA-256 与下载时间的情况下“复现”数据实验。
- 不把 WordScape 的 Google Drive 列表文件提交进 Git（其再分发许可 UNVERIFIED）。
- 不把“76 语言/46+ 语言/736K”等数字当成单一权威口径（各第一方页面数字不一致，引用时必须写明来源与日期，见 §6）。
- 不因“ODC-BY 1.0”字样就推断可以自由再分发文档原文。

---

## 6. 未确认项与数字口径（UNVERIFIED / 不一致清单）

- **官方数字互不一致**（VERIFIED = 各页面确写了这些数字，但它们不一致）：首页 JSON-LD 与 GitHub README 写 “46+ languages”，卡片描述/dataset 页/quality 页/llms.txt 写 76 种，HF YAML 语言标签只列 20 个代码；HF rows API 行数 736,706（2026-09-02），官网/llms.txt 写已分类 736,242（页面 lastVerified 2026-05-19）。引用时按来源分别标注。
- **id 与下载字节哈希的关系**：3/3 样本不符；官方无说明（UNVERIFIED）；可能原因（WARC 尾部字节修复后对象被重发布，[README](https://github.com/superdoc-dev/docx-corpus/blob/main/README.md)）仅作为推断（INFERENCE）。
- **WordScape URL 列表**：分享页可达（VERIFIED 2026-09-02），文件内容、大小、哈希未验证（UNVERIFIED）；列表再分发许可 UNVERIFIED。
- **两份数据源的文档层再分发许可与 PII 脱敏**：均无第一方声明（UNVERIFIED）。
- **DocxCorp 许可确认边界**：元数据 ODC-BY 1.0 = 官方声明 VERIFIED；文件级许可 = UNVERIFIED（页面可访问但无声明，不猜测）。

## 7. 附：本次核验的线上动作（时间点 2026-09-02，UTC+8）

- HF：数据集 API、tree API、raw 卡片、datasets-server rows API、parquet HEAD（均 HTTP 200）。
- DocxCorp：首页、/download、/dataset、/llms.txt、manifest（legal&en，HTTP 200）；下载 3 份样本 .docx 并计算 SHA-256；extracted/{id}.txt HEAD。
- GitHub：DS3Lab/WordScape 与 superdoc-dev/docx-corpus 的 Repo API、文件树 API、README/LICENSE/README_DOWNLOAD 原文，WordScape tags/releases API（空）。
- Google Drive：7 个分享页 HTTP 200（内容未下载验证）。
- 所有抓取结果仅用于本文；样本文件保留于系统临时目录，未进入项目仓库。
