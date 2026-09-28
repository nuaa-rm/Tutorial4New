#include <opencv2/opencv.hpp>
#include <algorithm>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "用法: pipeline_demo 图片路径\n";
        return 1;
    }
    cv::Mat image = cv::imread(argv[1]);
    if (image.empty()) return 2;
    cv::Mat hsv, low, high, mask, opened, closed, edges;
    cv::cvtColor(image, hsv, cv::COLOR_BGR2HSV);
    cv::inRange(hsv, cv::Scalar(0,70,50), cv::Scalar(10,255,255), low);
    cv::inRange(hsv, cv::Scalar(170,70,50), cv::Scalar(179,255,255), high);
    cv::bitwise_or(low, high, mask);
    auto kernel = cv::getStructuringElement(cv::MORPH_RECT, {3,3});
    cv::morphologyEx(mask, opened, cv::MORPH_OPEN, kernel);
    cv::morphologyEx(opened, closed, cv::MORPH_CLOSE, kernel);
    cv::Canny(closed, edges, 50, 150);
    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(closed, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
    cv::Mat annotated = image.clone();
    int kept = 0;
    for (const auto& contour : contours) {
        const double area = cv::contourArea(contour);
        if (area < 100.0) continue;
        auto rectangle = cv::minAreaRect(contour);
        const float shorter = std::min(rectangle.size.width, rectangle.size.height);
        const float longer = std::max(rectangle.size.width, rectangle.size.height);
        if (shorter <= 0 || longer / shorter < 1.5f) continue;
        cv::Point2f points[4];
        rectangle.points(points);
        for (int i = 0; i < 4; ++i)
            cv::line(annotated, points[i], points[(i+1)%4], cv::Scalar(0,255,0), 1);
        ++kept;
        std::cout << "保留面积=" << area << " 长宽比=" << longer / shorter << '\n';
    }
    for (const auto& pair : std::vector<std::pair<std::string, cv::Mat>>{
            {"mask.png",mask},{"opened.png",opened},{"closed.png",closed},
            {"edges.png",edges},{"annotated.png",annotated}})
        if (!cv::imwrite(pair.first, pair.second)) return 3;
    std::cout << "像素数=" << cv::countNonZero(mask) << ','
              << cv::countNonZero(opened) << ',' << cv::countNonZero(closed)
              << " 外轮廓=" << contours.size() << " 保留=" << kept << '\n';
}
