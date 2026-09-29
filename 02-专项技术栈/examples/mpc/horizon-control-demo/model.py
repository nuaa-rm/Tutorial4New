"""单轴离线模型：角度rad、角速度rad/s、保持的加速度rad/s²。"""
import numpy as np

def model(dt):
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError("dt须有限且为正")
    A = np.array([[1., dt], [0., 1.]])
    B = np.array([[dt*dt/2], [dt]])
    return A, B

def step(state, control, dt, gain=1.):
    A, B = model(dt)
    state = np.asarray(state, dtype=float)
    if state.shape != (2,) or not np.isfinite(state).all():
        raise ValueError("状态必须是两个有限数")
    if not np.isfinite([control, gain]).all() or gain <= 0:
        raise ValueError("控制须有限，实际增益须为正")
    return A @ state + B[:, 0]*control*gain
