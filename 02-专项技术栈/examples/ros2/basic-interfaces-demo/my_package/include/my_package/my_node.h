#ifndef MY_NODE_H
#define MY_NODE_H

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

#include "my_msgs/msg/my.hpp"

class my_node: public rclcpp::Node {
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr string_publisher_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr timer_publisher_;
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr string_subscription_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<my_msgs::msg::My>::SharedPtr  my_message_publisher_;
    rclcpp::Subscription<my_msgs::msg::My>::SharedPtr my_message_subscription_;
    int cnt_ = 0;
public:
    my_node() ;
    my_node(const rclcpp::NodeOptions &options);
    void subscription_callback(std_msgs::msg::String::SharedPtr msg);
    void timer_callback();
    void my_message_callback(my_msgs::msg::My::SharedPtr msg);
};

#endif //MY_NODE_H
