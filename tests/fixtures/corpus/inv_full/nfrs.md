| ID | Dimension | Requirement | Threshold | Evidence | Owner | Scenarios |
|---|---|---|---|---|---|---|
| N1 | Performance | Routing decision latency | p95 < 2s | Performance test report | Engineering | @scenario:approval-routing-by-amount |
| N2 | Auditability | Every decision writes an audit record | 100% of decisions | Audit log inspection | QA | @scenario:manager-rejects-with-reason |
