import numpy as np
import matplotlib.pyplot as plt

# --- Measured data (max times from output) ---
workers = np.array([1, 4, 8, 16, 32, 64, 96])
times_max = np.array([10.8437, 11.4552, 6.12348, 12.3622, 9.65286, 12.4096, 10.4546])

# --- Measured Speedup (times_max[0] * workers) ---
speedup_measured = (times_max[0] * workers) / times_max

# --- Theoretical Speedups (Gustafson's Law) for different serial fractions ---
serial_fractions = [0.0001, 0.001, 0.01]
colors = ['blue', 'green', 'purple']

# --- Plot ---
plt.figure(figsize=(8, 5))

# Measured speedup
plt.plot(workers, speedup_measured, 'o-', linewidth=2, markersize=8, color='red',
         label='Measured Speedup (using max time)')

# Theoretical speedups for each s (Gustafson’s Law)
for s, c in zip(serial_fractions, colors):
    speedup_theoretical = s + workers * (1 - s)
    plt.plot(workers, speedup_theoretical, '--', linewidth=2, color=c,
            label=f'Theoretical Speedup (s={s})')

# --- Formatting ---
plt.xlabel('Number of Processes')
plt.ylabel('Speedup (T₁ / Tₙ)')
plt.title('Weak Scaling: Measured vs. Theoretical Speedup (Gustafson’s Law)')
plt.xticks(workers, workers)
plt.grid(True, which='both', linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.savefig('weak_scaling_speedup_max.png', dpi=300)
plt.show()
