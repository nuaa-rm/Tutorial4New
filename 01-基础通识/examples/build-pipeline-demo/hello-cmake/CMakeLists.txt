cmake_minimum_required(VERSION 3.16)
project(hello_cmake LANGUAGES CXX)

set(ARMOR_NAME "training_armor")
message(STATUS "Armor: ${ARMOR_NAME}")
message(STATUS "Compiler: ${CMAKE_CXX_COMPILER}")

add_executable(hello hello.cpp)
target_compile_features(hello PRIVATE cxx_std_17)
