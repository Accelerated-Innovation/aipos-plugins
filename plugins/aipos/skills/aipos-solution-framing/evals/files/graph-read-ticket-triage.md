# Graph read — tool results from this session

Server connected: `opportunity-engine-mock` (tools: list_problems, get_problem, get_lineage, list_evidence, list_opportunities, get_work_item_links, get_evidence_text). Every record is SYNTHETIC fixture data.

### `opportunity-engine-mock` → `get_work_item_links(problem_id='fixture:prb-ticket-triage')`

```json
{
  "problem_id": "fixture:prb-ticket-triage",
  "promoted": false,
  "links": [],
  "total": 0,
  "schema_version": 1
}
```
### `opportunity-engine-mock` → `get_problem(problem_id='fixture:prb-ticket-triage')`

```json
{
  "problem_id": "fixture:prb-ticket-triage",
  "title": "[SYNTHETIC] Support tickets arrive uncategorized and are routed to the wrong team",
  "composite_score": 0.82,
  "evidence_references": [
    "reops:int-0412",
    "reops:int-0415",
    "reops:int-0419",
    "zendesk:tkt-88121",
    "zendesk:tkt-88340",
    "zendesk:tkt-88417",
    "gong:call-5530",
    "reops:study-ts-07"
  ],
  "personas": [
    {
      "name": "Support Agent",
      "confidence": 0.91
    },
    {
      "name": "Support Team Lead",
      "confidence": 0.74
    },
    {
      "name": "Enterprise Admin",
      "confidence": 0.52
    }
  ],
  "lineage_ref": "fixture:lin-ticket-triage",
  "schema_version": 1
}
```
### `opportunity-engine-mock` → `list_evidence(problem_id='fixture:prb-ticket-triage')`

```json
{
  "problem_id": "fixture:prb-ticket-triage",
  "items": [
    {
      "provenance_reference": "reops:int-0412",
      "source_system": "reops",
      "source_type": "interview_note",
      "external_record_id": "int-0412",
      "occurred_at": "2026-07-08T15:00:00Z",
      "record_url": "https://fixture.invalid/reops/int-0412",
      "schema_version": 1
    },
    {
      "provenance_reference": "reops:int-0415",
      "source_system": "reops",
      "source_type": "interview_note",
      "external_record_id": "int-0415",
      "occurred_at": "2026-07-09T14:30:00Z",
      "record_url": "https://fixture.invalid/reops/int-0415",
      "schema_version": 1
    },
    {
      "provenance_reference": "reops:int-0419",
      "source_system": "reops",
      "source_type": "interview_note",
      "external_record_id": "int-0419",
      "occurred_at": "2026-07-14T16:00:00Z",
      "record_url": "https://fixture.invalid/reops/int-0419",
      "schema_version": 1
    },
    {
      "provenance_reference": "zendesk:tkt-88121",
      "source_system": "zendesk",
      "source_type": "support_ticket",
      "external_record_id": "tkt-88121",
      "occurred_at": "2026-08-02T09:12:00Z",
      "record_url": "https://fixture.invalid/zendesk/tkt-88121",
      "schema_version": 1
    },
    {
      "provenance_reference": "zendesk:tkt-88340",
      "source_system": "zendesk",
      "source_type": "support_ticket",
      "external_record_id": "tkt-88340",
      "occurred_at": "2026-08-05T11:40:00Z",
      "record_url": "https://fixture.invalid/zendesk/tkt-88340",
      "schema_version": 1
    },
    {
      "provenance_reference": "zendesk:tkt-88417",
      "source_system": "zendesk",
      "source_type": "support_ticket",
      "external_record_id": "tkt-88417",
      "occurred_at": "2026-08-06T08:05:00Z",
      "record_url": "https://fixture.invalid/zendesk/tkt-88417",
      "schema_version": 1
    },
    {
      "provenance_reference": "gong:call-5530",
      "source_system": "gong",
      "source_type": "call_transcript",
      "external_record_id": "call-5530",
      "occurred_at": "2026-06-18T17:00:00Z",
      "record_url": "https://fixture.invalid/gong/call-5530",
      "schema_version": 1
    },
    {
      "provenance_reference": "reops:study-ts-07",
      "source_system": "reops",
      "source_type": "study_outcome",
      "external_record_id": "study-ts-07",
      "occurred_at": null,
      "record_url": null,
      "schema_version": 1
    }
  ],
  "total": 8
}
```
### `opportunity-engine-mock` → `get_lineage(problem_id='fixture:prb-ticket-triage')`

```json
{
  "problem_id": "fixture:prb-ticket-triage",
  "source_evidence_refs": [
    "reops:int-0412",
    "reops:int-0415",
    "reops:int-0419",
    "zendesk:tkt-88121",
    "zendesk:tkt-88340",
    "zendesk:tkt-88417",
    "gong:call-5530",
    "reops:study-ts-07"
  ],
  "originating_sources": [
    "reops:study-int-2026-07",
    "zendesk:view-triage-audit-2026-08",
    "gong:call-5530",
    "reops:study-ts-07"
  ],
  "schema_version": 1
}
```
