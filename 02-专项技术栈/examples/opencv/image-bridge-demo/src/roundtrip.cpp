#include <cv_bridge/cv_bridge.hpp>
#include <sensor_msgs/image_encodings.hpp>
#include <iostream>

int main() {
    cv::Mat src(8,8,CV_8UC3,cv::Scalar(0,0,255));
    std_msgs::msg::Header header;
    header.frame_id = "camera_optical_frame";
    header.stamp.sec = 12;
    header.stamp.nanosec = 345;
    auto msg = cv_bridge::CvImage(header,"bgr8",src).toImageMsg();
    auto out = cv_bridge::toCvCopy(msg,"bgr8");
    std::cout << out->image.rows << " " << out->image.cols << '\n';
    auto gray = cv_bridge::toCvCopy(msg,"mono8");
    auto output = cv_bridge::CvImage(msg->header,"mono8",gray->image).toImageMsg();
    if (output->header != header || gray->image.channels() != 1
        || output->encoding != "mono8") return 1;
    std::cout << "通道=" << gray->image.channels() << " 灰度="
              << int(gray->image.at<uchar>(0,0)) << " sec="
              << output->header.stamp.sec << " nanosec=" << output->header.stamp.nanosec
              << " frame=" << output->header.frame_id << '\n';
}
