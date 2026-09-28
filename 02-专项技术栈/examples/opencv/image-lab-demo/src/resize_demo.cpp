#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
int main() {
    cv::Mat a(40,80,CV_8UC3,cv::Scalar(0,0,0)), small;
    cv::circle(a,cv::Point(40,20),10,cv::Scalar(0,255,0),-1);
    cv::resize(a,small,cv::Size(),0.5,0.5,cv::INTER_AREA);
    if(!cv::imwrite("small.png",small)) return 1;
    std::cout << small.cols << " " << small.rows << "\n";
    cv::Mat rotated;
    auto matrix = cv::getRotationMatrix2D(cv::Point2f(40,20),30,1);
    cv::warpAffine(a,rotated,matrix,a.size());
    if (!cv::imwrite("rotated.png",rotated)) return 2;
}
