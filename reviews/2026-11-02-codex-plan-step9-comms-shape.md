# Codex adversarial review: step 9 + comms-shape plan (2026-11-02)

VERIFIED_AGAINST: fresh clone of claude/laughing-rubin-mkkadx-s9-lists-review @ c6f6367 (implementation base 0424a7f); proposal read from origin ref 12b3267
MODEL: Codex 6.1 Astra, reasoning=medium, run by the owner locally (read-only). Report pasted by the owner and reproduced verbatim; `P` = the plan, `S/` = `skills/ai-writing-suite/`.
Disposition of each finding: docs/plan-step9-and-comms-shape-2026-11-02.md, "Review log".

---

核验对象为目标分支的干净 clone，HEAD `c6f6367`，实现基线 `0424a7f`。研究提案读自已有远端引用 `12b3267`；fetch 因 `.git` 写保护未成功。两篇外部文章均已读取。现有 460 个单元测试及全部 8 个检查阶段通过；未改仓库文件，最终 diff 为空。以下 `P` 指计划，`S/` 指 `skills/ai-writing-suite/`。

## 发现，按严重性排序

1. **blocker · VERIFIED · Step 9 behavioral eval：宣称沿用 v1，实际改变发布规则。**
   P:189 要求明确 NOT WORSE，否则退回；PREREG.md:90 明确允许 Inconclusive，并把 pairwise WORSE 纳入发布判定。计划虽做 pairwise，却没让结果参与 verdict，也未明确 floor 的分母。
   **修复：**逐项写出新协议相对 v1 的变更、非劣界值、分析人群、pairwise 判定及 inconclusive 处理；不能把改变后的门槛称为原协议。
2. **major · VERIFIED · D/E：保留了比“虚假赞美”更严重的示例造假。**
   audit-report-format.md:41、49、53 的 Fix 分别新增“三个工具变一个屏幕”“每天检查三个指标”“不到一秒”，原稿没有这些事实；`conforming.md:9,17,21` 同样如此。P:132 又豁免 Fix 的来源检查。
   **修复：**同时重写示例的 Fix，使用来源已有信息或明确缺证建议；新增修复保真对照，不能只修 strengths 段。
3. **major · VERIFIED · D：包含关系抓不到目标缺陷，也不等于“同一句”。**
   Probe：`The dashboard is fast` 与 `fast, clean, and intuitive` 经小写规范化后，双向包含均为 False。P:106 的句子级禁止与 P:116 的片段包含检查并不一致。反过来，两处不同位置的相同短语会被误当成重叠。
   **修复：**引用绑定原稿位置；重复表述检查只作为提示。判断“赞美是否恰好肯定了被批评的属性”交给语义审阅，别用字符串包含硬拒。同一句中的事实清楚、修饰空泛可以同时成立。
4. **major · VERIFIED · E：计数和引用解析尚未构成可实现的契约。**
   check_report.py:50、157–160 逐行取字段；probe 中多行引文只取得第一行。现有逻辑仅检查是否有成对引号，不能解析嵌套引号或实例数量。重复同一片段 N 次也能满足“数量”，却未证明 N 个 occurrence。R1、T9 等模式的实例单位也不是天然的一句引文。
   **修复：**先规定 occurrence 单位、位置、外层引号/转义、多行字段和 `×N` 起始语法；每个 occurrence 必须指向不同来源位置。区分总命中、排除数、有效数和展示数。省略号不能简单拆成“各段都在原稿某处”：需同一有序跨度，或直接要求完整摘录。保留大小写，单独规范化排版引号及空白。
5. **major · JUDGMENT · A/B：三个 sibling 不是足够的改写触发条件。**
   P:28–35 会覆盖论证文里的普通三条 bullets；“mixed lists 不动”又没有定义 mixed 指内容还是句式。P:62 的统一 frame 与“不同词必须最前”可能互相冲突。独立发送的 subject lines 也不能把共享前缀移到一个收件人看不到的 heading。
   **修复：**以“独立可比较的记录、共享语义字段、共同呈现容器”为条件；豁免论证序列、独立分发文本和有意义的结构差异。统一结构应是有具体可读性收益时的选择，不是所有列表的义务。fsdatalab 原文的实例主要是 dashboard/feed，不能据此推出普通 bullets 的统一规则。
