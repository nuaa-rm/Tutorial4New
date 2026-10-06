# 固定为 1440×1080 BGR8，常量不占消息负载。
uint32 WIDTH=1440
uint32 HEIGHT=1080
uint32 CHANNELS=3
# 序号与单机单调时钟用于本实验测量。
uint64 sequence
uint64 sent_ns
# 像素内嵌在消息中，生成 std::array，不含字符串或动态数组。
uint8[4665600] data
