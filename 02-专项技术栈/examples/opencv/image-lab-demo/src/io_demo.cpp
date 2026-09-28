#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
int main() {
    cv::Mat a(32, 48, CV_8UC3, cv::Scalar(0, 255, 0));
    if (!cv::imwrite("input.png", a)) return 1;
    cv::Mat b = cv::imread("input.png");
    if (b.empty()) return 2;
    std::cout << b.rows << " " << b.cols << "\n";
}
