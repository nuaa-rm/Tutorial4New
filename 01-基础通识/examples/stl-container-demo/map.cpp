#include <iostream>
#include <map>
#include <unordered_map>
#include <string>

int main() {
    std::map<std::string,int> score;            //常见实现用红黑树，标准要求按键有序
    score["alice"] = 90;                        //插入或修改
    score.emplace("bob", 85);
    std::cout << score["alice"] << std::endl;   //按键访问
    std::cout << score.count("carol") << std::endl; //判断键是否存在：0
    for(auto& [name, s] : score){               //遍历，按字母序输出
        std::cout << name << ": " << s << std::endl;
    }

    std::unordered_map<std::string,int> fastScore; //哈希表实现，不保证遍历顺序
    fastScore["alice"] = 90;
    return 0;
}
