# 讨论:用 Ogilvy X 帖子改进 ai-writing-suite 去 AI 味引擎

- 日期:2026-07-03
- 触发:Nicolas Cole 的 X 帖子(把 Ogilvy 1982 备忘录 10 条规则做成 Claude Skill)——https://x.com/Nicolascole77/status/2072662998326415447
- 研究方式:STORM 风格只读 workflow(`wf_33f4a226-a9f`),5 视角并行检索 repo + X 帖子 → opus 综合;6 agents,0 error,348K tokens
- 分支现状:`feat/overstepping-eval-dimension`,工作树脏(一批 overstepping 改动未提交)。**本讨论不改任何代码。**

---

## 0. TL;DR

1. **Cole 的 skill 不挑战我们,反而背书我们**:他的 auditor 是「按永恒的人类写作质量审计、不追分数」,和我们「detector = 回归信号、绝不做 KPI」是同一立场。2026 landscape(高校放弃 AI 检测、~70% humanizer 打不过现代检测器)也从外部印证:**追分数的军备竞赛是正在丧失公信力的游戏,别玩。**
2. **真正能借的不是「不改写」这个产品形态,是那把「正向质量」尺子**——以及 Cole 那套「引用原句 + 为什么 + 具体改法 + 分级 + 哪里写得好」的审计报告格式。
3. **最大的一处真空是 Ogilvy 规则 9(把"要读者做什么"讲清)**:我们 8 个 pattern 文件里零覆盖,而它正好命中 comms-draft 的本职(产出能驱动行动的商务写作)。
4. **战略分叉(要你拍板)**:这些改进大多把技能从「去 AI 味」扩向「好写作教练」。要不要让 ai-writing-suite 走进 Cole 的地盘?——见 §5。

---

## 1. 框架纠正(采纳你的反驳)

我上一轮把区别定位成「**auditor vs rewriter**(产品形态)」,你反驳得对:comms-polish 本来就有 `detect / review / rewrite / edit` 四个 mode,**我们既审计也改写**,"不改写"根本不是有意义的差异,借鉴时也没人要照搬它。

真正的区别是**审计标准(rubric),不是产品形态**:

| | 尺子量什么 | 空间 |
|---|---|---|
| **Cole/Ogilvy** | 人类好写作有什么(像说话、把话说短、ask 讲清) | **positive-space** |
| **我们现引擎** | AI slop 多了什么(lexical/rhythm/hedging tells) | **negative-space** |

两边都做 polish/edit,产品形态一样。可借的是那把**正向质量的尺子**,而且它能同时喂给我们已有的 review mode(审)和 rewrite mode(朝 Ogilvy 方向改)。你的反驳不是削弱、是**强化**了 positive/negative 这个轴——它才是改进杠杆。

