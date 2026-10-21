# Quote approval agent — team notes (supplied for this contract)

[SYNTHETIC] Notes from the 2026-10-20 design session. Owner: Sales operations lead.

- **What it reads:** the quote record from the CPQ system (includes customer name and contact),
  and the discount policy document.
- **Tools:** `read_quote` (read only). `set_quote_status` changes the quote to approved or
  returned in CPQ — the deal desk manager confirms every status change. `send_approval_email`
  emails the account executive — the deal desk manager reviews each email before it goes.
- **What it produces:** an approval recommendation for the deal desk manager, citing policy
  clauses; the approval email to the account executive.
- **Rules:** never approve a discount above 20% (enforced by a policy check inside
  `set_quote_status`); always cite the policy clause behind a recommendation (model instruction
  only).
- **Escalation:** a requested discount above 20% goes to the deal desk manager and the agent
  holds the quote; a non-standard contract term goes to legal counsel and the agent holds the
  quote.
- **Checkpoints:** deal desk manager approves before each status change and before each email.
