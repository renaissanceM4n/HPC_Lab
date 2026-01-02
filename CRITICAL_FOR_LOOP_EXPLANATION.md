# HPC Raytracer - Critical For-Loop Explanation & Optimization Summary

## Die Kritische For-Schleife - Detaillierte Erklärung

### Location in Code
- **File**: `raytracer.cpp` (alle Übungen)
- **Lines**: 135-177 (Exercise 2-4)
- **Function**: `RayTracer::render()`

### Der Code:
```cpp
// DOUBLE NESTED LOOP - Kernelberechnung
for (int y = start_row; y < end_row; ++y) {
    for (int x = 0; x < width; ++x) {
        // Für JEDEN PIXEL: Ray-Casting + Intersection Testing + Shading
        // Diese Schleife ist der Hotspot!
    }
}
```

---

## Was Die Schleife Macht (Schritt-für-Schritt)

### Schritt 1: Ray-Generation (Line 141-143)
```cpp
double ndc_x = (x + 0.5) / width;              // Normalisierte x-Koordinate
double ndc_y = (y + 0.5) / height;             // Normalisierte y-Koordinate
double px = (2 * ndc_x - 1) * aspect_ratio * scale;  // Perspektive-Projektion
double py = (1 - 2 * ndc_y) * scale;
```
**Was passiert**: Erzeugt einen **Sichtstrahl (Ray)** von der Kamera durch das Pixel

### Schritt 2: Ray-Richtung berechnen (Line 147-148)
```cpp
Vec3 ray_dir = (camera_dir + right * px + cam_up * py).normalize();
Vec3 ray_orig = camera_pos;  // Startpunkt: Kameraposition
```
**Was passiert**: Normalisiert die Ray-Richtung (wichtig für Distanzberechnung)

### Schritt 3: Intersection Testing (Line 155-174)
```cpp
// Test gegen ALLE Kugeln (Spheres)
for (const auto& sphere : scene->spheres) {
    double t;
    if (intersect_sphere(ray_orig, ray_dir, sphere, t) && t < closest_t) {
        closest_t = t;      // Update: this object is closest so far
        hit_sphere = &sphere;
        hit_plane = nullptr;
    }
}

// Test gegen ALLE Ebenen (Planes)
for (const auto& plane : scene->planes) {
    double t;
    if (intersect_plane(ray_orig, ray_dir, plane, t) && t < closest_t) {
        closest_t = t;
        hit_plane = &plane;
        hit_sphere = nullptr;
    }
}
```

**Was passiert**: 
- Mathematische Gleichung: Ray = ray_orig + t * ray_dir
- Für jede Kugel: Löse ||ray - center||² = radius² nach t
- Finde die **kleinste positive t** (nächstes sichtbares Objekt)
- **Komplexität pro Pixel**: O(N_spheres + N_planes)

### Schritt 4: Schattenberechnung (Line 181-202)
```cpp
// Wenn wir eine Kugel getroffen haben:
if (hit_sphere) {
    Vec3 hit_point = ray_orig + ray_dir * closest_t;  // Auftreffpunkt
    Vec3 normal = (hit_point - hit_sphere->center).normalize();  // Oberflächennormal
    
    // Shadow Ray: Teste ob dieser Punkt im Schatten liegt
    Vec3 shadow_dir = -sunlight_dir;
    for (const auto& s : scene->spheres) {
        double t_shadow;
        // Teste ob dieser Punkt durch eine andere Kugel verdeckt ist
        if (&s != hit_sphere && intersect_sphere(shadow_origin, shadow_dir, s, t_shadow)) {
            in_shadow = true;  // Ja, in Schatten
            break;
        }
    }
}
```

**Was passiert**: 
- Schießt einen zusätzlichen Ray vom Auftreffpunkt zur Sonne
- Wenn dieser Ray durch eine andere Kugel geht → Pixel ist im Schatten
- **Zusätzliche Komplexität**: O(N_spheres) pro getroffenes Objekt

