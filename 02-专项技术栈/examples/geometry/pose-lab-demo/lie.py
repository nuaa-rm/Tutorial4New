"""六维顺序为 [rho, phi]；左乘扰动，rho并非总等于最终t。"""
import numpy as np

def hat(a):
    x, y, z = np.asarray(a)
    return np.array([[0., -z, y], [z, 0., -x], [-y, x, 0.]])

def coefficients(phi):
    theta = np.linalg.norm(phi)
    if theta < 1e-4:
        s = theta*theta
        return 1-s/6+s*s/120, .5-s/24+s*s/720, 1/6-s/120+s*s/5040
    return (np.sin(theta)/theta, (1-np.cos(theta))/theta**2,
            (theta-np.sin(theta))/theta**3)

def exp3(phi):
    A, B, _ = coefficients(phi); W = hat(phi)
    return np.eye(3)+A*W+B*(W @ W)

def left_jacobian(phi):
    _, B, C = coefficients(phi); W = hat(phi)
    return np.eye(3)+B*W+C*(W @ W)

def exp6(xi):
    rho, phi = np.asarray(xi)[:3], np.asarray(xi)[3:]
    T = np.eye(4); T[:3, :3] = exp3(phi)
    T[:3, 3] = left_jacobian(phi) @ rho
    return T
