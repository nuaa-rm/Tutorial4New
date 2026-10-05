#include <cv_bridge/cv_bridge.h>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/image_encodings.hpp>
#include <chrono>
#include <memory>

class BridgeDemo : public rclcpp::Node {
public:
    BridgeDemo() : Node("image_bridge_demo") {
        input_ = create_publisher<sensor_msgs::msg::Image>("image_in", 10);
        output_ = create_publisher<sensor_msgs::msg::Image>("image_out", 10);
        subscription_ = create_subscription<sensor_msgs::msg::Image>(
            "image_in", 10, [this](sensor_msgs::msg::Image::ConstSharedPtr msg) {
                convert(msg);
            });
        timer_ = create_wall_timer(std::chrono::milliseconds(500), [this] {
            std_msgs::msg::Header header;
            header.stamp = now();
            header.frame_id = "camera_optical_frame";
            cv::Mat src(8, 8, CV_8UC3, cv::Scalar(0, 0, 255));
            input_->publish(*cv_bridge::CvImage(header, "bgr8", src).toImageMsg());
        });
    }
private:
    void convert(const sensor_msgs::msg::Image::ConstSharedPtr& msg) {
        try {
            auto converted = cv_bridge::toCvCopy(msg, "mono8");
            auto output = cv_bridge::CvImage(msg->header, "mono8", converted->image)
                              .toImageMsg();
            output_->publish(*output);
            RCLCPP_INFO(get_logger(), "输入=%s 输出=%s 通道=%d frame=%s",
                        msg->encoding.c_str(), output->encoding.c_str(),
                        converted->image.channels(), output->header.frame_id.c_str());
        } catch (const cv_bridge::Exception& e) {
            RCLCPP_ERROR(get_logger(), "cv_bridge: %s", e.what());
        }
    }
    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr input_, output_;
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr subscription_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<BridgeDemo>());
    rclcpp::shutdown();
}
