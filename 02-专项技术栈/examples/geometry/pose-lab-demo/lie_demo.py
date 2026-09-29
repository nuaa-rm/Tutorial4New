"""指数/对数、左右乘和BCH一阶近似，全部核对实际旋转。"""
import json
import cv2
import numpy as np
from model import pose
from lie import hat, exp3, exp6, left_jacobian

phi = np.array([.3, -.2, .1]); R = exp3(phi)
assert np.allclose(R, cv2.Rodrigues(phi)[0])
assert np.allclose(hat([1., 2., 3.]) @ [2., 0., 1.], np.cross([1., 2., 3.], [2., 0., 1.]))
rotated = exp3([0., 0., np.pi/2]) @ [1., 0., 0.]
assert np.allclose(rotated, [0, 1, 0])
delta = np.array([1e-5, -2e-5, 1e-5])
log = lambda matrix: cv2.Rodrigues(matrix)[0].ravel()
left = log(exp3(delta) @ R)
right = log(R @ exp3(delta))
left_prediction = phi+np.linalg.solve(left_jacobian(phi), delta)
right_prediction = phi+np.linalg.solve(left_jacobian(-phi), delta)
left_error = float(np.linalg.norm(left-left_prediction))
right_error = float(np.linalg.norm(right-right_prediction))
assert max(left_error, right_error)<1e-9
T = exp6(np.r_[[1., 0., 0.], [0., 0., np.pi/2]])
rho = np.linalg.solve(left_jacobian(log(T[:3, :3])), T[:3, 3])
assert np.allclose(rho, [1, 0, 0])
pi_rotation = exp3([0., 0., np.pi])
assert np.allclose(exp3(log(pi_rotation)), pi_rotation)
broken = R+hat([.01, .02, .03])
print(json.dumps({"quarter_turn": rotated.tolist(), "se3_translation": T[:3, 3].tolist(),
    "left_bch_error": left_error, "right_bch_error": right_error,
    "left_right_difference": float(np.linalg.norm(left-right)),
    "element_add_orthogonality_error": float(np.linalg.norm(broken.T @ broken-np.eye(3)))}))
