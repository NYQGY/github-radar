# 开源雷达

静态项目库 + Python 标准库采集 + GitHub Actions 每日更新及每周归档。

## 当前状态

已通过 GitHub 连接器核验并收录用户提供的 10 个仓库，记录 2026-11-06 首次快照。没有虚构周增长。OpenAI 尚未接入，简介使用仓库原文。Sites 发布的是当前静态版本，不会执行 GitHub Actions。

## 在 GitHub 启用自动更新

1. 新建自己的 GitHub 仓库，将本目录内容（包括 .github）上传。不要上传 .git 和 .openai（它们属于 Sites 托管）。
2. Settings → Pages → Source 选择 GitHub Actions。
3. 在 Actions 中允许工作流运行，手动执行 Collect and publish，确认成功。
4. 工作流每天北京时间 09:17 采集，周一归档过去七日。定时任务可能延迟；失败会保留旧数据，不发布伪造结果。
5. 日常访问 GitHub Pages 的网址；Sites 的当前预览不会随 GitHub Pages 同步。

GitHub 自动提供 github.token，无须把 OpenAI 密钥用于 GitHub 采集。如果仓库规则不允许机器人直接推送，需要调整相应仓库权限或改为提交 PR。

## 本地

Python 3.12+，不需要第三方包。

    python scripts/collect.py
    python -m http.server 8080 --directory dist

未认证的 GitHub API 容易遇到共享 IP 限流；本地运行可从环境变量 GITHUB_TOKEN 读取令牌。

## 数据口径

仅对已跟踪项目排名，不代表 GitHub 全站。七日净增长使用北京日期对应的七日前快照；缺少基线显示观察中。当天重跑覆盖当日快照。周报保存当时项目数据，避免历史榜单随当前数据变化。

## OpenAI 配置待办

截图中的 key_ 开头字段为追踪 ID，不是认证密钥。后续在 GitHub Settings → Secrets and variables → Actions 保存 OPENAI_API_KEY，并选择模型后再接入中文摘要。不要把密钥写入源代码、data.json 或浏览器。

## 验证

    python -m unittest discover -s tests
    node --check dist/app.js
