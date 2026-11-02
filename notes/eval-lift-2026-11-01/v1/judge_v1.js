export const meta = {
  name: 'lift-v1-judge',
  description: 'v1 judges: absolute (notes hidden, typed severe changes, sentinels) and pairwise new-vs-main',
  phases: [{ title: 'Judge', detail: 'one agent per packet file' }],
}

// args: { model: 'opus', packets: [{ key, path, kind: 'abs'|'pair' }] }

const SEVERE = ['number_change', 'added_claim', 'dropped_fact', 'strengthened_certainty', 'weakened_certainty', 'scope_change']

const ABS_SCHEMA = {
  type: 'object',
  properties: { items: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' },
    would_send: { type: 'boolean' },
    severe_changes: { type: 'array', items: { type: 'object', properties: {
      type: { type: 'string', enum: SEVERE }, detail: { type: 'string' } }, required: ['type', 'detail'] } },
    over_edited: { type: 'boolean' },
    comment: { type: 'string' } }, required: ['id', 'would_send', 'severe_changes', 'over_edited'] } } },
  required: ['items'],
}
const PAIR_SCHEMA = {
  type: 'object',
  properties: { items: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' },
    preferred: { type: 'string', enum: ['A', 'B', 'tie'] },
    reason: { type: 'string' } }, required: ['id', 'preferred'] } } },
  required: ['items'],
}

const ABS = p => `You are an expert editor checking AI rewrites for fidelity. Read ${p} and nothing else. Each block gives an author's polish request (their text, and sometimes their notes) and ONE rewrite (Candidate A). Judge every block in the file, using its id.

For each block decide:
- severe_changes: every change in MEANING versus the author's text, typed as one of: number_change (a number, unit, or date changed), added_claim (a fact, cause, commitment, or claim not in the author's text or notes), dropped_fact (a fact, number, caveat, attribution, or commitment the author needed is gone), strengthened_certainty (hedge removed, possibility made fact, correlation made cause, "hope to" made "will"), weakened_certainty (a firm statement hedged or softened), scope_change (only / most / all / at least / about changed or dropped). Rewording that keeps the meaning is NOT a change. Removing pure hype or filler that carried no claim is NOT a change. If the author supplied notes, correcting the text to match the notes is NOT a change.
- would_send: imagine you ARE the author. Would you send this rewrite as-is? No if it changes your meaning, adds anything you did not say, drops something you needed, or reads worse than your own text.
- over_edited: true if it changed much more than the text needed (for example, rewrote good human writing, or turned terse bullets into prose).
- comment: one short sentence.
Be strict and literal about meaning; do not reward or punish style choices that keep the meaning.`

const PAIR = p => `You are an expert editor. Read ${p} and nothing else. Each block gives an author's polish request and two rewrites, Candidate A and Candidate B. For each block, pick the rewrite the author should send: the one that keeps the author's meaning (facts, numbers, hedges, scope words, attributions, commitments) and reads best for its audience, with meaning weighing more than style. Answer "tie" if they are equally good or the difference is negligible. Judge every block, using its id. Position and length must not matter.`

phase('Judge')
const res = await parallel(args.packets.map(pk => () =>
  agent(pk.kind === 'abs' ? ABS(pk.path) : PAIR(pk.path),
        { label: `judge:${pk.key}`, phase: 'Judge', schema: pk.kind === 'abs' ? ABS_SCHEMA : PAIR_SCHEMA, model: args.model })
    .then(r => r ? { key: pk.key, kind: pk.kind, model: args.model, items: r.items } : null)))
return { judges: res }
