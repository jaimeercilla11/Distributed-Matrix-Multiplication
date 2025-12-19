import json
import matplotlib.pyplot as plt
import numpy as np
import os

def load_results(filename='results/metrics.json'):
    """Carga los resultados del benchmark"""
    with open(filename, 'r') as f:
        return json. load(f)


def plot_scalability(results):
    """
    Gráfica 1: Scalability - Tiempo vs Tamaño de Matriz
    """
    sizes = [r['size'] for r in results]
    
    basic_times = []
    optimized_times = []
    parallel_times = {}  
    mapreduce_times = {}  
    
    for result in results:
        for test in result['tests']:
            name = test['name']
            time_val = test['total_time']
            
            if 'Básico' in name:
                basic_times.append(time_val)
            elif 'Optimizado' in name:
                optimized_times.append(time_val)
            elif 'Paralelo' in name: 
                workers = test['num_workers']
                if workers not in parallel_times: 
                    parallel_times[workers] = []
                parallel_times[workers].append(time_val)
            elif 'MapReduce' in name:
                workers = test['num_workers']
                if workers not in mapreduce_times:
                    mapreduce_times[workers] = []
                mapreduce_times[workers].append(time_val)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    ax.plot(sizes, basic_times, 'o-', label='Básico (secuencial)', 
            linewidth=2.5, markersize=10, color='#e74c3c')
    ax.plot(sizes, optimized_times, 's-', label='Optimizado (cache)', 
            linewidth=2.5, markersize=10, color='#3498db')
    
    colors_parallel = ['#2ecc71', '#27ae60', '#16a085', '#1abc9c']
    markers = ['^', 'v', '<', '>']
    
    for idx, (workers, times) in enumerate(sorted(parallel_times.items())):
        ax.plot(sizes, times, f'{markers[idx]}-', 
                label=f'Paralelo ({workers} workers)',
                linewidth=2.5, markersize=10, 
                color=colors_parallel[idx % len(colors_parallel)])
    
    colors_mapreduce = ['#f39c12', '#e67e22', '#d35400', '#e74c3c']
    markers_mr = ['D', 'p', 'h', '*']
    
    for idx, (workers, times) in enumerate(sorted(mapreduce_times. items())):
        ax.plot(sizes, times, f'{markers_mr[idx]}--', 
                label=f'MapReduce ({workers} workers)',
                linewidth=2, markersize=9, 
                color=colors_mapreduce[idx % len(colors_mapreduce)],
                alpha=0.8)
    
    ax.set_xlabel('Matrix Size (n×n)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontsize=14, fontweight='bold')
    ax.set_title('Scalability: Execution Time vs Matrix Size\n(Básico vs Optimizado vs Paralelo vs MapReduce)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.legend(fontsize=10, loc='upper left', ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_yscale('log')
    
    plt.tight_layout()
    plt.savefig('results/plots/scalability.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfica guardada:  results/plots/scalability.png")


def plot_speedup(results):
    """
    Gráfica 2: Speedup vs Number of Workers
    """
    sizes = [r['size'] for r in results]
    
    speedup_data = {}
    
    for result in results:
        size = result['size']
        speedup_data[size] = {}
        
        baseline_time = result['tests'][0]['total_time']
        
        for test in result['tests']: 
            if 'MapReduce' in test['name']: 
                workers = test['num_workers']
                speedup = baseline_time / test['total_time']
                speedup_data[size][workers] = speedup
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    markers = ['o', 's', '^', 'D']
    
    for idx, size in enumerate(sizes):
        workers_list = sorted(speedup_data[size]. keys())
        speedups = [speedup_data[size][w] for w in workers_list]
        
        ax.plot(workers_list, speedups, f'{markers[idx]}-', 
                label=f'{size}×{size}',
                linewidth=2.5, markersize=10,
                color=colors[idx % len(colors)])
    
    max_workers = max(max(speedup_data[size]. keys()) for size in sizes)
    ax.plot([1, max_workers], [1, max_workers], 'k--', 
            label='Ideal (linear)', linewidth=2, alpha=0.5)
    
    ax.set_xlabel('Number of Workers', fontsize=14, fontweight='bold')
    ax.set_ylabel('Speedup (vs Sequential)', fontsize=14, fontweight='bold')
    ax.set_title('Speedup vs Number of Workers', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks([1, 2, 4, 8])
    
    plt.tight_layout()
    plt.savefig('results/plots/speedup.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfica guardada: results/plots/speedup. png")


def plot_efficiency(results):
    """
    Gráfica 3: Efficiency vs Number of Workers
    """
    sizes = [r['size'] for r in results]
    
    efficiency_data = {}  
    
    for result in results:
        size = result['size']
        efficiency_data[size] = {}
        
        for test in result['tests']:
            if 'MapReduce' in test['name'] and 'efficiency' in test: 
                workers = test['num_workers']
                efficiency_data[size][workers] = test['efficiency']
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    markers = ['o', 's', '^', 'D']
    
    for idx, size in enumerate(sizes):
        workers_list = sorted(efficiency_data[size].keys())
        efficiencies = [efficiency_data[size][w] * 100 for w in workers_list]
        
        ax. plot(workers_list, efficiencies, f'{markers[idx]}-',
                label=f'{size}×{size}',
                linewidth=2.5, markersize=10,
                color=colors[idx % len(colors)])
    
    ax.axhline(y=100, color='k', linestyle='--', 
               label='Ideal (100%)', linewidth=2, alpha=0.5)
    
    ax.set_xlabel('Number of Workers', fontsize=14, fontweight='bold')
    ax.set_ylabel('Efficiency (%)', fontsize=14, fontweight='bold')
    ax.set_title('Parallel Efficiency vs Number of Workers',
                 fontsize=16, fontweight='bold', pad=20)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks([1, 2, 4, 8])
    ax.set_ylim([0, 110])
    
    plt.tight_layout()
    plt.savefig('results/plots/efficiency.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfica guardada:  results/plots/efficiency.png")


def plot_overhead(results):
    """
    Gráfica 4: Communication Overhead (Shuffle Time)
    """
    sizes = [r['size'] for r in results]
    
    overhead_data = {}  
    
    for result in results:
        size = result['size']
        
        for test in result['tests']: 
            if 'MapReduce' in test['name']:
                workers = test['num_workers']
                metrics = test['metrics']
                
                if 'overhead_percentage' in metrics:
                    if workers not in overhead_data: 
                        overhead_data[workers] = {}
                    overhead_data[workers][size] = metrics['overhead_percentage']
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    colors = ['#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    markers = ['^', 'D', 'v', 'p']
    
    for idx, (workers, data) in enumerate(sorted(overhead_data.items())):
        size_list = sorted(data.keys())
        overheads = [data[s] for s in size_list]
        
        ax.plot(size_list, overheads, f'{markers[idx]}-',
                label=f'{workers} workers',
                linewidth=2.5, markersize=10,
                color=colors[idx % len(colors)])
    
    ax.set_xlabel('Matrix Size (n×n)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Communication Overhead (%)', fontsize=14, fontweight='bold')
    ax.set_title('Communication Overhead vs Matrix Size',
                 fontsize=16, fontweight='bold', pad=20)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('results/plots/overhead.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfica guardada:  results/plots/overhead.png")


def plot_phase_breakdown(results):
    """
    Gráfica 5:  Breakdown de tiempos por fase (Map, Shuffle, Reduce)
    """
    last_result = results[-1]
    size = last_result['size']
    
    workers_list = []
    map_times = []
    shuffle_times = []
    reduce_times = []
    
    for test in last_result['tests']: 
        if 'MapReduce' in test['name']:
            metrics = test['metrics']
            workers_list.append(test['num_workers'])
            map_times.append(metrics.get('map_time', 0))
            shuffle_times.append(metrics.get('shuffle_time', 0))
            reduce_times.append(metrics.get('reduce_time', 0))
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    x = np.arange(len(workers_list))
    width = 0.6
    
    p1 = ax.bar(x, map_times, width, label='Map Phase', color='#3498db')
    p2 = ax.bar(x, shuffle_times, width, bottom=map_times, 
                label='Shuffle Phase (Communication)', color='#e74c3c')
    p3 = ax.bar(x, reduce_times, width, 
                bottom=np.array(map_times) + np.array(shuffle_times),
                label='Reduce Phase', color='#2ecc71')
    
    ax.set_xlabel('Number of Workers', fontsize=14, fontweight='bold')
    ax.set_ylabel('Time (seconds)', fontsize=14, fontweight='bold')
    ax.set_title(f'Phase Breakdown for {size}×{size} Matrix',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(workers_list)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    plt.tight_layout()
    plt.savefig('results/plots/phase_breakdown.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfica guardada:  results/plots/phase_breakdown. png")


def generate_all_plots(results_file='results/metrics.json'):
    """Genera todas las gráficas"""
    print("\n" + "=" * 80)
    print("GENERANDO GRÁFICAS")
    print("=" * 80)
    
    print(f"\nCargando resultados desde:  {results_file}")
    results = load_results(results_file)
    print(f"✓ Cargados {len(results)} conjuntos de resultados")
    
    os.makedirs('results/plots', exist_ok=True)
    
    print("\nGenerando gráficas...")
    plot_scalability(results)
    plot_speedup(results)
    plot_efficiency(results)
    plot_overhead(results)
    plot_phase_breakdown(results)
    
    print("\n" + "=" * 80)
    print("✓ TODAS LAS GRÁFICAS GENERADAS")
    print("=" * 80)
    print("\nGráficas disponibles en: results/plots/")
    print("  - scalability.png")
    print("  - speedup.png")
    print("  - efficiency.png")
    print("  - overhead.png")
    print("  - phase_breakdown.png")


if __name__ == "__main__":
    try:
        generate_all_plots()
    except FileNotFoundError:
        print("\nError: No se encontró el archivo results/metrics.json")
        print("Primero debes ejecutar:  python benchmark.py")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()