# benchmark.py
import time
import json
import os
import psutil
from distributed_matrix_multiplication import (
    MapReduceMatrixMultiplier,
    BasicMatrixMultiplier,
    OptimizedMatrixMultiplier,
    create_matrix,
    create_random_matrix,
    measure_memory
)

def benchmark_single_test(multiplier_class, A, B, num_workers=None, name="Test"):
    print(f"\n  Executing {name}...")
    
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
    
    print(f"    ✓ Time: {total_time:.4f}s | Memory: {mem_used:.2f}MB")
    
    return result


def benchmark_matrix_size(size, workers_list=[1, 2, 4, 8]):
    print(f"\n{'=' * 80}")
    print(f"BENCHMARK - {size}×{size} Matrices")
    print(f"{'=' * 80}")
    
    print(f"\nCreating matrices...")
    A = create_matrix(size, value=1.5)
    B = create_matrix(size, value=2.5)
    
    results = {
        'size': size,
        'tests': []
    }
    
    basic_result = benchmark_single_test(
        BasicMatrixMultiplier, A, B,
        name="Basic (sequential)"
    )
    results['tests'].append(basic_result)
    baseline_time = basic_result['total_time']
    
    optimized_result = benchmark_single_test(
        OptimizedMatrixMultiplier, A, B,
        name="Optimized (cache-friendly)"
    )
    results['tests'].append(optimized_result)
    
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
    print("COMPLETE BENCHMARK - Distributed Matrix Multiplication")
    print("=" * 80)
    print(f"\nSizes to test: {sizes}")
    print(f"Workers to test: {workers_list}")
    print(f"Available CPU cores: {psutil.cpu_count()}")
    
    all_results = []
    
    for size in sizes:
        try:
            results = benchmark_matrix_size(size, workers_list)
            all_results.append(results)
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            break
        except Exception as e:
            print(f"\n⚠️  Error with size {size}: {e}")
            import traceback
            traceback.print_exc()
    
    if all_results:
        save_results(all_results)
        print_summary(all_results)
    
    return all_results


def save_results(results, filename='results/metrics.json'):
    os.makedirs('results', exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to:  {filename}")


def print_summary(all_results):
    print("\n" + "=" * 80)
    print("GENERAL SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Size':<10} {'Method':<30} {'Time (s)':<12} {'Speedup':<10} {'Efficiency':<12}")
    print("-" * 80)
    
    for result in all_results:
        size = result['size']
        baseline = result['tests'][0]['total_time']
        
        for test in result['tests']:
            name = test['name']
            time_val = test['total_time']
            speedup = baseline / time_val
            
            efficiency = test.get('efficiency', speedup)
            efficiency_str = f"{efficiency:.2%}" if 'num_workers' in test else "-"
            
            print(f"{size:<10} {name:<30} {time_val:<12.4f} {speedup:<10.2f}x {efficiency_str:<12}")
        
        print()


if __name__ == "__main__":
    SIZES = [128, 256, 512, 1024]  
    WORKERS = [1, 2, 4, 8]          
    
    max_cores = psutil.cpu_count()
    WORKERS = [w for w in WORKERS if w <= max_cores]
    
    print(f"\nAvailable cores: {max_cores}")
    print(f"Workers to use: {WORKERS}")
    
    results = run_full_benchmark(sizes=SIZES, workers_list=WORKERS)
    
    print("\n✓ BENCHMARK COMPLETED")
    print("\nYou can run 'python generate_report.py' to generate plots")