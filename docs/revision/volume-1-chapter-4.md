# 卷一第四章：更高效的利用AI开发

修订日期：2026-10-31。新增为基础通识卷最后一个编号章，位于“卷一小结”之前。面向已学 Linux、Git、C++ 与 CMake 的新生，重点是把 AI 协作变成能解释、能验证、能交接的开发工作。

## 内容与文件

- `01-基础通识/Chapter4/chapter.tex`：章首目标、学时与边界；子文件入口；小结、10 道章末习题与 6 项现场验收。
- `principles.tex`：责任与反许愿式编程、LLM/Token/Attention 简介、Harness、模型与思考等级、上下文压缩/检索/记忆、权限与证据。
- `desktop.tex`：普通聊天/Work/代码代理/CLI 的适用场景，桌面版与 CLI 安装登录，项目与主界面、差异/终端/审查、浏览器/远程/云/调度、插件与 MCP。
- `cli_workflow.tex`：CLI 状态、配置来源与用量、编辑器上下文、Hooks 导览、权限、搜索、停止/后台、审查与 exec、Plan/Goal、恢复/新建/侧聊/分叉/历史回退、worktree 与子代理。
- `management.tex`：提示词与任务卡、基线与分步项目管理、独立审查与交接、AGENTS.md 与 Skill 编写、完整换算修复实验。
- `01-基础通识/answers.tex`：追加第四章 23 道随堂练习与 10 道章末题的对应题解。草稿题解已集中到既有文件，没有保留第二套答案。
- `01-基础通识/examples/ai-development-demo/`：完整离线 C++ 工程、任务卡、AGENTS.md 与待安装的教学 Skill 模板。
- 卷一 `main.tex`、`summary.tex`、根 README 与修订索引同步增加第四章；共享模板 `templates/cover.tex` 的卷一学习导览同步改为四个阶段，其他卷正文没有修改。未移动或重命名既有文件；新增截图及导览预览的变更见下文。

全章 27 个示例、23 道随堂练习、10 道章末题。题量按安装、入口、工具、历史、任务管理等实际能力拆分；章末题重在比较与自测，现场验收检查本人操作、解释和交付。核心小节均有独立示例/练习，设置、用量、IDE 与 Hooks 导览共用 CLI 启动练习核验；AGENTS 与 Skill 的相邻小节各有练习。静态结构检查不替代这些教学覆盖判断。

## 通用原理与软件示例的区分（同日修订）

按用户反馈，前部改为可迁移的 AI 使用原理，ChatGPT 桌面版与 Codex CLI 只承担具体软件演示：

- 删除前部 GPT 型号清单及 Power、Ultra、Fast 等专有菜单描述，改按任务能力、输入与上下文、工具环境、延迟/费用/部署条件选择模型。
- 区分模型、产品/客户端与 Harness；说明思考等级仅在支持时调整，不同产品的同名等级不能直接比较，增强模式也可能切换模型、工具或代理。
- 用任意可用工具完成同基线比较；上下文、压缩与记忆先讲通用机制，补充没有思考开关、自动记忆、压缩入口或本地访问时怎样继续工作。
- 普通聊天、工具任务与代码代理按实际能力选择，CLI 作为客户端入口讲解；后部安装地址、按钮与命令仍完整保留在明确标示的软件案例中。
- Plan/Goal、托管 worktree 与子代理权限按本例限定；Codex 历史回退的文件边界与其他产品可能提供的文件检查点分开说明。
- AGENTS.md/Skills 按用户进一步要求，只在开头提醒其他产品可能位置、文件名不同，后续保持 Codex 的具体位置与加载方式，不扩展兼容差异讨论。
- 同步相关练习、题解、章首/章末、现场验收与卷末小结。题量仍为 23 道随堂练习、10 道章末题；离线演示源码未改，沿用下方已完成的运行证据。

通用化修订的结构、PDF 与视觉检查单列在 [ai-development-generalization-20261031](evidence/ai-development-generalization-20261031/)，初版的页码及 PDF 指纹保留作历史记录。该阶段整卷 256 个物理页，本章位于物理 174–203 页（印刷页 165–194），新增题解位于物理 252–256 页；后续真实截图版以接下来一节及其证据为准。

## 真实截图与脱敏（同日初版）

按用户要求，添加三张本机真实窗口截图及正文交叉引用：

