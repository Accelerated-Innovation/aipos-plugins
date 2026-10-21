# Agent contract: Quote approval assistant

- Agent ID: quote-approval-agent
- Owner: Sales operations lead
- Status: reviewed
- Revision: 2 (2026-10-21)

## 1. Inputs

| Input | Source | Contains personal data | Notes |
|---|---|---|---|
| Quote record | CPQ system | yes | Customer name and contact on the quote header |
| Discount policy | Pricing policy repository | no | Read at the start of each run |

## 2. Tools

| Tool | Purpose | Side effect | Human confirms | Notes |
|---|---|---|---|---|
| read_quote | Load the quote under review | read | no | |
| set_quote_status | Mark the quote approved or returned | write | yes — Deal desk manager | |
| send_approval_email | Tell the account executive the outcome | external send | yes — Deal desk manager | Sent only after the status change is confirmed |

## 3. Outputs

| Output | Recipient | Format | Notes |
|---|---|---|---|
| Approval recommendation | Deal desk manager | Summary with policy citations | |
| Approval email | Account executive | Email | |

## 4. Guardrails

| Rule | Kind | Enforced by |
|---|---|---|
| Never approve a discount above 20% | must never | Policy check in set_quote_status |
| Always cite the policy clause behind a recommendation | must always | Model instruction |

## 5. Escalation

| Trigger | Goes to (human role) | Agent meanwhile | Notes |
|---|---|---|---|
| Requested discount above 20% | Deal desk manager | Stops and holds the quote | |
| Quote references a non-standard contract term | Legal counsel | Stops and holds the quote | |

## 6. Human checkpoints

| Checkpoint | Before | Approver (role) | What they approve |
|---|---|---|---|
| Status change review | set_quote_status | Deal desk manager | The approve or return decision |
| Email review | send_approval_email | Deal desk manager | The email content and recipient |
