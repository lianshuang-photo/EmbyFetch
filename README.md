# EmbyFetch

> 🚀 更快捷、更流畅的 Emby 媒体播放地址获取工具

一个用于获取 Emby 媒体服务器视频播放地址的 Python 脚本工具。获取到的播放地址可以直接在浏览器中打开观看，提供比 Emby 网页端更流畅的播放体验。

## 目录

- [功能特点](#功能特点)
- [快速开始](#快速开始)
- [使用说明](#使用说明)
- [配置说明](#配置说明)
- [注意事项](#注意事项)
- [依赖要求](#依赖要求)
- [贡献指南](#贡献指南)
- [鸣谢](#鸣谢)

## 功能特点

- 支持获取单集或多集视频的播放地址
- 交互式菜单操作，使用便捷
- 支持连续获取不同剧集的播放地址
- 支持将获取的播放地址导出为文件
- 提供退出选项（主菜单'q'退出程序，获取播放地址时'q'返回主菜单）
- 生成的播放地址可直接在浏览器中观看，具有以下优势：
  - 加载速度快，几乎无需缓冲
  - 播放流畅，不会出现卡顿
  - 相比 Emby 网页端有更好的播放体验
  - 支持浏览器原生播放器的所有功能

## 快速开始

1. 克隆项目到本地
```bash
git clone [项目地址]
cd emby_download
```

2. 安装依赖
```bash
pip install requests  # 仅需安装 requests，其他均为 Python 标准库
```

3. 配置文件设置
```bash
cp config.ini.example config.ini  # 复制配置文件模板
vim config.ini  # 或使用其他编辑器修改配置
```

4. 运行程序
```bash
python main.py
```

## 使用说明

1. 运行程序后，将显示主菜单，提供以下选项：
   - 获取播放地址
   - 退出程序（输入'q'）

2. 获取播放地址时：
   - 可以输入单个视频ID获取对应播放地址
   - 可以连续获取多个视频的播放地址
   - 随时可以输入'q'返回主菜单

3. 播放地址获取后：
   - 会自动显示在控制台
   - 可以直接在浏览器中打开链接观看，享受流畅的播放体验
   - 也可以使用专业下载工具进行下载，以便离线观看

## 配置说明

项目提供了配置文件模板 `config.ini.example`，将其复制为 `config.ini` 并修改相应配置项：

```ini
[emby]
url = http://media.emby.com
username = your_username
password = your_password
api_key = 
user_id = 

[download]
download_path = ./media
```

配置项说明：
- `url`: Emby 服务器地址（必填）
- `username`: 用户名（必填）
- `password`: 密码（必填）
- `api_key`: API密钥（可选，保持为空）
- `user_id`: 用户ID（可选，保持为空）
- `download_path`: 下载路径（默认为 ./media）

## 注意事项

- 建议使用浏览器或专业下载工具进行实际下载，而不是直接使用脚本下载
- 使用脚本直接下载可能导致系统性能问题
- 确保有足够的系统资源和网络带宽

## 依赖要求

- Python 3.x
- 第三方库：
  - requests
- Python 标准库：
  - json
  - os
  - time
  - configparser

## 贡献指南

1. Fork 本项目
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 鸣谢

本项目基于 [@hypzw88/emby_download](https://github.com/hypzw88/emby_download/) 进行开发和改进。感谢原作者的贡献！

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件
