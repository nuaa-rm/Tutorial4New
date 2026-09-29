"""堆叠未来状态；第i行块对应x[k+i+1]。"""
import numpy as np

def prediction(A, B, horizon):
    if not isinstance(horizon, int) or horizon < 1:
        raise ValueError("horizon须为正整数")
    n = A.shape[0]
    Phi = np.zeros((n*horizon, n))
    Theta = np.zeros((n*horizon, horizon))
    for i in range(horizon):
        Phi[n*i:n*(i+1)] = np.linalg.matrix_power(A, i+1)
        for j in range(i+1):
            Theta[n*i:n*(i+1), j] = (np.linalg.matrix_power(A, i-j) @ B)[:, 0]
    return Phi, Theta
