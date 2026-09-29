"""消去路标增量，再回代；仅演示当前阻尼正规方程。"""
import numpy as np

def solve(H, g, camera_size):
    A = H[:camera_size, :camera_size]; B = H[:camera_size, camera_size:]
    C = H[camera_size:, camera_size:]
    c = g[:camera_size]; p = g[camera_size:]
    X = np.linalg.solve(C, B.T); y = np.linalg.solve(C, p)
    camera = np.linalg.solve(A-B @ X, c-B @ y)
    landmark = np.linalg.solve(C, p-B.T @ camera)
    return np.r_[camera, landmark]
