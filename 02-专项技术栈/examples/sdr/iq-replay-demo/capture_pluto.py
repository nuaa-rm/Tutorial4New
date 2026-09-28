"""可选实机接收入口；不调用发射，不把真实样本套进教学解码器。"""
import argparse
from record import save_record


def capture(uri, lo_hz, folder):
    import adi
    sdr = adi.Pluto(uri=uri)
    sdr.sample_rate = 1_000_000
    sdr.rx_lo = lo_hz
    sdr.rx_rf_bandwidth = 200_000
    sdr.gain_control_mode_chan0 = "slow_attack"
    sdr.rx_buffer_size = 4096
    try:
        iq = sdr.rx()
        save_record(folder, iq, {"sample_rate_hz": int(sdr.sample_rate),
                    "rx_lo_hz": int(sdr.rx_lo), "source": "pluto-rx"})
        print("接收:", iq.shape, iq.dtype, "本振:", sdr.rx_lo)
    finally:
        sdr.rx_destroy_buffer()


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--uri", required=True, help="iio_info 给出的设备地址")
    cli.add_argument("--lo-hz", type=int, required=True, help="批准的接收中心频率")
    cli.add_argument("folder", help="新录包目录")
    args = cli.parse_args()
    capture(args.uri, args.lo_hz, args.folder)
