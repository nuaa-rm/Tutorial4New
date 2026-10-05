#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <thread>
#include <vector>
#include <unistd.h>
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_components/register_node_macro.hpp"
#include "image_path_demo/msg/frame.hpp"

namespace image_path_demo {
using Frame = image_path_demo::msg::Frame;
uint64_t steady_ns() {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(
    std::chrono::steady_clock::now().time_since_epoch()).count();
}

class Source : public rclcpp::Node {
public:
  explicit Source(const rclcpp::NodeOptions & options) : Node("source", options) {
    width_ = declare_parameter("width", 64);
    height_ = declare_parameter("height", 48);
    channels_ = declare_parameter("channels", 3);
    const double rate = declare_parameter("rate", 25.0);
    frames_ = declare_parameter("frames", 100);
    const int depth = declare_parameter("depth", 5);
    if (width_ <= 0 || height_ <= 0 || (channels_ != 1 && channels_ != 3) ||
        rate <= 0 || rate > 10000 || frames_ < 2 || depth < 1 ||
        uint64_t(width_) * height_ * channels_ > 64000000) {
      throw std::invalid_argument("核对尺寸、通道数、频率、帧数和队列深度");
    }
    auto qos = rclcpp::QoS(rclcpp::KeepLast(depth)).best_effort();
    if (declare_parameter("reliable", false)) qos.reliable();
    pub_ = create_publisher<Frame>("frames", qos);
    auto period = std::chrono::nanoseconds(int64_t(1e9 / rate));
    timer_ = create_wall_timer(period, [this] { tick(); });
  }
  ~Source() override {
    const double span = (last_ - first_) / 1e9;
    std::cout << "SOURCE {\"sent\":" << sent_ << ",\"send_hz\":"
              << (span > 0 ? (sent_ - 1) / span : 0) << "}" << std::endl;
  }
private:
  void tick() {
    // 等订阅端出现再测量；发布完取消定时器，留出接收排空时间。
    if (pub_->get_subscription_count() == 0) return;
    auto msg = std::make_unique<Frame>();
    auto & image = msg->image;
    image.header.stamp = now();
    image.header.frame_id = "camera_optical_frame";
    image.width = width_; image.height = height_;
    image.encoding = channels_ == 3 ? "bgr8" : "mono8";
    image.step = width_ * channels_;
    image.data.assign(size_t(image.step) * height_, uint8_t(sent_ % 256));
    msg->sequence = sent_;
    msg->source_pid = getpid();
    msg->source_address = reinterpret_cast<uintptr_t>(image.data.data());
    msg->sent_ns = steady_ns();
    if (sent_ == 0) first_ = msg->sent_ns;
    last_ = msg->sent_ns;
    // 发布以后 msg 已交出所有权，不能再读写它。
    pub_->publish(std::move(msg));
    if (++sent_ == frames_) {
      timer_->cancel();
      std::cout << "SOURCE_DONE " << sent_ << std::endl;
    }
  }
  int width_, height_, channels_, frames_, sent_ = 0;
  uint64_t first_ = 0, last_ = 0;
  rclcpp::Publisher<Frame>::SharedPtr pub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

class Sink : public rclcpp::Node {
public:
  explicit Sink(const rclcpp::NodeOptions & options) : Node("sink", options) {
    const int depth = declare_parameter("depth", 5);
    const int work_ms = declare_parameter("work_ms", 0);
    if (depth < 1 || work_ms < 0) throw std::invalid_argument("参数不能为负");
    auto qos = rclcpp::QoS(rclcpp::KeepLast(depth)).best_effort();
    if (declare_parameter("reliable", false)) qos.reliable();
    sub_ = create_subscription<Frame>("frames", qos,
      [this, work_ms](Frame::UniquePtr msg) {
        const auto arrival = steady_ns();
        if (latency_.empty()) first_ = arrival;
        last_ = arrival;
        latency_.push_back((arrival - msg->sent_ns) / 1e6);
        const auto address = reinterpret_cast<uintptr_t>(msg->image.data.data());
        const bool same_process = msg->source_pid == uint32_t(getpid());
        if (same_process && address == msg->source_address) ++pointer_matches_;
        const auto & data = msg->image.data;
        if (data.empty() || data.front() != uint8_t(msg->sequence % 256) ||
            data.back() != uint8_t(msg->sequence % 256)) ++bad_frames_;
        if (latency_.size() <= 3) {
          std::cout << "POINTER seq=" << msg->sequence
                    << " same_process=" << same_process
                    << " source=" << msg->source_address
                    << " sink=" << address << std::endl;
        }
        if (work_ms) std::this_thread::sleep_for(std::chrono::milliseconds(work_ms));
      });
  }
  ~Sink() override {
    std::sort(latency_.begin(), latency_.end());
    auto percentile = [this](double q) {
      return latency_.empty() ? 0.0 : latency_[size_t(q * (latency_.size() - 1))];
    };
    const double span = (last_ - first_) / 1e9;
    std::cout << "SINK {\"received\":" << latency_.size()
              << ",\"receive_hz\":" << (span > 0 ? (latency_.size() - 1) / span : 0)
              << ",\"p50_ms\":" << percentile(0.50)
              << ",\"p95_ms\":" << percentile(0.95)
              << ",\"p99_ms\":" << percentile(0.99)
              << ",\"pointer_matches\":" << pointer_matches_
              << ",\"bad_frames\":" << bad_frames_ << "}" << std::endl;
  }
private:
  std::vector<double> latency_;
  uint64_t first_ = 0, last_ = 0, pointer_matches_ = 0, bad_frames_ = 0;
  rclcpp::Subscription<Frame>::SharedPtr sub_;
};
}  // namespace image_path_demo
RCLCPP_COMPONENTS_REGISTER_NODE(image_path_demo::Source)
RCLCPP_COMPONENTS_REGISTER_NODE(image_path_demo::Sink)
