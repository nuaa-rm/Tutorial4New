#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
int main() {
    cv::Mat hsv(1, 3, CV_8UC3);
    hsv.at<cv::Vec3b>(0, 0) = {0, 255, 255};
    hsv.at<cv::Vec3b>(0, 1) = {179, 255, 255};
    hsv.at<cv::Vec3b>(0, 2) = {120, 255, 255};
    cv::Mat a, b, mask;
    cv::inRange(hsv, cv::Scalar(0,70,50), cv::Scalar(10,255,255), a);
    cv::inRange(hsv, cv::Scalar(170,70,50), cv::Scalar(179,255,255), b);
    cv::bitwise_or(a, b, mask);
    std::cout << cv::countNonZero(mask) << "\n";
}
