cmake_minimum_required(VERSION 3.16)
project(armor_demo LANGUAGES CXX)

add_library(armor STATIC src/armor.cpp)
target_include_directories(armor PUBLIC
    "${CMAKE_CURRENT_SOURCE_DIR}/include")
target_compile_features(armor PUBLIC cxx_std_17)

add_executable(armor_demo src/main.cpp)
target_link_libraries(armor_demo PRIVATE armor)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(armor PRIVATE -Wall -Wextra)
    target_compile_options(armor_demo PRIVATE -Wall -Wextra)
endif()

option(SAVE_OUTPUT "Enable save-output message" OFF)
if(SAVE_OUTPUT)
    target_compile_definitions(armor_demo PRIVATE SAVE_OUTPUT)
endif()