> ⚠️ 一个残留张力(研究也独立指出,tension #4):Cole 的 auditor 身份就是「只审不改」;我们**明确允许改写**(公司 DS 工具,合规)。所以我们借的是他的**审计报告输出契约**(只进 detect/review mode),而 rewrite mode 的"过度打磨压力"要和审计的"哪里写得好"清单**防火墙隔离**——同一个技能既审又改,两条 lane 不能串味。

---

## 2. 研究核心结论:验证,不是转向

- **P5 finding 1-2**:Cole 是**非竞品的独立印证**——「审计、别追一个数字」是可信的那一派。2026 外部证据(高校因误判/法律/公平代价放弃 AI 检测;检测是概率性而非定论;~70% humanizer 打不过现代检测器)从市场层面印证我们 brainstorm 文档 L143 的判断:「**不发布面向用户的 0-100 AI 味质量分作为 gate 或优化目标——这个"拒绝"本身就是差异点**」。
- **含义**:这轮**不该**再加特征词剥离器。收获集中在两处——(a) **packaging**:把我们已有的"审"能力做成 Cole 那样有结构的用户可见交付物;(b) **positive-space 覆盖**:补上我们从没量过的"人类好写作有、AI slop 缺"的 absence tells。

---

## 3. 六个改进提案(按价值排序,附我的质疑)

> 全部来自研究综合,我加了自己的批判视角。effort:S/M/L。

### #1 给 comms-polish 的 detect/review 加强制「审计报告」输出模板 —— effort M,风险低 ✅ 强推
- **依据**:5 个 reader 里 **2 个独立收敛到这**(P1 全部 + P5 finding 3)。现在 `SKILL.md:245` 只写「lead with findings and examples, grouped by severity」——含糊到 agent 可以用**转述**代替**原句**、severity 没有命名分级、没有一句话总评、没有"哪里写得好"。
- **改法**:一个固定契约 =(1)一句话点名**最大问题**;(2)findings 按**命名分级**(Critical=改变含义/可信度;Moderate=可读性/AI 味;Minor=风格小疵),每条 = 原句引用 → tell 名 → 为什么 → 具体改法;(3)结尾"哪里写得好"清单(2-3 处,给理由不是夸)。一处改动关掉 P1 五个 gap 里的四个。
- **我的质疑**:唯一风险是"哪里写得好"退化成拍马屁——用"限 2-3 处 + 必须给理由"压住。**这个几乎无争议,建议先做。**

### #2 加 judge-only 的「clear-ask / CTA 缺失」维度(Ogilvy 规则 9)—— effort M,风险中 ⚠️ 战略性
- **依据**:**全套唯一真空**——3 个 reader 确认 8 个 pattern 文件零覆盖(P2-3 / P4-2 / P5-4)。AI 起草的商务文常以 H3 式空洞升华("前景一片光明")收尾,而非"具体动作 + 负责人 + 截止"。有明确 ask = 人类目的性写作的正向证据。直接命中 comms-draft 本职。
- **我的质疑**:**这是最需要你拍板的一条**——它把技能从"去 AI 味"扩到"是不是好写作"(见 §5)。而且"有没有清晰 ask"是**意图相关**的:FYI 类文本本就无 CTA。必须 advisory、绝不 gate CI、允许"本就不需要 ask"判定,且**永不并入 AI-tell 分数**,否则 blind-eval 的构念被污染。

### #3 给在飞的 overstepping rubric 加第三条腿「payoff_clear」—— effort S,风险低 ✅ 顺手做
- **依据**:P4 finding 4。当前 overstepping rubric 只查 `overstepping_removed + meaning_preserved`,没查"删掉预设层后,活下来的那句 Y 是否仍是完整、无歧义的陈述"(可能变成掉了脚手架的残句)。加一条 rule-9 味的 PASS/FAIL。
- **我的质疑**:**最小、最有据**(折进已用 minimal-pair fixtures 压过的工作)。唯一风险是 judge 对"简洁但没问题"的句子误报 unclear——用现有 fixtures 校准。既然你这条分支本来就在做 overstepping,这条**顺手就做了**。

### #4 voice-onboard 接受「口语转录稿」样本类型 + 把规则 2/7 写成有界非目标 —— effort S,风险低
- **依据**:P3 finding 2。voice-onboard 现在只吃书面文本,连 v2 路线图都没列音频/转录。规则 2 的本质是**在被编辑成书面语之前**捕捉一个人的口语register(缩写、自我打断、重复强调)。最便宜的落地:让用户**粘贴自己说话的转录稿**当一种样本类型——v1 不需要转录引擎,用户自带文本。
- **我的质疑**:风险是把转录稿的口头 disfluency 当"voice"逐字复制——要注明"转录稿只教 register/节奏,不教逐字措辞"。同时把"agent 不能录音、不能隔夜"(规则 2/7)写成**明说的非目标**,免得日后被当"缺口"重新发现。

### #5 加 judge-only 的「首次出现的 jargon / 可读性」advisory(Ogilvy 规则 4)—— effort M,风险中
- **依据**:P2 finding 2。规则 4(写给八年级生)现在只被 AI 词表间接覆盖;一篇文可以过所有 AI 词检查却仍然可读性差。加轻量 advisory:标记首次出现未解释的领域黑话/缩写 + 粗略每句词数信号。
- **我的质疑**:**可读性"数字"恰恰是最容易被当靶子追、滑进检测器规避的东西**。只做定性的"这些词首次出现需加一句解释",**绝不发布 Flesch-Kincaid 分数当旋钮或 gate**。且 register 相关——DS 内部备忘录有合法黑话。

### #6 在 comms-draft 里原型「talk-first 种子步」—— effort L,风险高 🚩 只做 eval,不默认上线
- **依据**:P3 top_improvement。在 step2 和 step3 之间插一个口语register pass,用那段"转录稿式"文本当 step3 收紧的**字面种子**,把今天的"先写干净、再机械去均匀"(`SKILL.md:105-114`)翻转成 Ogilvy 的"先说乱、再轻改"。理论上是对 lived-emotion gap 最强的答案。
- **我的质疑(最强的一条)**:**一个被指示"像说话一样写"的 LLM 仍然在模拟 disfluency**——它可能只是换了件马甲的合成方差,产出研究 gap 警告的同款空洞 burstiness,除非那段口语真的来自用户。还会重排核心 drafting 流程 + 增加用户摩擦。**别凭理论上线**——做成 A/B、blind rater 比"talk-first 种子 vs 现流程",只在人类偏好胜出**且无 >30pt provenance 摆动**时保留。

---

## 4. 六个张力(讨论的骨头,别绕过)

1. **总评 vs 无 KPI 数字**:可以采纳 Cole 的"一句话点名最大问题 + 命名分级",但**绝不能硬化成一个 headline 数字**——severity 一旦变单一分数就变成被追的 KPI。守线:定性分级 + 点名问题,永不给复合评分。
2. **规则 2 的真冲突**:"录自己 / 转录"预设了一个有真嗓音和时间的人类作者;agent 只能处理手上的文本,既不能录用户也不能隔夜。talk-first 有**制造**研究 gap 所警告的合成 burstiness 的风险——只有用户提供的**真口语输入**能逃过,模型模拟的口语register 未必。**未解冲突:talk-first 是源头修复,还是表演?**
3. **positive-space 规则是检测器特征的近亲**:缩写率、可读性年级、完整否定聚集——正是 humanizer 会去调来打检测器的表层信号。把它们做成**指标**就有重建"检测器规避靶子"、违反"detector ≠ KPI"的风险。任何口语/可读性信号必须停留在 advisory + blind-eval 测试,绝不做旋钮或分数输入。
4. **审 vs 改的 mode 纪律**:见 §1 的防火墙——借 Cole 的输出契约只进 detect/review,rewrite mode 的过度打磨压力和审计的"哪里写得好"清单不能串。
5. **规则 9-10 是沟通有效性轴,不是 AI-tell**:加它把技能从"去 AI"扩向"是不是好写作",有 scope creep,且会**糊掉 blind-eval 构念**(provenance 摆动测的是 AI-vs-人类,不是好-vs-坏)。CTA 必须独立 advisory 维度,永不并入 AI-tell 分数。
6. **overstepping O4 与规则 10 的窄重叠**:O4(自问自答审判 theater)结构上就是规则 10 警告的"在文字里演一场本该面对面的对话";O1-O3 不是。**在 rubric 文档里交叉引用即可,别按规则 10 重构 overstepping 维度**——它有自己的经验基础。

---

## 5. 战略分叉 —— 真正要你(产品负责人)拍板的一件事

研究的 6 个 tension 反复绕着同一个没被回答的问题转:

> **ai-writing-suite 的边界是"去 AI 味"(de-AI),还是"好写作教练"(writing coach)?**

- **#1 / #3 / #4** 严格在"去 AI / 真实嗓音"车道内——低争议,不扩边界。
- **#2(CTA)/ #5(可读性)/ #6(talk-first)** 一旦做,就把技能推进 **Cole 的地盘**(按 Ogilvy 好写作规则审计)。这不是坏事——但它改变产品定义,也可能糊掉我们赖以立身的 blind-eval 构念(那套 eval 只会测 AI-vs-人类,不会测好-vs-坏;混进"好写作"维度后,30-40% 校准band 的意义要重想)。

**我的推荐(POV)**:
- **现在做**:#1(强推)+ #3(顺手,反正 overstepping 分支在飞)。两者都低风险、纯在去 AI 车道内、且 #1 是 2 个 reader 收敛点。
- **想清楚再做**:#2 单独作为"沟通有效性" advisory 维度,**明确标注它不是 de-AI**——如果你要技能长成"教练",这是最值得的第一步;如果你想让技能保持锋利的"去 AI"单一定位,就别做,留给一个独立技能。
- **只做 eval、别上线**:#6。
- **可选补强**:#4 / #5,不急。

---

## 6. 决策问题(下一步)

1. **边界**:ai-writing-suite 保持纯"去 AI 味",还是接受扩成"好写作教练"?(决定 #2/#5/#6 做不做)
2. **落地范围**:先只做 #1 + #3(低风险车道内),还是连 #2 一起?
3. **落地前提**:任何落地都要先决定 `feat/overstepping-eval-dimension` 这批未提交改动怎么处理(先 commit 收口,还是并进来)。

> 如果这几个分叉你想被"拷问"着一条条走清楚,我可以开 `/grill-me`(逐个 branch、每个我给推荐答案)。否则你直接选,我按选择出实施计划(仍是 plan-only,不写代码直到你说 go)。

---

## 7. X 帖子的二次蒸馏(前 6 提案之外还能学什么)

前 6 提案主要吃了 Ogilvy 规则 2/4/9 + Cole 的审计 UX。二刷帖子后,还有这些**没进提案**的可蒸馏点(按"新 + 有价值"排):

| 代号 | 蒸馏 | 帖子来源 | 落点 | effort | 取舍 |
|---|---|---|---|---|---|
| **A** | **压缩 / 想法密度 advisory**——"这稿能砍到 1/3 吗";内容配不上篇幅就是稀释 | 规则 5("never > 2 pages;装不下 = 你没想简单") | **de-AI ∩ 好写作** | M | **升为提案 #7(强推)** |
| **B** | **教练 register**——审计目标是"教会人内化"(而非替他改);可跨稿追踪某用户反复犯的 tell,教那个 pattern | Cole 核心自述:"the skill doesn't rewrite… I use it to keep internalizing these rules so I still do the rewriting" | 好写作(最大 remit 扩张) | L | 单独一轮想清楚,别顺手做 |
| **C** | **规则挂权威来源**——给 pattern/KB 条目标 Ogilvy / Roman-Raphaelson / Zinsser 等出处,让审计的 "why" 带权威而非 "AI-tell #37" | 规则 1(读 Roman-Raphaelson 3x);Cole 把 skill 锚在具名经典 | 质量/可信度升级 | S | 低成本,随手可加 |
| **D** | **"读出声"自然度检查**——judge 维度:默读一遍会不会绊口;区别于可读性分数 | 规则 3(read aloud)& 规则 7(read aloud next morning) | de-AI(节奏/burstiness) | S | 低成本,可并入 rhythm 维度 |

**只印证、无需新做的两条**:
- 规则 8(找同事改)= 我们 roadmap 里的 **3× 跨家族多判 judge**(第二视角)——印证该做。
- Cole "in the age of AI you cannot automate what you cannot articulate" = 印证我们**显式、引用来源的 pattern 目录**胜过黑箱 ML 检测的路线选择。

### 关键洞察:压缩(A)为什么是本轮最好的"两者兼得"候选
AI slop 最典型的失败模式是**稀释**——用两页说清一段话、把一个想法摊成三段。规则 5 的"装不下 2 页就说明你没想简单"直接命中它。所以"想法密度 / 能否砍到 1/3"这个 advisory **同时是 de-AI 信号(反 padding)和好写作信号(Ogilvy 简洁律)**,正落在"激进 + 两者都要"的甜区,且与现有 `genre_fit`(按渠道长度)正交——后者查渠道长度规范,前者查内容是否配得上篇幅。

### 建议增补到 build spine
- **#7 压缩/密度 advisory**:按 Q2 契约克隆 overstepping 模板(judge-only + 自带 minimal-pair fixtures@30-40% + N/A 判定 + 不进总分)。排在 #2/#5 同一批(positive-space 克隆批)。
- **C / D**:低 effort 顺手项,可搭 #1 或 rhythm 维度一起。
- **B(教练 register)**:标记为 v2 战略候选,单独 brainstorm,不进本轮。
