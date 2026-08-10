/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalkClosing

-- Machine-generated polynomial literals are longer than the style line
-- limit by nature; see the module docstring for their provenance.
set_option linter.style.longLine false

/-!
# Notary piece K, module 7: the transcribed solution satisfies the system

Campaign *Notary*, piece **K** of `docs/notary-k-plan.md`, wave K-δ. The
closed forms of the six walk unknowns, in pole-free transcription: per
entry a shift `e`, a unit denominator `den*`, and a numerator series
`num* = N₀ + N₁·A + N₂·B + N₃·A·B` with explicit integer-coefficient
polynomials, generated and verified by
`experiments/notary_kdelta_gen.py` / `notary_kdelta_gen3.py`
(`build/notary_kdelta_gen*.log`): the data satisfies
`X^e · den · x = num` against the walk numerically, and the twelve
cleared-row identities below hold *exactly* in the algebra
`ℚ(s)[A,B]/(A²−AA, B²−BB)` — each proof here is the machine-emitted
`linear_combination` certificate over `Kernel.A_sq` and `Kernel.B_sq`,
re-verified as a free-polynomial identity before emission.

The uniqueness module (`DepthOneKernelUnique.lean`) subtracts these rows
from the walk's own cleared rows and kills the difference by the
determinant certificate; no closed-form series is ever *defined* — only
the numerators and denominators, which are honest polynomials.
-/

namespace Polyplets
namespace GapWalk

open PowerSeries

-- ==================== start: int ====================
noncomputable def numJ1Int : PowerSeries ℚ :=
  (189 + (-4149) * X ^ 2 + 16935 * X ^ 4 + 56333 * X ^ 6 + (-3785) * X ^ 8 + (-799355) * X ^ 10 + (-234327) * X ^ 12 + 1035171 * X ^ 14 + (-425412) * X ^ 16) + ((-81) + (-153) * X + 2880 * X ^ 2 + 7008 * X ^ 3 + (-18696) * X ^ 4 + (-49374) * X ^ 5 + (-69285) * X ^ 6 + (-281951) * X ^ 7 + (-219981) * X ^ 8 + (-75049) * X ^ 9 + (-298822) * X ^ 10 + 348686 * X ^ 11 + 13798 * X ^ 12 + (-480) * X ^ 13 + 90475 * X ^ 14 + (-63375) * X ^ 15) * Kernel.A + ((-81) + 153 * X + 2880 * X ^ 2 + (-7008) * X ^ 3 + (-18696) * X ^ 4 + 49374 * X ^ 5 + (-69285) * X ^ 6 + 281951 * X ^ 7 + (-219981) * X ^ 8 + 75049 * X ^ 9 + (-298822) * X ^ 10 + (-348686) * X ^ 11 + 13798 * X ^ 12 + 480 * X ^ 13 + 90475 * X ^ 14 + 63375 * X ^ 15) * Kernel.B + ((-27) + 216 * X ^ 2 + 9453 * X ^ 4 + (-84290) * X ^ 6 + (-227241) * X ^ 8 + 3580 * X ^ 10 + 174743 * X ^ 12 + (-33618) * X ^ 14) * (Kernel.A * Kernel.B)
noncomputable def denJ1Int : PowerSeries ℚ :=
  648 + (-15516) * X ^ 2 + 47646 * X ^ 4 + 544608 * X ^ 6 + 696242 * X ^ 8 + 713300 * X ^ 10 + 15202 * X ^ 12 + (-1190936) * X ^ 14 + 468806 * X ^ 16
-- shift e = 2; den(0) = 648
noncomputable def numJ2Int : PowerSeries ℚ :=
  (792 * X + (-25545) * X ^ 3 + 248571 * X ^ 5 + (-491629) * X ^ 7 + (-2167561) * X ^ 9 + (-1096555) * X ^ 11 + 378337 * X ^ 13 + 841889 * X ^ 15 + (-145899) * X ^ 17) + ((-216) + (-864) * X + 5364 * X ^ 2 + 24957 * X ^ 3 + (-14589) * X ^ 4 + (-166446) * X ^ 5 + (-268738) * X ^ 6 + (-191365) * X ^ 7 + 121905 * X ^ 8 + (-136020) * X ^ 9 + 659544 * X ^ 10 + 461475 * X ^ 11 + (-420475) * X ^ 12 + 958818 * X ^ 13 + (-395530) * X ^ 14 + (-496923) * X ^ 15 + 217503 * X ^ 16) * Kernel.A + (216 + (-864) * X + (-5364) * X ^ 2 + 24957 * X ^ 3 + 14589 * X ^ 4 + (-166446) * X ^ 5 + 268738 * X ^ 6 + (-191365) * X ^ 7 + (-121905) * X ^ 8 + (-136020) * X ^ 9 + (-659544) * X ^ 10 + 461475 * X ^ 11 + 420475 * X ^ 12 + 958818 * X ^ 13 + 395530 * X ^ 14 + (-496923) * X ^ 15 + (-217503) * X ^ 16) * Kernel.B + (504 * X + (-14145) * X ^ 3 + 92958 * X ^ 5 + 47857 * X ^ 7 + 563116 * X ^ 9 + 659025 * X ^ 11 + (-778306) * X ^ 13 + 95615 * X ^ 15) * (Kernel.A * Kernel.B)
noncomputable def denJ2Int : PowerSeries ℚ :=
  1296 + (-31032) * X ^ 2 + 95292 * X ^ 4 + 1089216 * X ^ 6 + 1392484 * X ^ 8 + 1426600 * X ^ 10 + 30404 * X ^ 12 + (-2381872) * X ^ 14 + 937612 * X ^ 16
-- shift e = 3; den(0) = 1296
noncomputable def numJ3Int : PowerSeries ℚ :=
  (189 + (-6948) * X ^ 2 + 79926 * X ^ 4 + (-238888) * X ^ 6 + (-527714) * X ^ 8 + 120306 * X ^ 10 + 1181822 * X ^ 12 + 728916 * X ^ 14 + (-1314063) * X ^ 16 + 334854 * X ^ 18) + ((-81) + (-45) * X + 3231 * X ^ 2 + 2157 * X ^ 3 + (-41610) * X ^ 4 + (-33603) * X ^ 5 + 157248 * X ^ 6 + 140092 * X ^ 7 + 172275 * X ^ 8 + 455832 * X ^ 9 + 372555 * X ^ 10 + (-130775) * X ^ 11 + 249524 * X ^ 12 + (-379739) * X ^ 13 + (-868842) * X ^ 14 + 258478 * X ^ 15 + 301812 * X ^ 16 + (-44109) * X ^ 17) * Kernel.A + ((-81) + 45 * X + 3231 * X ^ 2 + (-2157) * X ^ 3 + (-41610) * X ^ 4 + 33603 * X ^ 5 + 157248 * X ^ 6 + (-140092) * X ^ 7 + 172275 * X ^ 8 + (-455832) * X ^ 9 + 372555 * X ^ 10 + 130775 * X ^ 11 + 249524 * X ^ 12 + 379739 * X ^ 13 + (-868842) * X ^ 14 + (-258478) * X ^ 15 + 301812 * X ^ 16 + 44109 * X ^ 17) * Kernel.B + ((-27) + (-63) * X ^ 2 + 19173 * X ^ 4 + (-180245) * X ^ 6 + (-30645) * X ^ 8 + 17967 * X ^ 10 + (-388097) * X ^ 12 + 352613 * X ^ 14 + (-68692) * X ^ 16) * (Kernel.A * Kernel.B)
