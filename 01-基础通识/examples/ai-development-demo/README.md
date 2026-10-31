# AI 辅助开发：从错误现象到可复核交付

本项目对应卷一第四章。依赖 C++17 编译器、CMake 3.20+、Git（版本管理练习时使用）。不需要模型、API Key、网络、硬件或 Python 包。

先将整个目录复制到自己的练习位置，例如 `~/rm-ai-lab`。所有构建命令在复制后的项目根执行：

```bash
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

**随书原版故意保留整数除法缺陷，第一次测试应失败。** 测试输出 `mm=1500 expected=1.5 actual=1`、`mm=-500 expected=-0.5 actual=0`、`failures=2`；CTest 返回非零。0 和 1000 两个整米用例会通过，这正是只看一个正常样本容易漏错的原因。

阅读 `task.md`，先手算结果、解释整数除法，再在复制后的工程中用代码代理或手动修复。正确方向是在除法前使运算成为浮点除法；单纯转换返回值不能找回已截断的小数。重新构建并运行同一组测试，预期 CTest 全部通过、返回 0。额外独立检查如 1、999、-1500 mm，确认没有仅迎合已知样本。

可以把练习副本初始化为自己的 Git 仓库（不要在教材仓库里照抄 init）：

```bash
git init -b main
git add .gitignore AGENTS.md CMakeLists.txt include src tests task.md README.md skill-template
git commit -m "保存带已知缺陷的教学基线"
git switch -c fix/distance-units
```

Git 身份未配置时，只在该练习仓库用 `git config user.name '你的名字'` 与 `git config user.email '你的邮箱'` 配置；不要复制其他人的身份。修复后自己运行 `git diff`，检查没有删除测试或放宽精度，再提交相关源码与必要说明。

`AGENTS.md` 保存本工程长期规则，`task.md` 保存本次验收。`skill-template/mm-conversion-review/SKILL.md` 是未安装的教学 Skill 模板；需要体验发现与调用时，在练习副本执行：

```bash
mkdir -p .agents/skills
cp -r skill-template/mm-conversion-review .agents/skills/
codex
```

在 Codex 中运行 `/skills` 查看，再发送 `$mm-conversion-review 请只审查当前换算修改`。界面若未刷新，重启 Codex。检查它是否读过接口、解释操作数类型、核对非整米及负数用例，并报告真实运行结果；不能只看回复有没有固定几个标题。

交付时可新建 `handoff.md`，记录基线/修复提交、结论、验证命令及退出状态、额外样本与未验证范围。这个工程只能证明数值函数在这些输入上的行为；不能证明真实相机距离、串口协议或实车控制已通过验收。
