# 测量元数据放在包装消息中，保留 Image 的正常时间戳和坐标系。
uint64 sequence
uint64 sent_ns
uint64 source_address
uint32 source_pid
sensor_msgs/Image image
