#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
int main() {
    cv::Mat a = cv::Mat::zeros(7, 7, CV_8UC1), out;
    a.at<uchar>(3,3) = 255;
    cv::medianBlur(a, out, 3);
    std::cout << int(out.at<uchar>(3,3)) << "\n";
    cv::Mat mean, gaussian, bilateral;
    cv::blur(a,mean,cv::Size(3,3));
    cv::GaussianBlur(a,gaussian,cv::Size(3,3),0);
    cv::bilateralFilter(a,bilateral,5,25,25);
    std::cout << "均值/高斯/双边中心=" << int(mean.at<uchar>(3,3)) << ','
              << int(gaussian.at<uchar>(3,3)) << ',' << int(bilateral.at<uchar>(3,3)) << '\n';
}
