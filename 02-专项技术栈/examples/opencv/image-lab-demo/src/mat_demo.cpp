#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
int main() {
    cv::Mat a(2, 2, CV_8UC1, cv::Scalar(1));
    cv::Mat b = a, c = a.clone();
    b.at<uchar>(0, 0) = 9;
    std::cout << int(a.at<uchar>(0, 0)) << " "
              << int(c.at<uchar>(0, 0)) << "\n";
}