### Schritt 5: Farbberechnung (Line 204-230)
```cpp
// Kombiniere: Ambient Light + Diffuse Light + Shadow
double diffuse = std::max(0.0, normal.dot(sunlight_dir));
double light_intensity = ambient + (1.0 - ambient) * diffuse * (in_shadow ? 0.5 : 1.0);

Color pixel_color = sphere->color * light_intensity;
```

**Was passiert**: Einfache Phong-Beleuchtung mit Schatten

---

## Computational Complexity

### Für ein einzelnes Bild (1024×1024 Pixel):

```
Außenschleife (Y):        1024 Iterationen
  Innenschleife (X):      1024 Iterationen
    Test alle Kugeln:     ~3 Kugeln (Snowman aus 3 Kugeln)
    Test alle Ebenen:     ~1 Ebene  (Boden)
    
    Falls Kugel getroffen:
      Test Schatten:      3 Kugeln
      
TOTAL: 1024 × 1024 × (3 + 1 + 3) = 7 Millionen Operationen MINIMUM
```

**Bei 48 MPI-Prozessen**: Jeder bekommt ~14.700 Pixel, muss aber alle 3+3 = 6 Kugeln testen

### Warum ist das der Bottleneck?

1. **Hohe Iteration Count**: 1 Million Pixel pro Frame
2. **Viele Berechnungen pro Iteration**: ~10-50 Floating-Point Operationen
3. **Cache Misses**: Zufällige Zugriffe auf Sphere-Array
4. **Branch Misprediction**: `if (intersect_sphere(...))` ist schwer vorherzusagen
5. **Keine Datenlokalität**: Next iteration nutzt komplett andere Daten

---

## Implementation Variationen

### Exercise 1: Sequential
```cpp
// Alles hintereinander, 1 Thread
for (int y = 0; y < height; ++y) {
    for (int x = 0; x < width; ++x) {
        // ... 7M operations in sequence ...
    }
}
// Total Zeit: ~7 Sekunden auf moderner CPU (1 core)
```

### Exercise 2: MPI mit Row Decomposition + Tile Distribution
```cpp
// Jeder MPI Prozess bearbeitet verschiedene Rows
int rows_per_rank = height / size;
int start_row = rank * rows_per_rank;

for (int y = start_row; y < end_row; ++y) {  // Only my rows!
    for (int x = 0; x < width; ++x) {
        // ... 7M / N_processes operations ...
    }
}
// Mit 48 MPI Prozessen: 7M / 48 ≈ 146K operations pro Prozess
// Aber: MPI Kommunikation overhead!
```

**Problem**: 
- Wenn manche Prozesse ihre Rows schneller fertig haben → Idle waiting
- Solution: **Tile Decomposition** (dynamisches Work-Stealing)

### Exercise 3: OpenMP Parallelization
```cpp
#pragma omp parallel for collapse(2)
for (int y = start_row; y < end_row; ++y) {
    for (int x = 0; x < width; ++x) {
        // ... jeder Thread bearbeitet andere Pixel ...
    }
}
// collapse(2): Fusioniere beide Loops zu 1M Iterationen
// OpenMP verteilt diese auf 8 Threads
// Jeder Thread: 1M / 8 = 125K Iterationen

// Vorteil: Shared Memory, NO Communication Overhead
// Nachteil: Single Node, Memory Bandwidth Saturation
```

**Skalierungsproblem**: 
- Mit 8 Threads auf 1 Node: OK
- Mit mehr Threads: Memory Bottleneck (alle Threads greifen auf scene->spheres zu)

