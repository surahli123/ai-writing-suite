# voice-onboard 声音蒸馏子技能 —— 借 Dana "the folder is the agent" 帖子的 sharpen brainstorm

- 日期：2026-07-03
- 触发：owner 读到 @0xxDana《why your AI sucks at writing + how to fix it》，想用其中方法 sharpen voice-onboard。
- 性质：brainstorm only（当前在 `feat/audit-report-template` 分支，有无关 in-flight 工作 → 不碰代码）。
- 源帖：https://x.com/0xxDana/status/2073030267552616936

---

## 0. 边界与硬约束（不能违反）

- **契约冻结**：`_shared/voice-profile.md` 的 `## H2` header 是 comms-polish 按 header 读的稳定契约。只能 **append 新 header**，不能改/删旧的（否则 silent fallback bug）。
- **人工闸门 + append-only**：self-improvement 禁止自动改 SKILL.md / catalog / profile schema。approved 规则只进 `learned-rules.md`。
- **OSS 引擎定位**（engine vs fuel）：这是公司 DS comms 工具的公开版，引擎通用、真实 playbook 由公司 fork 注入。voice-onboard 主面向"公司 DS 内部沟通"（memo / 分析报告 / LinkedIn），**不是纯个人 X drafter**。
- **eval 纪律**：baseline 要 fail 30-40%；detector = regression signal，**永不做 KPI**；blind + instance-specific。
- v1.1 已 SHIPPED，65 tests green。

---

## 1. Dana 帖子的可迁移内核（distilled 成对 voice-onboard 有用的 7 条）

1. **"The folder is the agent"** —— context 住在文件里，缺 context 再好的 prompt 也救不了。（voice-onboard 已是这哲学：profile = 文件契约。）
2. **Archive = ground truth**，让 model 从结构化 archive **计算分布**（80% 小写开头 / 57% 多行 / 20% 提问且与高互动相关），而非人工拍脑袋。规则：retweet ≠ 你的声音。
3. **Profile 要具体到数字 + 绝不用的词**。lazy（"casual, no corporate speak"）= 废；good = 真实百分比 + 精确用词 + 绝不用的词 + 带例子的话题角度。人做 model 做不了的部分：绝不写的话、你的观点、**工作声音 vs 个人声音的界线**。
4. **Cheat code：把 2-3 篇最强帖子存进 drafts/posted/ 当 "what good looks like" 锚点**，model 拿它当"好的样子"。
5. **CLAUDE.md（常驻行为）vs SKILL.md（任务 playbook）分层**：规则要**钝且可检查**（"never open with a rhetorical contrast" 可执行；"sound authentic" 不可检查 = 废）。
6. **Gotchas 是长期最高价值段**：每次纠正 model 超过一次的点就沉淀成规则 → 一个月后 agent 像定制的。
7. **The loop（week1 vs week4）**：每篇已发帖存 drafts/posted/（日期+话题），48h 后补互动数字；每次起草前先扫这文件夹。这个 feedback loop 是"静态工具 vs 会进步的工具"的全部差别。+ **register 分离**（X 小写简短 vs LinkedIn 句首大写讲论证，别混）。

---

## 2. voice-onboard 现状 vs Dana —— gap 表

| Dana idea | voice-onboard 现状 | 判定 | sharpen 机会 |
|---|---|---|---|
| archive 计算分布 | Step2 要 quantify，但框成人工判断；"trait 需出现 3+ 次" | 部分覆盖、偏手工 | 样本量够时让 model **算真实分布** |
| 绝不用的词（挖缺席） | Vocabulary Don't = "strongest signal, mine the absences" | **已覆盖且更强** | — |
| 数字化具体 profile | 10 维带 evidence，每条 3+ 次 | 已覆盖 | — |
| "what good looks like" 锚点 | 无。只抽象特征，不留具体 gold 样本 | **缺失** | 存 2-3 篇 verbatim exemplar |
| 钝可检查规则 vs vibes | profile 多为描述性 trait，非可执行断言 | **偏弱** | 蒸成 ~5 条 hard checkable rules |
| gotchas 沉淀 | learned-rules.md 人工闸门 loop | 已覆盖且更纪律 | — |
| work/personal / register 分离 | "别跨 genre 平均" + "可出两份 profile" + Scope&Calibration | 部分覆盖、未 formalize | 视需要 formalize（YAGNI 存疑） |
| 已发+互动 feedback loop | Step5 被动 calibration + 人工闸门 self-improve | 部分覆盖、非主动 outcome-coupled | 最大但最不 fit（见 §4-E） |
| 置信度门槛 | Low/Med/High by N | Dana 没有，**voice-onboard 更强** | — |
| contract schema 稳定 | H2 header 冻结契约 | Dana freeform，**voice-onboard 更强** | — |

