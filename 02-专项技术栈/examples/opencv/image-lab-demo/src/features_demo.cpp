#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
int main() {
    cv::Mat a(240,320,CV_8UC1);
    cv::RNG rng(42); rng.fill(a,cv::RNG::UNIFORM,0,256);
    auto orb=cv::ORB::create();
    std::vector<cv::KeyPoint> kp; cv::Mat desc;
    orb->detectAndCompute(a,cv::noArray(),kp,desc);
    if(desc.empty()) return 1;
    std::vector<cv::DMatch> matches;
    cv::BFMatcher(cv::NORM_HAMMING,true).match(desc,desc,matches);
    for(const auto& m:matches) if(m.distance!=0) return 2;
    std::cout << matches.size() << "\n";
}
