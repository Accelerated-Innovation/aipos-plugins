# Step 1 sources and the connector request

## The step 1 source list

Step 1 (Ingest Signals) is done when "signals land on a repeatable cadence, not on request". These
are the sources step 1 names (backlog item for this skill, Agentic PMLC workflow). Every one appears
in every report, connected or not; a source missing from the report reads as "fine".

| Source | Typical system | `source_system` values seen in the graph |
|---|---|---|
| Sales and support calls | Gong | `gong` |
| Support tickets | Zendesk | `zendesk` |
| Work-item tickets | Jira, Azure DevOps | `jira`, `ado` |
| CRM notes | Salesforce or another CRM | `salesforce`, `crm` |
| Product usage | Product analytics or telemetry | none defined yet |
| Eval drift | Model evaluation monitoring (engine E9 connectors) | none defined yet |

A `source_system` found in the graph that is not on this list (for example `reops` research
findings or `servicenow`) is reported in an "Also in the graph" row: it is evidence the graph
holds, not a step 1 source, and it does not fill a missing one.

What the engine itself can say, as verified on 2026-10-21 (discovery-engine `1a8919d`): only
Gong and Zendesk are wired for ingestion; no Jira/ADO, CRM, product-usage or eval-drift
ingestion exists; and **no ingestion-status read** — connection state, last ingestion, or volume
— is exposed over MCP or REST. Re-check this when the engine changes; do not repeat it as a
current fact without saying when it was verified.

## Drafting a connector request

One request per source that is not connected, or whose connection is unknown and which has no
records in the graph. It is a draft for a person to send; the skill sends nothing.

```markdown
**Connector request: <source>**
- To: <connector or data-platform owner, or "TBD — owner: <PM>; needed: who owns engine connectors">
- Why: step 1 lists <source> as a signal source; <what the report found: not connected / unknown, no records in N problems read>
- What to ingest: <record types, e.g. ticket title, description, status changes>, with a stable external ID per record so evidence keeps its provenance reference
- Personal data: <expected personal data>; redaction or masking at ingestion is a requirement, not an option
- Cadence wanted: <cadence> — TBD with the PM if not stated
- Done when: records from <source> appear in the graph with provenance references, and the engine exposes the source's connection state, last ingestion and volume through a status read
- Known blockers: <e.g. no engine connector exists for this source; ingestion-status read not yet available>
```
