# PAS 安装引导

> 这份文件同时写给两个读者：**你（新用户）** 和 **CC（执行者）**。
> 带「用户」标签的段落你来看，带「CC」标签的段落 CC 来读。
> 安装完成的标准：从 Claudian 启动后，CC 能读到 `.pas/CLAUDE.md` 和 `ROOT.md` 并进入 PAS 状态。

---

## 【用户】你需要提前做的一件事

在让 CC 开始之前，你需要去 [DeepSeek 开放平台](https://platform.deepseek.com/) 申请一个 API Key，把它复制出来备用。这是唯一需要你自己去做的事，其他全部交给 CC。

---

## 【CC】这是什么任务

你现在拿到的是 **PAS（Personal Assistant System）** 的项目文件，这是一套基于 Obsidian + Mem0 + DeepSeek 的个人知识管理系统。

你当前的任务是：**在这台机器上从零完成 PAS 的落地安装**，让系统在这台新机器上完整跑起来。

这不是常规对话任务，是一次**安装部署任务**。读完本文件后，按顺序执行，不要跳步。

---

## 【CC】执行顺序

### 第一步：读协议，了解系统

先读 `.pas/CLAUDE.md`，了解这个系统是什么、有哪些组件、运行逻辑是什么。这一步不做任何操作，只是建立背景认知。

---

### 第二步：侦测当前机器环境

运行以下侦测，把结果完整告诉用户，不要省略：

1. **Python 路径侦测**：找出这台机器上 Python x64 的实际安装路径。
   - 尝试 `where python`
   - 尝试 `py -3 -c "import struct; print(struct.calcsize('P')*8, 'bit')"` 确认是否为 64 位
   - 如果没有 Python，记录「未安装」，后续步骤安装

2. **库根路径确认**：用 Python 扫描，确认当前 `.pas/CLAUDE.md` 所在的库根绝对路径是什么。

3. **DeepSeek API Key 侦测**：
   ```
   python -c "import os; print(os.environ.get('DEEPSEEK_API_KEY','NOT FOUND'))"
   ```
   如果返回 `NOT FOUND`，记录「待写入」。

侦测完毕，把三项结果汇报给用户，等待用户确认后继续。

---

### 第三步：路径替换

协议和脚本里有两处硬编码路径来自原始安装机器，必须全部替换成本机实际路径：

- `<PYTHON_EXE>` → 替换为本机 Python 3.11 x64 实际路径，或使用 `py -3.11`
- `<PAS_ROOT>` → 替换为本机库根绝对路径

- <YOUR_USER_ID> → 替换为新用户自选的 user_id（建议使用稳定、简短、无空格的标识。先问用户要这个 id，再执行替换）

**需要检查并替换的文件范围：**
- `.pas/CLAUDE.md`
- `.pas/mem0_config.py`
- `.pas/` 目录下所有 `.py` 脚本
- 库根目录下所有 `.py` 脚本（如 `test_mem0.py`、`setup.bat`）
- .claude/settings.json（hook 注册配置，含两处 <PYTHON_PATH> 和两处 <VAULT_ROOT>）

**操作方式**：用 Python 脚本做全局字符串替换，不要手动逐个改。改完之后，把替换了哪些文件、替换了多少处，汇报给用户。

---

### 第四步：安装依赖

依次安装以下依赖，全部使用本机确认过的 Python x64 路径运行，不得使用系统默认 `python` 或 `pip`：

```
mem0ai
fastembed
qdrant-client
markitdown
```

如果库根目录存在 `setup.bat`，**优先运行它**，不要重复手动装。

装完后验证：逐个 `import` 确认没有报错。

---

### 第五步：写入 DeepSeek API Key

用户告诉你 API Key 之后，将其持久化到 Windows 系统环境变量：

```
DEEPSEEK_API_KEY = 用户提供的 Key
```

**写入方式**：通过 PowerShell 命令写入系统级环境变量（不是用户级）：

```powershell
[System.Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "用户提供的Key", "Machine")
```

写完后立即用 Python 验证是否生效：
```
python -c "import os; print(os.environ.get('DEEPSEEK_API_KEY','NOT FOUND'))"
```

如果返回 NOT FOUND，说明当前进程环境变量未刷新——这是正常的，重启 Claudian 后会生效。如实告知用户，不要报错。

---

### 第六步：验证 Mem0 配置

读 .pas/mem0_config.py，确认配置结构（LLM / Embedding / Qdrant 三项）。

然后照 mem0_config.py 的调用方式，写一个最小验证脚本：初始化 → 用本机 user_id 写入一条测试记录（infer=False）→ 用 m.search() 查回来 → 删除该测试记录。四步都通过，Mem0 链路确认可用。

不要凭记忆构造调用参数，参数格式以 mem0_config.py 和协议附录的 Mem0 操作规范为准（注意：user_id 在 add() 里是顶层参数，在 search() 里要放进 filters={}）。

---

### 第七步：验证启动

关闭当前 CC 窗口，重启 Claudian，新开一个空白文件，说一句话。

**验证标准**：CC 能读到 .pas/CLAUDE.md，输出里出现 PAS 相关内容，说明进入了 PAS 状态。ROOT.md 此时内容为空是正常的，不是安装失败——它会在日后使用中由 CC 逐步填充。

这一步通过，安装完成。

---

## 【CC】安装过程中的纪律

1. **路径问题用 Python 解决，不用 `dir` 命令**：含中文或空格的路径在 Bash 里极易失败。需要扫目录用 `os.listdir(path)` 或 pathlib。

2. **不凭记忆手写脚本**：无论是依赖验证还是路径替换，先看库里有没有现成脚本，有就照结构改，不要即兴拼 `python -c "..."` 单行命令。

3. **每步完成后汇报，等用户确认再继续**：不要把多个步骤连续执行完再汇报。

4. **遇到错误，第一动作是读已有文件**：读 `.pas/CLAUDE.md` 附录的环境配置说明，不是凭记忆重新试探。

---

## 【CC】安装完成后

安装完成后，读 `.pas/ROOT.md`，了解这个系统的用户画像部分当前是空的（或是模板）——这是正常的，用户会在日后使用中逐步填充。

你现在的角色和协议里写的完全一致：PAS 的执行者，准备好接受用户的第一个真实任务。
