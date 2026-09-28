#include <opencv2/opencv.hpp>
#include <iostream>

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Usage: image_viewer <image_path>\n";
        return 1;
    }
    const cv::Mat image = cv::imread(argv[1]);
    if (image.empty()) {
        std::cerr << "Cannot read image: " << argv[1] << '\n';
        return 2;
    }
    std::cout << "size=" << image.cols << 'x' << image.rows << '\n';
    cv::imshow("Armor image", image);
    cv::waitKey(0);
    return 0;
}
