#!/bin/bash
# lean-min-imports.sh [Module ...]: for each polyplets module (default: all),
# elaborate a copy with `import Mathlib` added and `#min_imports` at the end,
# and record the Mathlib imports it reports in polyplets/build/mi/<Module>.imports.
# Serial; each run loads all of Mathlib (~1 min). Apply with
# scripts/lean-apply-min-imports.py.
cd /Users/jasonp/src/polyominoes/polyplets || exit 1
D=build/mi; mkdir -p $D
if [ $# -gt 0 ]; then mods="$*"; else
  mods=$(cd Polyplets && find . -name '*.lean' | sed 's#^\./##; s#\.lean$##; s#/#.#g' | sort)
fi
for m in $mods; do
  f=Polyplets/$(echo $m | tr . /).lean
  out=$D/$(echo $m | tr . _)
  { grep '^import Polyplets' $f; echo 'import Mathlib'; echo 'import Mathlib.Tactic.MinImports'
    grep -v '^import ' $f; echo; echo '#min_imports'; } > $out.lean
  echo "=== $m $(date +%T)"
  LEAN_NUM_THREADS=1 nice -n 10 ~/.elan/bin/lake env lean $out.lean 2>&1 \
    | grep -E '^(public )?import ' | sed 's/^public //' | sort -u > $out.imports
  cat $out.imports
done
echo DONE
