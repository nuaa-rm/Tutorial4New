# ROS 疑难杂症资料整合

来源：[nuaa-rm/til 的 ROS疑难杂症目录](https://github.com/nuaa-rm/til/tree/3eefd14dcf0883b68b3481ef286933a690a2b85a/ROS%E7%96%91%E9%9A%BE%E6%9D%82%E7%97%87)，固定提交 `3eefd14dcf0883b68b3481ef286933a690a2b85a`。已读取目录内六份 Markdown 及一个 Shell 脚本；未执行外部脚本。

## 内容对应

| 原资料 | 教材去向与处理 |
|---|---|
| CLion下的ROS2开发指南.md | “CLion：让编辑、构建和运行使用同一套环境”：环境继承、单包项目、编译数据库、独立构建目录、运行参数、Debug、生成接口和 Git 忽略项。纠正安装前缀等于执行安装、改变根目录自动合并数据库等说法。 |
| ROS2_Launch详细指南.md | “用 Launch 保存一次完整启动”：Node、YAML、重映射、命名空间、启动参数、Include、条件、环境、退出事件、OpaqueFunction。两份完整可安装启动文件共用教学节点。 |
| ROS2日志系统指南.md | “日志：看见故障，也控制输出量”：级别、宏、限流、输出路由、格式与目录、缓冲、排障。纠正 FATAL 自动退出、默认按级别分 stdout/stderr、仅 Launch 才有文件日志等说法。 |
| ROS2环境变量详解.md | “先检查环境，再检查代码”：搜索路径、域、本机范围、RMW 切换与 daemon；DDS 专属配置、发现服务器、SROS2 和新版本发现变量保留用途与适用边界。日志变量集中在日志小节，避免重复。 |
| ROS2的AMENT指南.md | “ament、colcon 与可复现的小工程”：四种工具的职责、依赖类型、手动和自动 CMake、安装资源、测试、导出与组件注册边界。提供完整 training_tools 包，组件与库导出作为进阶入口。 |
| 局域网ROS禁用/README.md、disable-ros-lan.sh | 环境小节的临时设置、持久配置备份、验证和恢复。保留脚本管理配置的意图，改写成可检查步骤；删除 ROS1 Master、roscore、rostopic、11311 等混用内容，不照搬重复追加环境变量的脚本。 |

新增正文位于 `chapters/A_ros2_engineering.tex`，由 main 在原基础正文之后、原完整工程附录之前载入，保留原主题顺序。旧正文日志说明改为交叉引用。同步更新章首提要、小结、10 道章末题及现场验收。

新增 5 道随堂练习、4 道章末习题，完整答案全部加入卷末 `answers.tex`；其他章节答案保持原顺序。本卷现在有 82 道随堂题解、88 道章末题解，共 170 个 solution。

## 版本核对

按 Ubuntu 22.04 / Humble 编写，参照官方 [日志文档](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Logging.html)、[RMW 切换文档](https://docs.ros.org/en/humble/How-To-Guides/Working-with-multiple-RMW-implementations.html)，并读取 Humble 分支的 [ExecuteProcess](https://github.com/ros2/launch/blob/humble/launch/launch/actions/execute_process.py)、[rcutils 日志实现](https://github.com/ros2/rcutils/blob/humble/src/logging.c)、[ament_auto_package](https://github.com/ament/ament_cmake/blob/humble/ament_cmake_auto/cmake/ament_auto_package.cmake) 核对环境继承、默认输出流和自动安装接口。

不把较新版日志服务 CLI、日志格式占位符、发现范围变量作为 Humble 通用操作；不把通信域和本机范围描述成认证措施。

## 验证与交付

- `examples/ros2/training_tools` 提供与正文一致的完整手动 ament 示例；README 说明构建、运行与预期结果。
- 已完成两份 Python Launch 的语法检查、package.xml 与 YAML 解析、TeX 环境配对和新增题解编号检查；结果见 `ros-integration-checks.json`。
- Windows 主机未配置 ROS2，因此未声称 C++、Launch、DDS 与 CLion 实验已经运行通过；教材给出目标 Linux 环境中的完整验收步骤，无待填的正文空段落。
- 原 `main.pdf` 被其他程序占用，新预览使用 `validation/ros2-build/main.pdf`，构建日志单独保存。最终页数与版式检查见同目录验证结果。

最终两遍 XeLaTeX 均成功，共 167 页，无 Overfull、缺字和未定义引用。抽查环境、工程代码、Launch、日志/IDE 和卷末题解页面，修正一处示例开头孤悬后复编译；保留原有字体提示。
