================================================================================
HYBRID SCALING ANALYSIS - SPEEDUP EINBRUCH BEI 12 PROZESSEN
================================================================================

BEOBACHTUNG:
Der Speedup zeigt einen signifikanten Einbruch bei 12 Prozessen im Test 2.

TEST 2: Fixed 4 Threads, Varying Processes
============================================

Prozesse | Max Time (s) | Min Time (s) | Imbalanz (s) | Speedup | Ideal
---------|--------------|--------------|--------------|---------|-------
   4     |   50.3174    |   41.0190    |    9.30      |  1.00x  | 1.00x
   8     |   25.2384    |   20.3764    |    4.86      |  1.99x  | 2.00x
  12     |   33.3077    |   13.3832    |   19.92      |  1.51x  | 3.00x  ← EINBRUCH!
  16     |   25.1996    |   20.3450    |    4.85      |  2.00x  | 4.00x

URSACHENANALYSE:
================

1. **Massive Load-Imbalanz bei 12 Prozessen**
   - Max Time: 33.31 Sekunden
   - Min Time: 13.38 Sekunden
   - Differenz: 19.92 Sekunden (59% der Min-Time!)
   
   Das bedeutet: Ein Prozess ist nach 13 Sekunden fertig, aber der langsamste
   Prozess braucht noch 33 Sekunden. Der Speedup ist dadurch auf die Max-Time
   limitiert.

2. **Load-Balancing-Problem im Raytracer**
   - Die Arbeit wird nicht gleichmäßig auf die Prozesse verteilt
   - Bei 12 Prozessen auf einer NUMA-Domain ist die Verteilung besonders schlecht
   - Manche Prozesse zeichnen deutlich mehr Schneemanns als andere

3. **Warum erholt sich der Speedup bei 16 Prozessen?**
   - Max Time: 25.20 Sekunden (deutlich besser als bei 12!)
   - Min Time: 20.35 Sekunden (ähnlich wie bei 8)
   - Imbalanz: 4.85 Sekunden (viel kleiner als bei 12)
   - Die Verteilung funktioniert bei geraden Vielfachen besser

SCHLUSSFOLGERUNG:
=================

Der Speedup-Einbruch bei 12 Prozessen ist **nicht** ein Hardware-Problem,
sondern ein **Work-Distribution-Problem** in der Raytracer-Implementierung:

- Das MPI-Task-Scheduling oder die Datenverteilung funktioniert schlecht
  für 12 Prozesse auf einer NUMA-Domain
- Bei 8 und 16 Prozessen ist die Last-Balanz deutlich besser
- 12 ist kein Vielfaches der 4 Schneemanns, was zu ungleicher Verteilung führt
  (12 = 3×4, aber vielleicht werden die Schneemanns ungleichmäßig verteilt)

EMPFEHLUNGEN:
=============

1. Überprüfe die Work-Distribution im main.cpp/scene.cpp
2. Prüfe, wie die Schneemanns auf die MPI-Prozesse verteilt werden
3. Implementiere dynamisches Load-Balancing via MPI oder OpenMP
4. Führe Load-Balancing-Tests durch, um die ideale Prozess-Anzahl zu finden

================================================================================
