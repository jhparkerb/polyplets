# The accepted shape: every claim carries an in-tree, non-empty path

The gate must accept this file. Three legitimate shapes appear below: a table
row with a repo-relative receipt, a `status:` line with one, and a historical
mention carrying the `status-quote:` waiver token.

| instrument | what it establishes | status | receipt |
|---|---|---|---|
| fixture probe | the gate accepts a real path | **RUN** | `tests/fixtures/receipts/example.log` |
| not yet built | nothing | **WRITTEN, UNRUN** | plan only |
| in flight | nothing yet | **IN FLIGHT** | waiter attached |

status: PASSED — `tests/fixtures/receipts/example.log`

| note | text | status | receipt |
|---|---|---|---|
| history | status-quote: round 3 reported its ladder gate GREEN with no log | — | — |
