# 设计规格 — voice-onboard：Exemplar 锚点 + 可检查 Hard Rules

> 本文为 `design-voice-onboard-exemplars-hardrules-2026-07-03.md`（英文 canonical 版）的中文镜像。两份内容一致，以英文版为准。

- **日期：** 2026-07-03
- **状态：** SPEC —— 等 owner 批准。**owner 说 "go" 之前不写任何代码。**
- **流程：** brainstorming → grill-me（21 个分支逐一 resolve）→ 本 SPEC。
- **源 idea：** @0xxDana,《why your AI sucks at writing + how to fix it》(https://x.com/0xxDana/status/2073030267552616936)。
- **工作笔记 / 决策链：** `docs/brainstorm-voice-onboard-dana-sharpen-2026-07-03.md`。

---

## 1. 摘要

给 `voice-onboard` 加两个 append-only 的新 section 到 voice-profile 契约，并教会
`comms-polish` + `comms-draft` 消费它们：

- **B — Exemplars（范例锚点）：** 2-3 篇 verbatim「好的样子」样本，当 **few-shot 风格锚**
  用（校准作者「怎么写」；绝不照抄「写了什么」）。
- **C — Hard Rules（硬规则）：** 从 profile 最强信号蒸馏出的 ≤7 条钝的、**可检查**的祈使句，
  以 **advisory**（提示，绝不硬阻）方式执行。

两者都是 `_shared/voice-profile.md` 里的新 `## H2` section —— 这是 `comms-polish`/
`comms-draft` 已经在读的冻结契约。**无新文件、无新读路径。**

## 2. 动机

Dana 的方法强在**动态 / 语料 / 与结果耦合**；`voice-onboard` 强在**静态 / 纪律 / 契约**。
本 SPEC 把 Dana 的两个动态强项嫁接进来，**且不丢** `voice-onboard` 的纪律。

**Regime = 公司 DS 内部 comms（owner 决策 Q1=a）：** 样本少（常 3-10 篇）、无互动指标。
这砍掉两个看似诱人的点子：算真实统计分布（n<~50 时全是噪声）、互动反馈 loop（无指标）。
它也翻转了哲学：数据贫 regime 下，**具体 exemplar + 人的判断** 胜过统计挖掘。B 和 C 正是
数据贫场景对症的做法。

## 3. 范围

**本轮做：** B（Exemplars）+ C（Hard Rules），由 `comms-polish` 和 `comms-draft` 两者消费。

**不做 / 推迟：**
- **F — 隐性知识访谈**（主动问出「绝不写的词」、观点、work/personal 界线）：本 regime 下高价值，
  但它会改 `voice-onboard` 的 Step 流程 → **下一轮**单独聊（owner 已 flag）。
- **A — 算真实分布：** 关（小样本噪声）。
- **E — 互动→再 profile loop：** 关（内部 comms 无指标；且撞人工闸门反漂移设计）。
- **D — formalize 多 register profile：** 大部分已被现有 `Scope & Calibration` 覆盖；暂 YAGNI。

## 4. 约束与不变量（不可破）

1. **契约冻结：** `comms-polish`/`comms-draft` 按**命名 H2 header** 读 `voice-profile.md`。
   只能 **append** 新 header；绝不改名/删除旧的。
2. **人工闸门、append-only 的自我改进：** 除本次 owner 批准的改动外，绝不自动改任何 SKILL.md、
   pattern catalog 或 profile schema。
3. **OSS 引擎、非用户数据：** shipped 的 `voice-profile.md` 是*样例*（虚构「Sam」）。新 section
   用 Sam 的虚构内容 ship，仅展示 shape。
4. **eval 纪律：** 任何 fixture 守 30-40% baseline-fail 带；blind；instance-specific；judge 对齐
   human 标签。**detector = regression signal，绝不做 KPI。**
5. **不捏造 / never invent voice：** 数据薄 → section 诚实降级，绝不编 exemplar 或 rule。

## 5. 设计

### 5.1 `_shared/voice-profile.md` —— 两个新 H2 section

追加位置：**`## Scope & Calibration` 之后、`## Changelog` 之前**（Changelog 保持最后）。

**`## Exemplars`** —— 2-3 条。每条：
- **verbatim** 样本（代码块围栏），
- 一行 **「为何 gold」** 点明要模仿的维度（节奏? 直白? 结构?）—— 这行防止模型表面
  pattern-match 到错误维度，
- **genre 标签**（memo / analysis-report / LinkedIn / …）。

**`## Hard Rules`** —— ≤7 条（软上限；常 ~5），只收高置信。每条：
- 一条 **祈使句 + 可检查** 的断言（好、可检查：“Never use hype words like 'unlock' or 'amazing'”；
  坏、含糊：“Sound authentic”），
- 一个 **evidence** 指针（样本引文或作者亲述的「绝不写」），
- 从 `Vocabulary Don't` + `Things To Avoid`（+ 最强 `Signature Moves` 转正向）蒸馏。
  **author-specific**，不是通用 AI-tell catalog 的复制。

### 5.2 `_shared/host-profile-template.md`

加两个对应的空白字段，让 `voice-onboard` 的填表步骤能产出它们。

### 5.3 `voice-onboard/SKILL.md` —— 生产侧

- **Step 2（抽取）：** 在 10 维之后，从最强的 `Vocabulary Don't` / `Things To Avoid` 信号蒸馏出
  ≤7 条 hard rules（附 evidence）。
- **Step 3（填表 + 展示）：** 额外 **提议 2-3 个 exemplar 候选**（最像作者的样本）并点明「为何 gold」；
  展示草拟的 hard rules。
- **Step 4（确认 + 写入）：** 作者 **确认/替换** exemplar 与 rules（他们拥有「什么算好」）后再写入 ——
  延续现有人工闸门。
- **降级：** 样本太薄、抽不出可信 exemplar/rule 时，写 header + 诚实的空标记，沿用 profile 现有约定
  —— `Unknown — not enough signal`（voice-onboard 对信号不足的维度已在用的哨兵）或
  `None yet — add after a few polish runs` —— 绝不捏造。
- 更新技能的「What you read and write」，列出两个新输出 section。

### 5.4 `comms-polish/SKILL.md` —— 消费侧

- **Voice Matching 清单**（现枚举 Tone … Scope & Calibration）：**加入 `Exemplars` 和 `Hard Rules`。**
- **Rewrite step 7**（偏向 voice）：读**同 genre** 的 exemplar 当 **few-shot 风格锚**，并显式写
  **anti-copy 护栏** —— 只校准节奏/选词/结构，**绝不搬措辞或内容**（照抄伤 lexical originality，
  且违反「不加原文没有的内容」）。
- **`references/final-pass-checklist.md`：** 加一段 **Hard Rules 扫描** —— 逐条 pass/fail 查输出，
  **advisory**（提示、不阻）。genre 硬约束和事实仍然优先。

### 5.5 `comms-draft/SKILL.md` —— 消费侧

- **Inputs 清单**（L44-48）：**加入 `Exemplars` 和 `Hard Rules`。**
- **Step 3（在约束下起草）：** 用同 genre exemplar 当 few-shot 目标（同一 anti-copy 护栏）；
  把 hard rules 当写作时的额外**负面清单**。
- **Step 5（自扫）：** 把 hard-rules 检查纳入草稿后扫描。

### 5.6 优先级（冲突裁决）

各来源打架时：

1. **硬约束** —— genre 限制（280 字）、神圣代码块、事实、法律/安全警告 —— 永远赢。
2. **作者专属** —— Hard Rules + Exemplars + voice-profile + 该作者的 `learned-rules` —— 压过
   通用 AI-tell catalog（是 TA 的声音、不是 slop；先例：`learned-rules.md` 的 `LR-000`）。
3. **通用 AI-tell catalog** —— 默认；让位给作者专属。

Hard Rules（onboard 抽取）vs `learned-rules`（事后人工闸门纠错）撞 → **`learned-rules` 赢**
（更新、显式纠正过）。

### 5.7 优雅降级与 OSS 样例

- 缺 section 绝不报错（两个消费方已内建缺段降级）。
- present-but-empty 的哨兵内容（`Unknown — not enough signal` / `None yet`）视为**缺失** ——
  消费方既不 few-shot 它、也不拿它评分输出。
- 无同 genre exemplar 时 **跳过** exemplar few-shot 并标注 —— 绝不用跨 genre 的 exemplar 顶替。
- shipped 样例 profile 用**虚构 Sam** 数据展示这两段。

## 6. 测试与 eval

### 6.1 结构测试 —— 现在做（stdlib-only、CI-safe；对齐现有 stdlib 套件 —— 截至 2026-07-03 共 78 个测试）

- 新 section 能从 `voice-profile.md` 解析。
- `comms-polish` + `comms-draft` 的消费清单含 `Exemplars` + `Hard Rules`。
- 两个消费点都有 anti-copy 护栏文本。
- 优雅降级：section 缺失/`None yet` 时两个 skill 行为正常。
- Hard Rules 接成 **advisory**（出现在 final-pass 扫描；非硬阻）。

### 6.2 质量 eval —— 现在设计、数字 BLOCKED

要设计的 fixtures（暂不跑数字）：(a) exemplar on/off 的声音匹配；(b) hard-rule flag 的
precision/recall **加误报率**；(c) 生成稿与其 exemplar 之间的 **copy-rate / 最长公共片段重叠**
检查 —— **可用合成的同 genre 输入播种**，故能在 16-24 真稿到齐*之前*就跑，在 P3 block 之前
部分 de-risk anti-copy 护栏。守 30-40% 带；blind；instance-specific；judge 对齐 human。
**质量数字继承现有 P3 block（需 16-24 篇真实企业稿）—— 不报、不捏造。** 不引入新 blocker。

## 7. 上线

- **分支：** 从 `main` 开**新分支** `feat/voice-onboard-exemplars-hardrules` 实现
  （**不**在当前无关的 `feat/audit-report-template` 上做）。绝不 commit 到 `main`。
- **契约演进：** `voice-profile.md` Changelog 追加一行记两个新 section。**suite 版本
  1.1.0 → 1.2.0 在实现 + 验收后再 bump**，不现在。
- **本轮交付：** 仅本 SPEC → **STOP**。owner 说 "go" 前不写码。

## 8. 文件触碰地图（供后续实现计划）

1. `_shared/voice-profile.md` —— 加 `## Exemplars` + `## Hard Rules`（Sam 样例内容）。
2. `_shared/host-profile-template.md` —— 加两个空白字段。
3. `skills/voice-onboard/SKILL.md` —— 抽取 + 提议 + 确认 + 降级 + I/O 说明。
4. `skills/comms-polish/SKILL.md` —— Voice Matching 清单 + step 7 exemplar few-shot（anti-copy）。
5. `skills/comms-polish/references/final-pass-checklist.md` —— advisory Hard Rules 扫描。
6. `skills/comms-draft/SKILL.md` —— Inputs 清单 + step 3 few-shot（anti-copy）+ step 5 自扫。
7. `evals/` —— 结构测试现在做；质量 fixtures 设计好（数字推迟）。
8. `CHANGELOG.md` + `voice-profile.md` Changelog 行。

（byte 级精确编辑是 writing-plans 的交付物，不是本 SPEC。）

## 9. 决策 log（grill-me，21 分支，全 owner-approved 2026-07-03）

| # | 分支 | 决策 |
|---|---|---|
| B1+C1 | 存哪 | 方案1：`voice-profile.md` 两个新 H2 |
| X1 | 消费方 | `comms-polish` + `comms-draft` 都接 |
| B5 | exemplar 用法 | 参考不抄（anti-copy 护栏） |
| C5+C7 | 规则执行 | advisory（final-pass 扫描 + draft 负面清单） |
| C6 | 优先级 | 硬约束 > 作者专属 > 通用；learned-rules > hard-rules |
| B3+B4+B6 | exemplar shape | 2-3 ×（verbatim + 「为何 gold」+ genre）；提议→确认；只用同 genre |
| C2+C3+C4 | 规则 shape | ≤7、高置信；来自 Don't/Avoid；祈使+可检查+evidence |
| C8+X3 | 验证 | 结构测试现在做；质量数字等真稿 |
| B7+B8 | 降级 | OSS 样例用虚构 Sam；诚实标 "None yet"，绝不捏造 |
| X2+X4+X5 | 流程 | Changelog 行 + 版本后置；只出 spec 然后 STOP；从 main 开新分支 |

## 10. 待办 / 下一步

- **F（隐性知识访谈）** —— 下一轮、单独讨论（owner 已 flag）。
- **质量数字** —— 攒够 16-24 篇真实企业稿后解锁（P3）。
