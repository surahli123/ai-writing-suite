# v2 提案：让 ai-writing-suite 真正干活 — 2026-06-09（待批准，PLAN ONLY）

输入：`notes/diagnosis-kb-loading-rovodev-2026-06-09.md`（两个症状的根因）+
`notes/research-good-ai-writing-outcome-2026-06-09.md`（14 条研究发现）。

## 问题 → 根因 → 解法映射

| 用户症状 | 根因（诊断） | 解法（研究背书） |
|---|---|---|
| 子技能加载不到 knowledge | F1: v1 无任何可用技能读 `_shared/knowledge/`；F2: `../../` 相对路径在 RovoDev 断链 | P0 路径自愈 + P1/P2 把 KB 真正接进 draft/qa |
| 初稿不像人写的 | F3: comms-draft 是占位符，裸模型起草 | P1 draft-time 注入（findings 9-11：起草时就约束，优于事后 polish） |

## 分期（每期独立可验收，逐期审批）

### P0 — 路径自愈（小，~1 个 PR）
所有子技能从 `../../_shared/` 锚定改为"**套件根定位协议**"：先找到包含 `_shared/` 的
目录（从 SKILL.md 加载位置向上找），再用根相对路径。改动面：comms-polish、voice-onboard
的 SKILL.md 路径引用段 + router 一致化。
**验收**：四宿主路径语义一致；现有 58 tests 不回归；（理想）公司电脑复测 patterns 可加载。

### P1 — comms-draft 真实实现（核心，~2-3 个 PR）
playbook 引导起草，设计原则直接来自研究：
- 起草前读 KB（`_shared/knowledge/` INDEX → 相关条目）+ voice profile + 场景 preset；
- **draft-time 约束**：具体细节/真实经验注入（finding 10）、句长/句法变化（finding 9）、
  patterns 目录作为"起草时负面清单"而非事后清理；
- 自带"**vary/roughen**"步骤而非只 smooth（finding 11）；起草后自扫 patterns（复用
  comms-polish 的 re-scan 模式）。
**验收**：新增 eval fixtures（用 `evals/fixtures/calibration.py` 选可校准 n + miss 目标）；
盲评 before/after 演示（来源标签遮蔽，finding 3）；58+ tests 全绿。

### P2 — comms-qa mini-RAG（~1-2 个 PR）
zero-dep markdown 检索（INDEX.md 导航），回答 KB 问题 — 症状 1 的问答面。
**验收**：KB smoke 从 3 case 扩到含真实问答路径；引用必须落到具体 KB 文件。

### P3 — 评测升级（与 Phase 2b 合并）
- **盲评协议**写进 rubric（finding 3）；
- **逐任务动态验收标准**（style/format/length/content-integration/depth 五维 per-query，
  finding 5）替代单一固定 rubric；
- judge 对人类标注标定（finding 7 — Phase 2b 既有设计，保持）；
- detector 分数明确降级为回归信号，不当质量 KPI（finding 12/14）。
**仍 blocked**：owner 在企业电脑收集 ~16-24 份真实 AI 风草稿（n=24 → 8 misses）。

### comms-polish 增量（搭车 P1）
把 finding 11 写进 Rewrite Workflow：step 7 的 "vary rhythm" 强化为显式
"不要过度抛光；保留自然不完美" 原则 + 句长方差检查。

## 我不会做的（fence）
- 不动 `main`（feature branch → PR，每个 PR 先给你看 staged files）；
- 不把 judge/LLM 调用接进 CI（CI 保持 stdlib-only + key-free）;
- 不重新引入 generate-and-sync 打包；不动 `_shared/patterns/` 目录结构（engine 不拆）；
- P3 真实草稿收集仍由你在企业电脑完成，我不伪造评测数据；
- AI slop/死代码审计挂起，待 v2 改动落地后再排（避免冲突）。

## 待你决定
1. 批准分期顺序 P0→P1→P2→P3？还是先只做 P0+P1？（我建议 P0+P1 先行——直接命中两个症状）
2. P1 的 comms-draft 是否需要公司 playbook 结构信息才能设计好模板？（OSS 版先用通用
   5 篇种子 KB 设计，公司 fork 自然继承——我建议这样，不阻塞）
3. 公司电脑三个确认点（哪个子技能/什么 prompt、报错还是静默、playbook 是否已放入）——
   有了能把 P0 修复打磨得更准，没有也能开工。
