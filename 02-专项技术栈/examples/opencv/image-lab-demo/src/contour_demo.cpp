#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
int main() {
    cv::Mat a=cv::Mat::zeros(40,40,CV_8UC1);
    a(cv::Rect(5,5,20,10)).setTo(255);
    std::vector<std::vector<cv::Point>> cs;
    cv::findContours(a,cs,cv::RETR_EXTERNAL,cv::CHAIN_APPROX_SIMPLE);
    if(cs.size()!=1) return 1;
    std::cout << cs.size() << " " << cv::contourArea(cs[0]) << " "
              << cv::countNonZero(a) << "\n";
}
