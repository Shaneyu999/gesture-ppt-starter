# 第一次把项目上传到 GitHub：完整教程

本教程针对这个项目：

```text
C:\Users\Shane\Documents\Codex\2026-09-24\new-chat\outputs\gesture-ppt-starter
```

目标是把项目安全地上传到 GitHub，并保证不上传虚拟环境、摄像头数据、训练模型和密钥。

---

## 一、上传前必须先确认的事情

### 1. 检查 Git 是否安装

打开 PowerShell，运行：

```powershell
git --version
```

如果出现类似下面的输出，说明已经安装：

```text
git version 2.xx.x.windows.x
```

如果没有安装，可以执行：

```powershell
winget install --id Git.Git -e --source winget
```

安装后关闭并重新打开 PowerShell。

### 2. 配置 Git 身份

Git 需要知道提交者是谁：

```powershell
git config --global user.name "你的名字或GitHub用户名"
git config --global user.email "你的GitHub邮箱"
```

检查配置：

```powershell
git config --global --list
```

如果不想公开真实邮箱，可以使用 GitHub 提供的隐私邮箱：

```text
你的用户名@users.noreply.github.com
```

### 3. 确认项目目录

进入项目目录：

```powershell
cd C:\Users\Shane\Documents\Codex\2026-09-24\new-chat\outputs\gesture-ppt-starter
```

确认目录中有这些文件：

```text
README.md
pyproject.toml
requirements.txt
.gitignore
LICENSE
src/
tests/
docs/
configs/
scripts/
```

### 4. 运行测试

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

如果测试全部通过，再继续上传。

### 5. 检查 `.gitignore`

项目中的 `.gitignore` 应该包含：

```text
.venv/
runs/
data/gestures/
data/smoke/
*.pt
*.pth
.env
```

可以用下面的命令检查某个文件是否被忽略：

```powershell
git check-ignore -v .venv
git check-ignore -v runs
git check-ignore -v data/gestures
```

如果命令输出匹配规则，说明不会上传。

---

## 二、初始化本地 Git 仓库

### 1. 初始化

在项目根目录执行：

```powershell
git init
```

### 2. 查看当前状态

```powershell
git status
```

你会看到尚未跟踪的文件。

### 3. 添加文件

```powershell
git add .
```

再次检查：

```powershell
git status
```

重点确认没有出现以下内容：

```text
.venv/
data/gestures/
data/smoke/
runs/
best.pt
*.pth
.env
```

如果看到了，先不要提交，回到 `.gitignore` 检查规则。

### 4. 创建第一次提交

```powershell
git commit -m "Initial commit: gesture PPT control starter"
```

查看提交记录：

```powershell
git log --oneline
```

---

## 三、在 GitHub 创建远程仓库

1. 打开 <https://github.com> 并登录。
2. 点击右上角 `+`。
3. 选择 `New repository`。
4. Repository name 填写：

```text
gesture-ppt-starter
```

5. Description 可以填写：

```text
Real-time hand gesture recognition for PowerPoint and video control.
```

6. 选择 `Public` 或 `Private`。
7. 不要勾选 `Add a README file`。
8. 不要勾选 `Add .gitignore`。
9. 不要选择 License，因为本地项目中已经有 `LICENSE`。
10. 点击 `Create repository`。

创建后得到仓库地址，例如：

```text
https://github.com/你的用户名/gesture-ppt-starter.git
```

---

## 四、连接本地仓库和 GitHub

### 1. 添加远程仓库

```powershell
git remote add origin https://github.com/你的用户名/gesture-ppt-starter.git
```

### 2. 检查连接

```powershell
git remote -v
```

应该看到：

```text
origin  https://github.com/你的用户名/gesture-ppt-starter.git (fetch)
origin  https://github.com/你的用户名/gesture-ppt-starter.git (push)
```

### 3. 把主分支改成 main

```powershell
git branch -M main
```

### 4. 第一次推送

```powershell
git push -u origin main
```

第一次推送通常会弹出浏览器登录窗口。

推荐使用 **Git Credential Manager**：

1. 浏览器打开 GitHub 登录页面；
2. 登录 GitHub；
3. 授权 Git Credential Manager；
4. 返回 PowerShell，等待推送完成。

推送成功后，刷新 GitHub 仓库页面，就能看到项目文件。

---

## 五、如果 GitHub 要求输入用户名和密码

不要输入 GitHub 登录密码。可以创建一个 Personal Access Token：

1. 登录 GitHub；
2. 点击头像；
3. 进入 `Settings`；
4. 找到 `Developer settings`；
5. 选择 `Personal access tokens`；
6. 创建 token；
7. 给 token 勾选仓库读写权限；
8. 复制 token。

推送时：

- Username：GitHub 用户名；
- Password：粘贴 token。

不要把 token 写入代码、README 或远程地址。

不要这样做：

