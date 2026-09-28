#include <algorithm>
#include <iostream>
#include <vector>
int main() {

std::vector<int> vec{1,2,3,4,5,6};
(void)vec[0];         //访问（快速）
(void)vec.at(0);      //访问（安全，越界会抛异常）
(void)vec.front();    //第一个元素
(void)vec.back();     //最后一个元素
(void)vec.empty();    //检查是否为空
(void)vec.size();     //返回容器大小
vec.reserve(10);//预留空间，避免反复扩容
vec.clear();    //清除所有元素
vec.insert(vec.begin(),1);//插入元素
vec.erase(vec.begin());//删除元素
vec.push_back(1); //在最后添加
vec.emplace_back(); //在最后原位构造，省去一次拷贝
vec.pop_back();     //删除最后一个
    std::cout << "size=" << vec.size() << " capacity=" << vec.capacity() << "\n";
}
