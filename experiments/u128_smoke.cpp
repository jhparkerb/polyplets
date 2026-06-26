// u128_smoke.cpp -- frontier idea 09 dead-on-arrival smoke (docs/frontier/09-u128-counters.md).
// Does __uint128_t give CORRECT, hardware-backed double-width arithmetic on THIS ISA? Tests the
// two ops a CRT-free exact counter needs in the hot loop: add-with-carry (counter increment
// across the 2^64 boundary) and the 64x64->128 widening multiply. If either is wrong or won't
// compile on an ISA we count on (arm64 gympie / x86-64 ayr), 09 is dead before any benchmark.
// Build: g++ -std=c++20 -O2 -o build/u128_smoke experiments/u128_smoke.cpp   (run: ./build/u128_smoke)
#include <cstdio>
#include <cstdint>
#include <cinttypes>
using u128 = __uint128_t;

static void show(const char* tag, u128 v){
    uint64_t hi = (uint64_t)(v >> 64), lo = (uint64_t)v;        // no printf conv for 128-bit
    printf("  %-22s hi=0x%016" PRIx64 " lo=0x%016" PRIx64 "\n", tag, hi, lo);
}

int main(){
    int fail = 0;

    // 1) widening multiply: (2^64-1)^2 = 2^128 - 2^65 + 1  ==  hi=0xFFFFFFFFFFFFFFFE, lo=1
    u128 m = (u128)(uint64_t)-1 * (u128)(uint64_t)-1;
    u128 m_expect = ((u128)0xFFFFFFFFFFFFFFFEULL << 64) | 1u;
    printf("widening mul (2^64-1)^2:\n"); show("got", m); show("expect", m_expect);
    if (m != m_expect){ printf("  ** FAIL widening mul\n"); fail++; }

    // 2) add-with-carry across 2^64: (2^64-1) + 1 = 2^64  ==  hi=1, lo=0
    u128 c = (u128)(uint64_t)-1; c += 1;
    if (c != ((u128)1 << 64)){ printf("** FAIL carry add\n"); fail++; }

    // 3) hot-loop accumulate past 2^64: sum_{i<N} step, step ~ 0.4*2^64, N=8 -> ~3.2*2^64 (>u64).
    //    Mirrors a counter that overflows u64 (a(26)~1e20>2^64) but is exact in u128.
    const u128 step = ((u128)7378697629483820646ULL);        // ~0.4 * 2^64
    u128 acc = 0; for (int i=0;i<8;i++) acc += step;
    u128 acc_expect = step * 8;                               // multiply path cross-check
    show("accumulate x8", acc);
    if (acc != acc_expect){ printf("** FAIL accumulate\n"); fail++; }
    if (acc <= (u128)(uint64_t)-1){ printf("** FAIL accumulate did not exceed 2^64\n"); fail++; }

    // (reality: a(25)~1.5e19 < 2^64 < a(26)~1e20; 2^128~3.4e38 reached only ~a(48) -- check 3
    //  exercises the >2^64 regime that defeats a u64 counter but is exact in u128.)

    printf(fail ? "RESULT: FAIL (%d) -- u128 unusable on this ISA\n"
                : "RESULT: PASS -- u128 add+widening-mul correct on this ISA\n", fail);
    return fail ? 1 : 0;
}
