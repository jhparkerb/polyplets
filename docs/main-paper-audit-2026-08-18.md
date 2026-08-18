> **NOTE: authored by Claude at jasonp's direction, 2026-08-18.** An audit of
> `paper/technical-report.tex`, in the style of the L-paper passes. **Nothing in
> the paper was changed.** It is jasonp's prose under the P disclosure and stays
> read-only to the machine; everything below is a finding for him to accept,
> reject or reword.

# Audit of the main paper

Three passes, the same three run over the L papers: the numeric verifier, a
re-derivation of the arguments, and a literature-priority check. Plus the
question he asked alongside it — whether the published work we collided with can
be turned to our advantage — answered in §4.

## 1. Mechanical: clean

`paper/verify_technical_report.py`: **781 checks, 0 failures.** Every table in
the paper — a(n) through 40, the T(n,H) block, one-sided/free/bilateral/
asymmetric, non-polyominoes, the hole triangle — parses and matches banked data.

Spot checks the verifier does not do, all of which hold:

- The free count approaches a(n)/8 and the one-sided a(n)/4: at n = 32,
  free/a = 0.125000 to six places.
- Hole rows sum to a(n) (n = 4: 109 + 1 = 110).
- `T(n,n-1) = (25n-45)·3^(n-4)` reproduces banked cells: T(5,4) = 240,
  T(6,5) = 945.
- The two enclosure claims in §Definitions are right, and sharp: a 1-cell hole
  needs its four orthogonal neighbours, which are king-connected to each other,
  so 4 cells suffice; and two 1-cell holes at (0,0) and (1,1) are enclosed by
  exactly 6 cells — matching the hole table's `n=6, k=2` entry of 2.
- "Terms 1–18 match A006770" is correct as of the entry we imported: the
  verbatim OEIS text banked on 2026-06-19 ends at a(18). (Our working copy of
  `oeis/A006770.txt` shows a(19) because that is *our* staged addition.)

## 2. Arguments: two checked, one loose sentence, one understatement

### 2.1 The `T(n,n-1)` derivation — holds

The domino/split case analysis gives `16(n-3)` and `(4·1 + 1·5)(n-3) = 9(n-3)`
interior placements, so `25(n-3)·3^(n-4)`; the boundary term
`2·5·3^(n-3) = 30·3^(n-4)`; and `(25(n-3) + 30) = 25n - 45`. The arithmetic is
right at every step and the result matches banked cells. The `25` here is the
same constant that appears as the pair weight in the companion L1 proof, which
is a real cross-check and not a coincidence.

### 2.2 "P_k can be fixed after computing the 3k-th row" — right, and it looks wrong

`P_k` has degree `k`, so a blind fit needs `k+1` in-onset values, which live at
rows `2k+1 … 3k+1` — row `3k+1`, not `3k`. The paper's figure is correct
because the previous sentence supplies the leading coefficient `25^k/k!`: with
that known, `k` values suffice and row `3k` is enough. Worth keeping the two
sentences adjacent, since separating them makes the claim look off by one.

(In fact the repository can do better: L1's Corollary "two constants per level"
shows any **two** in-onset values pin a level once the levels below it are
known. That is a stronger statement than the paper needs and is his to use or
ignore.)

### 2.3 "λ ≈ 7.11, checkable from Table 1" — the one loose claim

A reader who checks gets neither number:

    a(40)^(1/40)      = 6.2208      (this is the Fekete floor, not lambda)
    a(40)/a(39)       = 6.9352
    a(39)/a(38)       = 6.9308

7.11 comes from extrapolating the ratio sequence, not from reading the table:
one Richardson-style step on the last two ratios gives 7.112. As written the
sentence invites a check that fails. The honest version names the operation —
"the ratios a(n)/a(n-1) rise through 6.9352 at n = 40 and extrapolate to
λ ≈ 7.11" — and it costs one clause.

### 2.4 The provenance sentence understates the work, in both directions

Abstract: *"Terms for 23 ≤ n ≤ 35 were computed twice on different machines;
a(36)–a(40) were computed once."*

What the run records actually show:

- **Every run recomputes the whole triangle up to its own n.** `ns_a37`
  reproduces a(36); `ns_a38` reproduces a(36) and a(37); `ns_a39` and `ns_a40`
  reproduce every earlier term. Checked directly this pass, all agreeing.
- So **a(36) was computed five times, a(37) four, a(38) three, a(39) twice.
  Only a(40) was computed once.** "a(36)–a(40) were computed once" gives away
  four terms' worth of corroboration.
- The recomputation is not a replay of stored numbers: a(28)'s run was
  ayr-solo and re-swept H3–H15 on x86, while a(24) had been produced on dalby
  (aarch64). The sweep bands genuinely re-run on the other machine and ISA.
- But **"twice" in the strong sense is not what happened for 23–35 either.**
  Those terms were each computed once by their own run and then recomputed by
  later runs — always with the *same engine and the same connectivity rule*,
  and with the high-H bands supplied by closed forms rather than swept. The
  independence is hardware and ISA, not method.

The OEIS entry's own comment is careful about this ("computed by the same
column/kink-carry transfer-matrix engine"); the paper's abstract is looser than
the OEIS text it will be read alongside. The accurate sentence is both stronger
and more modest than the current one: *every term through a(39) is recomputed by
at least one later run, across two machines and two instruction sets, by one
engine and one connectivity rule; a(40) alone was computed once.*

## 3. Literature-priority: nothing new to report, one gap

The paper's claims are the new terms, the T(n,H) triangle, the symmetry
companions, the hole stratification and a growth estimate. The N1–N6 sweeps
cover the diagonal law and the growth bounds; the enumeration itself collides
with nothing by construction. Mertens (1990) and Redelmeier are already the
right prior art and are cited in the OEIS entry.

The one gap: **§Reproducibility is empty**, and it is the section a stranger
reads first under a repo release. See `docs/acceptance-queue.md` items 2–4.

## 4. Turning the collisions into support

The three collisions found this week are not only losses. Each is a published
result that our machinery reproduced independently, which is exactly the shape
of an external validation — and P1's validation chapter is where they belong.

**4.1 The cut-count rule is the Potts spin representation, and that makes the
second source *more* defensible, not less.** The engine that produced a(23)–a(40)
tracks connectivity through frontier signatures, in the Jensen tradition. The
Motley/B1 second source evaluates `q^{components}` by colouring instead — which
is the Fortuin–Kasteleyn/Potts spin representation. These are the two classical
representations of one partition function, and their independence is a
structural fact from the literature rather than a claim about our own code. A
referee asking "why should two of your programs disagree if one is wrong?" now
gets a citation instead of an assurance. This is the single most useful
conversion available, and it costs one paragraph in the validation chapter.

**4.2 The perimeter-defect identity is published, so the prune is not ours to
justify.** `k = 2c + t` is Asinowski–Barequet–Zheng's `k = e + 2f`. Anywhere the
project's enumerations lean on that identity for exactness, the justification
can be a citation. Their framework — classify patterns, get a rational
generating function per defect with cyclotomic denominator — is also the most
promising route to *proving* the king perimeter results that are currently
interpolated.

**4.3 Reproducing a published universal law is a test the pipeline passed.**
Richard's rectangles area law for convex polygons, rederived unawares from our
kernel, means our king machinery landed on a known universality class. Likewise
the control arm reproducing Klarner–Rivest/Bender constants to certified
precision, and Bousquet-Mélou–Fédou's solved square case standing behind our
king kernel. Every one of those is an external anchor: independent of us, known
in advance, and hit exactly.

**4.4 The suggestion, concretely.** A short subsection of the validation
chapter — "external anchors" — listing what the machinery reproduces that it did
not produce: a(1)–a(18) against OEIS, Bender's and Klarner–Rivest's constants at
certified precision, Richard's limit law, and the FK/Potts identity behind the
second source. Four items, all checkable by the reader, none of them ours. That
is a stronger opening to a validation chapter than any internal consistency
check, because the reader does not have to trust us for any of it.

## 5. Nothing was changed

`paper/technical-report.tex` is untouched. §2.3 and §2.4 are the two items that
would change what the paper claims, and both are his call.