### Exercise 4: Hybrid MPI+OpenMP + Tile Decomposition
```cpp
// MPI distribuiert große Tiles auf Prozesse
// OpenMP parallelisiert innerhalb eines Prozesses

for (int y = start_row; y < end_row; ++y) {
    #pragma omp parallel for schedule(dynamic, 8)
    for (int x = 0; x < width; ++x) {
        // ... innerhalb eines MPI-Prozesses parallelisiert ...
    }
}

// Mit 2 MPI × 4 OpenMP = 8 Threads
// Bessere Load Balance durch dynamisches Scheduling
// + MPI ermöglicht Multi-Node
```

---

## Weitere Optimierungsmöglichkeiten

### Tier 1: Kritisch (5-10x Speedup möglich)

#### 1. **Bounding Volume Hierarchy (BVH)**
**Aktuelles Problem**: 
- Jeder Ray testet gegen ALLE 3 Kugeln
- Mit nur 3 Kugeln: OK
- Aber: Szenen können Tausende Objekte haben!

**Lösung - BVH Baum**:
```
Alle Objekte
     |
     +--- BV (Bounding Volume)
          |
          +--- Links: Ob. 1,2
          |    |
          |    +--- BV
          |         |
          |         +--- Obj 1
          |         +--- Obj 2
          |
          +--- Rechts: Obj 3
               |
               +--- BV
                    |
                    +--- Obj 3
```

**Wie es funktioniert**:
```cpp
bool ray_intersect_bvh(const Ray& ray, BVHNode* node) {
    // Schneller Test: Trifft Ray diese Bounding Box?
    if (!ray_hits_bbox(ray, node->bounds))
        return false;  // Skip alle Objekte in diesem Ast!
    
    if (node->is_leaf) {
        // Nur die 1-2 Objekte in dieser Box testen
        for (int obj_id : node->objects) {
            test_intersection(ray, scene->objects[obj_id]);
        }
    } else {
        // Rekursiv links und rechts durchsuchen
        ray_intersect_bvh(ray, node->left);
        ray_intersect_bvh(ray, node->right);
    }
}
```

**Impact**: 
- Aktuell: 1M Pixel × 3 = 3M Intersection Tests
- Mit BVH: 1M Pixel × log(3) = **~5M operations** (aber viele sind schnelle BBox Tests)
- **Bei 1000 Objekten**: 1M × 1000 → 1M × log(1000) = **100-200x Speedup!**

#### 2. **Frustum Culling**
**Idee**: Viele Objekte sind gar nicht sichtbar in der Kamera-Ansicht

```cpp
// Vor Rendering:
std::vector<int> visible_spheres;
for (int i = 0; i < scene->spheres.size(); ++i) {
    if (is_in_view_frustum(scene->spheres[i])) {
        visible_spheres.push_back(i);
    }
}

// Im Rendering Loop: Nur visible_spheres testen!
for (int sphere_id : visible_spheres) {
    test_intersection(ray, scene->spheres[sphere_id]);
}
```

**Impact**: 1.5-2x schneller (weniger Tests)

#### 3. **SIMD Vectorization**
**Idee**: Process 4-8 Rays gleichzeitig mit AVX-256

```cpp
// Aktuell: 1 Ray zur Zeit
for (int i = 0; i < num_rays; i++) {
    Vec3 result = trace_ray(rays[i]);
}

// Mit SIMD: 4 Rays gleichzeitig
__m256d ray_x = _mm256_setr_pd(rays[0].x, rays[1].x, rays[2].x, rays[3].x);
__m256d sphere_x = _mm256_set1_pd(sphere.center.x);
__m256d result_x = _mm256_sub_pd(ray_x, sphere_x);  // 4 Subtrakte gleichzeitig!
```

**Impact**: 3-4x für Intersection Tests

---

### Tier 2: Moderate Verbesserungen (1.5-2x möglich)

#### 4. **Dynamic Load Balancing (Exercise 4)**
**Aktuell**: Feste Tile-Größe → manche Tiles komplexer als andere

