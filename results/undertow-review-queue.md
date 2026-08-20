# Undertow review — the queue

Append-only. Row format:

    | id | lane | status | rank | what |

`status` is OPEN / CLOSED / DROPPED. A lane that closes a candidate files at
least two successor rows, different in kind, not parameter tweaks. Half-formed
rows are wanted. Cross-lane rows are wanted. Pruned near-misses go here, never
into a silent cap.

Each lane's FIRST action is to append its own findings list, timestamped,
before reading any other lane's output.

| id | lane | status | rank | what |
|---|---|---|---|---|
