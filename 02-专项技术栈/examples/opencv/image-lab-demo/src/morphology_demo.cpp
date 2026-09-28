#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
int main() {
    cv::Mat a = cv::Mat::zeros(12,12,CV_8UC1), out;
    a(cv::Rect(4,4,5,5)).setTo(255);
    a.at<uchar>(1,1)=255;
    auto k=cv::getStructuringElement(cv::MORPH_RECT,cv::Size(3,3));
    cv::morphologyEx(a,out,cv::MORPH_OPEN,k);
    std::cout << cv::countNonZero(a) << " " << cv::countNonZero(out) << "\n";
}
