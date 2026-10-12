# 把项目提交到 GitHub：新手教程

这份教程假设项目名为 `gesture-ppt-starter`，GitHub 用户名为 `your-name`。请把示例替换成自己的信息。

## 1. Git 和 GitHub 是什么

Git 是本地版本管理工具，GitHub 是托管 Git 仓库的网站。

本项目需要避免提交：

- 摄像头采集的真人图片；
- 训练后的模型权重；
- `runs/` 中的训练输出；
- 虚拟环境；
- 密钥和 token。

## 2. 安装和配置 Git

检查 Git：

```powershell
git --version
```

配置用户名和邮箱：

```powershell
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

检查：

```powershell
git config --global --list
```

## 3. 提交前检查项目

进入项目目录：

```powershell
cd C:\Users\Shane\Documents\Codex\2026-09-24\new-chat\outputs\gesture-ppt-starter
```

检查文件：

```powershell
Get-ChildItem -Force
```

运行测试：

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

检查 `.gitignore` 是否排除了：

```text
data/gestures/
data/smoke/
runs/
.venv/
*.pt
*.pth
```

## 4. 创建本地仓库

```powershell
git init
git status
git add .
git commit -m "Initial commit: gesture PPT control starter"
```

## 5. 在 GitHub 创建远程仓库

1. 登录 GitHub；
2. 点击右上角 `+`；
3. 选择 `New repository`；
4. 仓库名填写 `gesture-ppt-starter`；
5. 描述填写 `Real-time hand gesture recognition for PowerPoint and video control`；
6. 选择 `Public` 或 `Private`；
7. 不要勾选自动创建 README、`.gitignore` 或 License；
8. 点击 `Create repository`。

## 6. 连接远程仓库

```powershell
git remote add origin https://github.com/your-name/gesture-ppt-starter.git
git remote -v
```

把分支改为 `main`：

```powershell
git branch -M main
git push -u origin main
```

之后推送：

```powershell
git push
```

## 7. GitHub 登录

推荐使用 Git Credential Manager，或者在密码位置输入 Personal Access Token。

不要把 token 写进代码、README 或远程地址。

错误示例：

```text
https://username:token@github.com/your-name/gesture-ppt-starter.git
```

## 8. 日常提交流程

```powershell
git status
git diff
git add .
git commit -m "Add stable gesture debounce tests"
git push
```

提交前必须检查 `git status`，避免误提交摄像头数据或模型文件。

## 9. 分支和 Pull Request

创建功能分支：

```powershell
git switch -c feature/hand-landmarks
```

提交：

```powershell
git add .
git commit -m "Add hand landmark feature extractor"
git push -u origin feature/hand-landmarks
```

然后在 GitHub 创建 Pull Request。

## 10. Commit 信息示例

```text
Add webcam capture command
Fix cooldown logic for repeated gestures
Document keyboard control safety
Improve gesture data validation
Add MobileNetV3 training tests
```

避免：

```text
update
fix
aaa
final
```

## 11. 撤销提交

撤销最后一次提交但保留文件：

```powershell
git reset --soft HEAD~1
```

已经提交了错误文件：

```powershell
git rm --cached path/to/file
git commit -m "Remove generated file from Git"
```

如果公开了密码或 token，必须立即撤销或更换，不能只删除文件。

## 12. 大文件和数据

不要上传：

- 摄像头图片；
- 视频；
- `best.pt`；
- `.venv/`；
- `runs/`；
- 个人数据。

如果以后确实需要版本管理大文件，可以使用 Git LFS：

```powershell
git lfs install
git lfs track "*.pt"
git add .gitattributes
```

但本项目建议把模型放到 Release、网盘或 Hugging Face Hub，并在 README 中提供下载方式。

## 13. 从 GitHub 克隆和更新

```powershell
git clone https://github.com/your-name/gesture-ppt-starter.git
cd gesture-ppt-starter
git pull --rebase
```

## 14. 常见错误

### `remote origin already exists`

```powershell
git remote set-url origin https://github.com/your-name/gesture-ppt-starter.git
```

### `failed to push some refs`

```powershell
git pull --rebase origin main
git push
```

强制推送只能使用：

```powershell
git push --force-with-lease
```

不要随意使用 `git push --force`。

### 摄像头数据已经被 Git 跟踪

```powershell
git rm -r --cached data/gestures
git commit -m "Stop tracking gesture images"
```

### 模型文件被跟踪

```powershell
git rm --cached runs/gesture_model/best.pt
git commit -m "Remove trained checkpoint from Git"
```

## 15. README 应包含的内容

- 项目简介；
- 四种手势和动作映射；
- 摄像头要求；
- 安装命令；
- 数据采集命令；
- 训练命令；
- 预览和安全控制命令；
- 防误触机制；
- 常见问题；
- 隐私和限制；
- 许可证。

## 16. 发布前检查清单

- [ ] 代码能运行；
- [ ] 测试通过；
- [ ] README 命令和代码一致；
- [ ] 未提交摄像头图片；
- [ ] 未提交模型权重；
- [ ] 未提交 `.venv/`；
- [ ] 未包含 token 和密码；
- [ ] 已声明隐私与安全限制；
- [ ] 已添加 LICENSE；
- [ ] 已检查 `.gitignore`；
- [ ] 已成功推送远程仓库。

## 17. 推荐初始提交命令

```powershell
git init
git add .
git commit -m "Initial commit: gesture PPT control starter"
git branch -M main
git remote add origin https://github.com/your-name/gesture-ppt-starter.git
git push -u origin main
```

## 18. GitHub Release 建议

模型训练稳定后，可以创建 Release 并上传：

- `best.pt`；
- `metrics.json`；
- 演示视频；
- 使用说明；
- 模型版本和训练数据说明。

不要上传原始摄像头数据。发布模型前应确认训练数据许可和隐私要求。
