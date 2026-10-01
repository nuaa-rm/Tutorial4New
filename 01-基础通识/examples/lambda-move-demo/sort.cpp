#include<iostream>
#include<functional>
#include<utility>

template<class T>
void sort(T* array,int n,std::function<bool(T&,T&)> less){ //升序排序
    for(int i=0;i<n;i++){
        for(int j=i+1;j<n;j++){
            if(less(array[j],array[i])){
                std::swap(array[i],array[j]);
            }
        }
    }
}

typedef struct Block{
    char ch;
    int id;
}Block;

int main() {
    auto sum = [](int a,int b){
        return a+b;
    };

    std::cout << sum(1,2) << std::endl;

    Block blocks[5]={{'a',2},{'d',4},{'q',1},{'t',7},{'s',-1}};
    sort<Block>(blocks,5,[](Block& a1,Block& a2){//lambda表达式作为参数传递
        return a1.id > a2.id; //在本应传入小于关系用来升序排序的函数传入大于关系，用来降序排序
    });
    for(int i=0;i<5;i++){
        std::cout << "ch:" << blocks[i].ch << "  id:" << blocks[i].id << std::endl;
    }
    return 0;
}
