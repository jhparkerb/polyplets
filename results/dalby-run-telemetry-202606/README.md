# Telemetry rescued from dalby runs/ before the 2026-07-23 cleanup

Logs, cost profiles, and per-height .out tables copied out of the June
2026 run dirs (two aborted a35 attempts, the completed a35 split run,
holes n16-n19 per-height runs, a21fold) before deleting their ~68GB of
dead checkpoint/frontier state. The .bin/.idx/.tmp/ckpt bulk was torn
mid-run state or checkpoints of completed runs — no resume or forensic
value. Used 2026-07-23 to build the a(37)-a(41) ladder cost model
(docs/engine-record.md): ns_a35_split cost_profile = the H19 frontier
curve; ns_a35 rundir_size.log = the 51.8GB du anchor.
