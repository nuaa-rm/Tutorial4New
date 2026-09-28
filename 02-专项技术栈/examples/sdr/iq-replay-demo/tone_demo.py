"""复数正、负频率及混叠；幅值相同不等于信号相同。"""
import numpy as np

fs, count = 8000, 32
n = np.arange(count)
for frequency in [1000, -1000, 9000]:
    iq = np.exp(2j * np.pi * frequency * n / fs)
    step = np.angle(iq[1] * iq[0].conjugate())
    print("频率", frequency, "幅值", round(abs(iq[0]), 6),
          "相位差", round(float(step), 6))
    if frequency == 9000:
        assert np.allclose(iq, np.exp(2j * np.pi * 1000 * n / fs))
