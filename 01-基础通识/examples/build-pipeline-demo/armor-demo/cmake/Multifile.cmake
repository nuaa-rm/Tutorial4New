cmake_minimum_required(VERSION 3.16)
project(armor_demo LANGUAGES CXX)

set(ARMOR_SOURCES src/main.cpp src/armor.cpp)
add_executable(armor_demo ${ARMOR_SOURCES})
target_include_directories(armor_demo PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/include")
target_compile_features(armor_demo PRIVATE cxx_std_17)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(armor_demo PRIVATE -Wall -Wextra)
endif()

option(SAVE_OUTPUT "Enable save-output message" OFF)
if(SAVE_OUTPUT)
    target_compile_definitions(armor_demo PRIVATE SAVE_OUTPUT)
endif()
