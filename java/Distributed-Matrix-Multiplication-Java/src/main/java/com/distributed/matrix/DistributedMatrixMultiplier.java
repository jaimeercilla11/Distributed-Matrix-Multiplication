package com.distributed.matrix;

import com.hazelcast.config.Config;
import com.hazelcast.core. Hazelcast;
import com. hazelcast.core.HazelcastInstance;
import com. hazelcast.map.IMap;
import com.hazelcast.core.IExecutorService;

import java.io. Serializable;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Future;

public class DistributedMatrixMultiplier {

    private HazelcastInstance hazelcastInstance;
    private int numWorkers;

    public DistributedMatrixMultiplier(int numWorkers) {
        this.numWorkers = numWorkers;

        Config config = new Config();
        config.setClusterName("matrix-cluster");
        config.getNetworkConfig().getJoin().getMulticastConfig().setEnabled(false);
        config.getNetworkConfig().getJoin().getTcpIpConfig().setEnabled(true).addMember("127.0.0.1");

        System.setProperty("hazelcast. logging.type", "none");

        this.hazelcastInstance = Hazelcast.newHazelcastInstance(config);
    }

    public double[][] multiply(double[][] A, double[][] B) throws Exception {
        int n = A.length;
        int m = B[0].length;

        IMap<String, double[][]> distributedData = hazelcastInstance.getMap("matrices");
        distributedData.put("A", A);
        distributedData.put("B", B);

        int blockSize = Math.max(1, n / numWorkers);

        IExecutorService executor = hazelcastInstance.getExecutorService("matrix-executor");

        List<Future<BlockResult>> futures = new ArrayList<>();

        for (int workerId = 0; workerId < numWorkers; workerId++) {
            int startRow = workerId * blockSize;
            int endRow = (workerId == numWorkers - 1) ? n : (workerId + 1) * blockSize;

            if (startRow < n) {
                MatrixBlockTask task = new MatrixBlockTask(startRow, endRow, n, m);
                Future<BlockResult> future = executor.submit(task);
                futures.add(future);
            }
        }

        double[][] C = new double[n][m];

        for (Future<BlockResult> future : futures) {
            BlockResult blockResult = future.get();

            for (int i = blockResult.startRow; i < blockResult.endRow; i++) {
                System.arraycopy(
                        blockResult.data[i - blockResult.startRow],
                        0,
                        C[i],
                        0,
                        m
                );
            }
        }

        return C;
    }

    public BenchmarkResult benchmark(double[][] A, double[][] B) throws Exception {
        MatrixUtils.gc();
        double memBefore = MatrixUtils.getMemoryUsageMB();

        long startTime = System. nanoTime();
        double[][] result = multiply(A, B);
        long endTime = System. nanoTime();

        double memAfter = MatrixUtils.getMemoryUsageMB();
        double executionTime = (endTime - startTime) / 1_000_000_000.0;
        double memoryUsed = memAfter - memBefore;

        return new BenchmarkResult(
                "Hazelcast (" + numWorkers + " workers)",
                executionTime,
                memoryUsed,
                numWorkers,
                result
        );
    }

    public void shutdown() {
        if (hazelcastInstance != null) {
            hazelcastInstance. shutdown();
        }
    }

    static class MatrixBlockTask implements Callable<BlockResult>, Serializable {
        private static final long serialVersionUID = 1L;

        private int startRow;
        private int endRow;
        private int n;
        private int m;

        public MatrixBlockTask(int startRow, int endRow, int n, int m) {
            this.startRow = startRow;
            this.endRow = endRow;
            this.n = n;
            this.m = m;
        }

        @Override
        public BlockResult call() throws Exception {
            HazelcastInstance hz = Hazelcast.getAllHazelcastInstances().iterator().next();
            IMap<String, double[][]> distributedData = hz.getMap("matrices");

            double[][] A = distributedData.get("A");
            double[][] B = distributedData.get("B");

            int blockRows = endRow - startRow;
            double[][] blockResult = new double[blockRows][m];

            for (int i = 0; i < blockRows; i++) {
                int globalRow = startRow + i;
                for (int j = 0; j < m; j++) {
                    double sum = 0.0;
                    for (int k = 0; k < n; k++) {
                        sum += A[globalRow][k] * B[k][j];
                    }
                    blockResult[i][j] = sum;
                }
            }

            return new BlockResult(startRow, endRow, blockResult);
        }
    }

    static class BlockResult implements Serializable {
        private static final long serialVersionUID = 1L;

        int startRow;
        int endRow;
        double[][] data;

        public BlockResult(int startRow, int endRow, double[][] data) {
            this. startRow = startRow;
            this.endRow = endRow;
            this.data = data;
        }
    }
}