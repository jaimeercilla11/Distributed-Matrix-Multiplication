package com.distributed.matrix;

public class OptimizedMatrixMultiplier {

    public static double[][] multiply(double[][] A, double[][] B) {
        int n = A.length;
        int m = B[0].length;

        double[][] C = new double[n][m];

        for (int i = 0; i < n; i++) {
            for (int k = 0; k < A[0].length; k++) {
                double temp = A[i][k];
                for (int j = 0; j < m; j++) {
                    C[i][j] += temp * B[k][j];
                }
            }
        }

        return C;
    }

    public static BenchmarkResult benchmark(double[][] A, double[][] B) {
        MatrixUtils.gc();
        double memBefore = MatrixUtils.getMemoryUsageMB();

        long startTime = System.nanoTime();
        double[][] result = multiply(A, B);
        long endTime = System.nanoTime();

        double memAfter = MatrixUtils.getMemoryUsageMB();
        double executionTime = (endTime - startTime) / 1_000_000_000.0;
        double memoryUsed = memAfter - memBefore;

        return new BenchmarkResult(
                "Optimized (cache-friendly)",
                executionTime,
                memoryUsed,
                1,
                result
        );
    }
}