# 距离换算教学工程

- `include/distance.hpp` 定义输入为毫米、输出为米，负值表示负位移。
- 从项目根运行：`cmake -S . -B build`、`cmake --build build`、`ctest --test-dir build --output-on-failure`。
- 修改行为时保留接口及单位约定，不通过删除用例或放宽容差让测试通过。
- 构建产物不提交；交付说明写出改动原因、实际执行的验证与未验证范围。
- 本工程只验证纯函数的数值换算；串口输入、设备精度和实车行为另行验收。