| 原始取景 | 入书文件 | 说明 |
| --- | --- | --- |
| `/tmp/tutorial4new-ai-desktop-raw.png` | `images/ai/desktop-overview_revised.png` | 保留侧栏与输入等区域，实心遮挡项目/聊天名称、标题、正文和账号头像；添加 1–4 区域标注 |
| 同一主界面原图 | `images/ai/composer-controls_revised.png` | 只取输入、权限、模型/模式和停止控件，不含个人项目和对话 |
| `/tmp/tutorial4new-ai-review-raw.png` | `images/ai/review-pane_revised.png` | 只取当前教材源码的差异面板，遮挡文件路径；保留真实范围、行号、代码和颜色 |

来源为 2026-10-31 本机 Linux 的 ChatGPT 桌面版 Codex 入口，通过 Niri 的专用窗口截图命令取景。官方文档中若干图片实际是 HTML/CSS 界面示意，本次没有把它们当作真实截图。应用的精确构建号未单独核验，以取景日期及界面为准。

初版脱敏脚本为 `scripts/prepare_ai_screenshots.sh`（见提交 `bc7b581`），已用原图实际生成候选并逐张查看。初版要求已核对的原图尺寸，使用不透明遮挡和局部取景，移除元数据、透明通道及隐藏图层；不重绘功能控件。原图仅在临时目录处理，不纳入仓库。三张候选经隐私、图文和清晰度检查后，以 `_revised` 名称入库；当前骨架占位版见下一节，[图片说明](../../01-基础通识/images/ai/README.md)记录现行用途与复用方式。

三图放在 `desktop.tex` 的界面区域、输入区控件、差异面板讲解旁边。前部原理保持通用表述，截图里的 GPT 型号与模式明确标为本机实例，未改回通用型号推荐。实际打开本机差异面板和终端以取景，但终端画面的字形不适合作教材配图，未采用。

截图版重新编译至引用稳定，当前整卷 259 个物理页，本章为物理 174–206 页（印刷页 165–197），新增题解为物理 255–259 页。PNG 指纹、隐私复核及 PDF 视觉检查记录位于 [ai-development-screenshots-20261031](evidence/ai-development-screenshots-20261031/)。临时未脱敏原图已清理；安装、账号、调度、云端和真实设备的原有未实测范围继续保留。

## 骨架占位脱敏（同日修订）

按用户反馈，将主界面与差异面板的实心遮挡改为与深色界面协调的静态骨架占位：

- `desktop-overview_revised.png` 沿用原名：侧栏使用分层圆角占位条，标题使用短条，对话使用消息及代码块形状，头像使用中性圆形；左上 Dot 行与左下头像的矩形残留已清理。
- `review-pane_revised.png` 沿用原名：文件路径改为低对比度圆角短条，差异范围、计数、代码和行号保留。
- `composer-controls_revised.png` 不变：它本身只包含真实控件，没有隐私遮挡。

使用内置 imagegen 编辑已经脱敏的 Git 基图，生成占位候选；随后用 `prepare_ai_screenshots.sh` 的坐标蒙版只合入原隐私区，避免整张生图重绘真实界面。蒙版保护四个教学标号；左上行及账号圆形采用匹配背景的确定性整理。最终图保持原尺寸、RGB 展平且无元数据，没有添加示例命令或虚构运行结果。旧版本保留在 Git，不增加备份图片。

脚本现接收两张已脱敏基图、两张生图候选及一个新输出目录，不能直接接收含隐私的原始截图。提示词与验证证据见 [ai-development-skeleton-20261031](evidence/ai-development-skeleton-20261031/)；两图原隐私区以外的变化像素均为 0，四个教学标号、输入区、差异代码及工具栏另行核对一致。图注与相邻正文同步说明骨架条仅用于脱敏，并不表示软件正在加载。整卷编译至引用稳定，仍为 259 页；物理 184–186 页已逐页查看，其余 256 页文本不变。脚本的错误尺寸与已有输出目录保护实际检查通过。

本次只修改配图、对应图文、制图脚本与记录，不改变示例代码、题量或原有验收限制；章节规范仍为 19 项通过、1 项实际流程待补测。

## 卷首导览同步（同日追加）

根据第四章内容更新共享模板 `templates/cover.tex`：卷一的学习路径由三个阶段改为四个阶段，新增“用好 AI 协作，独立验证交付”，概括入口与模型选择、上下文、项目规则、Skill、Git/worktree 和独立检查。同步调整卷首引导语及封面关键词；面板收紧间距，保持原有字号与整体风格。卷二、卷三仍使用三个阶段。

刷新 `assets/covers/` 中卷一两页 PDF、默认 `preview.pdf`、卷一封面/导览 PNG、并排预览及三卷总览；生成预览沿用既有文件名，无既有文件移动或重命名。

提交前复核见 [ai-development-guide-20261031](evidence/ai-development-guide-20261031/)：