noncomputable def denJ3Int : PowerSeries ℚ :=
  648 + (-15516) * X ^ 2 + 47646 * X ^ 4 + 544608 * X ^ 6 + 696242 * X ^ 8 + 713300 * X ^ 10 + 15202 * X ^ 12 + (-1190936) * X ^ 14 + 468806 * X ^ 16
-- shift e = 4; den(0) = 648
noncomputable def numJmInt : PowerSeries ℚ :=
  ((-1170) * X + 35337 * X ^ 3 + (-274944) * X ^ 5 + 27441 * X ^ 7 + 1318864 * X ^ 9 + 1317299 * X ^ 11 + 20152 * X ^ 13 + (-1182573) * X ^ 15 + 326794 * X ^ 17) + (216 + 1026 * X + (-4626) * X ^ 2 + (-27531) * X ^ 3 + 1383 * X ^ 4 + 164895 * X ^ 5 + 281275 * X ^ 6 + 246550 * X ^ 7 + 217168 * X ^ 8 + 355140 * X ^ 9 + (-414760) * X ^ 10 + (-28179) * X ^ 11 + (-4941) * X ^ 12 + (-840677) * X ^ 13 + 247551 * X ^ 14 + 324872 * X ^ 15 + (-84162) * X ^ 16) * Kernel.A + ((-216) + 1026 * X + 4626 * X ^ 2 + (-27531) * X ^ 3 + (-1383) * X ^ 4 + 164895 * X ^ 5 + (-281275) * X ^ 6 + 246550 * X ^ 7 + (-217168) * X ^ 8 + 355140 * X ^ 9 + 414760 * X ^ 10 + (-28179) * X ^ 11 + 4941 * X ^ 12 + (-840677) * X ^ 13 + (-247551) * X ^ 14 + 324872 * X ^ 15 + 84162 * X ^ 16) * Kernel.B + ((-450) * X + 13191 * X ^ 3 + (-97617) * X ^ 5 + 32892 * X ^ 7 + (-233952) * X ^ 9 + (-529893) * X ^ 11 + 481459 * X ^ 13 + (-59358) * X ^ 15) * (Kernel.A * Kernel.B)
noncomputable def denJmInt : PowerSeries ℚ :=
  1296 + (-31032) * X ^ 2 + 95292 * X ^ 4 + 1089216 * X ^ 6 + 1392484 * X ^ 8 + 1426600 * X ^ 10 + 30404 * X ^ 12 + (-2381872) * X ^ 14 + 937612 * X ^ 16
-- shift e = 3; den(0) = 1296
noncomputable def numP2Int : PowerSeries ℚ :=
  (396 * X + (-11508) * X ^ 3 + 98523 * X ^ 5 + (-170854) * X ^ 7 + (-602639) * X ^ 9 + (-444824) * X ^ 11 + 253 * X ^ 13 + 420146 * X ^ 15 + (-108693) * X ^ 17) + ((-108) + (-432) * X + 2682 * X ^ 2 + 12762 * X ^ 3 + (-6099) * X ^ 4 + (-83328) * X ^ 5 + (-141524) * X ^ 6 + (-146120) * X ^ 7 + (-68031) * X ^ 8 + (-148032) * X ^ 9 + 92106 * X ^ 10 + (-12190) * X ^ 11 + (-105593) * X ^ 12 + 375504 * X ^ 13 + 75824 * X ^ 14 + (-132820) * X ^ 15 + (-21801) * X ^ 16) * Kernel.A + (108 + (-432) * X + (-2682) * X ^ 2 + 12762 * X ^ 3 + 6099 * X ^ 4 + (-83328) * X ^ 5 + 141524 * X ^ 6 + (-146120) * X ^ 7 + 68031 * X ^ 8 + (-148032) * X ^ 9 + (-92106) * X ^ 10 + (-12190) * X ^ 11 + 105593 * X ^ 12 + 375504 * X ^ 13 + (-75824) * X ^ 14 + (-132820) * X ^ 15 + 21801 * X ^ 16) * Kernel.B + (252 * X + (-6960) * X ^ 3 + 44895 * X ^ 5 + 31165 * X ^ 7 + 180822 * X ^ 9 + 195038 * X ^ 11 + (-233297) * X ^ 13 + 35893 * X ^ 15) * (Kernel.A * Kernel.B)
noncomputable def denP2Int : PowerSeries ℚ :=
  648 + (-15516) * X ^ 2 + 47646 * X ^ 4 + 544608 * X ^ 6 + 696242 * X ^ 8 + 713300 * X ^ 10 + 15202 * X ^ 12 + (-1190936) * X ^ 14 + 468806 * X ^ 16
-- shift e = 3; den(0) = 648
noncomputable def numP3Int : PowerSeries ℚ :=
  (378 + (-13122) * X ^ 2 + 137973 * X ^ 4 + (-300797) * X ^ 6 + (-1284765) * X ^ 8 + (-1012587) * X ^ 10 + 1001187 * X ^ 12 + 1658789 * X ^ 14 + (-787253) * X ^ 16 + (-65403) * X ^ 18) + ((-162) + (-198) * X + 5868 * X ^ 2 + 6978 * X ^ 3 + (-64977) * X ^ 4 + (-67584) * X ^ 5 + 187857 * X ^ 6 + 69173 * X ^ 7 + 178854 * X ^ 8 + 692213 * X ^ 9 + 457202 * X ^ 10 + 89352 * X ^ 11 + 510103 * X ^ 12 + (-631274) * X ^ 13 + (-1112111) * X ^ 14 + 242241 * X ^ 15 + 306358 * X ^ 16 + 507 * X ^ 17) * Kernel.A + ((-162) + 198 * X + 5868 * X ^ 2 + (-6978) * X ^ 3 + (-64977) * X ^ 4 + 67584 * X ^ 5 + 187857 * X ^ 6 + (-69173) * X ^ 7 + 178854 * X ^ 8 + (-692213) * X ^ 9 + 457202 * X ^ 10 + (-89352) * X ^ 11 + 510103 * X ^ 12 + 631274 * X ^ 13 + (-1112111) * X ^ 14 + (-242241) * X ^ 15 + 306358 * X ^ 16 + (-507) * X ^ 17) * Kernel.B + ((-54) + 72 * X ^ 2 + 31137 * X ^ 4 + (-289996) * X ^ 6 + (-173905) * X ^ 8 + 42568 * X ^ 10 + (-478833) * X ^ 12 + 320956 * X ^ 14 + (-21801) * X ^ 16) * (Kernel.A * Kernel.B)
noncomputable def denP3Int : PowerSeries ℚ :=
  648 + (-15516) * X ^ 2 + 47646 * X ^ 4 + 544608 * X ^ 6 + 696242 * X ^ 8 + 713300 * X ^ 10 + 15202 * X ^ 12 + (-1190936) * X ^ 14 + 468806 * X ^ 16
-- shift e = 4; den(0) = 648
-- E = 4, D:
noncomputable def denAllInt : PowerSeries ℚ :=
  1296 + (-31032) * X ^ 2 + 95292 * X ^ 4 + 1089216 * X ^ 6 + 1392484 * X ^ 8 + 1426600 * X ^ 10 + 30404 * X ^ 12 + (-2381872) * X ^ 14 + 937612 * X ^ 16
