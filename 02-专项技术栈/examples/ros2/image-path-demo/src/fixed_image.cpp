#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include <unistd.h>
#include "rclcpp/rclcpp.hpp"
#include "image_path_demo/msg/fixed_image.hpp"

using Image = image_path_demo::msg::FixedImage;
static_assert(rosidl_generator_traits::has_fixed_size<Image>::value);

uint64_t steady_ns() {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(
    std::chrono::steady_clock::now().time_since_epoch()).count();
}

class FixedImageNode : public rclcpp::Node {
public:
  FixedImageNode() : Node("fixed_image") {
    role_ = declare_parameter<std::string>("role", "receive");
    frames_ = declare_parameter("frames", 1000);
    const double rate = declare_parameter("rate", 250.0);
    loan_ = declare_parameter("loan", true);
    const bool require_loan = declare_parameter("require_loan", true);
    verify_full_ = declare_parameter("verify_full", false);
    if (frames_ < 2 || rate <= 0 || rate > 10000)
      throw std::invalid_argument("核对帧数和频率");
    auto qos = rclcpp::QoS(rclcpp::KeepLast(5)).best_effort();
    if (role_ == "send") {
      pub_ = create_publisher<Image>("fixed_frames", qos);
      report_capability(pub_->can_loan_messages());
      if (loan_ && !pub_->can_loan_messages())
        throw std::runtime_error("当前发布者不支持中间件借出");
      timer_ = create_wall_timer(std::chrono::nanoseconds(int64_t(1e9 / rate)),
        [this] { send(); });
    } else if (role_ == "receive") {
      // 只在回调内借读，不把引用或像素视图保存到回调外。
      sub_ = create_subscription<Image>("fixed_frames", qos,
        [this](const Image & image) { receive(image); });
      report_capability(sub_->can_loan_messages());
      if (require_loan && !sub_->can_loan_messages())
        throw std::runtime_error("当前订阅者未启用借读");
    } else {
      throw std::invalid_argument("role 应为 send 或 receive");
    }
  }

  ~FixedImageNode() override {
    std::sort(latency_.begin(), latency_.end());
    auto percentile = [this](double q) {
      return latency_.empty() ? 0.0 : latency_[size_t(q * (latency_.size() - 1))];
    };
    const double span = (last_ - first_) / 1e9;
    std::cout << "FIXED_STATS {\"role\":\"" << role_
              << "\",\"count\":" << count_
              << ",\"hz\":" << (span > 0 ? (count_ - 1) / span : 0)
              << ",\"p50_ms\":" << percentile(0.50)
              << ",\"p95_ms\":" << percentile(0.95)
              << ",\"p99_ms\":" << percentile(0.99)
              << ",\"bad_frames\":" << bad_frames_ << "}" << std::endl;
  }

private:
  void report_capability(bool can_loan) {
    std::cout << "FIXED_CAP {\"role\":\"" << role_
              << "\",\"can_loan\":" << can_loan
              << ",\"sizeof_message\":" << sizeof(Image) << "}" << std::endl;
  }

  void report_pointer(const Image & image) {
    if (count_ < 3) {
      std::cout << "FIXED_POINTER {\"role\":\"" << role_
                << "\",\"pid\":" << getpid()
                << ",\"sequence\":" << image.sequence
                << ",\"pixel_address\":"
                << reinterpret_cast<uintptr_t>(image.data.data()) << "}" << std::endl;
    }
  }

  void fill(Image & image) {
    image.sequence = count_;
    std::fill(image.data.begin(), image.data.end(), uint8_t(count_ % 256));
    image.sent_ns = steady_ns();
    if (count_ == 0) first_ = image.sent_ns;
    last_ = image.sent_ns;
    report_pointer(image);
  }

  void send() {
    if (pub_->get_subscription_count() == 0) return;
    if (loan_) {
      auto image = pub_->borrow_loaned_message();
      fill(image.get());
      pub_->publish(std::move(image));
    } else {
      auto image = std::make_unique<Image>(rosidl_runtime_cpp::MessageInitialization::SKIP);
      fill(*image);
      pub_->publish(std::move(image));
    }
    if (++count_ == uint64_t(frames_)) {
      timer_->cancel();
      std::cout << "FIXED_DONE " << count_ << std::endl;
    }
  }

  void receive(const Image & image) {
    const auto arrival = steady_ns();
    if (count_ == 0) first_ = arrival;
    last_ = arrival;
    latency_.push_back((arrival - image.sent_ns) / 1e6);
    const uint8_t expected = uint8_t(image.sequence % 256);
    bool valid = image.data.front() == expected && image.data.back() == expected;
    if (verify_full_)
      valid = std::all_of(image.data.begin(), image.data.end(),
        [expected](uint8_t pixel) { return pixel == expected; });
    if (!valid) ++bad_frames_;
    report_pointer(image);
    ++count_;
  }

  std::string role_;
  int frames_ = 1000;
  bool loan_ = true, verify_full_ = false;
  uint64_t count_ = 0, bad_frames_ = 0, first_ = 0, last_ = 0;
  std::vector<double> latency_;
  rclcpp::Publisher<Image>::SharedPtr pub_;
  rclcpp::Subscription<Image>::SharedPtr sub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  try {
    auto node = std::make_shared<FixedImageNode>();
    rclcpp::spin(node);
  } catch (const std::exception & error) {
    std::cerr << error.what() << std::endl;
    rclcpp::shutdown();
    return 2;
  }
  rclcpp::shutdown();
}
