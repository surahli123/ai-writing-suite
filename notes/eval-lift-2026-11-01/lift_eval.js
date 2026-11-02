export const meta = {
  name: 'skill-lift-eval-v0',
  description: 'A/B the writing suite: bare vs one-liner vs suite@main vs suite@main+PR67 vs two external unslop skills, blind-judged',
  phases: [
    { title: 'Rewrite', detail: '6 Sonnet arms, each rewrites the same 24 requests' },
    { title: 'Judge', detail: '4 blind judges (2 orderings x 2 halves), inherit the session model' },
  ],
}

const L = args.lift
const IDS = args.ids
const ARMS = [
  { key: 'bare', kind: 'none' },
  { key: 'oneliner', kind: 'oneliner' },
  { key: 'suite-main', kind: 'suite', root: L + '/suite-main/skills/ai-writing-suite' },
  { key: 'suite-pr67', kind: 'suite', root: L + '/suite-pr67/skills/ai-writing-suite' },
  { key: 'cursor-unslop', kind: 'ext', root: L + '/ext/cursor/plugins/pstack/skills/unslop' },
  { key: 'clay-unslop', kind: 'ext', root: L + '/ext/clay/unslop' },
]

const COMMON = `Read the requests from ${L}/items_arms.json (a JSON object with "items": [{id, request}]). Handle every request, in order, as if each came from a different user in a separate chat: do not carry facts or wording from one request into another.
For each request return: "output" = exactly the final text you would hand the user (the polished text itself, no preamble like "Here is"), and "notes" = anything else you would say to the user alongside it (empty string if nothing). Do not run any scripts or programs, do not install anything, and do not write or modify any files.`

const ONELINER = 'Guideline for every request: Rewrite so it does not read AI-generated. Keep every fact, number, name, the author\'s voice and their level of certainty; add nothing new; if a passage is already fine, leave it alone.'

function armPrompt(a) {
  if (a.kind === 'none') return `You are a helpful writing assistant.\n${COMMON}\nThe only file you may read is ${L}/items_arms.json. Use no other tools.`
  if (a.kind === 'oneliner') return `You are a helpful writing assistant.\n${COMMON}\nThe only file you may read is ${L}/items_arms.json. Use no other tools.\n${ONELINER}`
  if (a.kind === 'suite') return `You are a writing assistant with the "ai-writing-suite" agent skill installed at ${a.root} (the suite root: it contains SKILL.md, skills/, _shared/). These are prose-polish requests, so the matching sub-skill is comms-polish.
Before the first request, load the skill the way an agent harness would: read ${a.root}/skills/comms-polish/SKILL.md and follow its instructions, including reading the shared files it tells you to read (its _shared/... paths are relative to ${a.root}). Then apply the skill to every request. There is no voice profile for this user (the per-user state directory is empty): treat that as the skill's normal no-profile case and do not offer onboarding.
Read only ${L}/items_arms.json and files under ${a.root}. Do not read anything else in the filesystem.
${COMMON}`
  return `You are a writing assistant with an agent skill named "unslop" installed at ${a.root}.
Before the first request, load the skill the way an agent harness would: read ${a.root}/SKILL.md and follow its instructions, including reading the reference files it tells you to read (paths relative to ${a.root}). These are polish/rewrite requests from users who want the final text. There is no saved voice profile for this user. If the skill asks you to run a script, skip that step. Then apply the skill to every request.
Read only ${L}/items_arms.json and files under ${a.root}. Do not read anything else in the filesystem.
${COMMON}`
}

const ARM_SCHEMA = {
  type: 'object',
  properties: { items: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, output: { type: 'string' }, notes: { type: 'string' } }, required: ['id', 'output', 'notes'] } } },
  required: ['items'],
}

phase('Rewrite')
const armResults = await parallel(ARMS.map(a => () =>
  agent(armPrompt(a), { label: `arm:${a.key}`, phase: 'Rewrite', schema: ARM_SCHEMA, model: 'sonnet' })))
const arms = {}
ARMS.forEach((a, i) => { arms[a.key] = armResults[i] || { items: [] } })
const missingArms = ARMS.filter((a, i) => !armResults[i]).map(a => a.key)
if (missingArms.length) log(`Arms with no result: ${missingArms.join(', ')}`)
for (const a of ARMS) {
  const got = new Set((arms[a.key].items || []).map(x => x.id))
  const miss = IDS.filter(id => !got.has(id))
  if (miss.length) log(`${a.key} missing ${miss.length} items: ${miss.join(', ')}`)
}