-- row 1 (int): sizes cA=486 cB=1
set_option maxHeartbeats 1600000 in
-- the generated identity multiplies degree-40 numerators:
-- `ring` needs headroom beyond the default budget
theorem row1Int :
    ((1 * X ^ 3 + (-5) * X ^ 4) + ((-3) * X ^ 3) * Kernel.A) * (2 * X ^ 2) * numJ1Int +
      ((4 * X ^ 3 + (-6) * X ^ 4) + ((-4) * X ^ 3) * Kernel.A) * (1 * X) * numJ2Int +
      (((-2) * X ^ 3 + 2 * X ^ 4) + (2 * X ^ 3) * Kernel.A) * (2) * numJ3Int +
      ((2 * X ^ 2 + 4 * X ^ 3 + (-10) * X ^ 4) + ((-2) * X ^ 2 + (-6) * X ^ 3) * Kernel.A) * (1 * X) * numJmInt +
      ((2 * X ^ 2 + (-2) * X ^ 3 + (-4) * X ^ 4) + ((-2) * X ^ 2) * Kernel.A) * (2 * X) * numP2Int +
      ((1 * X ^ 3 + (-1) * X ^ 4) + ((-1) * X ^ 3) * Kernel.A) * (2) * numP3Int
      = (1296 * X ^ 4 + (-31032) * X ^ 6 + 95292 * X ^ 8 + 1089216 * X ^ 10 + 1392484 * X ^ 12 + 1426600 * X ^ 14 + 30404 * X ^ 16 + (-2381872) * X ^ 18 + 937612 * X ^ 20) * (((-1) + (-2) * X + 5 * X ^ 2) + (1 + 3 * X) * Kernel.A) := by
  unfold numJ1Int numJ2Int numJ3Int numJmInt numP2Int numP3Int
  linear_combination (((-540) * X ^ 4 + (-2502) * X ^ 5 + 5904 * X ^ 6 + 33222 * X ^ 7 + 12288 * X ^ 8 + 45414 * X ^ 9 + 196948 * X ^ 10 + (-128950) * X ^ 11 + 221828 * X ^ 12 + 770038 * X ^ 13 + (-296008) * X ^ 14 + 526250 * X ^ 15 + (-457640) * X ^ 16 + (-923542) * X ^ 17 + 530660 * X ^ 18 + 345670 * X ^ 19 + (-162240) * X ^ 20) + ((-108) * X ^ 4 + 450 * X ^ 5 + 1458 * X ^ 6 + (-9444) * X ^ 7 + 15654 * X ^ 8 + 16164 * X ^ 9 + (-190444) * X ^ 10 + 342190 * X ^ 11 + (-255384) * X ^ 12 + 501426 * X ^ 13 + 279634 * X ^ 14 + (-72944) * X ^ 15 + (-29730) * X ^ 16 + (-55448) * X ^ 17 + (-24856) * X ^ 18 + (-55770) * X ^ 19) * Kernel.B) * Kernel.A_sq + (0) * Kernel.B_sq

-- row 2 (int): sizes cA=1 cB=485
set_option maxHeartbeats 1600000 in
-- the generated identity multiplies degree-40 numerators:
-- `ring` needs headroom beyond the default budget
theorem row2Int :
    (((-1) * X ^ 3 + (-5) * X ^ 4) + (3 * X ^ 3) * Kernel.B) * (2 * X ^ 2) * numJ1Int +
      (((-4) * X ^ 3 + (-6) * X ^ 4) + (4 * X ^ 3) * Kernel.B) * (1 * X) * numJ2Int +
      ((2 * X ^ 3 + 2 * X ^ 4) + ((-2) * X ^ 3) * Kernel.B) * (2) * numJ3Int +
      ((2 * X ^ 2 + (-4) * X ^ 3 + (-10) * X ^ 4) + ((-2) * X ^ 2 + 6 * X ^ 3) * Kernel.B) * (1 * X) * numJmInt +
      ((2 * X ^ 2 + 2 * X ^ 3 + (-4) * X ^ 4) + ((-2) * X ^ 2) * Kernel.B) * (2 * X) * numP2Int +
      (((-1) * X ^ 3 + (-1) * X ^ 4) + (1 * X ^ 3) * Kernel.B) * (2) * numP3Int
      = (1296 * X ^ 4 + (-31032) * X ^ 6 + 95292 * X ^ 8 + 1089216 * X ^ 10 + 1392484 * X ^ 12 + 1426600 * X ^ 14 + 30404 * X ^ 16 + (-2381872) * X ^ 18 + 937612 * X ^ 20) * (((-1) + 2 * X + 5 * X ^ 2) + (1 + (-3) * X) * Kernel.B) := by
  unfold numJ1Int numJ2Int numJ3Int numJmInt numP2Int numP3Int
  linear_combination (0) * Kernel.A_sq + (((-540) * X ^ 4 + 2502 * X ^ 5 + 5904 * X ^ 6 + (-33222) * X ^ 7 + 12288 * X ^ 8 + (-45414) * X ^ 9 + 196948 * X ^ 10 + 128950 * X ^ 11 + 221828 * X ^ 12 + (-770038) * X ^ 13 + (-296008) * X ^ 14 + (-526250) * X ^ 15 + (-457640) * X ^ 16 + 923542 * X ^ 17 + 530660 * X ^ 18 + (-345670) * X ^ 19 + (-162240) * X ^ 20) + ((-108) * X ^ 4 + (-450) * X ^ 5 + 1458 * X ^ 6 + 9444 * X ^ 7 + 15654 * X ^ 8 + (-16164) * X ^ 9 + (-190444) * X ^ 10 + (-342190) * X ^ 11 + (-255384) * X ^ 12 + (-501426) * X ^ 13 + 279634 * X ^ 14 + 72944 * X ^ 15 + (-29730) * X ^ 16 + 55448 * X ^ 17 + (-24856) * X ^ 18 + 55770 * X ^ 19) * Kernel.A) * Kernel.B_sq

-- row 3 (int): sizes cA=1 cB=1
set_option maxHeartbeats 1600000 in
-- the generated identity multiplies degree-40 numerators:
-- `ring` needs headroom beyond the default budget
theorem row3Int :
    ((1 + (-5) * X ^ 2)) * (2 * X ^ 2) * numJ1Int +
      (((-6) * X ^ 2)) * (1 * X) * numJ2Int +
      ((1 * X ^ 2)) * (2) * numJ3Int +
      (((-8) * X ^ 2)) * (1 * X) * numJmInt +
      (((-2) * X ^ 2)) * (2 * X) * numP2Int +
      (((-1) * X ^ 2)) * (2) * numP3Int
      = (1296 * X ^ 4 + (-31032) * X ^ 6 + 95292 * X ^ 8 + 1089216 * X ^ 10 + 1392484 * X ^ 12 + 1426600 * X ^ 14 + 30404 * X ^ 16 + (-2381872) * X ^ 18 + 937612 * X ^ 20) * ((4)) := by
  unfold numJ1Int numJ2Int numJ3Int numJmInt numP2Int numP3Int
  linear_combination (0) * Kernel.A_sq + (0) * Kernel.B_sq

-- row 4 (int): sizes cA=1 cB=1
set_option maxHeartbeats 1600000 in
-- the generated identity multiplies degree-40 numerators:
-- `ring` needs headroom beyond the default budget
theorem row4Int :
    ((1 + (-8) * X ^ 2)) * (2 * X ^ 2) * numJ1Int +
      ((1 + (-12) * X ^ 2)) * (1 * X) * numJ2Int +
      ((2 * X ^ 2)) * (2) * numJ3Int +
      ((1 + (-19) * X ^ 2)) * (1 * X) * numJmInt +
      (((-4) * X ^ 2)) * (2 * X) * numP2Int +
      (((-1) * X ^ 2)) * (2) * numP3Int
      = (1296 * X ^ 4 + (-31032) * X ^ 6 + 95292 * X ^ 8 + 1089216 * X ^ 10 + 1392484 * X ^ 12 + 1426600 * X ^ 14 + 30404 * X ^ 16 + (-2381872) * X ^ 18 + 937612 * X ^ 20) * ((5)) := by
  unfold numJ1Int numJ2Int numJ3Int numJmInt numP2Int numP3Int
  linear_combination (0) * Kernel.A_sq + (0) * Kernel.B_sq