```text
https://username:token@github.com/username/repo.git
```

推荐使用 Git Credential Manager 或 SSH。

---

## 六、上传后的检查

打开 GitHub 仓库，检查：

- `README.md` 是否正常显示；
- 是否有 `src/`、`tests/`、`docs/`；
- 是否没有 `.venv/`；
- 是否没有 `data/gestures/`；
- 是否没有 `runs/`；
- 是否没有 `best.pt`；
- 是否没有个人信息和 token。

如果发现错误上传了文件，见第九节的处理方法。

---

## 七、以后修改代码后怎么再次上传

每次修改后按下面流程：

```powershell
cd C:\Users\Shane\Documents\Codex\2026-09-24\new-chat\outputs\gesture-ppt-starter

git status
git diff
git add .
git commit -m "Add gesture capture improvements"
git push
```

Commit 信息建议写清楚改动，例如：

```text
Add webcam capture command
Fix cooldown logic for repeated gestures
Document keyboard control safety
Add MobileNetV3 training tests
Improve README quick start
```

---

## 八、使用分支开发新功能

不要直接在 `main` 上做所有实验。新功能建议使用分支：

```powershell
git switch -c feature/hand-landmarks
```

修改并提交：

```powershell
git add .
git commit -m "Add hand landmark experiment scaffold"
git push -u origin feature/hand-landmarks
```

然后在 GitHub 页面创建 Pull Request，审查后再合并到 `main`。

---

## 九、常见错误和处理方法

### 1. `fatal: not a git repository`

原因：当前目录不是 Git 仓库。

解决：

```powershell
cd C:\Users\Shane\Documents\Codex\2026-09-24\new-chat\outputs\gesture-ppt-starter
git status
```

如果还没有初始化：

```powershell
git init
```

### 2. `remote origin already exists`

说明已经添加过远程仓库。修改地址：

```powershell
git remote set-url origin https://github.com/你的用户名/gesture-ppt-starter.git
```

### 3. `src refspec main does not match any`

通常是还没有提交，或者分支还没有创建。

解决：

```powershell
git add .
git commit -m "Initial commit"
git branch -M main
git push -u origin main
```

### 4. `failed to push some refs`

远程仓库有本地没有的提交。先拉取：

```powershell
git pull --rebase origin main
git push
```

不要随意使用：

```powershell
git push --force
```

如果确实需要覆盖，必须确认远程没有需要保留的内容，并使用：

```powershell
git push --force-with-lease
```

### 5. 不小心提交了 `.venv`

先从 Git 索引移除：

```powershell
git rm -r --cached .venv
git commit -m "Remove virtual environment from Git"
git push
```

本地 `.venv` 文件不会删除，只是不再被 Git 跟踪。

### 6. 不小心提交了摄像头数据

```powershell
git rm -r --cached data/gestures
git commit -m "Remove gesture images from Git"
git push
```

如果这些图片已经被公开，应立即删除仓库中的历史或重建仓库。仅删除最新提交不一定能彻底移除历史内容。

### 7. 不小心提交了模型权重

```powershell
git rm --cached runs/gesture_model/best.pt
git commit -m "Remove trained checkpoint from Git"
git push
```

模型建议放到 GitHub Release 或 Hugging Face Hub，不要直接放进普通 Git 仓库。

### 8. 文件超过 100 MB

GitHub 会拒绝大于 100 MB 的普通文件。

不要上传：

- 大型数据集；
- 视频；
- 多 GB 模型；
- 完整的虚拟环境。

如果确实需要版本管理大文件，可以使用 Git LFS：

```powershell
git lfs install
git lfs track "*.pt"
git add .gitattributes
```

但研究项目更推荐把模型发布到 Release。

---

## 十、绝对不能上传的内容

- `.venv/`；
- `data/gestures/` 中的摄像头图片；
- `data/smoke/` 中的训练图片；
- `runs/` 中的训练结果；
- `best.pt` 或其他模型权重；
- `.env` 文件；
- GitHub token；
- 密码；
- API key；
- 个人信息和未授权的人脸图片。

---

## 十一、推荐的第一次上传命令总览

确认项目路径正确后，依次执行：

```powershell
cd C:\Users\Shane\Documents\Codex\2026-09-24\new-chat\outputs\gesture-ppt-starter

$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v

git init
git add .
git status
git commit -m "Initial commit: gesture PPT control starter"
git branch -M main

git remote add origin https://github.com/你的用户名/gesture-ppt-starter.git
git push -u origin main
```

完成后刷新 GitHub 仓库页面即可。

---

## 十二、最简记忆版

```text
1. 本地初始化：git init
2. 添加文件：git add .
3. 提交：git commit -m "Initial commit"
4. 改主分支：git branch -M main
5. 连接 GitHub：git remote add origin <仓库地址>
6. 上传：git push -u origin main
7. 以后更新：git add . -> git commit -> git push
```
