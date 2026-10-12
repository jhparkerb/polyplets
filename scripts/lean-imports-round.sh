#!/bin/bash
# lean-imports-round.sh: repeat { root build; for every module that failed,
# compute its minimal Mathlib imports (scripts/lean-min-imports.sh) and apply
# them (scripts/lean-apply-min-imports.py) } until the build is green or a
# round makes no progress. Log: build/lean-imports-round.log. Serial, gympie.
cd /Users/jasonp/src/polyominoes || exit 1
prev=""
for round in 1 2 3 4 5 6 7 8 9 10 11 12; do
  echo "##### round $round $(date +%T)"
  scripts/lean-root-build.sh > /dev/null
  if tail -1 build/lean-root2.log | grep -q 'EXIT 0'; then echo "GREEN after round $round"; exit 0; fi
  fails=$(sed -n '/Some required targets logged failures:/,/^error: build failed/p' build/lean-root2.log \
            | grep '^- Polyplets\.' | sed 's/^- Polyplets\.//' | tr '\n' ' ')
  echo "failed: $fails"
  if [ -z "$fails" ] || [ "$fails" = "$prev" ]; then echo "NO PROGRESS; stopping"; exit 1; fi
  prev="$fails"
  scripts/lean-min-imports.sh $fails > /dev/null
  python3 scripts/lean-apply-min-imports.py $fails
  python3 scripts/lean-tactic-imports.py $fails
done
echo "ROUND LIMIT"; exit 1
