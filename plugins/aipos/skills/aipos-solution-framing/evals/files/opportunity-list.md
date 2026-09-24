# Graph read — tool results from this session

Server connected: `opportunity-engine-mock` (tools: list_problems, get_problem, get_lineage, list_evidence, list_opportunities, get_work_item_links, get_evidence_text). Every record is SYNTHETIC fixture data.

### `opportunity-engine-mock` → `list_opportunities(limit=10)`

```json
{
  "items": [
    {
      "problem_id": "fixture:prb-ticket-triage",
      "title": "[SYNTHETIC] Support tickets arrive uncategorized and are routed to the wrong team",
      "composite_score": 0.82,
      "components": {
        "evidence_strength": 0.71,
        "revenue_impact": 0.38,
        "persona_breadth": 0.55,
        "recency": 0.88,
        "validation_signal": 0.05
      },
      "strategic_weight": 1.0,
      "weight_config_version": "fixture-weights-v1",
      "links": [],
      "schema_version": 1
    },
    {
      "problem_id": "fixture:prb-invoice-dup",
      "title": "[SYNTHETIC] Duplicate vendor invoices reach payment before anyone notices",
      "composite_score": 0.77,
      "components": {
        "evidence_strength": 0.64,
        "revenue_impact": 0.72,
        "persona_breadth": 0.4,
        "recency": 0.8,
        "validation_signal": 0.3
      },
      "strategic_weight": 1.0,
      "weight_config_version": "fixture-weights-v1",
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
        }
      ],
      "schema_version": 1
    },
    {
      "problem_id": "fixture:prb-renewal-quotes",
      "title": "[SYNTHETIC] Renewal quotes take days to assemble",
      "composite_score": 0.74,
      "components": {
        "evidence_strength": 0.35,
        "revenue_impact": 0.66,
        "persona_breadth": 0.2,
        "recency": 0.95,
        "validation_signal": 0.0
      },
      "strategic_weight": 1.0,
      "weight_config_version": "fixture-weights-v1",
      "links": [],
      "schema_version": 1
    },
    {
      "problem_id": "fixture:prb-pricing-approvals",
      "title": "[SYNTHETIC] Pricing exceptions need three approvals before a quote can go out",
      "composite_score": 0.71,
      "components": {
        "evidence_strength": 0.35,
        "revenue_impact": 0.66,
        "persona_breadth": 0.2,
        "recency": 0.95,
        "validation_signal": 0.0
      },
      "strategic_weight": 1.0,
      "weight_config_version": "fixture-weights-v1",
      "links": [],
      "schema_version": 1
    },
    {
      "problem_id": "fixture:prb-redline-loss",
      "title": "[SYNTHETIC] Contract redlines get lost between email threads",
      "composite_score": 0.68,
      "components": {
        "evidence_strength": 0.35,
        "revenue_impact": 0.66,
        "persona_breadth": 0.2,
        "recency": 0.95,
        "validation_signal": 0.0
      },
      "strategic_weight": 1.0,
      "weight_config_version": "fixture-weights-v1",
      "links": [],
      "schema_version": 1
    },
    {
      "problem_id": "fixture:prb-renewal-risk",
      "title": "[SYNTHETIC] Customer success cannot see renewal risk until it is too late",
      "composite_score": 0.65,
      "components": {
        "evidence_strength": 0.35,
        "revenue_impact": 0.66,
        "persona_breadth": 0.2,
        "recency": 0.95,
        "validation_signal": 0.0
      },
      "strategic_weight": 1.0,
      "weight_config_version": "fixture-weights-v1",
      "links": [],
      "schema_version": 1
    },
    {
      "problem_id": "fixture:prb-quote-templates",
      "title": "[SYNTHETIC] Quote templates are out of date with current pricing",
      "composite_score": 0.6,
      "components": {
        "evidence_strength": 0.35,
        "revenue_impact": 0.66,
        "persona_breadth": 0.2,
        "recency": 0.95,
        "validation_signal": 0.0
      },
      "strategic_weight": 1.0,
      "weight_config_version": "fixture-weights-v1",
      "links": [],
      "schema_version": 1
    },
    {
      "problem_id": "fixture:prb-month-end",
      "title": "[SYNTHETIC] Month-end reports require manual spreadsheet stitching",
      "composite_score": 0.58,
      "components": {
        "evidence_strength": 0.52,
        "revenue_impact": 0.44,
        "persona_breadth": 0.15,
        "recency": 0.12,
        "validation_signal": 0.0
      },
      "strategic_weight": 1.0,
      "weight_config_version": "fixture-weights-v1",
      "links": [],
      "schema_version": 1
    },
    {
      "problem_id": "fixture:prb-schema-next",
      "title": "[SYNTHETIC] A problem served under a newer schema version",
      "composite_score": 0.41,
      "components": {
        "evidence_strength": 0.2,
        "revenue_impact": 0.2,
        "persona_breadth": 0.1,
        "recency": 0.9,
        "validation_signal": 0.0
      },
      "strategic_weight": 1.0,
      "weight_config_version": "fixture-weights-v1",
      "links": [],
      "schema_version": 2
    }
  ],
  "total": 9,
  "offset": 0,
  "limit": 10
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
### `opportunity-engine-mock` → `get_lineage(problem_id='fixture:prb-invoice-dup')`

```json
{
  "problem_id": "fixture:prb-invoice-dup",
  "source_evidence_refs": [
    "servicenow:INC-20931",
    "servicenow:INC-21007",
    "zendesk:tkt-80155"
  ],
  "originating_sources": [
    "servicenow:queue-ap-2026",
    "zendesk:view-vendor-2026"
  ],
  "schema_version": 1
}
```
### `opportunity-engine-mock` → `get_lineage(problem_id='fixture:prb-renewal-quotes')`

```json
{
  "problem_id": "fixture:prb-renewal-quotes",
  "source_evidence_refs": [
    "gong:call-7781"
  ],
  "originating_sources": [
    "gong:call-7781"
  ],
  "schema_version": 1
}
```
### `opportunity-engine-mock` → `get_lineage(problem_id='fixture:prb-pricing-approvals')`

```json
{
  "problem_id": "fixture:prb-pricing-approvals",
  "source_evidence_refs": [
    "gong:call-7781"
  ],
  "originating_sources": [
    "gong:call-7781"
  ],
  "schema_version": 1
}
```
### `opportunity-engine-mock` → `get_lineage(problem_id='fixture:prb-redline-loss')`

```json
{
  "problem_id": "fixture:prb-redline-loss",
  "source_evidence_refs": [
    "gong:call-7781"
  ],
  "originating_sources": [
    "gong:call-7781"
  ],
  "schema_version": 1
}
```
### `opportunity-engine-mock` → `get_lineage(problem_id='fixture:prb-renewal-risk')`

```json
{
  "problem_id": "fixture:prb-renewal-risk",
  "source_evidence_refs": [
    "gong:call-7781"
  ],
  "originating_sources": [
    "gong:call-7781"
  ],
  "schema_version": 1
}
```
### `opportunity-engine-mock` → `get_lineage(problem_id='fixture:prb-quote-templates')`

```json
{
  "problem_id": "fixture:prb-quote-templates",
  "source_evidence_refs": [
    "gong:call-7781"
  ],
  "originating_sources": [
    "gong:call-7781"
  ],
  "schema_version": 1
}
```
### `opportunity-engine-mock` → `get_lineage(problem_id='fixture:prb-month-end')`

```json
{
  "problem_id": "fixture:prb-month-end",
  "source_evidence_refs": [
    "salesforce:5003x-2201",
    "reops:int-0107",
    "zendesk:tkt-40211",
    "zendesk:tkt-40388"
  ],
  "originating_sources": [
    "salesforce:case-set-2022",
    "reops:study-2023-fin",
    "zendesk:view-reporting"
  ],
  "schema_version": 1
}
```
