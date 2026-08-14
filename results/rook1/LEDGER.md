# Round-1 spawn ledger

Opened 2026-08-13 by the lead, before the first spawn. One row appended at each
spawn, by the dispatcher, at the same keystroke as the spawn.

Why it exists: the triangle campaign's wind-down miscounted its own team three
ways (13 dispatched / 18 listed / 19 real), nine agents ran twelve hours past
their obituary and were found by accident, and agent time — the binding
resource — was accounted nowhere. **The round does not close until this ledger
matches the enumerated census of running agents**, which is what makes a
forgotten row fail closed rather than disappear.

Cap: 8 spawns this round, hard. Re-dispatching an already-spawned agent that has
filed (via SendMessage, onto a queue row) is free and preferred.

| # | id | type | model | spawned | filed | stopped | notes |
|---|---|---|---|---|---|---|---|
| 1 | R1-K | adversary | Fable | 2026-08-13 | — | — | brief-kill pass, wave 1, spawned alone; wave 2 gated on its PASS file |
