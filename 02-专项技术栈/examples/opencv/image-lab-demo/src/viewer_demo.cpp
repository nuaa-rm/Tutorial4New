#include <opencv2/opencv.hpp>
#include <iostream>

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "用法: viewer_demo 图片路径\n";
        return 1;
    }
    cv::Mat image = cv::imread(argv[1], cv::IMREAD_COLOR);
    if (image.empty()) {
        std::cerr << "无法读取: " << argv[1] << '\n';
        return 2;
    }
    std::cout << "尺寸=" << image.cols << 'x' << image.rows << '\n';
    cv::imshow("Image lab", image);
    const int key = cv::waitKey(0);
    if (key == 's' && !cv::imwrite("saved.png", image)) return 3;
    cv::destroyAllWindows();
    return 0;
}
