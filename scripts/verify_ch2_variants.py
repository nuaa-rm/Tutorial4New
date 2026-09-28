#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile,json,re
import argparse
parser=argparse.ArgumentParser(description="验证第二章关键参数和错误写法的变化")
parser.add_argument("--output",type=Path,required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]/'01-基础通识'; rows=[]
def run(name,source,standard='c++17',expect=None,compile_fail=False,args=(),flags=(),run_fail=False):
 p=folder/(name+'.cpp');p.write_text(source);binary=folder/name
 c=subprocess.run(['g++','-std='+standard,'-Wall','-Wextra','-pthread',*flags,'-I'+str(root/'examples/smart-pointer-demo'),str(p),'-o',str(binary)],capture_output=True,text=True)
 row={'variant':name,'compile':c.returncode,'diagnostics':c.stderr}
 if compile_fail: assert c.returncode!=0
 else:
  assert c.returncode==0,c.stderr
  r=subprocess.run(['timeout','5s',str(binary),*args],capture_output=True,text=True)
  row.update(run=r.returncode,stdout=r.stdout,stderr=r.stderr)
  if expect is not None:assert ' '.join(r.stdout.split())==expect,(name,r.stdout,expect)
  if run_fail:assert r.returncode!=0 and 'singular' in r.stderr
  else:assert r.returncode==0
 rows.append(row)
with tempfile.TemporaryDirectory(prefix='ch2-variants-') as temp:
 folder=Path(temp)
 run('designated-wrong-order',(root/'examples/class-basics-demo/designated.cpp').read_text().replace('.a = 1, .b = 3','.b = 3, .a = 1'),standard='c++20',compile_fail=True)
 run('forward-enabled',(root/'examples/lambda-move-demo/forward.cpp').read_text().replace('Fun(t);','//Fun(t);').replace('//Fun(std::forward<T>(t));','Fun(std::forward<T>(t));'),expect='右值引用 左值引用 右值引用 const 左值引用 const 右值引用')
 run('capture-nine',(root/'examples/lambda-move-demo/capture.cpp').read_text().replace('object.value = 5','object.value = 9'),expect='2 1 2 9 1')
 run('shared-move',(root/'examples/smart-pointer-demo/shared.cpp').read_text().replace('ptr1 = ptr2;','//ptr1 = ptr2;').replace('//ptr1 = std::move(ptr2);','ptr1 = std::move(ptr2);'))
 assert 'ptr1对象的引用次数为：1' in rows[-1]['stdout'] and 'ptr2对象的引用次数为：0' in rows[-1]['stdout']
 src=(root/'examples/stl-container-demo/adapters.cpp').read_text().replace('{1, 3, 2}','{2, 5, 1, 5}')
 run('adapters-repeat',src,expect='2 5 1 5 5 1 5 2 5 5 2 1')
 run('minimum-priority',src.replace('std::priority_queue<int> priority','std::priority_queue<int, std::vector<int>, std::greater<int>> priority').replace('#include <iostream>','#include <iostream>\n#include <functional>\n#include <vector>'),expect='2 5 1 5 5 1 5 2 1 2 5 5')
 run('overload-return-conflict','int f(int x) {return x;}\ndouble f(int x) {return x;}\nint main() {}',compile_fail=True)
 text=(root/'Chapter2/22_stl.tex').read_text();snippet=re.search(r'\\begin\{tcode\}\s*(std::vector<int> vec=\{1,2,3,4,5,6,7,8,9,10\};.*?错误示范.*?)\\end\{tcode\}',text,re.S).group(1)
 run('invalid-iterator-debug','#include <vector>\nint main() {\n'+snippet+'\n}',flags=('-D_GLIBCXX_DEBUG',),run_fail=True)
 # 多消费者核对收发集合，输出锁只负责保持日志每项完整。
 src=(root/'examples/thread-coordination-demo/bounded-queue.cpp').read_text().replace('BoundedQueue queue(3);','BoundedQueue queue(1);\n    std::mutex output_mutex;').replace('i < 10','i < 20').replace('std::thread consumer([&] {','auto consume = [&] {').replace('while (queue.pop(value)) std::cout << "consume " << value << \'\\n\';','while (queue.pop(value)) {\n            std::lock_guard<std::mutex> output_lock(output_mutex);\n            std::cout << "consume " << value << \'\\n\';\n        }').replace('    });\n    producer.join();','    };\n    std::thread consumer(consume), second(consume);\n    producer.join();').replace('consumer.join();','consumer.join();\n    second.join();')
 run('bounded-queue-two-consumers',src)
 values=[int(x) for x in re.findall(r'consume (\d+)',rows[-1]['stdout'])];assert sorted(values)==list(range(20))
 # 线程池输出可能交错，改成每任务独立计数，在析构后核验一次且仅一次。
 src=(root/'examples/thread-coordination-demo/pool.cpp').read_text().replace('#include <functional>','#include <functional>\n#include <array>')
 src=src[:src.index('int main()')]+'''int main() {
    std::array<int,8> received{};
    {
        ThreadPool pool(2);
        for (int i=0;i<8;++i) pool.enqueue([&,i] { ++received[i]; });
    }
    for (int n : received) std::cout << n << ' ';
    std::cout << '\\n';
}
'''
 run('pool-all-tasks',src,expect='1 1 1 1 1 1 1 1')
args.output.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(f'{len(rows)} 个变体检查通过，日志 {args.output}')