-- row 5 (int): sizes cA=578 cB=1
set_option maxHeartbeats 1600000 in
-- the generated identity multiplies degree-40 numerators:
-- `ring` needs headroom beyond the default budget
theorem row5Int :
    ((2 * X ^ 2 + (-11) * X ^ 3 + 16 * X ^ 4 + (-1) * X ^ 5 + (-6) * X ^ 6) + ((-2) * X ^ 2 + 9 * X ^ 3 + (-11) * X ^ 4 + 6 * X ^ 5) * Kernel.A) * (2 * X ^ 2) * numJ1Int +
      ((2 * X + (-10) * X ^ 2 + 4 * X ^ 3 + 34 * X ^ 4 + (-26) * X ^ 5 + (-12) * X ^ 6) + ((-2) * X + 8 * X ^ 2 + (-22) * X ^ 4 + 12 * X ^ 5) * Kernel.A) * (1 * X) * numJ2Int +
      ((2 * X ^ 2 + (-8) * X ^ 3 + (-2) * X ^ 4 + 24 * X ^ 5) + ((-2) * X ^ 2 + 6 * X ^ 3 + 4 * X ^ 4 + (-12) * X ^ 5) * Kernel.A) * (2) * numJ3Int +
      (((-4) * X ^ 2 + 16 * X ^ 3 + 4 * X ^ 4 + (-48) * X ^ 5) + (4 * X ^ 2 + (-12) * X ^ 3 + (-8) * X ^ 4 + 24 * X ^ 5) * Kernel.A) * (1 * X) * numJmInt +
      (((-2) * X + 7 * X ^ 2 + 10 * X ^ 3 + (-40) * X ^ 4 + (-4) * X ^ 5 + 21 * X ^ 6) + (2 * X + (-5) * X ^ 2 + (-11) * X ^ 3 + 23 * X ^ 4 + 3 * X ^ 5) * Kernel.A) * (2 * X) * numP2Int +
      (((-1) * X ^ 2 + 4 * X ^ 3 + 1 * X ^ 4 + (-12) * X ^ 5) + (1 * X ^ 2 + (-3) * X ^ 3 + (-2) * X ^ 4 + 6 * X ^ 5) * Kernel.A) * (2) * numP3Int
      = (1296 * X ^ 4 + (-31032) * X ^ 6 + 95292 * X ^ 8 + 1089216 * X ^ 10 + 1392484 * X ^ 12 + 1426600 * X ^ 14 + 30404 * X ^ 16 + (-2381872) * X ^ 18 + 937612 * X ^ 20) * ((2 + (-8) * X + (-2) * X ^ 2 + 24 * X ^ 3) + ((-2) + 6 * X + 4 * X ^ 2 + (-12) * X ^ 3) * Kernel.A) := by
  unfold numJ1Int numJ2Int numJ3Int numJmInt numP2Int numP3Int
  linear_combination ((1080 * X ^ 4 + 2448 * X ^ 5 + (-34836) * X ^ 6 + (-48762) * X ^ 7 + 321654 * X ^ 8 + 87406 * X ^ 9 + (-209622) * X ^ 10 + 1694466 * X ^ 11 + (-6446438) * X ^ 12 + (-1054270) * X ^ 13 + 4414398 * X ^ 14 + (-15519670) * X ^ 15 + 8597834 * X ^ 16 + (-7111406) * X ^ 17 + (-5801834) * X ^ 18 + 17061678 * X ^ 19 + (-413842) * X ^ 20 + (-5519826) * X ^ 21 + 763542 * X ^ 22) + (216 * X ^ 4 + (-1368) * X ^ 5 + (-2172) * X ^ 6 + 34446 * X ^ 7 + (-82992) * X ^ 8 + (-18982) * X ^ 9 + 625792 * X ^ 10 + (-2323386) * X ^ 11 + 5105572 * X ^ 12 + (-6650878) * X ^ 13 + 4556292 * X ^ 14 + 551770 * X ^ 15 + (-5991016) * X ^ 16 + 4730750 * X ^ 17 + 766328 * X ^ 18 + (-3074734) * X ^ 19 + 299676 * X ^ 20 + 921726 * X ^ 21) * Kernel.B) * Kernel.A_sq + (0) * Kernel.B_sq

-- row 6 (int): sizes cA=1 cB=578
set_option maxHeartbeats 1600000 in
-- the generated identity multiplies degree-40 numerators:
-- `ring` needs headroom beyond the default budget
theorem row6Int :
    (((-2) * X ^ 2 + (-11) * X ^ 3 + (-16) * X ^ 4 + (-1) * X ^ 5 + 6 * X ^ 6) + (2 * X ^ 2 + 9 * X ^ 3 + 11 * X ^ 4 + 6 * X ^ 5) * Kernel.B) * (2 * X ^ 2) * numJ1Int +
      ((2 * X + 10 * X ^ 2 + 4 * X ^ 3 + (-34) * X ^ 4 + (-26) * X ^ 5 + 12 * X ^ 6) + ((-2) * X + (-8) * X ^ 2 + 22 * X ^ 4 + 12 * X ^ 5) * Kernel.B) * (1 * X) * numJ2Int +
      (((-2) * X ^ 2 + (-8) * X ^ 3 + 2 * X ^ 4 + 24 * X ^ 5) + (2 * X ^ 2 + 6 * X ^ 3 + (-4) * X ^ 4 + (-12) * X ^ 5) * Kernel.B) * (2) * numJ3Int +
      ((4 * X ^ 2 + 16 * X ^ 3 + (-4) * X ^ 4 + (-48) * X ^ 5) + ((-4) * X ^ 2 + (-12) * X ^ 3 + 8 * X ^ 4 + 24 * X ^ 5) * Kernel.B) * (1 * X) * numJmInt +
      (((-2) * X + (-7) * X ^ 2 + 10 * X ^ 3 + 40 * X ^ 4 + (-4) * X ^ 5 + (-21) * X ^ 6) + (2 * X + 5 * X ^ 2 + (-11) * X ^ 3 + (-23) * X ^ 4 + 3 * X ^ 5) * Kernel.B) * (2 * X) * numP2Int +
      ((1 * X ^ 2 + 4 * X ^ 3 + (-1) * X ^ 4 + (-12) * X ^ 5) + ((-1) * X ^ 2 + (-3) * X ^ 3 + 2 * X ^ 4 + 6 * X ^ 5) * Kernel.B) * (2) * numP3Int
      = (1296 * X ^ 4 + (-31032) * X ^ 6 + 95292 * X ^ 8 + 1089216 * X ^ 10 + 1392484 * X ^ 12 + 1426600 * X ^ 14 + 30404 * X ^ 16 + (-2381872) * X ^ 18 + 937612 * X ^ 20) * (((-2) + (-8) * X + 2 * X ^ 2 + 24 * X ^ 3) + (2 + 6 * X + (-4) * X ^ 2 + (-12) * X ^ 3) * Kernel.B) := by
  unfold numJ1Int numJ2Int numJ3Int numJmInt numP2Int numP3Int
  linear_combination (0) * Kernel.A_sq + (((-1080) * X ^ 4 + 2448 * X ^ 5 + 34836 * X ^ 6 + (-48762) * X ^ 7 + (-321654) * X ^ 8 + 87406 * X ^ 9 + 209622 * X ^ 10 + 1694466 * X ^ 11 + 6446438 * X ^ 12 + (-1054270) * X ^ 13 + (-4414398) * X ^ 14 + (-15519670) * X ^ 15 + (-8597834) * X ^ 16 + (-7111406) * X ^ 17 + 5801834 * X ^ 18 + 17061678 * X ^ 19 + 413842 * X ^ 20 + (-5519826) * X ^ 21 + (-763542) * X ^ 22) + ((-216) * X ^ 4 + (-1368) * X ^ 5 + 2172 * X ^ 6 + 34446 * X ^ 7 + 82992 * X ^ 8 + (-18982) * X ^ 9 + (-625792) * X ^ 10 + (-2323386) * X ^ 11 + (-5105572) * X ^ 12 + (-6650878) * X ^ 13 + (-4556292) * X ^ 14 + 551770 * X ^ 15 + 5991016 * X ^ 16 + 4730750 * X ^ 17 + (-766328) * X ^ 18 + (-3074734) * X ^ 19 + (-299676) * X ^ 20 + 921726 * X ^ 21) * Kernel.A) * Kernel.B_sq

