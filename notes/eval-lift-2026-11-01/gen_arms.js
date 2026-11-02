export const meta = {
  name: 'lift-gen-arms',
  description: 'Generate rewrite outputs for one or more arms of the skill-lift eval (Sonnet)',
  phases: [{ title: 'Rewrite', detail: 'one Sonnet agent per arm' }],
}

// args: { arms: [{ key, kind: 'none'|'oneliner'|'suite'|'ext', root?, items_path }] }
// Each arm reads its own items file ({"items":[{id, request}]}) and returns {items:[{id, output, notes}]}.

const ONELINER = 'Guideline for every request: Rewrite so it does not read AI-generated. Keep every fact, number, name, the author\'s voice and their level of certainty; add nothing new; if a passage is already fine, leave it alone.'

function common(p) {
  return `Read the requests from ${p} (a JSON object with "items": [{id, request}]). Handle every request, in order, as if each came from a different user in a separate chat: do not carry facts or wording from one request into another.
For each request return: "output" = exactly the final text you would hand the user (the polished text itself, no preamble like "Here is"), and "notes" = anything else you would say to the user alongside it (empty string if nothing). Do not run any scripts or programs, do not install anything, and do not write or modify any files.`
}

function armPrompt(a) {
  const C = common(a.items_path)
  if (a.kind === 'none') return `You are a helpful writing assistant.\n${C}\nThe only file you may read is ${a.items_path}. Use no other tools.`
  if (a.kind === 'oneliner') return `You are a helpful writing assistant.\n${C}\nThe only file you may read is ${a.items_path}. Use no other tools.\n${ONELINER}`
  if (a.kind === 'suite') return `You are a writing assistant with the "ai-writing-suite" agent skill installed at ${a.root} (the suite root: it contains SKILL.md, skills/, _shared/). These are prose-polish requests, so the matching sub-skill is comms-polish.
Before the first request, load the skill the way an agent harness would: read ${a.root}/skills/comms-polish/SKILL.md and follow its instructions, including reading the shared files it tells you to read (its _shared/... paths are relative to ${a.root}). Then apply the skill to every request. There is no voice profile for this user (the per-user state directory is empty): treat that as the skill's normal no-profile case and do not offer onboarding.
Read only ${a.items_path} and files under ${a.root}. Do not read anything else in the filesystem.
${C}`
  return `You are a writing assistant with an agent skill installed at ${a.root}.
Before the first request, load the skill the way an agent harness would: read ${a.root}/SKILL.md and follow its instructions, including the reference files it tells you to read. There is no saved voice profile for this user. If the skill asks you to run a script, skip that step.
Read only ${a.items_path} and files under ${a.root}. Do not read anything else in the filesystem.
${C}`
}

const ARM_SCHEMA = {
  type: 'object',
  properties: { items: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, output: { type: 'string' }, notes: { type: 'string' } }, required: ['id', 'output', 'notes'] } } },
  required: ['items'],
}

phase('Rewrite')
const res = await parallel(args.arms.map(a => () =>
  agent(armPrompt(a), { label: `arm:${a.key}`, phase: 'Rewrite', schema: ARM_SCHEMA, model: 'sonnet' })))
const arms = {}
args.arms.forEach((a, i) => { arms[a.key] = res[i] || { items: [] } })
args.arms.forEach((a, i) => { if (!res[i]) log(`arm ${a.key} returned nothing`) })
return { arms }
