"""只维护连接归属与有界状态槽；不负责事件确认或后台重连。"""
from threading import Lock


class Session:
    priority = ("position", "status")

    def __init__(self):
        self.lock = Lock()
        self.generation = 0
        self.connection = None
        self.slots = {}
        self.expired = 0

    def connect(self, connection):
        with self.lock:
            old = self.connection
            self.generation += 1
            self.connection = connection
            self.slots.clear()
            generation = self.generation
        if old is not None:
            old.close()  # 只关闭刚才取出的旧对象
        return generation

    def put(self, generation, command, value, at):
        if command not in self.priority:
            raise ValueError("未知状态类型，不能无限添加槽位")
        with self.lock:
            if generation != self.generation or self.connection is None:
                return False
            self.slots[command] = (value, at)
            return True

    def take(self, generation, now, max_age):
        with self.lock:
            if generation != self.generation or self.connection is None:
                return None
            for command in self.priority:
                sample = self.slots.pop(command, None)
                if sample is None:
                    continue
                value, at = sample
                if now - at > max_age:
                    self.expired += 1
                    continue
                return command, value
            return None

    def disconnect(self, generation):
        with self.lock:
            if generation != self.generation or self.connection is None:
                return False
            old = self.connection
            self.connection = None
            self.slots.clear()
        old.close()
        return True
