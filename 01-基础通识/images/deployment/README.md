# 实机部署章节：实物照片与软件界面来源

资料核对与下载日期：2026-10-31，NanoKVM-USB 产品图于 2026-11-09 补入。正文见本卷 `Chapter4/physical.tex`、`desktop.tex`、`kvm.tex`；网络图来源由 `README-network.md` 单独记录。

本目录以下五张图片均为上游官方发布的原文件，仅使用便于维护的本地文件名，没有裁切、重绘、替换文字或修改界面。已逐张实际查看，正文以图注/段落说明应看的接口或按钮；因此没有给原图增加表示“已修改整理”的 `_revised` 后缀。照片保持原本外观，软件截图保持真实界面。截图中的名称、地址、ID 和密码属于上游演示，不是本项目设备或可供读者使用的登录凭据。

| 本地文件 | 上游原文件与介绍页 | 使用位置及读图目的 |
| --- | --- | --- |
| `portable-monitor.jpg` | [Waveshare 原图](https://www.waveshare.com/img/devkit/LCD/13.3inch-FHD-Monitor/13.3inch-FHD-Monitor-details-1.jpg)；[产品页](https://www.waveshare.com/13.3inch-FHD-Monitor.htm) | 便携屏正反面，识别其为独立视频输入设备；不要求采购同型号。 |
| `gnome42-rdp.png` | [GNOME 42 原图](https://release.gnome.org/42/rdp-screenshot.png)；[RDP 发布说明](https://release.gnome.org/42/#rdp-support) | Remote Desktop、Remote Control、Authentication 三组设置。原图为 GNOME 42 的 Fedora 示例，正文明确没有把它标作 Ubuntu 实机截图。 |
| `rustdesk-client.png` | [RustDesk 文档原图](https://raw.githubusercontent.com/rustdesk/doc.rustdesk.com/master/content/client/images/client.png)；[官方客户端说明](https://rustdesk.com/docs/en/client/) | 区分“本机 ID/一次性密码”和“目标 ID”入口。截图原有的数字标记也由上游提供。 |
| `nanokvm-usb-head.png` | [Sipeed 产品页](https://classic.sipeed.com/nanokvm/usb)的 [head 原图](https://classic.sipeed.com/assets/head.0b24c988.png)，与 [Sipeed Wiki 产品图](https://wiki.sipeed.com/hardware/assets/NanoKVM/usb/NanoKVM-USB.png) 相同 | 识别外壳的 `TARGET` 与 `HOST` 标记，以及露出的 Target USB 和 HDMI 输入。Host USB 位于图中背向读者的端面，位置对照 [官方接口图](https://wiki.sipeed.com/hardware/assets/NanoKVM/usb/interface.jpg)。 |
| `pikvm-v4.jpg` | [PiKVM 官方原图](https://docs.pikvm.org/v4/overview.jpg)；[V4 快速指南](https://docs.pikvm.org/v4/) | V4 Mini 与 Plus 实物，说明网络接到 KVM 本身，并提醒区分多个 RJ45 外形接口。 |

## 权属记录

- Waveshare 的产品照片、GNOME 发布说明截图、Sipeed 产品图以及 PiKVM 文档照片均保留各自原权利人权利。本次来源页面没有给所取图片逐项列出可独立适用的图片许可证，因此不将它们标成 CC0、公共领域或自行创作，也不从产品“开源”推导其宣传照片一律开放许可。教材中的图注保留官方来源，进一步再利用时应沿上述链接核对图片条款。
- RustDesk 文档仓库根目录采用 [MIT License](https://github.com/rustdesk/doc.rustdesk.com/blob/master/LICENSE.md)。本目录保存该许可证原文为 `LICENSE-rustdesk-docs.txt`。该记录说明文档仓库声明的许可，不扩大到 RustDesk 商标或其他站外资源。
- 本章新增照片没有用于证明任何硬件实测。没有在本环境连接便携屏、KVM 或远程机器人，也未验证 Windows 客户端、板端 BIOS、特定 Wayland 会话或脱网直连。正文给出的是依据官方资料编写的操作方法与验收条件。

## 正文技术资料

- [Ubuntu 22.04 LTS 发布说明](https://documentation.ubuntu.com/release-notes/22.04/)：该版本 GNOME 及 RDP 桌面共享支持。
- [Ubuntu Remote Desktop 测试计划](https://ubuntu.com/project/docs/maintainers/test-plans/desktop-team/RemoteDesktop/)：Sharing 设置、Remmina RDP 连接字段及结果核对。
- [GNOME 42 发布说明](https://release.gnome.org/42/)：RDP 设置图与 Sharing 入口。
- [Ubuntu 当前桌面共享帮助](https://help.ubuntu.com/stable/ubuntu-help/sharing-desktop.html.zh-CN)：客户端、凭据、证书指纹，以及新版本菜单和端口的条件；正文不会将其新版本“远程登录”能力套用到 22.04。
- [RustDesk 客户端](https://rustdesk.com/docs/en/client/)、[Linux 安装与限制](https://rustdesk.com/docs/en/client/linux/)：平台安装包、ID/密码操作、Wayland 实验支持与登录屏 X11 要求。
- [Sipeed NanoKVM-USB 快速上手](https://wiki.sipeed.com/hardware/zh/kvm/NanoKVM_USB/quick_start.html)、[官方客户端](https://github.com/sipeed/NanoKVM-USB)：接口照片、三条连接、网页摄像头与串口授权、桌面客户端。
- [PiKVM V4 快速指南](https://docs.pikvm.org/v4/)、[基础操作表](https://docs.pikvm.org/cheatsheet/)：HDMI/USB/网络与独立供电、DHCP 地址、Web 与系统账户、首次配置及控制台区分。
