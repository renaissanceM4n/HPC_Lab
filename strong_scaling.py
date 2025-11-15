import matplotlib.pyplot as plt
import numpy as np

# --- Max Local Computation Times (seconds) ---
times_max = np.array([
    682.88,    # 1 process
    358.231,   # 2 processes
    182.656,   # 4 processes
    97.6342,   # 8 processes
    49.3973,   # 16 processes
    24.7043,   # 32 processes
    12.4101,   # 64 processes
    45.7208    # 96 processes (outlier due to inter-socket communication)
])

# --- Number of processors ---
processors = np.array([1, 2, 4, 8, 16, 32, 64, 96])

# --- Measured Speedup ---
speedup_measured = times_max[0] / times_max

# --- Theoretical Speedups for different serial fractions ---
serial_fractions = [0.1, 0.01, 0.001]
colors = ['blue', 'green', 'purple']

# --- Plot ---
plt.figure(figsize=(8, 5))
plt.plot(processors, speedup_measured, 'o-', color='red', label='Measured Speedup (using max time)')

# Plot each theoretical speedup
for s, c in zip(serial_fractions, colors):
    speedup_theoretical = 1 / (s + (1 - s) / processors)
    plt.plot(processors, speedup_theoretical, '--', color=c, label=f'Theoretical Speedup (s={s})')

plt.xlabel('Number of Processors')
plt.ylabel('Speedup')
plt.title('Strong Scaling: Measured vs. Theoretical Speedup (Amdhal´s Law)')
plt.grid(True, linestyle='--', linewidth=0.5)
plt.legend()
plt.tight_layout()
plt.savefig('strong_scaling_speedup_max.png', dpi=300)
plt.show()
