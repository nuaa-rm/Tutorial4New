"""同一进程依次扮演本机 TCP 两端，累计收到四字节。"""
import socket
with socket.socket() as server:
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    with socket.create_connection(server.getsockname(), timeout=2) as client:
        conn, addr = server.accept()
        with conn:
            conn.settimeout(2)
            client.sendall(b"ping")
            data = bytearray()
            while len(data) < 4:
                part = conn.recv(4 - len(data))
                if not part:
                    raise EOFError("连接提前关闭")
                data.extend(part)
            print(data.decode())
