# 真正打开入口，再填写资料卡

依赖Python3.10+标准库。从本目录执行；默认root是当前教材仓库根目录，catalog默认是程序旁的catalog.csv。

```bash
python3 audit.py build
python3 audit.py geometry
python3 audit.py engineering
python3 audit.py communication
python3 audit.py lecture
python3 audit.py team
```

四个教材入口应输出真实路径、核对日期、内容SHA、主文件SHA、实际章名和封面显示版本，status为“入口与声明一致”。讲义目录本机未取得，team未给入口；owner为空时保持null，不能虚构负责人。观察结果后，仍需读文件，确认内容适用自己的输入、输出和实现环境。

通用形式为 `python3 audit.py 索引名称 [--catalog 清单路径] [--root 教材根目录]`。清单中的version是待核对的显示版本，chapter是待核对章名；故意改错任一项会报告不一致。显示版本不是唯一源码版本，因此另记SHA；同一个2026.08也可能有不同修订。日期只是本机检查日期，不是队内批准日期。

路径迁移实验请在练习副本修改文件位置、main.tex对应input与catalog.csv，重跑并对比SHA。只移动文件而不改input会报告未引用。脚本只支持本书明确的chapter/input/version写法，不是通用LaTeX解析器；不核对递归包含、协议字段、链接在线状态或责任人的授权，不把文件可打开等同于实现已适用。队内资料、协议修订与人员仍需取得真实出处和确认记录。
