# Destinations — Repo Package and Tracker Records

> **Tool-agnostic.** The repo package is the default and complete path. Trackers are optional adapters.
>
> **Canonical.** The create and update protocols in this file are the canonical write
> protocols for the GovKit skills. `aipos-epic-create`'s tracker adapters and
> `aipos-feature-slice`'s tracker write-back defer to these and carry only their own
> deltas — change the protocol here, and it changes everywhere.

## Contents

- [Choosing a destination](#choosing-a-destination)
- [The repo package writer](#the-repo-package-writer)
- [The create protocol](#the-create-protocol)
- [The update protocol](#the-update-protocol)
- [Jira adapter](#jira-adapter)
- [Aha adapter](#aha-adapter)
- [Azure DevOps and others](#azure-devops-and-others)
- [Copy-ready fallback](#copy-ready-fallback)

## Choosing a destination

Ask once, when there is something to write:

> Where should this go — the repo package, the tracker, or both?

| Destination | When | What happens |
|---|---|---|
| **Repo** (default) | No tracker connected, or the team works spec-first | Feature package files under `features/<key>/` |
| **Tracker** | A tracker MCP is connected and the PM wants records | Records created or updated, after the protocols below |
| **Both** | The common case for teams already on GovKit | Package written, then records created from it |

**The repo path is complete on its own.** A PM with no tracker, no MCP, and no intention of getting either gets the full skill: story map, feature package, tagged Gherkin, NFRs, DoD. Never present the markdown output as a fallback or a consolation — it is the artifact every other GovKit skill actually reads.

If no tracker is connected, don't ask. Write the package and say where it landed.

## The repo package writer

Default layout, per `feature-template.md`:

```text
features/<key>/
  feature_source.md
  acceptance.feature
  nfrs.md
  eval_criteria.yaml      # GenAI mode only
```

`<key>` is the tracker key when one exists (`AI-124`), otherwise a slug from the feature name (`route-high-value-claims`). When stubs are created before keys exist, use slugs and rename later — or better, create the tracker records first and use their keys, which keeps repo and tracker traceable to each other.

Rules:

- **Never overwrite silently.** If a file exists, show what is being replaced and confirm. A `feature_source.md` that has been hand-edited since generation is somebody's work.
- Writing files is not the same as writing to a tracker — it is local, reversible, and visible in `git diff`. One confirmation for the set is enough; the ceremony below is for records other people can see.
- Epic mode writes a `story-map.md` holding the backbone, slices, and boundaries. It is the record of *why* the features are these features, and it is the first thing someone asks for three months later. Put it at `epics/<key>/story-map.md` when an epic package exists (the layout `aipos-epic-create` writes), so the epic, the reasoning that split it, and the resulting features stay traceable to each other; otherwise put it beside the feature directories.

## The create protocol

**Creating records is the most outward-facing thing any GovKit skill does.** Every other skill in this plugin is update-in-place or read-only; this one can bring new records into existence that teammates will see, automations will fire on, and reports will count.

Before creating anything:

1. **Preview the complete set.** Every feature to be created, with all its stub fields, as a table. Not a summary — the actual field values.
2. **Name the destination precisely.** Tracker, project or workspace, parent epic, record type. *"Create 6 features in the CLAIMS project in Jira, all linked to CLAIMS-88?"*
3. **State what cannot be undone.** Say plainly that record keys are permanent and deleting them later is not something this skill will do.
4. **One explicit yes, covering the whole set.** Never create records one at a time hoping nobody notices the drift, and never treat a "proceed" from an earlier step as authorization.
5. **Create, then report.** List every created record with its key and link. If creation fails partway, **stop** — report exactly which records exist and which do not. A partial create that is reported honestly is recoverable; one that is glossed over is not.

A bare "proceed", "looks good", or "yes" from the proceed protocol **never** authorizes a create. The proceed protocol exists to make thinking cheap, not to make writes cheap.

If the PM adds, renames, or removes a feature after the preview, re-preview. The confirmation covered the set they saw.

## The update protocol

For writing feature detail into an existing record. Same protocol the rest of GovKit uses:

1. **Preview the exact content** — the final field text verbatim, not a description of it.
2. **Summarize the delta** in a line or two. If the write replaces existing content wholesale, say so explicitly and show what is being replaced.
3. **Name the destination precisely** — tracker, record key, field name.
4. **One explicit yes.** One record per confirmation; never batch confirmations across records.
5. **Read back and verify.** Fetch the record, compare against the preview, report either way. A silent partial write is worse than a failed one.

If any step fails — wrong field key, MCP error, read-back mismatch — stop, report, and fall back to copy-ready output rather than retrying blind.

Field mapping from the package:

| Package artifact | Typical tracker field |
|---|---|
| `feature_source.md` summary + scope | Description |
| `acceptance.feature` | Acceptance Criteria |
| `nfrs.md` | NFR field, or appended to Description |
| Definition of Done | Definition of Done field, or a checklist |
| Privacy impact | Privacy field, or appended to Description |
| `eval_criteria.yaml` | Evaluation Criteria field, or an attachment |

Where a tracker has no matching field, append to the description under a heading rather than dropping the content — and say which sections were appended rather than mapped.

## Jira adapter

Atlassian MCP tools.

| Step | Tool |
|---|---|
| Read the epic | `getJiraIssue` |
| Discover valid issue types and fields | `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields` |
| Create a feature | `createJiraIssue` |
| Link to the epic | Parent field on create, or `createIssueLink` |
| Update fields | `editJiraIssue` |
| Read-back verification | `getJiraIssue` |

- **Resolve issue types and field IDs before creating.** Projects differ: "Feature" may not exist, custom field IDs are per-instance. Never guess a field ID — fetch the metadata.
- Acceptance Criteria may be a custom field or part of the description. Ask which the team uses if it isn't obvious from the epic record.
- Rich-text fields hold ADF or wiki markup. Write Gherkin in the format the field already uses; a wiki-markup code block stays a wiki-markup code block. Tags are plain `@word` tokens and survive every format.
- Epic linkage is `parent` on team-managed projects and may be an Epic Link custom field on older company-managed ones. Check, don't assume.

## Aha adapter

Aha! MCP tools.

| Step | Tool |
|---|---|
| Locate the workspace | `find_project` |
| Resolve custom field keys | `fields_metadata`, `field_options_metadata` |
| Read the epic | `read_records` |
| Create a feature | `manage_record` (create) |
| Update fields | `manage_record` (update) |
| Read-back verification | `read_records` |

- **Custom field keys are workspace-specific. Always resolve them with `fields_metadata`; never guess.** This is the single most common cause of a write that reports success and lands nowhere.
- Aha! features often hold acceptance criteria as child **requirement** records, one per rule or scenario group. Creating requirements is a create — it goes through the create protocol, and the preview shows every requirement.
- Release and feature type are usually constrained option lists. Resolve allowed values with `field_options_metadata` before proposing defaults; an invalid option fails the write or, worse, silently sets nothing.
- This skill does not create attachments. Where an artifact belongs as a file (`eval_criteria.yaml`), write it to the repo and hand the PM the filename.

## Azure DevOps and others

No MCP adapter in the current toolset — use the copy-ready fallback.

For teams with their own tooling: the Acceptance Criteria field is `Microsoft.VSTS.Common.AcceptanceCriteria`, and work items are creatable via the REST API. The same create and update protocols apply, unchanged.

## Copy-ready fallback

When no tracker MCP is connected, when an adapter hits a case it can't handle, or when the PM declines the write — emit copy-ready blocks in the same shape `aipos-feature-refine` and `aipos-feature-slice` use.

For stubs:

````markdown
## Feature stubs — ready to create in <tracker>

| Name | Epic | Release | Type | Owner | Description |
|---|---|---|---|---|---|
````

For a fleshed-out feature:

````markdown
## Tracker field updates — <KEY or name>

### Description
<summary, scope, out of scope, dependencies, flows>

### Acceptance Criteria
```gherkin
<final tagged Gherkin>
```

### Non-Functional Requirements
<the nfrs.md table>

### Definition of Done
<the checklist>
````

Copy-ready means copy-ready: no unresolved placeholders, no draft markers, no question comments left in the Gherkin. Open questions belong in the summary you show the PM and in `feature_source.md`'s gaps section — not embedded in text somebody is about to paste into a tracker.
