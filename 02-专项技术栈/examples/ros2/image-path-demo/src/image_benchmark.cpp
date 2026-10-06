#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>
#include "rclcpp/rclcpp.hpp"
#include "image_path_demo/msg/frame.hpp"
#include "image_path_demo/msg/fixed_image.hpp"

using DynamicImage = image_path_demo::msg::Frame;
using FixedImage = image_path_demo::msg::FixedImage;

auto steady_ns() {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(
    std::chrono::steady_clock::now().time_since_epoch()).count();
}

template<class Message>
decltype(auto) pixels(Message & message) {
  if constexpr (std::is_same_v<std::remove_cv_t<Message>, FixedImage>)
    return (message.data);
  else
    return (message.image.data);
}

// 两种接口共用同一收发实现，仅准备图像字段的方式不同。
template<class Message>
class ImageBenchmark : public rclcpp::Node {
public:
  ImageBenchmark() : Node("image_benchmark") {
    role_ = declare_parameter<std::string>("role", "receive");
    frames_ = declare_parameter("frames", 1000);
    const double rate = declare_parameter("rate", 250.0);
    loan_ = declare_parameter("loan", false);
    verify_full_ = declare_parameter("verify_full", false);
    if (frames_ < 2 || rate <= 0 || rate > 10000)
      throw std::invalid_argument("核对帧数和频率");
    auto qos = rclcpp::QoS(rclcpp::KeepLast(5)).best_effort();
    if (role_ == "send") {
      pub_ = create_publisher<Message>("benchmark_frames", qos);
      capability(pub_->can_loan_messages());
      if (loan_ && !pub_->can_loan_messages())
        throw std::runtime_error("当前类型与配置不支持中间件借出");
      timer_ = create_wall_timer(std::chrono::nanoseconds(int64_t(1e9 / rate)),
        [this] { send(); });
    } else if (role_ == "receive") {
      // 两种接口都在回调内读样本，返回后不再保存引用或像素视图。
      sub_ = create_subscription<Message>("benchmark_frames", qos,
        [this](const Message & message) { receive(message); });
      capability(sub_->can_loan_messages());
    } else {
      throw std::invalid_argument("role 应为 send 或 receive");
    }
  }
  ~ImageBenchmark() override {
    std::sort(latency_.begin(), latency_.end());
    auto percentile = [this](double q) {
      return latency_.empty() ? 0.0 : latency_[size_t(q * (latency_.size() - 1))];
    };
    const double span = (last_ - first_) / 1e9;
    std::cout << "BENCH_STATS {\"role\":\"" << role_
              << "\",\"count\":" << count_
              << ",\"hz\":" << (span > 0 ? (count_ - 1) / span : 0)
              << ",\"p95_ms\":" << percentile(0.95)
              << ",\"p99_ms\":" << percentile(0.99)
              << ",\"bad_frames\":" << bad_frames_ << "}" << std::endl;
  }
private:
  void capability(bool supported) {
    std::cout << "BENCH_CAP {\"role\":\"" << role_
              << "\",\"can_loan\":" << supported << "}" << std::endl;
  }
  void fill(Message & message) {
    if constexpr (std::is_same_v<Message, DynamicImage>) {
      auto & image = message.image;
      image.header.stamp = now();
      image.header.frame_id = "camera_optical_frame";
      image.width = 1440; image.height = 1080;
      image.encoding = "bgr8"; image.step = 1440 * 3; image.is_bigendian = 0;
      image.data.resize(4665600);
      message.source_address = 0; message.source_pid = 0;
    }
    auto & data = pixels(message);
    std::fill(data.begin(), data.end(), uint8_t(count_ % 256));
    message.sequence = count_;
    message.sent_ns = steady_ns();
    if (count_ == 0) first_ = message.sent_ns;
    last_ = message.sent_ns;
  }
  void send() {
    if (pub_->get_subscription_count() == 0) return;
    if (loan_) {
      auto message = pub_->borrow_loaned_message();
      fill(message.get());
      pub_->publish(std::move(message));
    } else {
      auto message = std::make_unique<Message>(rosidl_runtime_cpp::MessageInitialization::SKIP);
      fill(*message);
      pub_->publish(std::move(message));
    }
    if (++count_ == uint64_t(frames_)) {
      timer_->cancel();
      std::cout << "BENCH_DONE " << count_ << std::endl;
    }
  }
  void receive(const Message & message) {
    const auto arrival = steady_ns();
    if (count_ == 0) first_ = arrival;
    last_ = arrival;
    latency_.push_back((arrival - message.sent_ns) / 1e6);
    const auto & data = pixels(message);
    const uint8_t expected = uint8_t(message.sequence % 256);
    bool valid = data.size() == 4665600 && data.front() == expected && data.back() == expected;
    if (verify_full_)
      valid = valid && std::all_of(data.begin(), data.end(),
        [expected](uint8_t pixel) { return pixel == expected; });
    if (!valid) ++bad_frames_;
    ++count_;
  }
  std::string role_;
  int frames_ = 1000;
  bool loan_ = false, verify_full_ = false;
  uint64_t count_ = 0, first_ = 0, last_ = 0, bad_frames_ = 0;
  std::vector<double> latency_;
  typename rclcpp::Publisher<Message>::SharedPtr pub_;
  typename rclcpp::Subscription<Message>::SharedPtr sub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  try {
    const auto arguments = rclcpp::remove_ros_arguments(argc, argv);
    if (arguments.size() != 2 || (arguments[1] != "dynamic" && arguments[1] != "fixed"))
      throw std::invalid_argument("选择 dynamic 或 fixed 图像接口");
    rclcpp::Node::SharedPtr node;
    if (arguments[1] == "fixed") node = std::make_shared<ImageBenchmark<FixedImage>>();
    else node = std::make_shared<ImageBenchmark<DynamicImage>>();
    rclcpp::spin(node);
  } catch (const std::exception & error) {
    std::cerr << error.what() << std::endl;
    rclcpp::shutdown();
    return 2;
  }
  rclcpp::shutdown();
}