---

## 3. 中心张力（一句话）

Dana 强在**动态 / 语料 / 与结果耦合**（archive→算分布→互动相关→已发 loop→exemplar 锚点→可检查规则）；voice-onboard 强在**静态 / 纪律 / 契约**（evidence 门槛、置信度、稳定 schema、人工闸门反漂移）。
**sharpen = 把 Dana 的动态强项嫁接进来，且不丢 voice-onboard 的纪律。**

---

## 4. Sharpen 候选（leverage / cost / risk / eval-hook / fit）

**A. 样本量够时算真实分布**（不止 3+ 启发式）
leverage 中-高（保真度↑，契合 DS owner 的 feature-distribution 心智）｜cost 中｜risk 低-中（"model 报数字"会幻觉 → 要求给计数/抽样 evidence；3-10 篇算 % 噪声大，只在大 archive 有意义 = genre-gated）｜eval：数值 vs 定性，comms-polish 匹配节奏是否更好｜fit：数字塞进现有 header，**不破契约**。

**B. Exemplar 锚点（"what good looks like"）** ⟵ 推荐
leverage 高（具体 gold 样本保留抽象特征丢失的质感；使 comms-draft/polish 能 few-shot）｜cost 低（加 `## Exemplars` 段存 2-3 篇 verbatim，**append 新 header 安全**）｜risk 低-中（存用户真实文本 → 只能用户自有、OSS 不 ship；comms-polish 不能照抄，只当"目标 bar"）｜eval：few-shot-against-exemplar vs features-only｜fit：强，对应 Dana cheat code。

**C. 输出钝可检查 hard rules（非纯描述 trait）** ⟵ 推荐
leverage 高（把描述 profile 桥接成 comms-polish 能真检查的 checklist；Dana 核心洞见）｜cost 中（把最强 Don't/avoid 蒸成 ~5 条 imperative rule，新 `## Hard Rules` 段）｜risk 中（过刚会压平声音/误报 → 呼应 owner "detector≠KPI"；规则须 author-specific + evidence-backed + 少）｜eval：规则执行 precision/recall vs 留出作者真文本｜fit：强，且与 learned-rules.md 机制平行（区分：learned-rules 是纠错沉淀，voice hard-rules 是样本抽取）。

**D. Register/persona 分离 formalize（work vs personal, X vs LinkedIn）**
leverage 中-高｜cost 中（多 profile / register 维；comms-polish 要选对 register = 改契约选择逻辑）｜risk 中｜fit：部分已被 "Scope & Calibration" 覆盖 → **YAGNI 存疑**，除非 owner 现在就要多 register。

**E. Outcome-coupled loop（互动→再 profile）** ⟵ push back，多半 defer
Dana 头号卖点，但对**本 suite 定位最不 fit**：内部 DS comms（memo/分析报告）通常**没有互动指标**；engagement 耦合只适配外部社交。且与**人工闸门反漂移**冲突（Dana 自动 promote pattern；voice-onboard 禁止自动 promote）。且**已被部分实现**（learned-rules 的人工闸门版就是纪律化 gotchas loop）。→ 别追最亮的东西。

---

## 5. 我的推荐

对**本 suite 定位**：**B（exemplar 锚点）+ C（可检查 hard rules）** = leverage 最高、risk 最低、fit 最好、append-only 安全。A 好但受样本量/genre 限。D 多半已覆盖。E 是"个人 X drafter 的好点子、DS comms 引擎的陷阱" → flag + defer。

---

## 6. 待 owner 定的开放问题

1. **主表面/样本 regime**：voice-onboard 主要为 (a) 公司 DS 内部 comms（小样本、无互动）｜(b) 外部 thought-leadership（大 archive、有互动）｜(c) 引擎保持表面无关、按样本量+指标可得性优雅降级？—— 决定 A/E 是否在桌上。
2. 这轮想 **v2 一次到位** 还是先做 **B+C 一个小切口**？
3. 是否顺带把 **Chinese 双语抽取**（现列 v2 deferred）纳入？owner 双语，可能是真需求。

