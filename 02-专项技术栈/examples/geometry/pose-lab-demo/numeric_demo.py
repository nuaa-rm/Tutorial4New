"""分开核对RQ内外参分离与SVD旋转投影。"""
import json
import cv2
import numpy as np
from dlt import rotation_projection

K = np.array([[800., 10, 320], [0, 820, 240], [0, 0, 1]])
R = cv2.Rodrigues(np.array([.1, .2, .3]))[0]
M = K @ R
_, recovered_K, recovered_R, *_ = cv2.RQDecomp3x3(M)
assert np.allclose(recovered_K @ recovered_R, M)
assert np.allclose(recovered_K, K) and np.allclose(recovered_R, R)
Q, upper = np.linalg.qr(M)
assert np.allclose(Q @ upper, M)
reflection = np.diag([1., 1., -1.])
U, _, Vt = np.linalg.svd(reflection)
corrected = rotation_projection(reflection)
noisy = np.array([[1., .02, 0], [-.01, .99, 0], [0, .01, 1.01]])
projected = rotation_projection(noisy)
assert np.allclose(projected.T @ projected, np.eye(3))
assert abs(np.linalg.det(corrected)-1) < 1e-12
print(json.dumps({"rq_K": recovered_K.tolist(), "rq_det": float(np.linalg.det(recovered_R)),
    "qr_rotation_error": float(np.linalg.norm(Q-R)),
    "reflection_det": float(np.linalg.det(U @ Vt)),
    "corrected_det": float(np.linalg.det(corrected)),
    "projection_distance": float(np.linalg.norm(noisy-projected))}))
