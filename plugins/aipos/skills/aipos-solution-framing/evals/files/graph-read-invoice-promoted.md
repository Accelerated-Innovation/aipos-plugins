# Graph read — tool results from this session

Server connected: `opportunity-engine-mock` (tools: list_problems, get_problem, get_lineage, list_evidence, list_opportunities, get_work_item_links, get_evidence_text). Every record is SYNTHETIC fixture data.

### `opportunity-engine-mock` → `get_work_item_links(problem_id='fixture:prb-invoice-dup')`

```json
{
  "problem_id": "fixture:prb-invoice-dup",
  "promoted": true,
  "links": [
    {
      "problem_id": "fixture:prb-invoice-dup",
      "link_id": "fixture:lnk-1",
      "link_type": "promoted",
      "target_system": "aha",
      "target_type": "feature",
      "external_record_id": "fixture-aha-7001",
      "external_reference": "OPP-12",
      "record_url": "https://fixture.invalid/aha/OPP-12",
      "container_ref": null,
      "linked_by": "fixture:subject-pm-1",
      "linked_at": "2026-08-14T12:00:00+00:00",
      "status": "active",
      "outcome_emitted": false,
      "schema_version": 1
    },
    {
      "problem_id": "fixture:prb-invoice-dup",
      "link_id": "fixture:lnk-2",
      "link_type": "attached",
      "target_system": "jira",
      "target_type": "story",
      "external_record_id": "fixture-jira-9",
      "external_reference": "PROJ-9",
      "record_url": "https://fixture.invalid/jira/PROJ-9",
      "container_ref": "PROJ",
      "linked_by": "fixture:subject-pm-1",
      "linked_at": "2026-07-01T12:00:00+00:00",
      "status": "severed",
      "outcome_emitted": false,
      "schema_version": 1
    }
  ],
  "total": 2,
  "schema_version": 1
}
```
### `opportunity-engine-mock` → `get_problem(problem_id='fixture:prb-invoice-dup')`

```json
{
  "problem_id": "fixture:prb-invoice-dup",
  "title": "[SYNTHETIC] Duplicate vendor invoices reach payment before anyone notices",
  "composite_score": 0.77,
  "evidence_references": [
    "servicenow:INC-20931",
    "servicenow:INC-21007",
    "zendesk:tkt-80155"
  ],
  "personas": [
    {
      "name": "AP Clerk",
      "confidence": 0.88
    },
    {
      "name": "Controller",
      "confidence": 0.61
    }
  ],
  "lineage_ref": "fixture:lin-invoice-dup",
  "schema_version": 1
}
```
