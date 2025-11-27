import matplotlib.pyplot as plt
import numpy as np

# --- Max Local Computation Times (seconds) ---
times_max = np.array([
    689.211,   # 1
    361.392,   # 2
    241.614,   # 3
    182.585,   # 4
    153.473,   # 5
    129.505,   # 6
    109.398,   # 7
    97.6739,   # 8
    86.6075,   # 9
    77.9155,   # 10
    70.8362,   # 11
    65.355,    # 12
    60.154,    # 13
    56.0345,   # 14
    52.3322,   # 15
    49.4053,   # 16
    46.2659,   # 17
    45.0344,   # 18
    43.4768,   # 19
    39.2981,   # 20
    39.8764,   # 21
    35.9119,   # 22
    34.3512,   # 23
    35.7806,   # 24
    39.6418,   # 25
    30.0772,   # 26
    38.3815,   # 27
    32.048,    # 28
    27.0874,   # 29
    26.3854,   # 30
    25.509,    # 31
    24.7,      # 32
    23.9729,   # 33
    23.2304,   # 34
    23.3397,   # 35
    26.9462,   # 36
    31.8608,   # 37
    38.5189,   # 38
    21.9731,   # 39
    30.2193,   # 40
    39.4352,   # 41
    24.2505,   # 42
    35.8162,   # 43
    21.2913,   # 44
    34.5203,   # 45
    20.5464,   # 46
    35.9603,   # 47
    22.7208,   # 48
    39.738,    # 49
    27.0936,   # 50
    15.4429,   # 51
    34.0771,   # 52
    22.0087,   # 53
    43.7014,   # 54
    32.0972,   # 55
    20.7491,   # 56
    44.5245,   # 57
    34.1098,   # 58
    23.3964,   # 59
    13.1786,   # 60
    39.6351,   # 61
    29.3182,   # 62
    19.4341,   # 63
    12.4158,   # 64
    39.7866,   # 65
    30.1711,   # 66
    20.8117,   # 67
    11.6138,   # 68
    44.7195,   # 69
    36.1171,   # 70
    26.7994,   # 71
    18.1738,   # 72
    10.8288,   # 73
    46.8293,   # 74
    38.5523,   # 75
    30.1155,   # 76
    22.1344,   # 77
    13.7358,   # 78
    55.4185,   # 79
    47.7474,   # 80
    39.8237,   # 81
    32.0915,   # 82
    24.6232,   # 83
    17.0642,   # 84
    9.60614,   # 85
    56.3727,   # 86
    48.8024,   # 87
    41.7293,   # 88
    34.4454,   # 89
    27.6323,   # 90
    21.0605,   # 91
    14.2288,   # 92
    8.56813,   # 93
    59.2118,   # 94
    52.8247,   # 95
    45.8401    # 96
])

# --- Number of processors ---
processors = np.arange(1, 97)

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
