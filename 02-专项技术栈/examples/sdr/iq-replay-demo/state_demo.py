"""离线 profile 切换与数据源取舍；采用同一个逻辑时钟。"""
from dataclasses import dataclass

PROFILES = {"level1": (1_000_000, 200_000),
            "level2": (1_000_000, 300_000),
            "information": (1_000_000, 400_000)}
TRANSITIONS = {("level1", "ok1"): "level2",
               ("level2", "ok2"): "information"}


@dataclass
class Stages:
    state: str = "level1"
    generation: int = 0

    def handle(self, event):
        target = "level1" if event == "reset" else TRANSITIONS.get(
            (self.state, event), self.state)
        if target != self.state or event == "reset":
            self.generation += 1  # 实机在此清空旧缓冲并重新配置。
        self.state = target
        return self.state, self.generation, PROFILES[self.state]


def select_source(now, sources, ttl=0.2):
    for name, stamp, coordinate in sources:
        if 0 <= now - stamp <= ttl:
            return name, coordinate
    return None


if __name__ == "__main__":
    stages = Stages()
    for event in ["ok2", "ok1", "timeout", "ok2", "reset"]:
        print(event, "->", stages.handle(event))
    sources = [("radio", 9.7, (1.25, 2.5)),
               ("vision", 9.9, (1.1, 2.4))]
    print("10.0 秒:", select_source(10.0, sources))
    print("11.0 秒:", select_source(11.0, sources))
    assert select_source(10.0, sources)[0] == "vision"
    assert select_source(11.0, sources) is None
