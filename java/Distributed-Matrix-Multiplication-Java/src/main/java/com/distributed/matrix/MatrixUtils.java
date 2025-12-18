package com.distributed.matrix;

import java.util.Random;

public class MatrixUtils {

    public static double[][] createMatrix(int n, double value) {
        double[][] matrix = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                matrix[i][j] = value;
            }
        }
        return matrix;
    }

    public static double[][] createRandomMatrix(int n, double min, double max) {
        Random random = new Random();
        double[][] matrix = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                matrix[i][j] = min + (max - min) * random.nextDouble();
            }
        }
        return matrix;
    }

    public static boolean verifyResult(double[][] result, double expectedValue, int size) {
        double tolerance = 0.01;
        return Math.abs(result[0][0] - expectedValue) < tolerance;
    }

    public static void printMatrix(double[][] matrix, int maxRows, int maxCols) {
        int rows = Math.min(matrix.length, maxRows);
        int cols = Math.min(matrix[0].length, maxCols);

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                System.out.printf("%.2f ", matrix[i][j]);
            }
            System.out.println(i < rows - 1 ? "" : ".. .");
        }
    }

    public static double getMemoryUsageMB() {
        Runtime runtime = Runtime. getRuntime();
        return (runtime.totalMemory() - runtime.freeMemory()) / (1024.0 * 1024.0);
    }

    public static void gc() {
        System.gc();
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}