- 按 README 直接执行 XeLaTeX 两遍，整卷仍为 259 个物理页，无未定义引用、重复标签、缺字或需重编提示；保留原有字体替代与第一章 Night Theme Switcher 的溢出提示。
- 实际查看整卷第 2 个物理页及独立封面/导览预览，四个阶段的文字、连线、编号和页脚完整。与已检查的截图版 PDF 比较，仅物理 1–2 页文字变化，其余 257 页文本逐页一致。
- 用同一环境分别编译修改前后共享模板的卷二、卷三封面与导览，渲染逐像素一致。
- 结构与题解定位检查通过；在临时副本复现示例原版的预期失败，改为浮点除法后 CTest 与独立边界输入通过，随书教学缺陷保留。

本次未补测安装、账号、调度、云端或设备流程，原有未完成范围继续保留。

## 官方资料与版本边界

功能资料按 2026-10-31 官方页面搜索并实际读取，正文在相关位置给出可点击链接。主要来源：

- [App](https://learn.chatgpt.com/docs/app)、[Linux app](https://learn.chatgpt.com/docs/linux/linux-app)、[Codex CLI](https://learn.chatgpt.com/docs/codex/cli)、[Authentication](https://learn.chatgpt.com/docs/auth)。
- [Models](https://learn.chatgpt.com/docs/models)、[Glossary](https://learn.chatgpt.com/docs/glossary)、[Conversation state](https://developers.openai.com/api/docs/guides/conversation-state)、[Memories](https://learn.chatgpt.com/docs/customization/memories)。
- [Projects](https://learn.chatgpt.com/docs/projects)、[Code review](https://learn.chatgpt.com/docs/code-review)、[Browser](https://learn.chatgpt.com/docs/browser)、[Scheduled tasks](https://learn.chatgpt.com/docs/automations)。
- [Developer commands](https://learn.chatgpt.com/docs/developer-commands)、[Desktop slash commands](https://learn.chatgpt.com/docs/reference/slash-commands)、[Config basics](https://learn.chatgpt.com/docs/config-file/config-basic)、[Hooks](https://learn.chatgpt.com/docs/hooks)、[Security](https://learn.chatgpt.com/docs/agent-approvals-security)。
- [Goals](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)、[Long-running work](https://learn.chatgpt.com/docs/long-running-work)、[Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)、[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)。
- [History revert](https://learn.chatgpt.com/docs/app-server#revert-thread-history)：只用来核实历史与文件的边界，没有要求读者使用内部协议。
- [Prompting](https://learn.chatgpt.com/docs/prompting)、[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Build skills](https://learn.chatgpt.com/docs/build-skills)、[Plugins](https://learn.chatgpt.com/docs/plugins)、[Docs MCP](https://developers.openai.com/learn/docs-mcp)。

正文没有固定价格、上下文窗口容量或永久模型排名。Linux 桌面 Preview 与 Ubuntu 22.04 的支持差异明确写出。CLI 双 Esc 按当前文档解释为编辑上一消息并分叉；文件恢复另用 Git。Goal 不编造统一的预算调整按钮或 `/goal budget` 命令。GUI 名称、功能、平台、账号与管理策略会继续变化，读者需复核实际选择器与帮助。

## 实际验证与限制

证据目录：[evidence/ai-development-20261031](evidence/ai-development-20261031/)。

1. 本机只读检查 Codex CLI `0.166.0` 的版本与帮助。没有更换本机安装或运行安装脚本，没有读取/复制登录凭据。
2. 离线示例在 `/tmp` 完整副本配置并构建。保留随书原版整数除法缺陷：1500 与 -500 两用例按预期失败，CTest 返回 8；将副本改为 `/ 1000.0` 后 CTest 返回 0。额外独立样本 `1、999、-1500、INT_MAX、INT_MIN` 通过。正文与实际源码由 `lstinputlisting` 同源引入。
3. CMake 最低版本统一为 3.20，因为 `ctest --test-dir` 是 3.20 引入。验证使用本机已有 CLion 附带 CMake/CTest 和 g++，工具版本、命令、退出状态及原始日志见 `runtime.json` 与相邻日志。独立审查者另在 `/tmp` 副本复现了原失败、修复与相同边界结果。
4. 手动 worktree 示例在独立 `/tmp/rm-ai-worktree-proof-yuklvxjd` 仓库实跑：建立两个目录、候选分支修改提交、主目录仍保留基线、分支差异、快进合入、干净状态、正常移除 worktree 与删除已合入分支均符合讲解。未对教材 Git 仓库执行这些实验操作。
5. 教学 Skill 通过内置 `quick_validate.py`（输出 `Skill is valid!`）；其名称/描述、触发边界、AGENTS 发现链与目录位置经独立内容审查。该检查不代表已在真实账号中测完自动选择、插件连接或模型行为。
6. `check_tex_structure.py ... --chapter 4` 通过：23 道随堂练习、10 道章末题，资源/包含关系、唯一标签、引用与答案定位有效。额外检查答案对每个题目标签恰好引用一次，环境成对；`git diff --check` 通过。详见 `structure.log` 与 `static.json`。
7. 初版采用仓库记录的 XeLaTeX 直接编译方式，两遍至引用稳定；当时整卷 254 个物理页，新章位于物理 174–201 页（印刷页 165–192），新增题解位于物理 250–254 页。检查目录、新章、卷末小结及新增题解的渲染，修复段尾孤行与安装/CLI/Goal/worktree 短命令块拆页。当时的页码、日志与视觉记录见 `pdf-check.json`，通用化修订后的当前记录见上方新证据目录。初次 latexmk 自动调用无文献输入的 biber 失败，改用直接 XeLaTeX 构建；没有为此修改共享模板。整卷保留原有 Fandol 字体替代提示与第一章 Night Theme Switcher 旧段落的 21.59 pt 溢出；新增章节没有缺字、未定义引用或溢出。

**未实操的范围：**各平台重新安装、真实账号模型调用、GUI 按钮全流程、外部账号连接、插件发布审查、定时任务运行及云/远程功能。这些部分已按官方文档给出前提、步骤、结果判断与练习，仍需在相应平台与账号上补测。没有创建定时任务、发送评论、修改外部账号或操作设备。离线数值与 worktree 检查不能推导出任何设备或实车验收结论。

## 章节规范 20 项检查

| 项 | 结论 | 位置或证据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | `chapter.tex` 学习目标、2–3 天建议学时及本卷/版本边界 |
| 2 核心示例 | 通过 | 27 个 example；入口、安装、工具、模式、规则与交付均有前提/步骤/结果判断 |
| 3 完整小项目 | 通过 | `examples/ai-development-demo`，C++17/CMake，明确教学缺陷 |
| 4 正文展示项目 | 通过 | `management.tex` 综合实验，目录、完整接口/实现/测试/CMake、规则与 Skill 同源引入 |
| 5 命令说明 | 通过 | 安装、CLI、MCP、worktree 与构建提供形式、目录、参数与替换说明 |
| 6 随堂练习 | 通过 | 23 题，合并练习的范围见上文，各核心能力有明确任务 |
| 7 难点归纳 | 通过 | 模型/Harness、上下文机制、模式/历史、插件/技能/规则有小结或对比表 |
| 8 易错与操作影响 | 通过 | 覆盖凭据、沙箱、外部写入、Arch 升级、重定向、删除/回退与历史边界 |
| 9 本章小结 | 通过 | `chapter.tex` 知识地图及工程责任 |
| 10 章末习题 | 通过 | 10 题，基础、提高、综合与实践设计 |
| 11 现场验收 | 通过 | 6 项可演示任务，检查本人解释/操作，不重复自测题 |
| 12 题解 | 通过 | 33 题完整对应既有 `answers.tex`，开放题有判断依据 |
| 13 语言与读者 | 通过 | 承接前三章，使用你/我们，解释操作原因与结果；反许愿式编程有具体自检 |
| 14 图片查看 | 通过 | 三张截图已审查；本次两张骨架脱敏图及 PDF 实际尺寸复核，原隐私区外像素不变，输入区图未改 |
| 15 图片标记 | 通过 | 继续沿用三个 `_revised.png` 名称；两图重新整理后复核，正文、脚本输出与图片说明同步 |
| 16 文件组织 | 通过 | Chapter4 五个主题文件，示例与证据独立；无既有文件移动 |
| 17 包含与引用 | 通过 | main 接入、目录/小结及卷首导览同步；结构检查，无重复/未定义标签 |
| 18 源码与排版 | 通过 | 沿用共享层级和环境；新章长表达式移入代码环境，最终渲染检查 |
| 19 实际运行 | 未完成 | 数值实验、独立边界、worktree、静态 Skill 验证及本机差异/终端面板取景已完成；安装、完整 GUI/账号/调度等流程仍待补测 |
| 20 编译与 PDF | 通过 | XeLaTeX 编译至引用稳定；截图、导览与骨架占位版检查见对应 `pdf-check.json`，最新 259 页且物理 184–186 页已查看；卷二/三共享模板回归沿用导览版一致结论 |

截图追加后统计：19 项通过、1 项未完成、0 项不适用。新增章节单独记录，没有降低既有全书硬件验收标准，也未并入 2026-09-29 首次修订的历史统计。
