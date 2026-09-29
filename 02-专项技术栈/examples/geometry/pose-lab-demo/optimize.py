"""小规模阻尼位姿优化；接受步骤前核对实际代价和正深度。"""
import numpy as np
from residual import residual, jacobians
from lie import exp6

def cost(error, huber):
    norm = np.linalg.norm(error, axis=1)
    if huber <= 0: return .5*np.sum(norm**2)
    return np.sum(np.where(norm <= huber, .5*norm**2, huber*(norm-.5*huber)))

def optimize(points, observed, initial, huber=0., iterations=40):
    T = initial.copy(); damping = 1e-3; history = []
    for _ in range(iterations):
        error = residual(points, observed, T)
        value = float(cost(error, huber)); history.append(value)
        weight = np.ones(len(points)) if huber <= 0 else np.minimum(
            1., huber/np.maximum(np.linalg.norm(error, axis=1), 1e-12))
        J = np.vstack([jacobians(p, T)[0] for p in points])
        root = np.repeat(np.sqrt(weight), 2)
        J = J*root[:, None]; e = error.ravel()*root
        H = J.T @ J; g = -J.T @ e
        diagonal = np.maximum(np.diag(H), 1.)
        delta = np.linalg.solve(H+damping*np.diag(diagonal), g)
        candidate = exp6(delta) @ T
        try: proposed = float(cost(residual(points, observed, candidate), huber))
        except ValueError: proposed = np.inf
        if proposed < value:
            T = candidate; damping = max(damping/3, 1e-12)
            if np.linalg.norm(delta) < 1e-10: break
        else:
            damping *= 10
            if damping > 1e12: break
    history.append(float(cost(residual(points, observed, T), huber)))
    return T, history