---

## 7. 决策 log

- **2026-07-03 · Q1 表面/regime = (a)** 公司 DS 内部 comms 为主（memo/分析报告，样本少、无互动）。
  - 后果：**E（互动 loop）+ A（算真实分布）双双下桌**（少样本统计 = 噪声）。
  - 后果：少样本让"挖缺席"失灵 → "绝不写的词"**必须问人**，不能推断 → 浮现候选 **F（tacit-knowledge 主动访谈）**。
  - 哲学翻转：数据贫 regime → **具体 exemplar + 人的隐性知识** 为主，而非统计挖掘。
- **2026-07-03 · Q2 scope = (2) B + C**。F 挪下一轮（要改 voice-onboard 的 Step 访谈流程，风险/评审面更大，单独做）。

## 8. B + C 收敛设计（进行中）

**B — Exemplar 锚点**：存 2-3 篇 verbatim gold 样本 + 每篇 1 行"为什么 gold" + genre 标签。voice-onboard **提议候选、作者确认**（延续现有 Step3-4 人工闸门）。
- 关键护栏：exemplar 是"目标 bar"参考，**comms-polish/draft 不得照抄措辞**（否则自我抄袭/过拟合）——必须在消费点显式写明。
- genre 绑定：memo 的 exemplar 不能拿去校准 LinkedIn（挂到 Scope & Calibration）。

**C — 可检查 hard rules**：把 `Vocabulary Don't` + `Things To Avoid` 里最强的信号**蒸成 ≤5-7 条 imperative 可检查断言**（"never open with a rhetorical contrast" 而非 "sound authentic"）。每条附 evidence。
- 不是新信息，是**为"执行"重新表达**（描述性 profile → 可跑的 checklist）。comms-polish 在 final-pass 逐条 pass/fail。
- **与 learned-rules.md 区分**：learned-rules = 跨会话的人工闸门**纠错沉淀**；voice hard-rules = onboard 时从样本+访谈**抽取**。两个 loop 不要混。
- 护栏（呼应 owner "detector≠KPI"）：规则要少、高置信、author-specific，过刚会压平声音/误报。

### 存哪 —— 两个方案

**方案 1 · In-contract（推荐）**：给 `voice-profile.md` append 两个新 `## H2`：`## Exemplars` + `## Hard Rules`。
- 优：不加新文件/读路径（append-only 安全，契约冻结纪律天然偏这个）；单一 source of truth；测试面最小。
- 代价：profile 文件变长、raw 样本进契约文件。
- 注意：comms-polish/comms-draft **仍需一处小改**去*消费*这两段（读 `## Hard Rules`→跑 checklist；读 `## Exemplars`→few-shot）。不是"零接线"，但省掉新文件读路径。

**方案 2 · Side-files（更模块化）**：exemplar 单独 `_shared/voice-exemplars.md`；hard rules 进 `## Hard Rules`。
- 优：抽象 profile 与 raw 样本分离更干净。
- 代价：comms-polish/draft 要新学一个读路径 = 新契约面 + 更多接线 + 更多测试。

**判断**：这个规模下方案 2 的模块化收益 < 它的接线/测试成本（YAGNI）→ 推荐**方案 1**。

---

## 9. Grill 决策树（branch tracker，one-at-a-time，逐个 resolve）

候选 "3"（B+C+**F** tacit-访谈）= **later 单独聊**，不在本轮。本轮只 B+C。

**B — Exemplars**
- **B1 存哪**：profile `## Exemplars` vs 单独文件 ｜ rec: profile ｜ status: OPEN ⟵ 正在问
- **B2 数量**：2-3、min 2 ｜ rec: 2-3 ｜ OPEN
- **B3 选样**：onboard 提议+作者确认 vs 作者直供 ｜ rec: 提议+确认 ｜ OPEN
- **B4 元数据**：verbatim + "为何 gold" 一行 + genre 标签 ｜ rec: 三者都要 ｜ OPEN
- **B5 消费**：comms-polish/draft 当"目标 bar"参考、**禁照抄措辞** ｜ rec: 参考禁抄 ｜ OPEN
- **B6 genre 绑定**：exemplar 按 genre 标、只用同 genre ｜ rec: yes ｜ OPEN
- **B7 OSS 样例**：shipped sample 用虚构 Sam 展示 shape、不含真数据 ｜ rec: yes ｜ OPEN
- **B8 空样本**：无 gold 时优雅缺省（section 可选、标 absent）｜ rec: yes ｜ OPEN

