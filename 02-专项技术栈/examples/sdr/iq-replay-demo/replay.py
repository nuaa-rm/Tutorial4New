"""生成与回放分开，保证回放真的从文件读取。"""
import argparse
from decode import decode
from record import load_record, save_record
from synth import synthesize


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("action", choices=["generate", "decode"])
    cli.add_argument("folder", help="录包目录")
    cli.add_argument("--x-mm", type=int, default=1250)
    cli.add_argument("--phase", type=float, default=0.7)
    cli.add_argument("--offset-hz", type=float, default=125)
    cli.add_argument("--noise", type=float, default=0.03)
    cli.add_argument("--corrupt", action="store_true")
    args = cli.parse_args()
    if args.action == "generate":
        iq, metadata = synthesize(args.x_mm, args.phase, args.offset_hz,
                                  args.noise, corrupt=args.corrupt)
        save_record(args.folder, iq, metadata)
        print("已保存复数样本:", len(iq))
    else:
        iq, metadata = load_record(args.folder)
        fields, details = decode(iq, metadata)
        print("同步起点:", details["start"], "帧:", details["frame_hex"])
        print("有效字段:", fields)
