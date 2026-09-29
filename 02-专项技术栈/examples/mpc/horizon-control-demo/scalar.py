"""保留原来能手算的一步优化，再比较重新规划与旧序列。"""
import json

def control(y, weight=1., limit=.2):
    return max(-limit, min(limit, (1-y)/(1+weight)))

def roll(disturb=False, old=None):
    y = 0.; values = []; controls = []
    for k in range(6):
        u = control(y) if old is None else old[k]
        y += u
        if disturb and k == 2: y -= .1
        controls.append(u); values.append(y)
    return {"controls": controls, "states": values}

if __name__ == "__main__":
    base = roll(); closed = roll(True); copied = roll(True, base["controls"])
    u = control(0.)
    print(json.dumps({"bounded_u": u, "cost": (1-u)**2+u*u,
                      "weight9_u": control(0., 9.), "base": base,
                      "feedback": closed, "old_sequence": copied}))
