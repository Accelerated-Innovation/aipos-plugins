# Routing cases

These cases test selection from the complete skill catalog before any skill body
is loaded. They complement the coaching cases under each skill's `evals/`.

`cases.json` records the prompt, available context, allowed primary action and
ordered handoffs, whether a mistake crosses a critical boundary, and the case's
development or held-out split. `none` means the request is outside AIPOS;
`clarify` means missing context prevents a useful choice. A correct selection
does not prove that the selected skill executes correctly.

Descriptions come from actual `SKILL.md` frontmatter. Do not copy them here.
Keep held-out paraphrases out of description tuning. Read the
[ownership model](../../docs/plans/2026-09-19-aipos-plugin-consolidation.md#ownership-and-workflow)
when adding cases; one requested action should have one owner, with explicit
handoffs when the requested result needs more than one skill.

