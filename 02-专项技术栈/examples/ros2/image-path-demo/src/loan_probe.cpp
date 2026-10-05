#include <iostream>
#include <memory>
#include <utility>
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "std_msgs/msg/float64.hpp"

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("loan_probe");
  auto small = node->create_publisher<std_msgs::msg::Float64>("loan_value", 5);
  auto image = node->create_publisher<sensor_msgs::msg::Image>("loan_image", 5);
  std::cout << "LOAN {\"float64\":" << small->can_loan_messages()
            << ",\"image\":" << image->can_loan_messages() << "}" << std::endl;
  // API 可以回退到本地分配器，所以借出成功不等于中间件借出成功。
  auto loan = small->borrow_loaned_message();
  loan.get().data = 42.0;
  small->publish(std::move(loan));
  // 发布后不能继续使用 loan.get()。这里只检查发布端能力。
  rclcpp::shutdown();
}
