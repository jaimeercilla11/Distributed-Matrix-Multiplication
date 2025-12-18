package com.distributed.matrix;

public class BasicMatrixMultiplier {

    public static double[][] multiply(double[][] A, double[][] B) {
        int n = A.length;
        int m = B[0].length;
        int p = B.length;

        double[][] C = new double[n][m];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                double sum = 0.0;
                for (int k = 0; k < p; k++) {
                    sum += A[i][k] * B[k][j];
                }
                C[i][j] = sum;
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

        double memAfter = MatrixUtils. getMemoryUsageMB();
        double executionTime = (endTime - startTime) / 1_000_000_000.0;
        double memoryUsed = memAfter - memBefore;

        return new BenchmarkResult(
                "Basic (sequential)",
                executionTime,
                memoryUsed,
                1,
                result
        );
    }
}