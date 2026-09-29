"""独立中心差分：位姿按左乘扰动，点按世界坐标相加。"""
import json
import numpy as np
from model import pose, project
from residual import jacobians
from lie import exp6

T = pose([.1, -.2, .05], [.1, -.1, 2.])
point = np.array([.2, .1, .3]); eps = 1e-6
Jpose, Jpoint = jacobians(point, T)
numeric_pose = np.empty((2, 6)); numeric_point = np.empty((2, 3))
for i in range(6):
    delta = np.eye(6)[i]*eps
    numeric_pose[:, i] = -(project(point[None], exp6(delta) @ T)-
                          project(point[None], exp6(-delta) @ T))[0]/(2*eps)
for i in range(3):
    delta = np.eye(3)[i]*eps
    numeric_point[:, i] = -(project((point+delta)[None], T)-
                           project((point-delta)[None], T))[0]/(2*eps)
errors = [float(np.max(abs(Jpose-numeric_pose))), float(np.max(abs(Jpoint-numeric_point)))]
assert max(errors) < 1e-6
print(json.dumps({"pose_max_error": errors[0], "point_max_error": errors[1]}))
