# Destinations — Repo Package and Tracker Records

> **Tool-agnostic.** The repo package is the default and complete path. Trackers are optional adapters.

## Contents

- [Choosing a destination](#choosing-a-destination)
- [The repo package writer](#the-repo-package-writer)
- [The create and update protocols](#the-create-and-update-protocols)
- [Section-scoped updates](#section-scoped-updates)
- [Jira adapter](#jira-adapter)
- [Aha adapter](#aha-adapter)
- [Azure DevOps and others](#azure-devops-and-others)
- [Copy-ready fallback](#copy-ready-fallback)

## Choosing a destination

Ask once, at Step 9, when there is something to write:

> Where should this go — the repo epic package, the tracker, or both?

| Destination | When | What happens |
|---|---|---|
| **Repo** (default) | No tracker connected, or the team works spec-first | `epics/<key>/epic.md` (+ `epic_eval_criteria.yaml` in GenAI mode) |
| **Tracker** | A tracker MCP is connected and the PM wants a record | Record created or updated after the protocols below |
| **Both** | Teams already running GovKit | Package written, then the record populated from it |

**The repo path is complete on its own.** A PM with no tracker gets the full skill: the interview, the epic, the evaluation criteria. Never present markdown as a fallback or consolation — it is the artifact `aipos-feature-create` actually reads.

If no tracker is connected, don't ask. Write the package and say where it landed.

## The repo package writer

```text
epics/<key>/
  epic.md
  epic_eval_criteria.yaml    # GenAI mode only
  story-map.md               # later, written by aipos-feature-create
```

Rules:

- **Never overwrite silently.** If `epic.md` exists, show what is being replaced and confirm — it may have been hand-edited since generation.
- Writing files is local, reversible, and visible in `git diff`. One confirmation for the package is enough; the ceremony below is for records other people can see.
- Use the tracker key as `<key>` whenever one exists, so the repo and the tracker stay traceable to each other. Create the tracker record first when you can, and use the key it returns.

## The create and update protocols

**The canonical protocols live in `../../aipos-feature-create/references/tracker-adapters.md` — read and follow them.** In brief: preview the exact final content (never a summary), name the destination precisely, state what cannot be undone, one explicit yes, then create/write, read back, and report honestly — including partial failures. A bare "proceed" never authorizes a write, and if any step fails, stop and fall back to copy-ready output rather than retrying blind.

Epic-specific deltas:

- The create preview shows **every field with its actual value** — an epic has many negotiated sections, and a section list is not a preview. *"Create an Epic in the CLAIMS project in Jira?"* is the destination form.
- One record per confirmation, always — an epic create is never batched with feature creates.

Field mapping:

| Epic section | Typical tracker field |
|---|---|
| Elevator pitch | Elevator Pitch, or Description |
| User problem(s) + personas + impact | User Problems |
| Alignment to business objectives | Goals / Initiatives link, or Description |
| Success metrics | Success Metrics |
| GenAI evaluation criteria | Evaluation Criteria field, or appended to Success Metrics |
| Evidence and insights | Evidence / Research, or Description |
| Initial scope / MVP | Initial Scope |
| Risks and mitigations | Risks |
| NFRs | NFR field, or appended to Description |
| Target release · Owner · Category | The corresponding record fields |

Where a tracker has no matching field, append under a heading rather than dropping content — and say which sections were appended rather than mapped.

## Section-scoped updates

When the PM asked to improve specific sections, **write only those sections.**

This matters more for epics than for anything else in GovKit. Epic fields are negotiated: the success metrics may have been agreed with a VP, the scope with three teams. Regenerating an untouched field because it was in the buffer silently discards those negotiations, and nobody notices until a review.

So:

- Preview only the sections being written, and say explicitly which fields are left untouched.
- If you noticed a problem in a section outside scope, mention it in one line — do not fix it uninvited.
- Never write a field back "unchanged". A no-op write still stamps the record's modified-by and modified-at, which is misleading in an audit trail and confusing in a change feed.

## Jira adapter

Atlassian MCP tools.

| Step | Tool |
|---|---|
| Discover issue types and fields | `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields` |
| Read the existing epic | `getJiraIssue` |
| Create | `createJiraIssue` |
| Update fields | `editJiraIssue` |
| Link to goals or initiatives | `createIssueLink` |
| Read-back verification | `getJiraIssue` |

- **Resolve the Epic issue type and field IDs before writing.** Custom field IDs are per-instance; never guess one.
- Most epic-template sections have no native Jira field and land in the description. Structure it with headings that match the template, so `aipos-feature-create` can read the sections back out.
- Rich-text fields hold ADF or wiki markup — write in the format the field already uses.
- On team-managed projects the epic is a standard issue type; on company-managed ones it may carry Epic Name and Epic Colour fields. Check the metadata.

## Aha adapter

Aha! MCP tools.

| Step | Tool |
|---|---|
| Locate the workspace | `find_project` |
| Resolve custom field keys | `fields_metadata`, `field_options_metadata` |
| Read the existing epic | `read_records` |
| Create | `manage_record` (create) |
| Update fields | `manage_record` (update) |
| Read-back verification | `read_records` |

- **Custom field keys are workspace-specific. Always resolve them with `fields_metadata`; never guess.** This is the most common cause of a write that reports success and lands nowhere.
- Aha! epic templates vary by workspace and often carry named fields for elevator pitch, user problems, and success metrics. Map to them where they exist rather than concatenating everything into the description.
- Personas may exist as records. **Read them to offer choices; do not create them.** Persona creation is a separate governance act with its own owner.
- Release and category are usually constrained option lists — resolve allowed values with `field_options_metadata` before proposing defaults.
- This skill does not create attachments. Where an artifact belongs as a file (`epic_eval_criteria.yaml`), write it to the repo and hand the PM the filename.

## Azure DevOps and others

No MCP adapter in the current toolset — use the copy-ready fallback. For teams with their own tooling: Epics are a standard work item type, creatable via the REST API, and the same create and update protocols apply unchanged.

## Copy-ready fallback

When no tracker MCP is connected, when an adapter hits a case it can't handle, or when the PM declines the write:

````markdown
## Epic field updates — <KEY or name>

### Elevator Pitch
<text>

### User Problems
<problem statement, personas, quantified impact>

### Success Metrics
<the table>

### Evaluation Criteria
<GenAI mode — the table>

### Evidence & Insights
<qualitative and quantitative>

### Initial Scope / MVP
<in scope and out of scope>

### Risks & Mitigations
<the table>

### Non-Functional Requirements
<the table>
````

Copy-ready means copy-ready: no unresolved placeholders, no draft markers. Open questions belong in the summary you show the PM and in `epic.md`'s gaps section — never embedded in text somebody is about to paste into a tracker.
