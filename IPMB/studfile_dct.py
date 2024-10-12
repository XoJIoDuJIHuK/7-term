import numpy as np
import math

N = 8

def zeta(x):
    return 0.5 ** 0.5 if x == 0 else 1

def dct(block, **kwargs):
    omega = np.zeros((N, N))
    for u in range(8):
        for v in range(8):
            temp = 0
            for x in range(N):
                for y in range(N):
                    temp += (
                        block[x][y] * 
                        math.cos(x * u * (2 * x + 1) / 2 / N) * 
                        math.cos(x * v * (2 * y + 1) / 2 / N)
                    )
            omega[u][v] = zeta(u) * zeta(v) / (2 * N) ** 0.5 * temp
    return omega

def idct(coeffs, **kwargs):
    c = np.zeros((N, N))
    for x in range(8):
        for y in range(8):
            temp = 0
            for u in range(N):
                for v in range(N):
                    temp += (
                        zeta(u) * zeta(v) * coeffs[u][v] *
                        math.cos(x * u * (2 * x + 1) / 2 / N) *
                        math.cos(x * v * (2 * y + 1) / 2 / N)
                    )
            c[u][v] = 1 / (2 * N) ** 0.5 * temp
    return c