-- ==================== start: bare ====================
noncomputable def numJ1Bare : PowerSeries ℚ :=
  (360 * X + (-4041) * X ^ 3 + (-23532) * X ^ 5 + 138239 * X ^ 7 + (-505472) * X ^ 9 + (-289731) * X ^ 11 + 971140 * X ^ 13 + (-389363) * X ^ 15) + ((-216) + 432 * X + 6444 * X ^ 2 + (-6939) * X ^ 3 + (-29817) * X ^ 4 + 14301 * X ^ 5 + (-248517) * X ^ 6 + (-46746) * X ^ 7 + (-210118) * X ^ 8 + (-139898) * X ^ 9 + 231750 * X ^ 10 + 15413 * X ^ 11 + 133271 * X ^ 12 + 4205 * X ^ 13 + (-81965) * X ^ 14) * Kernel.A + (216 + 432 * X + (-6444) * X ^ 2 + (-6939) * X ^ 3 + 29817 * X ^ 4 + 14301 * X ^ 5 + 248517 * X ^ 6 + (-46746) * X ^ 7 + 210118 * X ^ 8 + (-139898) * X ^ 9 + (-231750) * X ^ 10 + 15413 * X ^ 11 + (-133271) * X ^ 12 + 4205 * X ^ 13 + 81965 * X ^ 14) * Kernel.B + ((-360) * X + 9207 * X ^ 3 + (-43005) * X ^ 5 + (-207374) * X ^ 7 + (-94958) * X ^ 9 + 140247 * X ^ 11 + (-9581) * X ^ 13) * (Kernel.A * Kernel.B)
noncomputable def denJ1Bare : PowerSeries ℚ :=
  1296 + (-31032) * X ^ 2 + 95292 * X ^ 4 + 1089216 * X ^ 6 + 1392484 * X ^ 8 + 1426600 * X ^ 10 + 30404 * X ^ 12 + (-2381872) * X ^ 14 + 937612 * X ^ 16
-- shift e = 1; den(0) = 1296
noncomputable def numJ2Bare : PowerSeries ℚ :=
  (270 + (-7668) * X ^ 2 + 52839 * X ^ 4 + 45834 * X ^ 6 + (-312719) * X ^ 8 + (-248664) * X ^ 10 + 63121 * X ^ 12 + 28866 * X ^ 14 + 19721 * X ^ 16) + ((-162) + (-18) * X + 4428 * X ^ 2 + 1260 * X ^ 3 + (-25758) * X ^ 4 + (-17754) * X ^ 5 + (-56850) * X ^ 6 + 33854 * X ^ 7 + (-97062) * X ^ 8 + 205634 * X ^ 9 + 2328 * X ^ 10 + 8568 * X ^ 11 + 130086 * X ^ 12 + (-207702) * X ^ 13 + (-27922) * X ^ 14 + 72670 * X ^ 15) * Kernel.A + ((-162) + 18 * X + 4428 * X ^ 2 + (-1260) * X ^ 3 + (-25758) * X ^ 4 + 17754 * X ^ 5 + (-56850) * X ^ 6 + (-33854) * X ^ 7 + (-97062) * X ^ 8 + (-205634) * X ^ 9 + 2328 * X ^ 10 + (-8568) * X ^ 11 + 130086 * X ^ 12 + 207702 * X ^ 13 + (-27922) * X ^ 14 + (-72670) * X ^ 15) * Kernel.B + (54 + (-1602) * X ^ 2 + 12555 * X ^ 4 + (-15171) * X ^ 6 + 66792 * X ^ 8 + 154956 * X ^ 10 + (-87721) * X ^ 12 + (-5447) * X ^ 14) * (Kernel.A * Kernel.B)
noncomputable def denJ2Bare : PowerSeries ℚ :=
  648 + (-15516) * X ^ 2 + 47646 * X ^ 4 + 544608 * X ^ 6 + 696242 * X ^ 8 + 713300 * X ^ 10 + 15202 * X ^ 12 + (-1190936) * X ^ 14 + 468806 * X ^ 16
-- shift e = 2; den(0) = 648
noncomputable def numJ3Bare : PowerSeries ℚ :=
  ((-1476) * X + 39969 * X ^ 3 + (-234834) * X ^ 5 + (-486331) * X ^ 7 + (-258698) * X ^ 9 + 1026355 * X ^ 11 + 1060154 * X ^ 13 + (-1392153) * X ^ 15 + 349414 * X ^ 17) + ((-216) + 756 * X + 6048 * X ^ 2 + (-20925) * X ^ 3 + (-39267) * X ^ 4 + 133767 * X ^ 5 + (-61191) * X ^ 6 + 133470 * X ^ 7 + 259222 * X ^ 8 + 300454 * X ^ 9 + (-77394) * X ^ 10 + 255659 * X ^ 11 + (-400675) * X ^ 12 + (-580641) * X ^ 13 + 367417 * X ^ 14 + 167092 * X ^ 15 + (-85176) * X ^ 16) * Kernel.A + (216 + 756 * X + (-6048) * X ^ 2 + (-20925) * X ^ 3 + 39267 * X ^ 4 + 133767 * X ^ 5 + 61191 * X ^ 6 + 133470 * X ^ 7 + (-259222) * X ^ 8 + 300454 * X ^ 9 + 77394 * X ^ 10 + 255659 * X ^ 11 + 400675 * X ^ 12 + (-580641) * X ^ 13 + (-367417) * X ^ 14 + 167092 * X ^ 15 + 85176 * X ^ 16) * Kernel.B + ((-468) * X + 13797 * X ^ 3 + (-101613) * X ^ 5 + (-9368) * X ^ 7 + 144310 * X ^ 9 + (-198239) * X ^ 11 + 29899 * X ^ 13 + 20306 * X ^ 15) * (Kernel.A * Kernel.B)
noncomputable def denJ3Bare : PowerSeries ℚ :=
  1296 + (-31032) * X ^ 2 + 95292 * X ^ 4 + 1089216 * X ^ 6 + 1392484 * X ^ 8 + 1426600 * X ^ 10 + 30404 * X ^ 12 + (-2381872) * X ^ 14 + 937612 * X ^ 16
