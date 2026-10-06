#include <algorithm>
#include <iostream>
#include <memory>
#include <utility>
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "image_path_demo/msg/fixed_image.hpp"

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("loan_probe");
  using FixedImage = image_path_demo::msg::FixedImage;
  auto qos = rclcpp::QoS(5).best_effort();
  auto image = node->create_publisher<sensor_msgs::msg::Image>("loan_image", qos);
  auto fixed = node->create_publisher<FixedImage>("loan_fixed_image", qos);
  std::cout << "LOAN {\"image\":" << image->can_loan_messages()
            << ",\"fixed_image\":" << fixed->can_loan_messages() << "}" << std::endl;

  // 普通 Image 的借出包装器使用本地分配器回退。
  auto image_loan = image->borrow_loaned_message();
  auto & dynamic = image_loan.get();
  dynamic.header.stamp = node->now();
  dynamic.header.frame_id = "camera";
  dynamic.width = FixedImage::WIDTH;
  dynamic.height = FixedImage::HEIGHT;
  dynamic.encoding = "bgr8";
  dynamic.is_bigendian = 0;
  dynamic.step = FixedImage::WIDTH * FixedImage::CHANNELS;
  dynamic.data.assign(dynamic.step * dynamic.height, 42);
  image->publish(std::move(image_loan));

  // FixedImage 为 true 时直接填充中间件样本，否则也使用本地分配器。
  auto fixed_loan = fixed->borrow_loaned_message();
  auto & embedded = fixed_loan.get();
  embedded.sequence = 1;
  embedded.sent_ns = 0;
  std::fill(embedded.data.begin(), embedded.data.end(), 42);
  fixed->publish(std::move(fixed_loan));
  // 两类图像均为 1440×1080 BGR8；发布后停止访问借出对象及其引用。
  std::cout << "PUBLISHED {\"image\":1,\"fixed_image\":1}" << std::endl;
  rclcpp::shutdown();
}
