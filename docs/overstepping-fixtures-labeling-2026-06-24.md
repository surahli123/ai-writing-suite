# 越位感 (Over-stepping) 评测 fixture · 标注工作表

> **目的：** 验证「越位感判官」能否把*过界*和*合法对比*区分开。
> 这些例子全部来自**公开 AI 文本**（HC3 真实 ChatGPT 输出 + 公开 humanizer 仓库里收录的真实 AI 例子）—— 不是我凭空编的。
> **你的任务（~10 分钟）：** 填最后两列「你的判断 / 备注」。**重点是质疑我的初判**，尤其是 hard-negative（F4–F6）。如果你也拿不准，就标 `ambiguous` → 这条直接删掉，不进评测集。

## 怎么标
- **judge 类（F1–F6）：** 这段文字是不是「越位」？ → `over` (过界) / `clean` (没问题) / `ambiguous` (说不清)
- **before/after 类（F7–F8）：** 改后那版是不是真的把越位修掉了、且没改坏？ → `fixed` / `not-fixed` / `over-fixed`(改过头)

## 为什么故意放「看着像、其实合法」的例子
文章原话：「不是X而是Y」不是天然错误 —— 只有当 X 是**真实、普遍**的旧认知，它才是有效纠偏；否则是先造靶子。
所以 F5/F6 的「不是…而是…」是**合法**的（hard-negative）。一个只会「见到 not-X-but-Y 就报警」的笨基线，会在这几条上误报 → 这正是评测要抓的能力。

---

## A. Judge fixtures（单段文字，判断是否越位）

| # | 语言 | 文本（逐字摘自来源） | 疑似子型 | 我的初判 | 我的信心 | 我的理由 | 来源 | **你的判断** | **你的备注** |
|---|---|---|---|---|---|---|---|---|---|
| F1 | EN | "At its core, the value proposition is clear: streamlining processes, enhancing collaboration, and fostering alignment. **It's not just about autocomplete; it's about** unlocking creativity at scale... The tool serves as a catalyst. The assistant functions as a partner. The system stands as a foundation for innovation." | P2 不是X而是Y + 意义膨胀 | **over** | 高 | "not just X; it's Y" 的戏剧化铺陈 + 一连串空泛拔高，典型 AI slop | blader/humanizer SKILL.md（收录的真实 AI 例子） | | |
| F2 | EN | "**Many people believe** that the color of your eyes can reveal certain things about your personality or your health, **but these beliefs are not supported by** scientific evidence." | P1 预设读者认知 + 先立靶后破 | **over** | 中 | 先替读者设定一个认知再推翻；但也可看作正常辟谣 → 信心中等 | HC3 reddit_eli5（真实 ChatGPT） | | |
| F3 | ZH | "**这不是**你的男友不爱你，**而是**他可能认为你是成年人，应该自己处理自己的健康问题。" | P2 不是X而是Y + 替读者预设担忧 | **over** | 中 | 替读者预设一个「他不爱我」的担忧当靶子再否定 | HC3-Chinese psychology（真实 ChatGPT） | | |
| F4 | EN | "**Imagine that you are** holding an apple in your hand and you want to cut it in half with a knife." | P3 预设心理画面 | **clean** | 高 | 这是具体的教学设想，不是替读者判断他想错了 → hard-negative | HC3 reddit_eli5（真实 ChatGPT） | | |
| F5 | ZH | "爱**并不是**一种感觉，**而是**一种行为。" | P2 不是X而是Y | **clean** | 中 | 「爱=感觉」是真实普遍的旧认知 → 有效认知翻转，不是造靶子 → hard-negative（判断点） | HC3-Chinese open_qa（真实 ChatGPT） | | |
| F6 | ZH | "真正的转型**不是**看投入绝对值，**而是**看投入是否匹配到能产生实际改变的最小单元。" | P2 不是X而是Y | **clean** | 中 | 「转型=砸钱」是真实常见认知，对比是 earned → hard-negative | dongbeixiaohuo/writing-agent（人工改过的 demo 正文） | | |

## B. Before/After fixtures（判断改写有没有把越位修掉）

| # | 语言 | BEFORE（真实，越位） | AFTER（去越位改写） | 我的初判 | 我的理由 | 你的判断 | 备注 |
|---|---|---|---|---|---|---|---|
| F7 | EN | "Many people believe that the color of your eyes can reveal certain things about your personality or your health, but these beliefs are not supported by scientific evidence." (= F2) | "Eye color doesn't reliably indicate personality or health — there's no scientific evidence for the link." | **fixed** | 去掉「many people believe…but」的立靶，直接陈述事实 | | |
| F8 | ZH | "这不是你的男友不爱你，而是他可能认为你是成年人，应该自己处理自己的健康问题。" (= F3) | "他可能认为你是成年人，应该自己处理健康问题。" | **fixed** | 去掉「不是你男友不爱你」的预设担忧靶子，直接说判断 | | |

---

## 标完之后会怎么用
- 你确认/修正的标签 = **gold label**（人是 ground truth）。
- 这套只做 **directional 烟雾测试**（6–8 条），**不是** kappa 校准（kappa 需 ≥40 条，那是另一个还被阻塞的「真实企业稿件质量校准」eval）。
- 判官维度**仅供参考、绝不卡 CI**（遵守「detector/judge 不当 KPI」原则）。
- 通用例子 → 正好该放进 OSS engine（engine vs fuel：真实企业稿件是后加的 fuel）。

## 来源 / 可复现
- HC3：`Hello-SimpleAI/HC3`(EN) + `HC3-Chinese`(ZH)，经 HF datasets-server API 拉取 400 条真实 ChatGPT 回答，脚本 `scratchpad/scan_overstepping.py` 扫描越位句。
- 仓库例子：`scratchpad/competitors/{blader-humanizer, dongbeixiaohuo-writing-agent}`（推文里的公开 humanizer 仓库）。
- 仅工作表，未改任何 skill 代码；仓库在 `main`，未提交。
