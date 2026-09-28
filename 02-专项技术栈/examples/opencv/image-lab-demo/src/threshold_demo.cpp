#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
int main() {
    cv::Mat gray = (cv::Mat_<uchar>(1,3) << 126,127,128);
    cv::Mat binary;
    cv::threshold(gray, binary, 127, 255, cv::THRESH_BINARY);
    for (int x=0; x<3; ++x) std::cout << int(binary.at<uchar>(0,x)) << " ";
    std::cout << "\n";
    cv::Mat scene(20,40,CV_8UC1,cv::Scalar(50)), otsu, adaptive;
    scene(cv::Rect(20,0,20,20)).setTo(200);
    const double chosen = cv::threshold(scene, otsu, 0, 255,
                                       cv::THRESH_BINARY | cv::THRESH_OTSU);
    cv::adaptiveThreshold(scene, adaptive, 255, cv::ADAPTIVE_THRESH_GAUSSIAN_C,
                          cv::THRESH_BINARY, 11, 2);
    if (!cv::imwrite("otsu.png",otsu) || !cv::imwrite("adaptive.png",adaptive)) return 1;
    std::cout << "Otsu=" << chosen << " 非零=" << cv::countNonZero(otsu)
              << " adaptive非零=" << cv::countNonZero(adaptive) << '\n';
}
