import time
import json
import os
import psutil

from destributed_matrix_multiplication import (
    MapReduceMatrixMultiplier,
    BasicMatrixMultiplier,
    OptimizedMatrixMultiplier,
    ParallelMatrixMultiplier,
    create_matrix,
    create_random_matrix,
    measure_memory
)

def benchmark_single_test(multiplier_class, A, B, num_workers=None, name="Test"):
    print(f"\n  Ejecutando {name}...")
    
    mem_before = measure_memory()
    start_time = time.time()
    
    if num_workers is not None:
        with multiplier_class(num_workers=num_workers) as mult:
            C, metrics = mult.multiply(A, B)
    else:
        mult = multiplier_class()
        C, metrics = mult.multiply(A, B)
    
    total_time = time.time() - start_time
    mem_after = measure_memory()
    mem_used = mem_after - mem_before
    
    result = {
        'name': name,
        'total_time': total_time,
        'memory_mb': mem_used,
        'metrics': metrics
    }
    
    if num_workers: 
        result['num_workers'] = num_workers
    
    print(f"    ✓ Tiempo:  {total_time:.4f}s | Memoria: {mem_used:.2f}MB")
    
    return result


def benchmark_matrix_size(size, workers_list=[1, 2, 4, 8]):
    print(f"\n{'=' * 80}")
    print(f"BENCHMARK - Matrices {size}×{size}")
    print(f"{'=' * 80}")
    
    print(f"\nCreando matrices...")
    A = create_matrix(size, value=1.5)
    B = create_matrix(size, value=2.5)
    
    results = {
        'size': size,
        'tests': []
    }
    
    basic_result = benchmark_single_test(
        BasicMatrixMultiplier, A, B,
        name="Básico (secuencial)"
    )
    results['tests'].append(basic_result)
    baseline_time = basic_result['total_time']
    
    optimized_result = benchmark_single_test(
        OptimizedMatrixMultiplier, A, B,
        name="Optimizado (cache-friendly)"
    )
    results['tests'].append(optimized_result)
    
    for num_workers in workers_list: 
        parallel_result = benchmark_single_test(
            ParallelMatrixMultiplier, A, B,
            num_workers=num_workers,
            name=f"Paralelo ({num_workers} workers)"
        )
        
        parallel_result['speedup'] = baseline_time / parallel_result['total_time']
        parallel_result['efficiency'] = parallel_result['speedup'] / num_workers
        
        results['tests'].append(parallel_result)
    
    for num_workers in workers_list: 
        mapreduce_result = benchmark_single_test(
            MapReduceMatrixMultiplier, A, B,
            num_workers=num_workers,
            name=f"MapReduce ({num_workers} workers)"
        )
        
        mapreduce_result['speedup'] = baseline_time / mapreduce_result['total_time']
        mapreduce_result['efficiency'] = mapreduce_result['speedup'] / num_workers
        
        results['tests'].append(mapreduce_result)
    
    return results


def run_full_benchmark(sizes=[128, 256, 512, 1024], workers_list=[1, 2, 4, 8]):
    print("=" * 80)
    print("BENCHMARK COMPLETO - Distributed Matrix Multiplication")
    print("=" * 80)
    print(f"\nTamaños a probar: {sizes}")
    print(f"Workers a probar: {workers_list}")
    print(f"CPU cores disponibles: {psutil.cpu_count()}")
    
    all_results = []
    
    for size in sizes:
        try:
            results = benchmark_matrix_size(size, workers_list)
            all_results.append(results)
        except KeyboardInterrupt:
            print("\n\nInterrumpido por el usuario")
            break
        except Exception as e:
            print(f"\nError con tamaño {size}: {e}")
            import traceback
            traceback.print_exc()
    
    if all_results:
        save_results(all_results)
        print_summary(all_results)
    
    return all_results


def save_results(results, filename='results/metrics.json'):
    """Guarda los resultados en formato JSON"""
    os.makedirs('results', exist_ok=True)
    
    with open(filename, 'w') as f:
        json. dump(results, f, indent=2)
    
    print(f"\n✓ Resultados guardados en:  {filename}")


def print_summary(all_results):
    """Imprime un resumen de todos los resultados"""
    print("\n" + "=" * 80)
    print("RESUMEN GENERAL")
    print("=" * 80)
    
    print(f"\n{'Tamaño':<10} {'Método':<30} {'Tiempo (s)':<12} {'Speedup':<10} {'Efficiency':<12}")
    print("-" * 80)
    
    for result in all_results:
        size = result['size']
        baseline = result['tests'][0]['total_time']
        
        for test in result['tests']:
            name = test['name']
            time_val = test['total_time']
            speedup = baseline / time_val
            
            efficiency = test. get('efficiency', speedup)
            efficiency_str = f"{efficiency:.2%}" if 'num_workers' in test else "-"
            
            print(f"{size:<10} {name:<30} {time_val:<12.4f} {speedup:<10.2f}x {efficiency_str:<12}")
        
        print()


if __name__ == "__main__":
    SIZES = [128, 256, 512, 1024]  
    WORKERS = [1, 2, 4, 8]     
    
    max_cores = psutil.cpu_count()
    WORKERS = [w for w in WORKERS if w <= max_cores]
    
    print(f"\nCores disponibles: {max_cores}")
    print(f"Workers a usar: {WORKERS}")
    
    results = run_full_benchmark(sizes=SIZES, workers_list=WORKERS)
    
    print("\n✓ BENCHMARK COMPLETADO")
    print("\nPuedes ejecutar 'python generate_report.py' para generar las gráficas")