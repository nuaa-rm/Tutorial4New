#include <algorithm>
#include <iostream>
#include <vector>
int main() {

std::vector<int> vec{1, 2, 3, 4, 5, 6, 7, 8, 9, 0};
vec.erase(vec.begin()+5);            //删除第6个元素
vec.erase(vec.begin()+5, vec.end()); //删除第6个元素之后的所有

std::vector<int> vec1{1, 2, 3, 4, 5, 6, 7, 8, 9, 0};
std::iter_swap(vec1.begin(), vec1.begin()+1); //交换第一个和第二个元素

std::vector<int> vec2{1, 2, 3, 4, 5, 6, 7, 8, 9, 0};
std::sort(vec2.begin(), vec2.end(), [](int a, int b){
    return a > b;                  //降序排序
});

//remove_if 只把不满足条件的元素挪到前面，并不真正删除
//正确姿势是 erase-remove 惯用法：
vec2.erase(std::remove_if(vec2.begin(), vec2.end(), [](int a){
    return a > 5;
}), vec2.end());                    //这才真正删除了大于5的元素
    for (int x : vec2) std::cout << x << " ";
    std::cout << "\n";
}