**C — Hard Rules**
- **C1 存哪**：profile `## Hard Rules` vs learned-rules vs 单独文件 ｜ rec: profile + **与 learned-rules 分离** ｜ OPEN
- **C2 数量**：≤5-7、只高置信 ｜ rec: ≤7 ｜ OPEN
- **C3 来源**：从 `Vocabulary Don't`+`Things To Avoid` 蒸（tacit = F = later）｜ rec: 现有维度 ｜ OPEN
- **C4 形态**：imperative + checkable + 每条附 evidence ｜ rec: yes ｜ OPEN
- **C5 消费**：comms-polish final-pass 逐条 pass/fail，并入现有 layered checklist ｜ rec: yes ｜ OPEN
- **C6 优先级/冲突**：author hard-rule vs 通用 AI-tell vs learned-rule 谁赢 ｜ rec: author > 通用；detector≠KPI ｜ OPEN
- **C7 误报护栏**：规则少 + author-specific + **advisory 非 gating** ｜ rec: advisory ｜ OPEN
- **C8 eval**：rule precision/recall vs 留出作者真文本，守 30-40% baseline ｜ rec: 加 fixtures ｜ OPEN

**X — 横切**
- **X1 本轮消费面**：只接 comms-polish vs 同时接 comms-draft ｜ rec: 两者都接（读同一文件）｜ OPEN
- **X2 schema 版本/changelog bump** ｜ rec: yes ｜ OPEN
- **X3 测试**：section 存在 + 消费 + 护栏 ｜ rec: yes ｜ OPEN
- **X4 本轮交付**：只出 SPEC → STOP 等批准（brainstorming HARD GATE + owner "plan=plan only"）｜ rec: spec only ｜ OPEN
- **X5 分支**：现在 `feat/audit-report-template`（无关 in-flight）→ 实现时开新 feat 分支 ｜ rec: new branch ｜ OPEN

Grill 顺序（按杠杆）：B1+C1 存哪 → X1 消费面 → B5+C5 消费机制+护栏 → 内容(B3/B4/C3/C4) → C6/C7 → C8/X3 → 边缘(B6/B7/B8) → 流程(X2/X4/X5)。

