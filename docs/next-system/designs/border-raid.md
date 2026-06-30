# Border Raid — cross-machine work stealing (ANALYZED, PARKED)

**Goal:** let an idle box steal a key-/column-range of a busy peer's dominant
height, to break the "indivisible monster height" wall-clock floor (a(23): H18 was
7.4 h on dalby, indivisible, while ayr idled ~7 h).

**Verdict: not worth building.** The network topology makes fine-grained
cross-machine stealing bandwidth-infeasible to the cloud box, and the diagonal
injection dissolves most of the motivation. Recorded here with the measurements.

## Why it doesn't work (measured 2026-06-30)

**Topology:** ayr is on the home **gigabit LAN** (192.168.1.201, behind NAT);
**dalby** is a cloud box in a Helsinki DC (public IP). They cannot reach each other
directly — **gympie is the only bridge** (`dalby ↔ internet ↔ gympie ↔ LAN ↔ ayr`).
dalby→ayr would need ssh through gympie as a jump host (possible, ugly).

**Bandwidth is the wall, not routing:** gympie's uplink to dalby is **sub-MB/s**
(~4 Mbit; 10 MB wouldn't transfer promptly). The column sweep's merge is
**all-to-all** (memory: merge cannot be partition-preserved), so distributing one
height across machines means shipping ~0.4–1 GB of map output **per column** to the
merge host. Over a 4 Mbit uplink that is minutes-to-hours per column — it costs more
than the work it offloads. No ssh config fixes this.

**The LAN leg (gympie↔ayr) IS fast enough**, but: (a) the cheap implementation
there is a **shared NFS mount + remote `map_worker` spawn** (the existing pool spans
both boxes over one run dir — no transport code), not an RPC layer; (b) ROI is
modest — gympie adds only ~10 cores to ayr's 30; (c) see next section.

## Why the motivation largely evaporated

The k≤7 diagonal injection (wired + validated against the a(23) swept rows) replaces
the tall heights — exactly the indivisible monsters — with closed forms. a(23) peak
frontiers per swept height:

```
H18=11.1M  H17=4.7M  H16=1.9M  H15=0.7M  H14=0.3M   (~2.4× per height up)
```

With k≤7 injected, a(25)'s peak *swept* height is **H=17 (~½ of H18)**; push the
injection further and no single height dominates. So **static height-balancing +
injection** captures nearly all the wall-clock that cross-machine stealing would
have — the balanced a(23) split (`dalby={H1–15,H18}`, `ayr={H16,H17}`) already
recovered ~18% in analysis, with zero cross-machine traffic.

## Decision

PARK. For multi-box runs use: (1) k≤7 injection; (2) static balanced split from a
cost model; (3) dalby (80 cores, big RAM) as the whole-height worker for the single
largest height. Revisit only the **LAN-NFS** variant (gympie+ayr) if a(25) profiling
shows one height dominating the home-cluster wall — and even then, NFS + remote
spawn, not a bespoke transport.
