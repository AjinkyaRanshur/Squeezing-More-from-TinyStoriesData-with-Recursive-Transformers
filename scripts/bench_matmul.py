# scripts/bench_matmul.py
import time
import torch


def bench(n: int, dtype: torch.dtype, iters: int = 50) -> float:
    A = torch.randn(n, n, device="cuda", dtype=dtype)
    B = torch.randn(n, n, device="cuda", dtype=dtype)

    for _ in range(10):          # warm-up: kernel selection + GPU clock ramp-up
        A @ B
    torch.cuda.synchronize()

    t0 = time.perf_counter()
    for _ in range(iters):
        A @ B
    torch.cuda.synchronize()     # wait for the GPU to actually finish
    seconds = time.perf_counter() - t0

    flops_per_matmul = ...       # TODO: FLOPs for an (n x n) @ (n x n) matmul
    return flops_per_matmul * iters / seconds / 1e12


if __name__ == "__main__":
    for dtype in (torch.float32, torch.bfloat16):
        for n in (1024, 2048, 4096):
            print(f"{str(dtype):16} n={n:<5} {bench(n, dtype):7.2f} TFLOP/s")