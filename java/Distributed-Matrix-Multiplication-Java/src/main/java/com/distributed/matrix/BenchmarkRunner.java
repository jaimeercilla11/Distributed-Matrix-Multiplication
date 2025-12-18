package com.distributed.matrix;

import com.google.gson.Gson;
import com. google.gson.GsonBuilder;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class BenchmarkRunner {

    public static void main(String[] args) {
        System.out.println("================================================================================");
        System.out.println("COMPLETE BENCHMARK - Distributed Matrix Multiplication (Java + Hazelcast)");
        System.out.println("================================================================================");

        int[] sizes = {128, 256, 512, 1024};
        int[] workerCounts = {1, 2, 4, 8};

        int availableCores = Runtime.getRuntime().availableProcessors();
        System.out.println("\nAvailable CPU cores: " + availableCores);
        System.out.println("Matrix sizes to test: " + arrayToString(sizes));
        System.out.println("Worker counts to test: " + arrayToString(workerCounts));

        List<Map<String, Object>> allResults = new ArrayList<>();

        for (int size : sizes) {
            try {
                Map<String, Object> sizeResults = benchmarkMatrixSize(size, workerCounts);
                allResults.add(sizeResults);
            } catch (Exception e) {
                System.err.println("\nError with size " + size + ": " + e.getMessage());
                e.printStackTrace();
            }
        }

        if (! allResults.isEmpty()) {
            saveResults(allResults);
            printSummary(allResults);
        }

        System.out.println("\nBENCHMARK COMPLETED");
        System.out.println("\nResults saved to: results/metrics.json");
    }

    private static Map<String, Object> benchmarkMatrixSize(int size, int[] workerCounts) throws Exception {
        System.out.println("\n================================================================================");
        System.out. println("BENCHMARK - " + size + "x" + size + " Matrices");
        System.out. println("================================================================================");

        System.out.println("\nCreating matrices...");
        double[][] A = MatrixUtils.createMatrix(size, 1.5);
        double[][] B = MatrixUtils.createMatrix(size, 2.5);

        List<Map<String, Object>> tests = new ArrayList<>();

        System.out.println("\n  Executing Basic (sequential)...");
        BenchmarkResult basicResult = BasicMatrixMultiplier.benchmark(A, B);
        System.out.println("    " + basicResult);
        tests.add(resultToMap(basicResult, 0));

        double baselineTime = basicResult.getExecutionTime();

        System.out.println("\n  Executing Optimized (cache-friendly)...");
        BenchmarkResult optimizedResult = OptimizedMatrixMultiplier. benchmark(A, B);
        System.out.println("    " + optimizedResult);
        tests.add(resultToMap(optimizedResult, baselineTime));

        for (int workers : workerCounts) {
            System.out.println("\n  Executing Hazelcast (" + workers + " workers)...");

            DistributedMatrixMultiplier multiplier = new DistributedMatrixMultiplier(workers);
            try {
                BenchmarkResult hazelcastResult = multiplier.benchmark(A, B);
                System.out.println("    " + hazelcastResult);

                Map<String, Object> resultMap = resultToMap(hazelcastResult, baselineTime);
                resultMap.put("speedup", baselineTime / hazelcastResult. getExecutionTime());
                resultMap.put("efficiency", (baselineTime / hazelcastResult. getExecutionTime()) / workers);

                tests.add(resultMap);
            } finally {
                multiplier.shutdown();
            }
        }

        Map<String, Object> sizeResults = new HashMap<>();
        sizeResults.put("size", (double) size);
        sizeResults. put("tests", tests);

        return sizeResults;
    }

    private static Map<String, Object> resultToMap(BenchmarkResult result, double baselineTime) {
        Map<String, Object> map = new HashMap<>();
        map.put("name", result.getName());
        map.put("total_time", result.getExecutionTime());
        map.put("memory_mb", result.getMemoryUsedMB());
        map.put("num_workers", result.getNumWorkers());

        if (baselineTime > 0) {
            map.put("speedup", result.getSpeedup(baselineTime));
        }

        return map;
    }

    private static void saveResults(List<Map<String, Object>> results) {
        try {
            new java.io.File("results").mkdirs();

            Gson gson = new GsonBuilder().setPrettyPrinting().create();
            FileWriter writer = new FileWriter("results/metrics.json");
            gson.toJson(results, writer);
            writer.close();

            System.out.println("\nResults saved to: results/metrics.json");
        } catch (IOException e) {
            System. err.println("Error saving results: " + e.getMessage());
        }
    }

    private static void printSummary(List<Map<String, Object>> allResults) {
        System.out.println("\n================================================================================");
        System.out.println("GENERAL SUMMARY");
        System.out.println("================================================================================");

        System.out.printf("\n%-10s %-30s %-12s %-10s %-12s%n",
                "Size", "Method", "Time (s)", "Speedup", "Efficiency");
        System.out.println("--------------------------------------------------------------------------------");

        for (Map<String, Object> sizeResult : allResults) {
            // CORREGIDO: Usar Number en lugar de Double
            int size = ((Number) sizeResult.get("size")).intValue();

            @SuppressWarnings("unchecked")
            List<Map<String, Object>> tests = (List<Map<String, Object>>) sizeResult.get("tests");

            // CORREGIDO: También usar Number para total_time
            double baseline = ((Number) tests.get(0).get("total_time")).doubleValue();

            for (Map<String, Object> test :  tests) {
                String name = (String) test.get("name");
                double time = ((Number) test.get("total_time")).doubleValue();
                double speedup = baseline / time;

                String efficiencyStr = "-";
                if (test.containsKey("efficiency")) {
                    double efficiency = ((Number) test.get("efficiency")).doubleValue();
                    efficiencyStr = String.format("%.2f%%", efficiency * 100);
                }

                System.out.printf("%-10d %-30s %-12.4f %-10.2fx %-12s%n",
                        size, name, time, speedup, efficiencyStr);
            }

            System. out.println();
        }
    }

    private static String arrayToString(int[] array) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < array.length; i++) {
            sb.append(array[i]);
            if (i < array.length - 1) sb.append(", ");
        }
        sb.append("]");
        return sb.toString();
    }
}