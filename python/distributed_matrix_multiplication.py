import multiprocessing as mp
import time
import psutil
import os
from collections import defaultdict

class MapReduceMatrixMultiplier:
    def __init__(self, num_workers=4):
        self.num_workers = num_workers
        self.pool = None
        
    def __enter__(self):
        self.pool = mp.Pool(processes=self.num_workers)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pool:
            self.pool.close()
            self.pool.join()
    
    @staticmethod
    def map_worker(args):
        A_block, B, block_id, start_row = args
        results = []
        
        for local_i, row_A in enumerate(A_block):
            global_i = start_row + local_i
            for j in range(len(B[0])):
                partial_sum = sum(row_A[k] * B[k][j] for k in range(len(row_A)))
                results.append(((global_i, j), partial_sum))
        
        return results
    
    def shuffle_phase(self, map_results):
        shuffled = defaultdict(list)
        
        for result_list in map_results:
            for key, value in result_list:
                shuffled[key].append(value)
        
        return shuffled
    
    @staticmethod
    def reduce_worker(args):
        key, values = args
        return (key, sum(values))
    
    def multiply(self, A, B, measure_overhead=True):
        n = len(A)
        m = len(B[0])
        
        block_size = max(1, n // self.num_workers)
        
        metrics = {}
        
        if measure_overhead:
            start_map = time.time()
        
        map_tasks = []
        for block_id in range(self.num_workers):
            start_row = block_id * block_size
            end_row = min(start_row + block_size, n)
            
            if start_row < n:
                A_block = A[start_row:end_row]
                map_tasks.append((A_block, B, block_id, start_row))
        
        map_results = self.pool.map(self.map_worker, map_tasks)
        
        if measure_overhead:
            metrics['map_time'] = time. time() - start_map
        
        if measure_overhead:
            start_shuffle = time.time()
        
        shuffled = self.shuffle_phase(map_results)
        
        if measure_overhead:
            metrics['shuffle_time'] = time.time() - start_shuffle
        
        if measure_overhead:
            start_reduce = time.time()
        
        reduce_tasks = list(shuffled.items())
        
        reduced_results = self.pool.map(self.reduce_worker, reduce_tasks)
        
        if measure_overhead:
            metrics['reduce_time'] = time.time() - start_reduce
        
        C = [[0.0 for _ in range(m)] for _ in range(n)]
        
        for (i, j), value in reduced_results:
            C[i][j] = value
        
        if measure_overhead:
            metrics['total_time'] = sum([
                metrics['map_time'],
                metrics['shuffle_time'],
                metrics['reduce_time']
            ])
            metrics['computation_time'] = metrics['map_time'] + metrics['reduce_time']
            metrics['communication_overhead'] = metrics['shuffle_time']
            metrics['overhead_percentage'] = (
                metrics['communication_overhead'] / metrics['total_time']
            ) * 100
        
        return C, metrics

class ParallelMatrixMultiplier:
    def __init__(self, num_workers=4):
        self.num_workers = num_workers
        self.pool = None
        
    def __enter__(self):
        self.pool = mp.Pool(processes=self.num_workers)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.pool:
            self.pool. close()
            self.pool. join()
    
    @staticmethod
    def multiply_row_block(args):
        A_block, B, start_row = args
        results = []
        
        for local_i, row_A in enumerate(A_block):
            global_i = start_row + local_i
            row_result = []
            for j in range(len(B[0])):
                value = sum(row_A[k] * B[k][j] for k in range(len(row_A)))
                row_result.append(value)
            results.append((global_i, row_result))
        
        return results
    
    def multiply(self, A, B):
        n = len(A)
        m = len(B[0])
        
        start_time = time.time()
        
        block_size = max(1, n // self.num_workers)
        
        tasks = []
        for block_id in range(self.num_workers):
            start_row = block_id * block_size
            end_row = min(start_row + block_size, n)
            
            if start_row < n:
                A_block = A[start_row:end_row]
                tasks.append((A_block, B, start_row))
        
        results = self. pool.map(self.multiply_row_block, tasks)
        
        C = [[0.0 for _ in range(m)] for _ in range(n)]
        
        for block_result in results:
            for i, row in block_result:
                C[i] = row
        
        total_time = time.time() - start_time
        
        return C, {'total_time': total_time}

class BasicMatrixMultiplier:
    @staticmethod
    def multiply(A, B):
        """Multiplicación básica O(n³) - método ijk"""
        n = len(A)
        m = len(B[0])
        p = len(B)
        
        C = [[0.0 for _ in range(m)] for _ in range(n)]
        
        start = time.time()
        
        for i in range(n):
            for j in range(m):
                for k in range(p):
                    C[i][j] += A[i][k] * B[k][j]
        
        elapsed = time.time() - start
        
        return C, {'total_time': elapsed}


class OptimizedMatrixMultiplier: 
    @staticmethod
    def multiply(A, B):
        n = len(A)
        m = len(B[0])
        
        C = [[0.0 for _ in range(m)] for _ in range(n)]
        
        start = time.time()
        
        for i in range(n):
            for k in range(len(A[0])):
                temp = A[i][k]
                for j in range(m):
                    C[i][j] += temp * B[k][j]
        
        elapsed = time.time() - start
        
        return C, {'total_time': elapsed}


def create_matrix(n, m=None, value=1.0):
    if m is None:
        m = n
    return [[value for _ in range(m)] for _ in range(n)]


def create_random_matrix(n, m=None, min_val=0.0, max_val=10.0):
    import random
    if m is None: 
        m = n
    return [[random.uniform(min_val, max_val) for _ in range(m)] for _ in range(n)]


def measure_memory():
    process = psutil.Process(os. getpid())
    return process.memory_info().rss / (1024 * 1024)  # MB


if __name__ == "__main__":   
    print("=" * 80)
    print("QUICK TEST - MapReduce Matrix Multiplication")
    print("=" * 80)
    
    size = 128
    print(f"\nCreating {size}×{size} matrices...")
    A = create_matrix(size, value=2.0)
    B = create_matrix(size, value=3.0)
    
    print("\nExecuting MapReduce with 4 workers...")
    with MapReduceMatrixMultiplier(num_workers=4) as multiplier:
        C, metrics = multiplier.multiply(A, B)
    
    print("\nResults:")
    print(f"  Map time:          {metrics['map_time']:.4f}s")
    print(f"  Shuffle time:     {metrics['shuffle_time']:.4f}s")
    print(f"  Reduce time:       {metrics['reduce_time']:.4f}s")
    print(f"  Total time:        {metrics['total_time']:.4f}s")
    print(f"  Overhead:         {metrics['overhead_percentage']:.2f}%")
    
    expected = 6.0 * size
    print(f"\n  Verification:  C[0][0] = {C[0][0]:.2f} (expected:  {expected:.2f})")
    print(f"  ✓ Correct" if abs(C[0][0] - expected) < 0.01 else "  ✗ Error")
    
    print("\n" + "=" * 80)