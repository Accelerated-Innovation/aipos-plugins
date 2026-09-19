# Epic: Faster claims triage for regional adjusters

**Key:** CLM-88
**Owner:** Dana Whitfield
**Type:** Epic
**Target release:** FY26 Q2

## Elevator pitch

For regional claims adjusters who are drowning in first-notice-of-loss volume, our
claims workspace triages incoming claims, surfaces the documents that matter, and routes
high-value or unusual claims to the right person before the response clock runs out.
Unlike the current shared inbox, it makes the queue an ordered worklist instead of a pile.

## User problems

- Adjusters open every claim to find out whether it is urgent. There is no ordering signal
  in the shared inbox, so triage is manual and inconsistent between regions.
- High-value claims sit unassigned because nobody owns the routing decision. Two of last
  quarter's SLA breaches were claims worth over $250k that sat for four days.
- Supporting documents arrive across email, fax gateway, and the partner portal. Adjusters
  reassemble the file by hand before they can make a determination.
- Nobody can reconstruct why a claim was assigned to a given adjuster, which makes audit
  responses slow and, twice this year, inconclusive.

## Personas

- **Regional adjuster (primary)** — handles 30–60 open claims; measured on cycle time and
  determination quality.
- **Claims supervisor** — owns the regional queue, reassigns work, answers to the SLA report.
- **Compliance analyst** — reconstructs decision history for audits and regulator requests.

## Success metrics

- Median time from claim receipt to first adjuster action: 9.5 hours today → under 2 hours.
- SLA breaches on claims over $250k: 6 last year → 0.
- Percentage of claims where the complete document set is assembled automatically: 0% → 80%.

## Evidence

- Shadowing study, March: 8 adjusters, 40 hours observed. Mean 22 minutes per claim spent
  locating and assembling documents.
- SLA breach log FY25: 14 breaches, 6 on claims over $250k.
- Supervisor interviews (4): all four independently described the shared inbox as "the
  bottleneck" and none could describe the current routing rule.

## Initial scope thinking

Auto-assemble the document set, put an ordered worklist in front of the adjuster, and make
routing an explicit, auditable rule rather than whoever-notices-first. Automated summary of
the assembled claim file has been requested repeatedly by supervisors but is not committed.

## Non-functional expectations

- Regional data residency: EU claims data does not leave the EU region.
- Decision audit records retained per the group retention standard.
- The workspace is used during regional business hours; nightly maintenance windows are
  acceptable.

## Open questions

- Does routing need to respect adjuster licensing by state, or only by region?
- Is the fax gateway in scope for FY26, or does it stay manual?
