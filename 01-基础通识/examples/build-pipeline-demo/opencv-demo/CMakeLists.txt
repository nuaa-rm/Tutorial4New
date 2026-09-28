cmake_minimum_required(VERSION 3.16)
project(opencv_demo LANGUAGES CXX)

find_package(OpenCV REQUIRED)
add_executable(image_viewer main.cpp)
target_compile_features(image_viewer PRIVATE cxx_std_17)
target_include_directories(image_viewer PRIVATE ${OpenCV_INCLUDE_DIRS})
target_link_libraries(image_viewer PRIVATE ${OpenCV_LIBS})