6. **major · VERIFIED · A/T7：用 action/object/name 的存在代替可核查性，放宽过头。**
   P:45 的新定义会让 `Optimize customer outcomes`、`Unlock enterprise value` 因有动词和宾语获得豁免；现有 T7 示例 `Optimized RandomX performance` 本身就含名称，structural-tells.md:118。
   **修复：**仅豁免“对明确对象报告具体动作或状态”的结构；有名词不代表有信息。保留空泛收益/性能夸赞的正例，与真实状态清单配对测试。
7. **major · VERIFIED · B/C：新规则与既有权限、报告格式冲突。**
   P:80 将 light-edit 限为标点、拼写及同义词统一，而 `comms-polish/SKILL.md:107–118` 还允许语法、歧义及用户来源中的事实纠正。C 的缺槽发现又未必对应任何 AI-tell ID，也不能合法给出填槽 Fix；现有报告契约却要求两者（`audit-report-contract.md:36–42`）。
   **修复：**把 B 的限制限定为“列表结构变换”，保留现有事实权限；为一致性/缺证另设明确的 report-only 输出位置，不强塞 catalog finding。缺少 interval 也应先判断指标是否可比、该槽是否适用。
8. **major · VERIFIED · A/F 与测试：确定性检查仍执行相反规则。**
   Probe：六条真实动词开头状态项仍得到 `bullet-np-list: high`；单独一个 `Moreover` 得到 `transition: medium`。对应 `detector.py:176,307–327`；bold 数量规则在 270–274。`detector_blind` 不修复这些行为。
   **修复：**若 detector 延后，明确其与新 catalog 的分歧，不能用其绿灯证明 A/F 成功；加真实模型的正负对照，至少覆盖正常列表、空泛宣传列表、孤立连接词和连接词簇。新 status checker 要按实体对齐；probe 中交换 login/checkout 的 Investigating/Fixed，现有全文检查返回空列表。
9. **major · VERIFIED · Step 9 eval：主要指标测不到主要收益。**
   P:186 沿用隐藏 Notes 的 v1 judge；因此 C 的漏报、乱报仍不进入评分。`run2/report.md` 已明确这一盲区，并报告 main 的 W=1、S=0。原 24 项还在 PREREG:127–131 明确标为受污染。K=3 不会把 24 个内容样本变成 72 个独立样本；全零差值的 bootstrap CI 也不能证明总体零风险。
   **修复：**旧 24 项仅作回归；新项分别报告列表可读性、状态保真、Notes 精确率/召回率及 review 正确性。配对变体按源文档聚类抽样；加入“需要编辑”的难例，避免身份输出拿满分。恢复约 10 项 owner 盲标，不能只靠同家族 judge 和哨兵。
10. **major · VERIFIED · Step 10：路由接收 mixed 请求，流程却没有对应交付契约。**
    P:250 把“polish＋add”交给 shape；Entry A 从 notes 开始，Entry B 又规定不改写、fix 转 polish。没有明确保留旧技能的“已有内容保真＋返回完整修订文档＋完成 polish”（comms-draft/SKILL.md:77）。只做 review 不能完成用户已经要求的 polish。
    **修复：**增加明确的 mixed-mode 分支，区分既有内容、授权新增、未支持材料和最终整篇交付；不能把它作为旧 one-shot 案例一起退休。
11. **major · VERIFIED · Step 10 stages：停止规则和来源范围不一致。**
    P:13、213、218 要求 thesis/outline 两次停止；211 又合并短请求；224 要作者主动结束 sharpen，实际上形成第三个停止点。P:231 只与最初 notes 比较，会把作者在后续问答补充的事实误报为无来源，也无法识别“模型提出、作者只是认可”的贡献归属。
    **修复：**写成明确状态转换：短请求如何合并确认、何时默认进入 fill、什么修改需要再次确认。来源账本覆盖原稿、notes、后续回答及获准来源，区分“作者提供”与“作者认可”；称为 claim provenance，别把它等同贡献评估。
12. **major · JUDGMENT · Step 10 eval：目前只能支持 pilot，不能支持非劣结论。**
    8 个 packet 没有 K、CI、非劣界值、最大轮数、未完成会话处理或 bare 的交互权限。旧 skill 最多两轮，shape 却无限 sharpen；成本比较不公平。“一律拒绝第一 framing”测的是服从脚本，不是抗迎合。核心收益 intent/cost 又完全不影响 verdict。
    **修复：**三个 arm 共用信息揭示规则、停止条件和预算；用脚本化作者回答替代自由发挥的 agreeable agent。加入“作者错误地坚持无证据结论”和“作者正确纠正模型”两类。记录最终未完成率、全部输入输出 token、作者轮数；8 项仅报 pilot，不声称总体 non-inferiority。
