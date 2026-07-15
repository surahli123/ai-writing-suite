# 诊断：公司电脑(RovoDev)上的两个问题 — 2026-06-09

症状（用户报告，公司笔记本 in-house RovoDev，手动安装）：
1. 子技能无法正确加载 knowledge
2. 初稿（initial draft）依然不像人写的

## 结论先行

两个症状都指向同一个根因：**v1 的"燃料管线"根本没接上** —— `_shared/knowledge/`
(KB/fuel) 在 v1 里没有任何可用子技能去读它；而"起草"能力（comms-draft）整个是
v2 占位符。再叠加一个 RovoDev 特有的相对路径脆弱性。这不是回归 bug，是 v1 范围
缺口 + 一个移植性缺陷。

## 发现（按证据）

### F1 — v1 没有任何工作子技能读 `_shared/knowledge/`（设计现状，非 bug）

`grep -rn "knowledge"` 全树验证：引用 `_shared/knowledge/` 的只有两个 v2 占位符：

- `skills/comms-qa/SKILL.md:8-9` — "will answer questions from the knowledge base
  under `_shared/knowledge/` … **Coming in v2**"
- `skills/comms-draft/SKILL.md:8-13` — "will draft a new page guided by the
  knowledge base … **Coming in v2**"

两个可用技能（comms-polish、voice-onboard）只读 `_shared/patterns/`（engine）、
`voice-profile.md`、`learned-rules.md` —— **没有一行指向 knowledge/**。
含义：如果公司侧把真实 Comms Playbook 放进了 `_shared/knowledge/`，期待 polish
或 draft 用它 —— 现状是**什么都不会发生**。"engine vs fuel" 架构存在，但油管没接。

### F2 — `../../_shared/` 相对路径在 RovoDev 上大概率断裂（移植性缺陷）

- `skills/comms-polish/SKILL.md:14` — "reads the consolidated catalog under
  `../../_shared/patterns/`"；`:72-73`（voice-profile）、`:221`（learned-rules）同模式。
- `skills/voice-onboard/SKILL.md:32-33,110,140,143` — 同样的 `../../_shared/` 引用。

这些路径只有在 agent **相对 SKILL.md 文件位置**解析时才正确。Claude Code 会注入
"Base directory for this skill: …"，所以没问题；RovoDev 手动拷贝安装
（`~/.rovodev/skills/ai-writing-suite`，见 `docs/packaging.md` RovoDev 节），会话
cwd = 用户项目目录 —— agent 按 cwd 解析 `../../_shared/` 就指到不存在的地方 →
静默找不到 → 即兴发挥。这能直接解释"加载不到 knowledge"的体感（即使用户说的
knowledge 实际是 patterns）。

**修复方向**：子技能不再用 `../../` 锚定，改为"**先定位套件根目录**（包含
`_shared/` 的那一层，从本 SKILL.md 被加载的位置向上找），再用根相对路径
`_shared/patterns/…`"。router 已有类似的自给自足补丁（PR #6），子技能没有。

### F3 — "初稿不像人写的"：因为 comms-draft 不存在

`skills/comms-draft/SKILL.md` 整个是占位符（13 行，无任何起草逻辑）。router
(`SKILL.md:47`) 指示"v2; until then, say it's not built yet"。用户在 RovoDev 上
要初稿时，agent 要么拒绝、要么（更可能）**无视占位符直接用裸模型起草** ——
没有 playbook 结构、没有 patterns 目录的反 AI 腔约束 → 产出一股 AI 味是预期内的。
v1 唯一的质量能力是事后 polish，不是起草。

## 待用户确认（下次在公司电脑测试时顺手记录）

1. 当时显式调用的是哪个子技能？原始 prompt 是什么？
2. "加载不到 knowledge" 的具体表现：报错？还是静默没读、输出里看不到 KB 痕迹？
3. 公司侧是否已把真实 playbook 放进 `_shared/knowledge/`？还是用的 OSS 5 篇种子 KB？
4. RovoDev 安装路径是哪一个（`~/.rovodev/skills/`？）、`_shared/` 是否完整拷入？

## 对"让套件真正干活"的含义（待研究报告回来后定方案）

把 v2 拉到现在做，优先级建议：
1. **comms-draft 真实实现**（playbook 引导起草 + 起草时即用 patterns 约束，
   而非裸模型起草后再 polish）—— 直接命中症状 2。
2. **KB 接线 + 路径自愈**（suite-root 定位协议，所有子技能统一）—— 命中症状 1。
3. comms-qa mini-RAG（症状 1 的"问答"面）。
4. 质量标准/评测升级 —— 等 deep-research 报告（wf_cc8f728c-2bf）回来，
   用它定"什么算好初稿"，再设 comms-draft 的验收 eval（30-40% 校准带规则照旧，
   `evals/fixtures/calibration.py` 选 n）。

状态：deep-research-tiered workflow 后台运行中（Task wms7ooq6g）。
本文件未提交（repo hook 阻止 plan/handover 类文件入库；notes/ 同性质，保持 untracked）。
