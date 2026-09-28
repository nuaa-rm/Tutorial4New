#include <algorithm>
#include <iostream>
#include <vector>
int main() {
std::vector<int> vec={1,2,3,4,5,6,7,8,9,10};
for(auto it = vec.begin(); it != vec.end(); ){ //注意：这里没有++it
    if(*it % 2 == 0){
        it = vec.erase(it); //erase返回下一个有效迭代器
    }else{
        ++it;
    }
}
    for (int x : vec) std::cout << x << " ";
    std::cout << "\n";
}