13. **major · VERIFIED · Archive/migration：遗漏运行依赖和持久化兼容。**
    若 capability ID 改名，漏改 `evals/capabilities/known_human_negatives.py:12` 会留下不存在的依赖；`core/test_discovery.py:22,29–35` 也固定 `comms_draft`。用户规则实际存于 `<state>/learned-rules.md`，按 scope 匹配（`_shared/state-location.md:8–16`、`learned-rules.md:65–66`）；改模板不能迁移已有 `scope: comms-draft`。
    **修复：**选择保留内部 capability ID 或同步依赖；为旧 scope 提供读取兼容，并明确它只适用于哪些新阶段。补旧名称调用的升级说明及目标宿主加载检查。历史 review/notes 保留原名，不能全库机械替换。
14. **minor · VERIFIED · 测试计划遗漏具体断言，已有引号测试还是空操作。**
    `CombinedConfusionMatrix.test_mixed_realistic_judge_matches_hand_computed_numbers` 在 test_fixtures.py:1153 固定 `(2,16,24,3)`；新增后应为 `(2,18,25,3)`，不是只改 27/18。`test_draft_criteria_coupling.py:18–20` 固定旧阶段标题；`run_draft_cases.py:54` 固定最多三问，与新五问不符。`test_smart_quotes_accepted`、`test_guillemet_quotes_accepted`（152–164）的 replace 目标在当前 fixture 出现 0 次。
    **修复：**列出这些断言的迁移；让引号测试先断言输入确实改变。不要靠删除旧测试来解决阶段语义差异。
15. **minor · VERIFIED · A/G/C 与 attribution：仍有漏项和错误文件描述。**
    G 保留的 Rhythm 维度仍要求句长变化（`final-pass-checklist.md:99`）；tone 仅加“running prose”仍保留强制变奏；R4 仍要求刻意选第二、第三个词。P:99 所谓“SKILL step 5 已要求 consistency notes”不实，指令实际在 checklist:24–34。Step 9 借用来源却只在 Step 10 新 NOTICE 安排 credit；现有 suite NOTICE:3 仍概括吸收来源均为 MIT。
    **修复：**删除剩余机械变奏指令，纠正锚点；Step 9 独立交付来源说明，区分 MIT 吸收材料与非授权文章的思想参考。Tenex 页面标示保留权利；不要复制其问句、prompt 或配套文字。Ng 仅有二手摘要，应明确标注，不能作为已核验的课程结论。

## 7 个 reviewer questions

1. **T7 能否兼顾？** 当前定义不能；改成具体事件/动作，而非“出现 object/name”。
2. **三项触发是否可用？** 不足。看语义与呈现容器，不看条目数。
3. **D/E 是否成立？** D 的硬拒算法不成立；E 需先定义引用语法、位置和计数单位。
4. **扩大 Notes 是否安全？** 可以，但限定为带位置的一致性/缺证发现，并单独评分；不是开放杂项评论区。
5. **一个 skill 两入口是否合理？** 可以。路由必须明确：语言表达反馈归 polish，论点/证据压力测试归 shape；同时改两个 child description，因为宿主可能绕过 router。
6. **最便宜可信的 eval？** Step 9 保留 K=3，用少量新鲜难例＋owner 约 10 项盲标，旧 24 项只做回归。Step 10 先做 8 个脚本作者 packet、每 arm 固定两次的 pilot，再做 2–3 篇真实文档；不从小 pilot 宣称非劣。
7. **遗漏什么？** mixed-mode 完整交付、旧 scope 兼容、capability 依赖、上述固定断言、Notes 的可评估输出及 Step 9 attribution。

## 应直接删除

- 用字符串包含硬判“虚假赞美”，以及禁止赞美有任何缺点的整句。
- 无条件的“一种 frame／不同词最前／共同前缀上移”。
- R4 的刻意换冷门词、制造意外比喻，以及剩余强制变奏指令。
- 无限定的 `Never refuse`。保留用户明确要求时跳过流程，但不得跳过来源与保真约束。
- 把 notes 差分称作作者贡献评估；把全绿静态检查或小样本 NOT WORSE 当作新技能有效性的证明。
