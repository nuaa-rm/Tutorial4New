cmake_minimum_required(VERSION 3.16)
project(ide_demo LANGUAGES CXX)
add_executable(ide_demo main.cpp)
target_compile_features(ide_demo PRIVATE cxx_std_17)
