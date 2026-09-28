#include <rclcpp/rclcpp.hpp>
#include <my_package/my_node.h>

int main(int argc, char **argv)
{
    rclcpp::init(argc,argv);
    rclcpp::spin(std::make_shared<my_node>());
    rclcpp::shutdown();
}
