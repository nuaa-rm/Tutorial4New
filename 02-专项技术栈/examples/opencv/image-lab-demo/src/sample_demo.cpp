#include <opencv2/opencv.hpp>
#include <iostream>

int main() {
    cv::Mat hsv(120, 160, CV_8UC3, cv::Scalar(0, 0, 25));
    hsv(cv::Rect(20, 20, 30, 60)).setTo(cv::Scalar(1, 255, 255));
    hsv(cv::Rect(100, 20, 30, 60)).setTo(cv::Scalar(179, 255, 255));
    hsv(cv::Rect(110, 40, 1, 1)).setTo(cv::Scalar(0, 0, 25));
    hsv.at<cv::Vec3b>(5, 5) = {1, 255, 255};
    cv::circle(hsv, {75, 95}, 10, cv::Scalar(120, 255, 255), -1);
    cv::Mat bgr;
    cv::cvtColor(hsv, bgr, cv::COLOR_HSV2BGR);
    if (!cv::imwrite("scene.png", bgr)) return 1;
    cv::VideoWriter writer("scene.avi", cv::VideoWriter::fourcc('M','J','P','G'),
                           20.0, bgr.size());
    if (!writer.isOpened()) {
        std::cerr << "当前后端无法创建 MJPG 视频\n";
        return 2;
    }
    for (int i = 0; i < 20; ++i) writer.write(bgr);
    writer.release();
    std::cout << "scene.png: 160x120; scene.avi: 20 帧\n";
}