-- shift e = 3; den(0) = 1296
noncomputable def numJmBare : PowerSeries ℚ :=
  ((-540) + 15192 * X ^ 2 + (-98307) * X ^ 4 + (-146040) * X ^ 6 + 305753 * X ^ 8 + 548296 * X ^ 10 + 59847 * X ^ 12 + (-374376) * X ^ 14 + 99775 * X ^ 16) + (324 + 252 * X + (-8640) * X ^ 2 + (-6732) * X ^ 3 + 49869 * X ^ 4 + 40827 * X ^ 5 + 92937 * X ^ 6 + 71351 * X ^ 7 + 184242 * X ^ 8 + (-219746) * X ^ 9 + 79190 * X ^ 10 + (-125106) * X ^ 11 + (-242851) * X ^ 12 + 257803 * X ^ 13 + 53057 * X ^ 14 + (-73177) * X ^ 15) * Kernel.A + (324 + (-252) * X + (-8640) * X ^ 2 + 6732 * X ^ 3 + 49869 * X ^ 4 + (-40827) * X ^ 5 + 92937 * X ^ 6 + (-71351) * X ^ 7 + 184242 * X ^ 8 + 219746 * X ^ 9 + 79190 * X ^ 10 + 125106 * X ^ 11 + (-242851) * X ^ 12 + (-257803) * X ^ 13 + 53057 * X ^ 14 + 73177 * X ^ 15) * Kernel.B + ((-108) + 3348 * X ^ 2 + (-28683) * X ^ 4 + 42657 * X ^ 6 + (-6142) * X ^ 8 + (-196182) * X ^ 10 + 77589 * X ^ 12 + 9217 * X ^ 14) * (Kernel.A * Kernel.B)
noncomputable def denJmBare : PowerSeries ℚ :=
  1296 + (-31032) * X ^ 2 + 95292 * X ^ 4 + 1089216 * X ^ 6 + 1392484 * X ^ 8 + 1426600 * X ^ 10 + 30404 * X ^ 12 + (-2381872) * X ^ 14 + 937612 * X ^ 16
-- shift e = 2; den(0) = 1296
noncomputable def numP2Bare : PowerSeries ℚ :=
  (540 + (-14418) * X ^ 2 + 85113 * X ^ 4 + 160506 * X ^ 6 + (-116551) * X ^ 8 + (-159214) * X ^ 10 + 98467 * X ^ 12 + (-197306) * X ^ 14 + 91663 * X ^ 16) + ((-324) + (-36) * X + 9018 * X ^ 2 + 2826 * X ^ 3 + (-52821) * X ^ 4 + (-34365) * X ^ 5 + (-129711) * X ^ 6 + 2593 * X ^ 7 + (-168690) * X ^ 8 + 197294 * X ^ 9 + (-103176) * X ^ 10 + 9912 * X ^ 11 + 240331 * X ^ 12 + (-151821) * X ^ 13 + (-47043) * X ^ 14 + 46813 * X ^ 15) * Kernel.A + ((-324) + 36 * X + 9018 * X ^ 2 + (-2826) * X ^ 3 + (-52821) * X ^ 4 + 34365 * X ^ 5 + (-129711) * X ^ 6 + (-2593) * X ^ 7 + (-168690) * X ^ 8 + (-197294) * X ^ 9 + (-103176) * X ^ 10 + (-9912) * X ^ 11 + 240331 * X ^ 12 + 151821 * X ^ 13 + (-47043) * X ^ 14 + (-46813) * X ^ 15) * Kernel.B + (108 + (-3150) * X ^ 2 + 23967 * X ^ 4 + (-20043) * X ^ 6 + 73110 * X ^ 8 + 143656 * X ^ 10 + (-96673) * X ^ 12 + 6513 * X ^ 14) * (Kernel.A * Kernel.B)
noncomputable def denP2Bare : PowerSeries ℚ :=
  1296 + (-31032) * X ^ 2 + 95292 * X ^ 4 + 1089216 * X ^ 6 + 1392484 * X ^ 8 + 1426600 * X ^ 10 + 30404 * X ^ 12 + (-2381872) * X ^ 14 + 937612 * X ^ 16
-- shift e = 2; den(0) = 1296
noncomputable def numP3Bare : PowerSeries ℚ :=
  ((-2412) * X + 64476 * X ^ 3 + (-351291) * X ^ 5 + (-1022348) * X ^ 7 + (-1308143) * X ^ 9 + 753412 * X ^ 11 + 2016383 * X ^ 13 + (-1212116) * X ^ 15 + 140439 * X ^ 17) + ((-432) + 1188 * X + 11844 * X ^ 2 + (-32076) * X ^ 3 + (-68220) * X ^ 4 + 198549 * X ^ 5 + (-205461) * X ^ 6 + 213345 * X ^ 7 + 309447 * X ^ 8 + 422474 * X ^ 9 + 100718 * X ^ 10 + 515458 * X ^ 11 + (-547946) * X ^ 12 + (-752387) * X ^ 13 + 352739 * X ^ 14 + 150761 * X ^ 15 + (-55601) * X ^ 16) * Kernel.A + (432 + 1188 * X + (-11844) * X ^ 2 + (-32076) * X ^ 3 + 68220 * X ^ 4 + 198549 * X ^ 5 + 205461 * X ^ 6 + 213345 * X ^ 7 + (-309447) * X ^ 8 + 422474 * X ^ 9 + (-100718) * X ^ 10 + 515458 * X ^ 11 + 547946 * X ^ 12 + (-752387) * X ^ 13 + (-352739) * X ^ 14 + 150761 * X ^ 15 + 55601 * X ^ 16) * Kernel.B + ((-828) * X + 23544 * X ^ 3 + (-159783) * X ^ 5 + (-120835) * X ^ 7 + 187634 * X ^ 9 + (-160530) * X ^ 11 + (-55631) * X ^ 13 + 46813 * X ^ 15) * (Kernel.A * Kernel.B)
noncomputable def denP3Bare : PowerSeries ℚ :=
  1296 + (-31032) * X ^ 2 + 95292 * X ^ 4 + 1089216 * X ^ 6 + 1392484 * X ^ 8 + 1426600 * X ^ 10 + 30404 * X ^ 12 + (-2381872) * X ^ 14 + 937612 * X ^ 16
-- shift e = 3; den(0) = 1296
-- E = 3, D:
noncomputable def denAllBare : PowerSeries ℚ :=
  1296 + (-31032) * X ^ 2 + 95292 * X ^ 4 + 1089216 * X ^ 6 + 1392484 * X ^ 8 + 1426600 * X ^ 10 + 30404 * X ^ 12 + (-2381872) * X ^ 14 + 937612 * X ^ 16
