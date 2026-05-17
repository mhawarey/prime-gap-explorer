# Prime Gap Explorer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A desktop Tkinter tool for computational exploration of **prime gaps** and the conjectures that govern them. Computes π(N), the full prime sequence up to N via a NumPy-backed sieve of Eratosthenes, extracts the gap series g_n = p_{n+1} - p_n, and evaluates four classical conjectures.

## Conjectures evaluated

| Conjecture | Statement | Status if violated |
|---|---|---|
| **Cramér** (1936) | lim sup g_n / (ln p_n)² = 1 | open; no known limit |
| **Firoozbakht** (1982) | p_{n+1}^{1/(n+1)} < p_n^{1/n} for all n ≥ 1 | strongest gap-growth conjecture; no known violations |
| **Oppermann** (1882) | For n ≥ 2: π(n²+n) > π(n²) and π((n+1)²) > π(n²+n) | would imply Legendre, Brocard, and the second Hardy–Littlewood |
| **Merit ratio** | g_n / ln(p_n), informal density measure | – |

## Features

- Vectorized sieve in NumPy; handles N up to ~10⁸ on a modern laptop.
- Threaded computation keeps the UI responsive.
- Plots gap series with ln(p) and (ln p)² envelopes and the gap-length histogram.
- Reports record gaps, max Cramér ratio, max merit, Firoozbakht violations, and the smallest n (if any) where Oppermann fails.

## Quick start

```bash
pip install -r requirements.txt
python prime_gap_explorer.py
```

Default N = 2,000,000 runs in under a second. Try 10,000,000 for serious record-gap territory.

## Why this matters

Prime gaps sit at the intersection of analytic number theory, the Riemann hypothesis, and combinatorial random-matrix models. The Maynard–Tao bounded-gaps revolution (2013–14) reignited the field, but exploration-grade open tooling for these conjectures remains thin. This repo provides a clean, reproducible substrate.

## References

- Cramér, H. (1936). *On the order of magnitude of the difference between consecutive prime numbers.* Acta Arithmetica, 2, 23–46.
- Firoozbakht, F. (1982). *A new conjecture concerning prime numbers.* (privately circulated; appears in many surveys).
- Granville, A. (1995). *Harald Cramér and the distribution of prime numbers.* Scandinavian Actuarial Journal.
- Maynard, J. (2016). *Small gaps between primes.* Annals of Mathematics, 181, 383–413.
- Soundararajan, K. (2007). *The distribution of prime numbers.* In Equidistribution in Number Theory, Springer.

## Author

**Dr. Mosab Hawarey**
>
PhD, Geodetic & Photogrammetric Engineering (ITU) | MSc, Geomatics (Purdue) | MBA (Wales) | BSc, MSc (METU)

- GitHub: https://github.com/mhawarey
- Personal: https://hawarey.org/mosab
- ORCID: https://orcid.org/0000-0001-7846-951X

## License

MIT License
