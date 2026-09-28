"""两个终端运行的本机 TCP；客户端每次连接发两帧并接收回显。"""
import argparse
import socket
from framing import LengthParser, encode_length
from state import Session


def server(host, port, rounds):
    session = Session()
    previous = None
    with socket.socket() as listener:
        listener.bind((host, port))
        listener.listen(1)
        listener.settimeout(15)
        print("监听", listener.getsockname(), flush=True)
        for _ in range(rounds):
            connection, _ = listener.accept()
            connection.settimeout(3)
            generation = session.connect(connection)
            parser = LengthParser()  # 新连接不继承半帧
            if previous is not None:
                closed = session.disconnect(previous)
                print("迟到清理", previous, "实际清理:", closed, flush=True)
            try:
                while True:
                    chunk = connection.recv(2)
                    if not chunk:
                        print("断开，丢弃半帧字节:", len(parser.buffer), flush=True)
                        break
                    for payload in parser.feed(chunk):
                        connection.sendall(encode_length(payload))
                        print("代次", generation, "回显", payload, flush=True)
            except (ValueError, OSError) as error:
                print("本连接失败:", error, flush=True)
            finally:
                session.disconnect(generation)
                previous = generation


def client(host, port):
    with socket.create_connection((host, port), timeout=3) as connection:
        connection.sendall(encode_length(b"AB") + encode_length(b"XYZ"))
        connection.shutdown(socket.SHUT_WR)  # 发完了，仍可接收回显
        parser, frames = LengthParser(), []
        while True:
            chunk = connection.recv(2)
            if not chunk:
                break
            frames.extend(parser.feed(chunk))
        assert frames == [b"AB", b"XYZ"] and not parser.buffer
        print("收到回显:", frames)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("role", choices=["server", "client"])
    cli.add_argument("--host", default="127.0.0.1")
    cli.add_argument("--port", type=int, default=8765)
    cli.add_argument("--rounds", type=int, default=2)
    args = cli.parse_args()
    if args.role == "server":
        server(args.host, args.port, args.rounds)
    else:
        client(args.host, args.port)
