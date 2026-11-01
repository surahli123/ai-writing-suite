export const meta = {
  name: 'lift-judge',
  description: 'Blind-judge prepared candidate packets for the skill-lift eval (session model)',
  phases: [{ title: 'Judge', detail: 'one judge per packet file (orderings p1/p2)' }],
}

// args: { packets: [{ key, path }] }  Each packet file is plain text written by build_packets.py:
// per item, the author's original request followed by candidates labeled A, B, C...

const LABELS = ['A', 'B', 'C', 'D', 'E', 'F']
const SCHEMA = {
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

const PROMPT = p => `You are an expert editor judging rewrites blind. Read ${p} and nothing else. For each item it gives an author's polish request (their draft, and sometimes their notes) followed by several assistants' answers, labeled A, B, C... in random order. You do not know which assistant wrote which, and labels mean nothing across items. Judge every item in the file.

For EACH candidate decide:
- meaning_changes: every concrete change in meaning versus the author's draft. Types: added_claim (anything not in the draft or notes), dropped_fact, strengthened_certainty (hedge removed, possibility turned into fact, correlation into cause), weakened_certainty, scope_change (only/most/all/about changed), number_change, other. Pure rewording that keeps meaning is NOT a change. If the author gave notes, a change that corrects the draft to match the notes is not a meaning change.
- unsupported_claims_kept: only when notes are given: claims in the candidate that the notes do not support (e.g. a causal explanation or certainty the notes do not establish), whether inherited from the draft or added.
- would_send: imagine you ARE the author. Given what you meant (your draft, and your notes when shown), would you send this version as-is with no further edits? Answer no if it changes meaning, adds anything you did not say, drops something you needed, or reads worse than your own draft.
- over_edited: true if it changed much more than needed (especially if the draft was already good human writing).
- comment: one short sentence.
Then rank all candidates by how much the text reads like a skilled human professional wrote it for that audience (reads_human_rank, best first; judge the text, ignore meaning here), and pick the single version you would send (best), weighing meaning above style.
Messages to the author shown in [brackets] are part of what the assistant said; count a flagged gap or question as helpful, not as a meaning change.`

phase('Judge')
const res = await parallel(args.packets.map(pk => () =>
  agent(PROMPT(pk.path), { label: `judge:${pk.key}`, phase: 'Judge', schema: SCHEMA })
    .then(r => r ? { perm_key: pk.key, items: r.items } : null)))
return { judges: res }
