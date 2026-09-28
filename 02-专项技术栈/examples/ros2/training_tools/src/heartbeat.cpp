#include <chrono>
#include <memory>
#include <string>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

class Heartbeat : public rclcpp::Node {
public:
  Heartbeat() : Node("heartbeat") {
    const auto text = declare_parameter<std::string>("text", "ready");
    pub_ = create_publisher<std_msgs::msg::String>("status", 10);
    timer_ = create_wall_timer(std::chrono::milliseconds(200),
      [this, text]() {
        std_msgs::msg::String msg;
        msg.data = text;
        pub_->publish(msg);
        RCLCPP_DEBUG(get_logger(), "publish: %s", text.c_str());
        RCLCPP_INFO_ONCE(get_logger(), "first heartbeat");
        RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 2000,
                            "heartbeat alive");
      });
  }
private:
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Heartbeat>());
  rclcpp::shutdown();
  return 0;
}
