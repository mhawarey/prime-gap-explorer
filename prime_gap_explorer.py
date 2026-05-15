"""
Prime Gap Explorer — Computational study of prime gaps and conjectures.

Computes primes up to N with a segmented sieve of Eratosthenes,
extracts the gap sequence g_n = p_{n+1} - p_n, then evaluates:

    - Cramér conjecture:  limsup g_n / (ln p_n)^2 = 1
    - Firoozbakht conjecture: p_{n+1}^{1/(n+1)} < p_n^{1/n}
    - Oppermann conjecture: pi((n+1)^2) - pi(n^2 + n) > 0
                            and pi(n^2 + n) - pi(n^2) > 0 for n >= 2
    - Merit ratio: g_n / ln(p_n)

Reports record gaps and the smallest counterexample (if any) discovered
for each conjecture up to the search bound.

Author: Dr. Mosab Hawarey (@DrHawarey)
License: MIT
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk, messagebox
import threading

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def segmented_sieve(limit: int) -> np.ndarray:
    """Return all primes <= limit using a NumPy-backed sieve of Eratosthenes."""
    if limit < 2:
        return np.array([], dtype=np.int64)
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(math.isqrt(limit)) + 1):
        if sieve[i]:
            sieve[i * i :: i] = False
    return np.flatnonzero(sieve).astype(np.int64)


def gap_statistics(primes: np.ndarray) -> dict:
    """Compute gap series and conjecture statistics."""
    gaps = np.diff(primes)
    log_p = np.log(primes[:-1].astype(np.float64))
    cramer_ratio = gaps / (log_p ** 2)
    merit = gaps / log_p

    # Firoozbakht: check p_{n+1}^{1/(n+1)} < p_n^{1/n}
    n_idx = np.arange(1, len(primes) + 1, dtype=np.float64)
    root_p = primes.astype(np.float64) ** (1.0 / n_idx)
    firoozbakht_violations = np.where(np.diff(root_p) >= 0)[0]

    # Record gaps (first occurrence of each new maximum)
    records = []
    current_max = 0
    for i, g in enumerate(gaps):
        if g > current_max:
            current_max = int(g)
            records.append((int(primes[i]), int(g)))

    return {
        "gaps": gaps,
        "log_p": log_p,
        "cramer_ratio": cramer_ratio,
        "merit": merit,
        "max_gap": int(gaps.max()),
        "max_gap_after_prime": int(primes[gaps.argmax()]),
        "max_cramer_ratio": float(cramer_ratio.max()),
        "max_cramer_at_prime": int(primes[cramer_ratio.argmax()]),
        "max_merit": float(merit.max()),
        "firoozbakht_violations": firoozbakht_violations,
        "records": records,
    }


def oppermann_check(primes: np.ndarray, n_max: int) -> tuple[bool, int]:
    """
    Check Oppermann's conjecture for n in [2, n_max]:
    pi(n^2 + n) - pi(n^2) > 0  AND  pi((n+1)^2) - pi(n^2 + n) > 0.
    Returns (holds_for_all, first_failing_n_or_zero).
    """
    # Build cumulative pi via search; primes is sorted ascending
    bounds = []
    for n in range(2, n_max + 1):
        b1 = n * n
        b2 = n * n + n
        b3 = (n + 1) ** 2
        if b3 > primes[-1]:
            break
        pi1 = np.searchsorted(primes, b1, side="right")
        pi2 = np.searchsorted(primes, b2, side="right")
        pi3 = np.searchsorted(primes, b3, side="right")
        if not (pi2 > pi1 and pi3 > pi2):
            return False, n
    return True, 0


class PrimeGapApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Prime Gap Explorer")
        self.root.geometry("1180x780")
        self.primes: np.ndarray | None = None
        self.stats: dict | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        left = ttk.Frame(self.root, padding=10)
        left.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left, text="Prime Gap Explorer",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(left, text="Sieve bound N").pack(anchor="w", pady=(10, 2))
        self.n_var = tk.StringVar(value="2000000")
        ttk.Entry(left, textvariable=self.n_var, width=18).pack(anchor="w")

        self.run_btn = ttk.Button(left, text="Compute", command=self._run_async)
        self.run_btn.pack(fill=tk.X, pady=10)

        self.status = ttk.Label(left, text="Ready.", foreground="#444")
        self.status.pack(anchor="w")

        self.out = tk.Text(left, width=42, height=30, wrap="word",
                           font=("Consolas", 9))
        self.out.pack(fill=tk.BOTH, pady=8)

        ttk.Label(left, text="Dr. Mosab Hawarey • MIT License",
                  font=("Segoe UI", 8), foreground="#777").pack(anchor="w")

        right = ttk.Frame(self.root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.fig, self.axes = plt.subplots(2, 1, figsize=(8, 7), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _run_async(self) -> None:
        try:
            N = int(self.n_var.get())
        except ValueError:
            messagebox.showerror("Input", "N must be a positive integer.")
            return
        if N < 100:
            messagebox.showerror("Input", "Use N >= 100.")
            return
        self.run_btn.configure(state="disabled")
        self.status.configure(text=f"Sieving up to {N:,} …")
        threading.Thread(target=self._compute, args=(N,), daemon=True).start()

    def _compute(self, N: int) -> None:
        try:
            primes = segmented_sieve(N)
            self.primes = primes
            stats = gap_statistics(primes)
            self.stats = stats
            opp_ok, opp_fail = oppermann_check(primes, int(math.isqrt(N)) - 1)

            cramer_violations = int(np.sum(stats["cramer_ratio"] > 1.0))

            report = (
                f"Sieve bound N = {N:,}\n"
                f"Primes found = {len(primes):,}\n"
                f"Largest prime <= N : {int(primes[-1]):,}\n\n"
                f"=== Gap statistics ===\n"
                f"Max gap     : {stats['max_gap']} (after p={stats['max_gap_after_prime']:,})\n"
                f"Max merit   : {stats['max_merit']:.4f}\n\n"
                f"=== Cramér conjecture ===\n"
                f"  limsup g_n / (ln p_n)^2 = 1\n"
                f"  Max observed ratio: {stats['max_cramer_ratio']:.4f}\n"
                f"  at p = {stats['max_cramer_at_prime']:,}\n"
                f"  Values > 1 found : {cramer_violations}\n"
                f"  (not a counterexample — conjecture is limsup,\n"
                f"   ratios can transiently exceed 1)\n\n"
                f"=== Firoozbakht conjecture ===\n"
                f"  p_{{n+1}}^{{1/(n+1)}} < p_n^{{1/n}}\n"
                f"  Violations found : {len(stats['firoozbakht_violations'])}\n"
                + (f"  First at index   : {int(stats['firoozbakht_violations'][0]):,}\n"
                   if len(stats['firoozbakht_violations']) else "")
                + f"\n=== Oppermann conjecture ===\n"
                f"  pi(n²+n) > pi(n²) and pi((n+1)²) > pi(n²+n)\n"
                f"  Holds for all checked n: {opp_ok}\n"
                + (f"  First failing n: {opp_fail}\n" if not opp_ok else "")
                + f"\n=== Record gaps (first 12) ===\n"
            )
            for p, g in stats["records"][:12]:
                report += f"  g={g:>4d} after p={p:>12,}\n"

            self._update_ui(report, stats, primes)
        except Exception as exc:
            self._on_error(exc)

    def _update_ui(self, report: str, stats: dict, primes: np.ndarray) -> None:
        def apply():
            self.out.delete("1.0", tk.END)
            self.out.insert(tk.END, report)
            self.status.configure(text="Done.")
            self.run_btn.configure(state="normal")

            self.axes[0].clear()
            sub_p = primes[:-1]
            sub_g = stats["gaps"]
            self.axes[0].plot(sub_p, sub_g, '.', ms=0.4, color="#446")
            ln = np.log(sub_p.astype(np.float64))
            self.axes[0].plot(sub_p, ln ** 2, lw=0.8, color="C3", label="(ln p)²")
            self.axes[0].plot(sub_p, ln, lw=0.8, color="C2", label="ln p")
            self.axes[0].set_title("Prime gaps and Cramér / merit envelopes")
            self.axes[0].set_xlabel("prime p"); self.axes[0].set_ylabel("g_n")
            self.axes[0].legend(); self.axes[0].grid(alpha=0.3)
            self.axes[0].set_xscale("log")

            self.axes[1].clear()
            bins = np.arange(0, stats["gaps"].max() + 2)
            self.axes[1].hist(stats["gaps"], bins=bins, color="C0", edgecolor="white")
            self.axes[1].set_title("Distribution of gap lengths")
            self.axes[1].set_xlabel("gap length"); self.axes[1].set_ylabel("count")
            self.axes[1].set_yscale("log"); self.axes[1].grid(alpha=0.3)
            self.fig.tight_layout()
            self.canvas.draw_idle()

        self.root.after(0, apply)

    def _on_error(self, exc: Exception) -> None:
        def apply():
            self.status.configure(text="Error.")
            self.run_btn.configure(state="normal")
            messagebox.showerror("Prime Gap Explorer", str(exc))
        self.root.after(0, apply)


def main() -> None:
    root = tk.Tk()
    PrimeGapApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
