# KB Retrieval Semantics

For a normalized query token set `query`, each INDEX entry receives this score:

1. Primary: `|query ∩ (keywords ∪ summary)|`.
2. Tiebreak: `|query ∩ summary|`.

Scores are compared lexicographically, with higher values winning. A full tie
returns every tied entry in stable INDEX table order, and the consumer opens all
returned files. This is the executable form of `INDEX.md`'s own tie clause:
"If two entries tie, open both and synthesize." Zero total overlap returns no
match (`None`).

The hand-computed smoke cases established when the knowledge base was frozen are
the authority for these semantics. INDEX wording such as "scan Keywords, then
Summary" describes the two information layers used during retrieval; it does not
give keyword overlap strict priority over summary overlap.