**Lösung**: 
```cpp
// Tiles mit vielen sichtbaren Objekten → kleinere Tiles
// Tiles mit wenigen Objekten → größere Tiles
if (estimated_sphere_count > 5) {
    tile_size = 8;   // Fine-grained
} else {
    tile_size = 16;  // Coarse-grained
}
```

**Impact**: 1.2-1.5x (bessere Thread Auslastung)

#### 5. **Scheduled OpenMP Loop (Exercise 3 & 4)**
```cpp
// Aktuell: Implizit static scheduling
#pragma omp parallel for collapse(2)

// Besser: Dynamic scheduling
#pragma omp parallel for collapse(2) schedule(dynamic, 32)
```

**Warum**:
- Innere Rows haben unterschiedliche Arbeit (Objekte oben vs. unten im Bild)
- `schedule(dynamic)` verteilt unvollendete Work an idle Threads

**Impact**: 1.05-1.2x

---

### Tier 3: Erweiterte Optimierungen

#### 6. **Ray Packet Tracing**
Wie SIMD aber auf ganzer Ray-Hierarchie

#### 7. **Deferred Rendering**
2-Pass: Erst Geometrie, dann Shading

#### 8. **Adaptive Sampling**
Unterschiedliche Precision je nach Region

---

## Zusammenfassung der Optimierungen

| Optimierung | Impact | Difficulty | Parallelization |
|-------------|--------|-----------|-----------------|
| BVH Tree | 3-5x | Medium | All |
| Frustum Culling | 1.5-2x | Low | All |
| SIMD | 3-4x | Medium | All |
| Dynamic Scheduling | 1.2-1.5x | Low | OMP/Hybrid |
| Adaptive Tiles | 1.2-1.5x | Medium | MPI/Hybrid |
| **Combined** | **6-15x** | **High** | **All** |

---

## Code Wo Die For-Schleife Angewendet Wird

### Alle Übungen
- **Exercise 1**: [main.cpp](exercise1/main.cpp) - keine Parallelisierung
- **Exercise 2**: [raytracer.cpp](exercise2/raytracer.cpp#L135) - mit MPI
- **Exercise 3**: [raytracer.cpp](exercise3/raytracer.cpp#L120) - mit `#pragma omp parallel for collapse(2)`
- **Exercise 4**: [raytracer.cpp](exercise4/raytracer.cpp#L135) - Hybrid MPI+OpenMP

### Intersection Testing (auch kritisch)
- [raytracer.cpp](exercise4/raytracer.cpp#L155) - Sphere intersection loop
- [raytracer.cpp](exercise4/raytracer.cpp#L165) - Plane intersection loop
- [raytracer.cpp](exercise4/raytracer.cpp#L185) - Shadow intersection loop

---

## Recommendations for Your Report

### Screenshots to Include:

1. **MAP Profiling Results**:
   - Zeige: `intersect_sphere()` ist Top-1 Function (60-70% time)
   - Zeige: Call stack depth (shadow tests)

2. **Vampir Timeline**:
   - Zeige: MPI Kommunikation während Rendering
   - Zeige: Load Imbalance zwischen Processes

3. **Performance Metrics**:
   - Strong Scaling: Ex1 vs Ex2 vs Ex3 vs Ex4
   - Weak Scaling: Verhältnis zu Bild-Größe

4. **Optimization Impact**:
   - Graph: Mit/ohne Optimierungen
   - Predicted speedup mit BVH

---

## Final Note

**Die For-Schleife ist ein perfektes HPC-Lernbeispiel weil:**

1. ✅ **Embarrassingly Parallel**: Keine Abhängigkeiten zwischen Pixels
2. ✅ **Skaliert linear** mit Prozessoren (ideal case)
3. ✅ **Zeigt echte Bottlenecks**: Intersection Testing
4. ✅ **Erlaubt viele Optimierungen**: BVH, SIMD, Scheduling
5. ✅ **Messbar**: Performance Profiling tools funktionieren gut damit

Das ist genau das Problem das Supercomputer trainiert sind zu lösen!
