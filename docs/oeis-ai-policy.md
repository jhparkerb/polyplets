# OEIS AI policy and precedents — research notes for the submission

2026-07-05, web research (two passes: policy/accepted cases, then a mine
of the public rejection pipeline). Informs how we submit the six
sequences. Submission remains gated on jasonp's viva (local process).

## The policy

- Oct 2023: blanket ban ("Use of AI for OEIS Submissions is Forbidden"),
  approved two days after A361990's ChatGPT-credit forced the issue.
- **16 Apr 2026: softened to accountability**
  (https://oeis.org/wiki/Use_of_AI_for_OEIS_Submissions_is_Forbidden —
  old title redirects): "All sequences in the OEIS must have a human
  author... That author is responsible for the correctness of any
  content produced by a large language model."
- Still prohibited: AI text in pink-box replies; AI as author/co-author;
  AI-generated full comment text; "any AI-generated program that you do
  not understand how it works or its operational limits"; bulk/serial AI
  submissions. AI-written programs the submitter understands are
  implicitly tolerated.
- "A sequence you asked an AI to generate" is the #1 real example on
  https://oeis.org/wiki/Examples_of_what_not_to_submit

## Accepted precedents

- A361990 (Israel, 2023): ChatGPT-suggested idea, human Maple + independent
  Python; Sloane extension: "fully checked by the OEIS Editors."
- A384729 (Kleinwaks, Jun 2025, post-policy): "all code was written by
  the LLM, though with significant prompting" — disclosed in-entry,
  human-defended bound argument. Accepted.

## Rejected precedents (post-Apr-2026, mined from keyword:recycled histories)

Rejections are public: recycled drafts keep pink-box history at
oeis.org/history?seq=Axxxxxx (pool churns ~monthly, so only recent cases
are discoverable).

- A396919: LLM artifacts (hidden zero-width chars), formula errors,
  obsequious LLM-styled replies -> Irvine: "Rejected, NFO, violation of
  AI-policies" (Jul 3 2026).
- A396591: APPROVED, then reverted after Arndt: "this is clearly
  AI-generated and should not have been accepted." Post-acceptance
  reversion exists.
- A396876: author dodged "How much of this is AI-generated?" -> Irvine:
  refusing to answer "makes me increasingly suspicious." Withdrawn.
- A396748: AI text in pink boxes alone -> "please recycle."
- A394641: merely AI-SOUNDING prose (translation tool) tainted a
  borderline entry into rejection.
- A396719 (the control): "Did you use AI to generate this sequence?"
  answered precisely ("AI was used solely as a coding assistant...; all
  mathematical content was derived and verified by myself") — three
  sibling sequences from the same work were APPROVED; the one rejection
  was table format, explicitly not AI.

## Implications adopted for our batch

1. "How much is AI-generated?" is now a routine editor probe (Arndt,
   Yuen) — have the one-paragraph answer ready, jasonp's own words,
   Chen-Wei-Shi-shaped: exactly what AI did + exactly what he verified.
2. %C comment text must be jasonp-authored (rewrite pass over the staged
   oeis/A*.txt comments; Claude checks meaning against tier definitions
   only). AI-sounding prose is itself a live rejection trigger.
3. Pink-box replies: jasonp's alone, always.
4. No program text in the entries (b-files + repo/report links only), so
   the program-understanding clause binds through the correctness
   warranty — addressed by the viva process.
5. Six related extensions in one batch is normal practice, not "bulk".