// Blind labels: perm1 rotates the arm order by item index; perm2 reverses perm1.
const LABELS = ['A', 'B', 'C', 'D', 'E', 'F']
const perms = { p1: {}, p2: {} }
IDS.forEach((id, i) => {
  const order = ARMS.map((_, j) => ARMS[(j + i) % ARMS.length].key)
  perms.p1[id] = {}; perms.p2[id] = {}
  order.forEach((k, j) => { perms.p1[id][LABELS[j]] = k })
  order.slice().reverse().forEach((k, j) => { perms.p2[id][LABELS[j]] = k })
})

function packet(id, pk) {
  const m = perms[pk][id]
  return `### Item ${id}\n` + LABELS.map(lab => {
    const o = (arms[m[lab]].items || []).find(x => x.id === id)
    const text = o ? o.output : '(no output)'
    const notes = o && o.notes && o.notes.trim() ? `\n[Message to author: ${o.notes.trim()}]` : ''
    return `--- Candidate ${lab} ---\n${text}${notes}`
  }).join('\n\n')
}

const JUDGE_SCHEMA = {
  type: 'object',
  properties: { items: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' },
    candidates: { type: 'array', items: { type: 'object', properties: {
      label: { type: 'string', enum: LABELS },
      would_send: { type: 'boolean' },
      meaning_changes: { type: 'array', items: { type: 'object', properties: {
        type: { type: 'string', enum: ['added_claim', 'dropped_fact', 'strengthened_certainty', 'weakened_certainty', 'scope_change', 'number_change', 'other'] },
        detail: { type: 'string' } }, required: ['type', 'detail'] } },
      unsupported_claims_kept: { type: 'array', items: { type: 'string' } },
      over_edited: { type: 'boolean' },
      comment: { type: 'string' } }, required: ['label', 'would_send', 'meaning_changes', 'over_edited'] } },
    reads_human_rank: { type: 'array', items: { type: 'string', enum: LABELS } },
    best: { type: 'string', enum: LABELS } }, required: ['id', 'candidates', 'reads_human_rank', 'best'] } } },
  required: ['items'],
}

const half = Math.ceil(IDS.length / 2)
const CHUNKS = [{ key: 'a', ids: IDS.slice(0, half) }, { key: 'b', ids: IDS.slice(half) }]
const JOBS = []
for (const pk of ['p1', 'p2']) for (const c of CHUNKS) JOBS.push({ pk, c })

phase('Judge')
const judges = await parallel(JOBS.map(j => () => agent(`You are an expert editor judging rewrites blind. For each item below, an author sent a polish request (the original request, including their draft and sometimes their notes, is in ${L}/items_judge.json under the same id; read that file and nothing else). Six assistants answered; their outputs are labeled A-F in random order. You do not know which assistant wrote which, and labels mean nothing across items.

For EACH candidate decide:
- meaning_changes: every concrete change in meaning versus the author's draft. Types: added_claim (anything not in the draft or notes), dropped_fact, strengthened_certainty (hedge removed, possibility turned into fact, correlation into cause), weakened_certainty, scope_change (only/most/all/about changed), number_change, other. Pure rewording that keeps meaning is NOT a change. If the author gave notes, a change that corrects the draft to match the notes is not a meaning change.
- unsupported_claims_kept: only when notes are given: claims in the candidate that the notes do not support (e.g. a causal explanation or certainty the notes do not establish), whether inherited from the draft or added.
- would_send: imagine you ARE the author. Given what you meant (your draft, and your notes when shown), would you send this version as-is with no further edits? Answer no if it changes meaning, adds anything you did not say, drops something you needed, or reads worse than your own draft.
- over_edited: true if it changed much more than needed (especially if the draft was already good human writing).
- comment: one short sentence.
Then rank all six by how much the text reads like a skilled human professional wrote it for that audience (reads_human_rank, best first; judge the text, ignore meaning here), and pick the single version you would send (best), weighing meaning above style.
Messages to the author shown in [brackets] are part of what the assistant said; count a flagged gap or question as helpful, not as a meaning change.

${j.c.ids.map(id => packet(id, j.pk)).join('\n\n')}`,
  { label: `judge:${j.pk}-${j.c.key}`, phase: 'Judge', schema: JUDGE_SCHEMA })
  .then(r => r ? { perm_key: j.pk, chunk: j.c.key, items: r.items } : null)))

return { arm_names: ARMS.map(a => a.key), arms, perms, judges }
