# Next-system on-disk layout — A SKETCH, NOT A SPEC

> ⚠️ **NOT PRESCRIPTIVE.** This is a *putative* layout drawn to make the design tangible —
> to see roughly how the decisions in [`docs/frontier/NEXT-SYSTEM.md`](frontier/NEXT-SYSTEM.md)
> land as files, components, and rough sizes. It is **illustrative, not binding**: file
> boundaries will move, names will change, the LOC figures are estimates (±30%, and the Go
> side is the softest since there's no current Go to anchor against). Nothing here is a
> commitment. The real layout is whatever the build actually converges to. Treat it as a
> conversation aid, not a checklist.

Embodies: small trusted C++ core behind the `libenum` seam · Go owning all
orchestration/verification · static classifier + static column decomposition, templated on
counter width · map-reduce *shape* as a hand-rolled external merge-sort (no framework) ·
fitness tests as first-class · the published dataset as a verifiable artifact.

```
polyplet/
├── core/                       # C++ libenum — the single-source-of-truth enumeration core
│   ├── libenum.h               #   PUBLIC API (the fitness-function seam): map_shard(), merge()   ~30
│   ├── signature.{h,cpp}       #   boundary connectivity sig: canon form, SORT KEY, serialize    ~140
│   ├── transition.{h,cpp}      #   column king-closure map (per-state successors)                 ~140
│   ├── classifier.h            #   reduce op + completion test (triangle) — TEMPLATED             ~70
│   ├── counter.h               #   u64 / u128 counter type — TEMPLATED                            ~40
│   ├── run.h                   #   state (sig+count_vec) (de)serialize + sort-key contract        ~80
│   └── mapreduce.{h,cpp}       #   map_shard() + merge(): the external-sort core algorithms       ~180
│                               #   ── core subtotal ~680  (today's binary compiles ~2,840) ──
├── worker/                     # C++ thin process wrappers — link core, do the file I/O
│   ├── map_worker.cpp          #   read run → core.map_shard → write run + exit-accounting         ~90
│   └── merge_worker.cpp        #   read runs → core.merge → write run + exit-accounting            ~70
├── orchestrator/               # Go — owns ALL liveness/safety/scheduling (replaces the bash)
│   ├── cmd/orchestrate/main.go #   entry: parse job, drive the column map→merge DAG              ~120
│   ├── scheduler.go            #   work-stealing queue, shard assignment, the run DAG            ~400
│   ├── governor.go             #   budget guards, graceful stop, restart-from-checkpoint        ~250
│   ├── store.go                #   run-storage interface (local NVMe v1 → dist/cloud later)     ~200
│   ├── checkpoint.go           #   wall-clock cadence, resume, accounting fold-in               ~180
│   ├── telemetry.go            #   collect worker accounting                                    ~150
│   ├── manifest.go             #   per-a(n) provenance manifest                                 ~120
│   └── *_test.go               #   unit tests                                                   ~400
│                               #   ── orchestrator subtotal ~1,820 ──
├── verify/                     # Go — independent verifier (separate tool, reads published data)
│   ├── cmd/verify/main.go      #   load published dataset, run checks                           ~100
│   ├── consistency.go          #   row-sum identity · mod-p CRT · growth-ratio smoothness       ~300
│   ├── spotcheck.go            #   re-run sampled shards, compare to published runs             ~150
│   └── *_test.go               #                                                                ~150
│                               #   ── verify subtotal ~700 ──
├── test/                       # cross-cutting gates + architecture fitness functions
│   ├── gate_regression.cpp     #   small-n byte-identical to known a(n)/T(n,H)                  ~120
│   ├── gate_fold.cpp           #   fold == unfold                                                ~60
│   ├── arch_fitness.go         #   BOUNDARY tests: core imports no I/O; orch never reaches      ~150
│   │                           #     into core internals; classifier/counter only via templates
│   └── fixtures/
│       ├── b006770.txt         #   known a(n) — the regression oracle (data)
│       ├── triangle_known.txt  #   known T(n,H) low rows (data)
│       └── run_n14.bin         #   a small captured sorted run, for worker/merge tests (data)
├── data/                       # the PUBLISHED, verifiable artifact (the validation strategy)
│   ├── triangle/               #   T(n,H) results per n
│   ├── manifests/              #   per-a(n) provenance (cores·sec, peak RSS, spill bytes, rev…)
│   └── residues/               #   mod-p residues, for anyone's independent CRT check
├── docs/
│   ├── NEXT-SYSTEM.md          #   the design record
│   ├── correctness.md          #   the transfer-matrix bijection proof (the algorithm-proof layer)
│   └── formats.md              #   on-disk run / checkpoint / triangle format spec
├── Makefile                    #   C++ build + rev-stamping (build/<rev>/{map,merge}_worker)
├── go.mod
└── README.md
```

## Rough sizes, against today
| component | lang | LOC | replaces |
|---|---|---:|---|
| **core (libenum)** | C++ | **~680** | today's ~2,840-line binary (5 sweep forks → 1 templated classifier) |
| workers | C++ | ~160 | — (new, thin) |
| orchestrator | Go | ~1,820 | ~880 bash drivers + the Python orchestration/observability |
| verifier | Go | ~700 | scattered Python gates/analysis |
| gates + fitness | C++/Go | ~330 | `gate_tma.py` et al. |
| **total code** | | **~3,690** | vs **~13,100** today (C++ 6.4k + Python 5.8k + shell 0.9k) |

## Notes
- **v1 is a strict subset.** A working single-box a(24) system is `core/` + `worker/` + a *simple*
  orchestrator (scheduler + governor + checkpoint, ~800 Go, no store abstraction / distribution /
  full manifest) + the regression/fold gates + the verifier's consistency checks — **~2,000 LOC end
  to end.** `store.go`'s pluggable backend, distribution, and `spotcheck.go` grow later. "Start small,
  scale by component" made concrete.
- **The trusted surface is `core/libenum.h` + its ~680 lines.** Everything a wrong count could hide in
  lives there; it fits in context whole; `arch_fitness.go` mechanically forbids anything else from
  reaching past the `libenum.h` seam — boundary enforced, not hoped for.
- **Deliberately absent:** no Python, no GF-recovery/series-analysis tree. If symbolic GF work is ever
  revived it's an isolated CAS side-tool *outside* this layout, not a row in this table.