-- row 1 (bare): sizes cA=445 cB=1
set_option maxHeartbeats 1600000 in
-- the generated identity multiplies degree-40 numerators:
-- `ring` needs headroom beyond the default budget
theorem row1Bare :
    ((1 * X ^ 2 + (-5) * X ^ 3) + ((-3) * X ^ 2) * Kernel.A) * (1 * X ^ 2) * numJ1Bare +
      ((4 * X ^ 2 + (-6) * X ^ 3) + ((-4) * X ^ 2) * Kernel.A) * (2 * X) * numJ2Bare +
      (((-2) * X ^ 2 + 2 * X ^ 3) + (2 * X ^ 2) * Kernel.A) * (1) * numJ3Bare +
      ((2 * X + 4 * X ^ 2 + (-10) * X ^ 3) + ((-2) * X + (-6) * X ^ 2) * Kernel.A) * (1 * X) * numJmBare +
      ((2 * X + (-2) * X ^ 2 + (-4) * X ^ 3) + ((-2) * X) * Kernel.A) * (1 * X) * numP2Bare +
      ((1 * X ^ 2 + (-1) * X ^ 3) + ((-1) * X ^ 2) * Kernel.A) * (1) * numP3Bare
      = (1296 * X ^ 3 + (-31032) * X ^ 5 + 95292 * X ^ 7 + 1089216 * X ^ 9 + 1392484 * X ^ 11 + 1426600 * X ^ 13 + 30404 * X ^ 15 + (-2381872) * X ^ 17 + 937612 * X ^ 19) * (((-1) + 1 * X) + (1) * Kernel.A) := by
  unfold numJ1Bare numJ2Bare numJ3Bare numJmBare numP2Bare numP3Bare
  linear_combination (((-756) * X ^ 3 + (-1224) * X ^ 4 + 13158 * X ^ 5 + 6570 * X ^ 6 + (-16272) * X ^ 7 + 143148 * X ^ 8 + (-240018) * X ^ 9 + 224506 * X ^ 10 + 34620 * X ^ 11 + 96224 * X ^ 12 + 152178 * X ^ 13 + (-261522) * X ^ 14 + (-250680) * X ^ 15 + 85052 * X ^ 16 + 128570 * X ^ 17 + (-11154) * X ^ 18) + (108 * X ^ 3 + (-396) * X ^ 4 + (-2142) * X ^ 5 + 9432 * X ^ 6 + 594 * X ^ 7 + (-45228) * X ^ 8 + 96540 * X ^ 9 + (-133936) * X ^ 10 + 225624 * X ^ 11 + 105052 * X ^ 12 + (-13630) * X ^ 13 + 38168 * X ^ 14 + (-69078) * X ^ 15 + (-31460) * X ^ 16 + 10816 * X ^ 17) * Kernel.B) * Kernel.A_sq + (0) * Kernel.B_sq

-- row 2 (bare): sizes cA=1 cB=446
set_option maxHeartbeats 1600000 in
-- the generated identity multiplies degree-40 numerators:
-- `ring` needs headroom beyond the default budget
theorem row2Bare :
    (((-1) * X ^ 2 + (-5) * X ^ 3) + (3 * X ^ 2) * Kernel.B) * (1 * X ^ 2) * numJ1Bare +
      (((-4) * X ^ 2 + (-6) * X ^ 3) + (4 * X ^ 2) * Kernel.B) * (2 * X) * numJ2Bare +
      ((2 * X ^ 2 + 2 * X ^ 3) + ((-2) * X ^ 2) * Kernel.B) * (1) * numJ3Bare +
      ((2 * X + (-4) * X ^ 2 + (-10) * X ^ 3) + ((-2) * X + 6 * X ^ 2) * Kernel.B) * (1 * X) * numJmBare +
      ((2 * X + 2 * X ^ 2 + (-4) * X ^ 3) + ((-2) * X) * Kernel.B) * (1 * X) * numP2Bare +
      (((-1) * X ^ 2 + (-1) * X ^ 3) + (1 * X ^ 2) * Kernel.B) * (1) * numP3Bare
      = (1296 * X ^ 3 + (-31032) * X ^ 5 + 95292 * X ^ 7 + 1089216 * X ^ 9 + 1392484 * X ^ 11 + 1426600 * X ^ 13 + 30404 * X ^ 15 + (-2381872) * X ^ 17 + 937612 * X ^ 19) * ((1 + 1 * X) + ((-1)) * Kernel.B) := by
  unfold numJ1Bare numJ2Bare numJ3Bare numJmBare numP2Bare numP3Bare
  linear_combination (0) * Kernel.A_sq + ((756 * X ^ 3 + (-1224) * X ^ 4 + (-13158) * X ^ 5 + 6570 * X ^ 6 + 16272 * X ^ 7 + 143148 * X ^ 8 + 240018 * X ^ 9 + 224506 * X ^ 10 + (-34620) * X ^ 11 + 96224 * X ^ 12 + (-152178) * X ^ 13 + (-261522) * X ^ 14 + 250680 * X ^ 15 + 85052 * X ^ 16 + (-128570) * X ^ 17 + (-11154) * X ^ 18) + ((-108) * X ^ 3 + (-396) * X ^ 4 + 2142 * X ^ 5 + 9432 * X ^ 6 + (-594) * X ^ 7 + (-45228) * X ^ 8 + (-96540) * X ^ 9 + (-133936) * X ^ 10 + (-225624) * X ^ 11 + 105052 * X ^ 12 + 13630 * X ^ 13 + 38168 * X ^ 14 + 69078 * X ^ 15 + (-31460) * X ^ 16 + (-10816) * X ^ 17) * Kernel.A) * Kernel.B_sq

-- row 3 (bare): sizes cA=1 cB=1
set_option maxHeartbeats 1600000 in
-- the generated identity multiplies degree-40 numerators:
-- `ring` needs headroom beyond the default budget
theorem row3Bare :
    ((1 + (-5) * X ^ 2)) * (1 * X ^ 2) * numJ1Bare +
      (((-6) * X ^ 2)) * (2 * X) * numJ2Bare +
      ((1 * X ^ 2)) * (1) * numJ3Bare +
      (((-8) * X ^ 2)) * (1 * X) * numJmBare +
      (((-2) * X ^ 2)) * (1 * X) * numP2Bare +
      (((-1) * X ^ 2)) * (1) * numP3Bare
      = (1296 * X ^ 3 + (-31032) * X ^ 5 + 95292 * X ^ 7 + 1089216 * X ^ 9 + 1392484 * X ^ 11 + 1426600 * X ^ 13 + 30404 * X ^ 15 + (-2381872) * X ^ 17 + 937612 * X ^ 19) * ((1)) := by
  unfold numJ1Bare numJ2Bare numJ3Bare numJmBare numP2Bare numP3Bare
  linear_combination (0) * Kernel.A_sq + (0) * Kernel.B_sq

-- row 4 (bare): sizes cA=1 cB=1
set_option maxHeartbeats 1600000 in
-- the generated identity multiplies degree-40 numerators:
-- `ring` needs headroom beyond the default budget
theorem row4Bare :
    ((1 + (-8) * X ^ 2)) * (1 * X ^ 2) * numJ1Bare +
      ((1 + (-12) * X ^ 2)) * (2 * X) * numJ2Bare +
      ((2 * X ^ 2)) * (1) * numJ3Bare +
      ((1 + (-19) * X ^ 2)) * (1 * X) * numJmBare +
      (((-4) * X ^ 2)) * (1 * X) * numP2Bare +
      (((-1) * X ^ 2)) * (1) * numP3Bare
      = (1296 * X ^ 3 + (-31032) * X ^ 5 + 95292 * X ^ 7 + 1089216 * X ^ 9 + 1392484 * X ^ 11 + 1426600 * X ^ 13 + 30404 * X ^ 15 + (-2381872) * X ^ 17 + 937612 * X ^ 19) * ((1)) := by
  unfold numJ1Bare numJ2Bare numJ3Bare numJmBare numP2Bare numP3Bare
  linear_combination (0) * Kernel.A_sq + (0) * Kernel.B_sq

