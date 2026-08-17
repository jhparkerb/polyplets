# Ghost Ship — contamination log

One entry; no C1–C6 event occurred.

1. 2026-08-15 ~18:55 EDT, mid-run: after s11 banked rc=1, the lead
   extracted three envelope status fields (`type`, `subtype`, `is_error`)
   from `usage/session-11.json` via a field-projection script, to
   distinguish timeout/launch-failure from an in-session error. No result
   text, no report content, no counts were read. Ruled non-contaminating:
   same observability class as the rc code (§4 "machine health"). Logged
   because the usage files also embed result text and the projection is
   the only thing separating this read from a C1 event.

Abstention otherwise held: no report content read before HALT; bulletin
never written; stop rule checked only by the launcher's grep; the one
mid-run MANIFEST/telemetry read set (hashes, failures.log, err sizes,
cron.log) is within §4's permitted list. Protocol deviations that are not
contamination (cadence compression, manual launches, NOT_BEFORE parking)
are recorded in DIVERGENCES.md D2 with receipts.
