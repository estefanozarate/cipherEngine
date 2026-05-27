import os, time

MB = 1024 * 1024
n  = 128 * MB  # 128 MB de prueba

# Cuánto tarda solo os.urandom
t = time.perf_counter()
key = os.urandom(n)
print(f"os.urandom:  {n/MB/(time.perf_counter()-t):.1f} MB/s")

# Cuánto tarda solo el XOR
data = os.urandom(n)
t = time.perf_counter()
result = bytes(a ^ b for a, b in zip(data, key))
print(f"XOR puro:    {n/MB/(time.perf_counter()-t):.1f} MB/s")

# Cuánto tarda numpy XOR (mucho más rápido)
import numpy as np
a = np.frombuffer(data, dtype=np.uint8)
k = np.frombuffer(key,  dtype=np.uint8)
t = time.perf_counter()
result = np.bitwise_xor(a, k)
print(f"XOR numpy:   {n/MB/(time.perf_counter()-t):.1f} MB/s")

