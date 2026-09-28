#include <opencv2/opencv.hpp>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    cv::VideoCapture capture;
    if (argc == 2) capture.open(argv[1]);
    else if (argc == 3 && std::string(argv[1]) == "--camera")
        capture.open(std::stoi(argv[2]));
    else {
        std::cerr << "用法: video_demo 视频路径 或 --camera 设备编号\n";
        return 1;
    }
    if (!capture.isOpened()) {
        std::cerr << "无法打开视频源\n";
        return 2;
    }
    cv::Mat frame;
    int count = 0;
    while (capture.read(frame) && !frame.empty()) {
        ++count;
        cv::imshow("Video lab", frame);
        if (cv::waitKey(30) == 27) break;
    }
    std::cout << "读取帧数=" << count << '\n';
    capture.release();
    cv::destroyAllWindows();
    return 0;
}
