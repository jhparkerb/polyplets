DIRECTION: adjudicate s13's PENDING r=7 registered prediction (its receipt was never written — run died), then close out the loop with a capstone synthesis of the 14-session edifice and one push on the subleading (nu-law) order.
SHAPE: adjudicate, verify, synthesize

Plan: (1) rerun experiments/s13_tau_profiles.py at MAXR=7 NUCAP=250, king
mode, both primes, with S13_OUT_SUFFIX=_r7, and compare the reconstructed
inner profiles chi_7/phi_7/psi00_7 and orders against the registered
prediction out_s13_r7_prediction.txt (written by s13 before any r=7 data
existed). (2) Being the final session, write results/FINAL-SYNTHESIS.md:
the complete claim graph — what is established about the area statistic on
convex king animals, with receipts and rigor status — so the corpus is
usable without reading 14 reports. (3) With remaining time, spot-verify
load-bearing early claims by independent recomputation and, if compute
allows, probe the next Laurent order (s13 OPEN 2) where nu_Delta(B_r) =
ceil(r/2) lives.

## CARRY   (hard cap 25 lines -- successors must read this)
(filled as results land)

## LOG

Read all 13 CARRY sections. s13 claim 6 (r=7 registered prediction) was
PENDING: out_s13_r7_prediction.txt existed (written before any r=7
chassis data), but out_s13_tau_profiles_r7.json was absent at session
start — out_s13_tau_run_r7.log looked truncated mid-poly. I launched a
king-only rerun (PID 2579059)... and then s13's ORIGINAL background run
(PID 2578223, still alive across the session boundary) completed at
20:31 and wrote the full both-modes receipts. I killed my now-redundant
rerun by its exact captured PID (it shared S13_OUT_SUFFIX=_r7 and would
have overwritten the complete receipt with a king-only one). Lesson
logged for the file: a "missing" receipt can be a run still in flight —
check the PID file (s13_pids.txt) before rerunning.

ADJUDICATION r=7 (new tool experiments/s14_adjudicate_profiles.py —
recomputes the s13 z-form recursion exactly, parses the registered
prediction file, and checks chassis inner profiles for ALL THREE phases
M00/M10/M11 plus the order laws ord(M00)=-(4r+2), ord(M10)=-(4r+4),
ord(M11)=-(4r+6); s13's own C4 checked only M10/M11 and no orders):
  * sanity on banked r<=6 receipts: 84 identities ALL PASS
    (out_s13_tau_profiles.json, both modes, both primes);
  * r=7: prediction file MATCHES recursion (chi_7 8 coeffs, phi_7 15
    coeffs, c_7=99225/64=(7!)^2/2^14, orders -32/-34); chassis receipts
    MATCH at all 96 identities (r<=7, 3 phases, 2 modes, 2 primes).
  => s13 claim 6 CONFIRMED. Receipt: out_s14_r7_adjudication.txt.

EXTENSION r=8: registered my own prediction out_s14_r8_prediction.txt
(chi_8, phi_8, psi00_8=-(16)!/(4 z^17), c_8=99225/2=(8!)^2/2^15, orders
-36/-38) BEFORE any r=8 chassis data existed, then launched
s13_tau_profiles.py MAXR=8 NUCAP=300 king (PID 2579265,
out_s14_tau_run_r8.log). Adjudication below when it lands.

VALUE LAW at r=7: the fresh r7 receipt's val@s=1 records (king, both
primes) show lead M11^(r)(1) = c_r at Laurent order -(4r+4) for every
r=0..7 (1/128, 1/256, 1/128, 9/256, 9/32, 225/64, 2025/32, 99225/64 =
exactly (r!)^2/2^(r+7)) — s12's "M11 carries c_r" localization now
visible through r=7 in raw chassis data (out_s13_tau_profiles_r7.txt,
lines 58..709).

FOUNDATION RE-AUDIT (cheap, final-session due diligence): re-expanded
the s01 univariate closed form F(t) = [t^2(2-10t+14t^2-5t^3-4t^4) -
t^3(1+2t)^2 sqrt(1-4t)]/((2+t)(1-4t)^2) with a FRESH exact-Fraction
series implementation (sqrt via coefficient recursion, nothing shared
with the s01 fitter or DP): all 200 terms of king_semiperim_200.txt
match, zero non-integer coefficients. Receipt:
out_s14_foundation_recheck.txt.

CAPSTONE: wrote results/FINAL-SYNTHESIS.md — the complete tractability
map of the 14-session loop (layers: box/semiperimeter algebraic-proven;
area q-series + certified asymptotics + non-D-finiteness status; moment
hierarchy + limit law + local transfer; new sequences/constants; rigor
ledger; dead ends). Entry point for any future reader of this corpus.