-- row 5 (bare): sizes cA=539 cB=1
set_option maxHeartbeats 1600000 in
-- the generated identity multiplies degree-40 numerators:
-- `ring` needs headroom beyond the default budget
theorem row5Bare :
    ((2 * X + (-11) * X ^ 2 + 16 * X ^ 3 + (-1) * X ^ 4 + (-6) * X ^ 5) + ((-2) * X + 9 * X ^ 2 + (-11) * X ^ 3 + 6 * X ^ 4) * Kernel.A) * (1 * X ^ 2) * numJ1Bare +
      ((2 + (-10) * X + 4 * X ^ 2 + 34 * X ^ 3 + (-26) * X ^ 4 + (-12) * X ^ 5) + ((-2) + 8 * X + (-22) * X ^ 3 + 12 * X ^ 4) * Kernel.A) * (2 * X) * numJ2Bare +
      ((2 * X + (-8) * X ^ 2 + (-2) * X ^ 3 + 24 * X ^ 4) + ((-2) * X + 6 * X ^ 2 + 4 * X ^ 3 + (-12) * X ^ 4) * Kernel.A) * (1) * numJ3Bare +
      (((-4) * X + 16 * X ^ 2 + 4 * X ^ 3 + (-48) * X ^ 4) + (4 * X + (-12) * X ^ 2 + (-8) * X ^ 3 + 24 * X ^ 4) * Kernel.A) * (1 * X) * numJmBare +
      (((-2) + 7 * X + 10 * X ^ 2 + (-40) * X ^ 3 + (-4) * X ^ 4 + 21 * X ^ 5) + (2 + (-5) * X + (-11) * X ^ 2 + 23 * X ^ 3 + 3 * X ^ 4) * Kernel.A) * (1 * X) * numP2Bare +
      (((-1) * X + 4 * X ^ 2 + 1 * X ^ 3 + (-12) * X ^ 4) + (1 * X + (-3) * X ^ 2 + (-2) * X ^ 3 + 6 * X ^ 4) * Kernel.A) * (1) * numP3Bare
      = (1296 * X ^ 3 + (-31032) * X ^ 5 + 95292 * X ^ 7 + 1089216 * X ^ 9 + 1392484 * X ^ 11 + 1426600 * X ^ 13 + 30404 * X ^ 15 + (-2381872) * X ^ 17 + 937612 * X ^ 19) * ((1 + (-5) * X + 5 * X ^ 2 + 3 * X ^ 3) + ((-1) + 4 * X + (-3) * X ^ 2) * Kernel.A) := by
  unfold numJ1Bare numJ2Bare numJ3Bare numJmBare numP2Bare numP3Bare
  linear_combination ((2052 * X ^ 3 + (-5364) * X ^ 4 + (-45234) * X ^ 5 + 135486 * X ^ 6 + 81813 * X ^ 7 + (-521235) * X ^ 8 + 1877046 * X ^ 9 + (-4482150) * X ^ 10 + 3036169 * X ^ 11 + (-1475875) * X ^ 12 + (-2466230) * X ^ 13 + 2478450 * X ^ 14 + (-4353217) * X ^ 15 + 1436975 * X ^ 16 + 4826802 * X ^ 17 + (-1422026) * X ^ 18 + (-1476449) * X ^ 19 + 324987 * X ^ 20) + ((-108) * X ^ 3 + 936 * X ^ 4 + 774 * X ^ 5 + (-25344) * X ^ 6 + 59685 * X ^ 7 + 52140 * X ^ 8 + (-492378) * X ^ 9 + 1534848 * X ^ 10 + (-2897515) * X ^ 11 + 2677056 * X ^ 12 + (-806190) * X ^ 13 + (-2377616) * X ^ 14 + 2063143 * X ^ 15 + (-353812) * X ^ 16 + (-671358) * X ^ 17 + 408720 * X ^ 18 + 89739 * X ^ 19) * Kernel.B) * Kernel.A_sq + (0) * Kernel.B_sq

-- row 6 (bare): sizes cA=1 cB=539
set_option maxHeartbeats 1600000 in
-- the generated identity multiplies degree-40 numerators:
-- `ring` needs headroom beyond the default budget
theorem row6Bare :
    (((-2) * X + (-11) * X ^ 2 + (-16) * X ^ 3 + (-1) * X ^ 4 + 6 * X ^ 5) + (2 * X + 9 * X ^ 2 + 11 * X ^ 3 + 6 * X ^ 4) * Kernel.B) * (1 * X ^ 2) * numJ1Bare +
      ((2 + 10 * X + 4 * X ^ 2 + (-34) * X ^ 3 + (-26) * X ^ 4 + 12 * X ^ 5) + ((-2) + (-8) * X + 22 * X ^ 3 + 12 * X ^ 4) * Kernel.B) * (2 * X) * numJ2Bare +
      (((-2) * X + (-8) * X ^ 2 + 2 * X ^ 3 + 24 * X ^ 4) + (2 * X + 6 * X ^ 2 + (-4) * X ^ 3 + (-12) * X ^ 4) * Kernel.B) * (1) * numJ3Bare +
      ((4 * X + 16 * X ^ 2 + (-4) * X ^ 3 + (-48) * X ^ 4) + ((-4) * X + (-12) * X ^ 2 + 8 * X ^ 3 + 24 * X ^ 4) * Kernel.B) * (1 * X) * numJmBare +
      (((-2) + (-7) * X + 10 * X ^ 2 + 40 * X ^ 3 + (-4) * X ^ 4 + (-21) * X ^ 5) + (2 + 5 * X + (-11) * X ^ 2 + (-23) * X ^ 3 + 3 * X ^ 4) * Kernel.B) * (1 * X) * numP2Bare +
      ((1 * X + 4 * X ^ 2 + (-1) * X ^ 3 + (-12) * X ^ 4) + ((-1) * X + (-3) * X ^ 2 + 2 * X ^ 3 + 6 * X ^ 4) * Kernel.B) * (1) * numP3Bare
      = (1296 * X ^ 3 + (-31032) * X ^ 5 + 95292 * X ^ 7 + 1089216 * X ^ 9 + 1392484 * X ^ 11 + 1426600 * X ^ 13 + 30404 * X ^ 15 + (-2381872) * X ^ 17 + 937612 * X ^ 19) * ((1 + 5 * X + 5 * X ^ 2 + (-3) * X ^ 3) + ((-1) + (-4) * X + (-3) * X ^ 2) * Kernel.B) := by
  unfold numJ1Bare numJ2Bare numJ3Bare numJmBare numP2Bare numP3Bare
  linear_combination (0) * Kernel.A_sq + ((2052 * X ^ 3 + 5364 * X ^ 4 + (-45234) * X ^ 5 + (-135486) * X ^ 6 + 81813 * X ^ 7 + 521235 * X ^ 8 + 1877046 * X ^ 9 + 4482150 * X ^ 10 + 3036169 * X ^ 11 + 1475875 * X ^ 12 + (-2466230) * X ^ 13 + (-2478450) * X ^ 14 + (-4353217) * X ^ 15 + (-1436975) * X ^ 16 + 4826802 * X ^ 17 + 1422026 * X ^ 18 + (-1476449) * X ^ 19 + (-324987) * X ^ 20) + ((-108) * X ^ 3 + (-936) * X ^ 4 + 774 * X ^ 5 + 25344 * X ^ 6 + 59685 * X ^ 7 + (-52140) * X ^ 8 + (-492378) * X ^ 9 + (-1534848) * X ^ 10 + (-2897515) * X ^ 11 + (-2677056) * X ^ 12 + (-806190) * X ^ 13 + 2377616 * X ^ 14 + 2063143 * X ^ 15 + 353812 * X ^ 16 + (-671358) * X ^ 17 + (-408720) * X ^ 18 + 89739 * X ^ 19) * Kernel.A) * Kernel.B_sq


/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only; `native_decide` (`Lean.ofReduceBool`) is
out of bounds here, as is anything beyond the standard three. -/

/--
info: 'Polyplets.GapWalk.row5Int' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms row5Int

/--
info: 'Polyplets.GapWalk.row6Bare' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms row6Bare

end GapWalk
end Polyplets
