# 第 5 章网络配图与资料

资料核对日期：2026-10-31。图片用于教材讲解；商标、界面和原图版权归其原权利人。

| 文件 | 内容及来源 | 处理与检查 |
|---|---|---|
| `network_paths_revised.png` | 教材自绘局域网、直连与 Tailscale 网络路径；生成脚本 `scripts/render_deployment_network.py` | 候选图 `network_paths_candidate.png` 已在本地实际打开检查，统一浅青/深灰配色、中文字体与箭头后发布 `_revised`。原候选仅放 `/tmp`，不在源码堆备份。正文实际尺寸由整卷 PDF 复查。 |
| `kvm_wiring_revised.png` | 教材自绘 USB KVM/IP KVM 接线，脚本 `scripts/render_deployment_kvm.py` | 实际查看后确认视频/HID方向、笔记本侧单线与目标侧供电；以 `_revised` 标记。候选仅存 `/tmp`。 |
| `tailscale_magicdns.png` | Tailscale 官方 MagicDNS 文档中的 Enable MagicDNS 界面图，https://tailscale.com/docs/features/magicdns ，原图 https://tailscale.com/_next/static/media/magic-dns-toggle.a34b50f9.png | 原图下载后实际打开检查，保持界面原貌与英文，不改写按钮或状态。无账户数据。正文说明它只演示未启用时的入口。 |

## 官方资料

- Avahi：https://avahi.org/ ，说明 mDNS/DNS-SD 和 `.local` 查询。
- nss-mdns：https://github.com/avahi/nss-mdns ，核对 NSS、`getent hosts` 与 `nslookup` 的区别，以及 UDP 5353 条件。
- NetworkManager：https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nm-settings-nmcli.html ，核对 `manual`、`never-default` 与连接配置。
- Tailscale 安装：https://tailscale.com/docs/install/linux 。
- Ubuntu 22.04 稳定源：https://pkgs.tailscale.com/stable/#ubuntu-2204 ，核对 `jammy` 签名密钥与 APT 配置。正文分步下载并用 `install` 写入，避免无条件管道覆盖。
- MagicDNS：https://tailscale.com/docs/features/magicdns ，核对设备名、完整域名和开关。
- 通过 Tailscale 使用普通 SSH：https://tailscale.com/docs/reference/ssh-over-tailscale 。
- Tailscale SSH：https://tailscale.com/docs/features/tailscale-ssh ，核对与普通 OpenSSH 的区别。
- Ping 与 TCP 服务排错：https://tailscale.com/docs/reference/troubleshooting/network-configuration/tcp-connection-two-devices 。
- 设备密钥到期：https://tailscale.com/docs/features/access-control/key-expiry 。

- Windows TCP/IP 界面：https://support.microsoft.com/en-us/windows/experience/connectivity-networking/essential-network-settings-and-tasks-in-windows 。

## 验证边界

此处完成官方资料核对、图片生成及查看，未为本教材更改任何主机名、网络连接、账户、Tailscale 设置或防火墙。Ubuntu 双端网线、mDNS 跨设备、跨互联网 SSH、客户端隔离及实际设备密钥续期需在获准设备验证；不能据文档命令宣称实机完成。

## 字体修正

2026-10-31 按图 5.4 的阅读反馈修正自绘图字体：Noto Sans CJK 的 TTC 文件默认第 0 项是日文字形 JP，脚本现明确选择第 2 项简体中文 SC，并检查实际字体族名称，防止静默选错。图 5.4 与同源设置的图 5.6 同步重新生成，保持原有尺寸、文字和接线关系；沿用已有 `_revised` 文件名，旧图保存在 Git 历史。候选图及书中实际尺寸均须重新查看。
