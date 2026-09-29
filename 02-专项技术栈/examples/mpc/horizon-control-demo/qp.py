"""完整有限时域QP：加速度/预测角速度约束，可选硬终点。"""
import numpy as np
from scipy import sparse
import osqp
from model import model
from prediction import prediction

def solve(state, reference, dt=.05, horizon=15, q=20., r=.1,
          amax=2., vmax=.8, terminal=False, max_iter=4000):
    state = np.asarray(state, dtype=float)
    if state.shape != (2,) or not np.isfinite(state).all():
        raise ValueError("状态必须是两个有限数")
    if not np.isfinite([reference, q, r, amax, vmax]).all():
        raise ValueError("参考与参数须有限")
    if min(q, r, amax, vmax) <= 0 or max_iter < 1:
        raise ValueError("权重、上限与迭代数须为正")
    A, B = model(dt); Phi, Theta = prediction(A, B, horizon)
    desired = np.tile([reference, 0.], horizon)
    weights = np.tile([q, .5], horizon)  # 角速度回到0的软代价。
    offset = Phi @ state
    H = 2*(Theta.T @ (weights[:, None]*Theta)+r*np.eye(horizon))
    g = 2*Theta.T @ (weights*(offset-desired))
    D = np.vstack([np.eye(horizon), Theta[1::2]])
    lower = np.r_[np.full(horizon, -amax), -vmax-offset[1::2]]
    upper = np.r_[np.full(horizon, amax), vmax-offset[1::2]]
    if terminal:
        D = np.vstack([D, Theta[-2]])
        value = reference-offset[-2]
        lower = np.r_[lower, value]; upper = np.r_[upper, value]
    solver = osqp.OSQP()
    solver.setup(P=sparse.csc_matrix(H), q=g, A=sparse.csc_matrix(D),
                 l=lower, u=upper, verbose=False, polishing=False,
                 eps_abs=1e-7, eps_rel=1e-7, max_iter=max_iter)
    result = solver.solve(raise_error=False)
    valid = result.info.status_val == 1 and np.isfinite(result.x).all()
    violation = None
    if valid:
        values = D @ result.x
        violation = float(max(0., np.max(lower-values), np.max(values-upper)))
    return {"U": result.x if valid else None, "violation": violation,
            "status": result.info.status, "status_val": result.info.status_val,
            "solver_ms": result.info.run_time*1000, "iterations": result.info.iter,
            "Phi": Phi, "Theta": Theta, "weights": weights,
            "desired": desired, "H": H, "g": g}