### 已 resolve log
- **B1+C1 → 方案1**：`voice-profile.md` 加 `## Exemplars` + `## Hard Rules` 两个新 H2（append-only，与 learned-rules 分离）。[owner approved 2026-07-03]
- **X1 代码实证**：`comms-polish`(SKILL L82-90, Voice Matching + final-pass-checklist) 与 `comms-draft`(SKILL L44-48, step2/3/5) **都**已读 voice-profile.md，且都**显式枚举**要消费的 section → 新 section 必须加进各自清单才会被读。价值分布：**exemplar 对 comms-draft（从零生成、few-shot 目标）价值最高；hard rules 对 comms-polish（final-pass 逐条 pass/fail）价值最高**。消费点：exemplar→polish step7/draft step3；rules→polish final-pass-checklist/draft step3+5 负面清单。
- **X1 → polish + comms-draft 都接**。[owner approved]
- **B5 → 参考不抄**：exemplar 只校准 **HOW**（节奏/选词/结构感），禁搬措辞/整句；当 few-shot 风格锚、非内容源；消费点显式写 anti-copy 护栏。依据：照抄 → 伤 lexical originality（research 5 gaps 之一）+ 撞"不加原文没有内容"铁律。[owner approved]
- **C5+C7 → advisory**：hard rules 插 comms-polish `references/final-pass-checklist.md`（逐条 pass/fail）+ comms-draft step3/5 负面清单；违规 flag/提示、**不硬阻**输出。依据：owner 铁律 detector=regression signal NEVER KPI；只有 genre 硬约束（280 字/代码）才硬阻。[owner approved]
- **C6 → 优先级栈**：硬约束(280字/代码/事实/法律安全) > 作者专属(Hard Rules/Exemplars/voice/该作者 learned-rules) > 通用 AI-tell catalog；作者声音撞通用 tell → 作者赢。Hard Rules(onboard 抽取) vs learned-rules(事后纠错) 撞 → learned-rules 赢。先例：learned-rules `LR-000`。[owner approved]
- **B3+B4+B6 → `## Exemplars` shape**：2-3 条，每条 = verbatim 原文 + 一行"为何 gold"(点明学哪维) + genre 标签；选样 = voice-onboard 提议候选 → 作者确认/替换(人工闸门，延续 Step3-4)；用法 = comms-polish/draft 只用同 genre exemplar。[owner approved]
- **C2+C3+C4 → `## Hard Rules` shape**：≤7 条(软上限、常 ~5)、只高置信；来源 = `Vocabulary Don't`+`Things To Avoid`(+最强 `Signature Moves` 转正向)蒸馏，tacit 访谈(F)=later；形态 = 祈使句+可检查+**附 evidence**；author-specific(非通用 AI-tell 复制)。[owner approved]
- **C8+X3 → 验证策略**：**结构测试现在做**(stdlib/CI-safe：新 section 可解析、polish+draft 消费清单已含新段、anti-copy 护栏文本在、缺 section 优雅降级、rules=advisory 非 gating；对齐现有 65 测试)。**质量 eval 现在设计 fixtures**(exemplar on/off 声音匹配、hard-rule precision/recall+误报率；守 baseline 30-40%/blind/instance-specific/judge 对齐 human)、但**质量数字 BLOCKED 在同一 16-24 真稿缺口(P3)、不报、不造假**。[owner approved]
- **B7+B8 → 降级**：OSS shipped `voice-profile.md` 的两个新 section 用**虚构 Sam** 展示 shape、不含真人数据；样本太薄抽不出可信 exemplar/rule 时 section 可选、写 header + 诚实标 "None yet"、**绝不编**（对齐 confidence 门槛 + never invent voice）。[owner approved]
- **X2+X4+X5 → 流程**：`voice-profile.md` changelog 加一行记两新段(append-only)；suite 版本 1.1.0→1.2.0 等实现+验收后；**本轮只出 SPEC → STOP、不写码、等 owner "go"**；实现从 `main` 开新分支 `feat/voice-onboard-exemplars-hardrules`（不在当前无关的 audit 分支）。[owner approved]

---

## ✅ Grill 完成（10 组 / 21 分支全 owner-approved，2026-07-03）

- SPEC（EN，canonical）→ `docs/design-voice-onboard-exemplars-hardrules-2026-07-03.md`
- SPEC（中文镜像）→ `docs/design-voice-onboard-exemplars-hardrules-2026-07-03.zh.md`
- 状态：**只出 SPEC，未写码、未提交、未开分支**。等 owner 审 + "go"。

---

## 对抗评审结果（OMC，2026-07-03）

- Workflow：4 OMC 镜头（architect + 3 critic，Opus）× grounded-in-repo，每 finding 再过 refute。25 agents、0 error、21 findings、**0 survived**。
- 复核（不橡皮图章）：0-survivor 可信 —— reviewers 带 file:line、互抓引用错、refute 具体；21 条实质 finding 逐条按具体理由击落。**无 BLOCKER/CONCERN 存活。**
- 范围限制：只验了 spec 内部自洽 + 与仓库一致，**未验运行时行为**（质量 = 延后的 P3）。
- 残留（SUGGESTION 级，refute 自己吐出来的）：
  - **R1** test 数 65→**78**（已亲跑 `pytest --collect-only` 确认）
  - **R2** degrade sentinel 对齐现有 `Unknown — not enough signal` 约定
  - **R3** §5.1 例子 "rhetorical contrast" 撞 Sam 的 Signature Move → 换 Sam-consistent 例
  - **R4** 加 "无同 genre exemplar → skip、标注、不跨 genre 替" 一行（3 个 reviewer 都绊到）
  - **R5** §6.2 加 synthetic-seedable copy-rate/overlap fixture（不需 16-24 真稿、部分解锁 anti-copy）
  - **R6/R7** writing-plans 阶段 note；**R8** 未替换样例哨兵（pre-existing、非 B+C 引入）
- 报告：`docs/review-adversarial-spec-voice-onboard-2026-07-03.md`
- 建议：fold R1-R5 后 spec 即 "go"-ready。仍未写码。
