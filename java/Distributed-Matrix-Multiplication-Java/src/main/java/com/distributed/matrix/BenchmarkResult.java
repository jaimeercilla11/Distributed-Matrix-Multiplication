package com.distributed.matrix;

import java.io. Serializable;

public class BenchmarkResult implements Serializable {
    private static final long serialVersionUID = 1L;

    private String name;
    private double executionTime;
    private double memoryUsedMB;
    private int numWorkers;
    private double[][] result;

    public BenchmarkResult(String name, double executionTime, double memoryUsedMB,
                           int numWorkers, double[][] result) {
        this.name = name;
        this.executionTime = executionTime;
        this.memoryUsedMB = memoryUsedMB;
        this.numWorkers = numWorkers;
        this.result = result;
    }

    public String getName() { return name; }
    public double getExecutionTime() { return executionTime; }
    public double getMemoryUsedMB() { return memoryUsedMB; }
    public int getNumWorkers() { return numWorkers; }
    public double[][] getResult() { return result; }

    public double getSpeedup(double baselineTime) {
        return baselineTime / executionTime;
    }

    public double getEfficiency() {
        if (numWorkers <= 1) return 1.0;
        return getSpeedup(executionTime) / numWorkers;
    }

    @Override
    public String toString() {
        return String.format("%-30s | Time: %8.4fs | Memory: %8.2f MB | Workers: %d",
                name, executionTime, memoryUsedMB, numWorkers);
    }
}