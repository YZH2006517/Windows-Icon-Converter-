# 图片转Windows图标工具

一个简单易用的Python工具，将图片转换为Windows桌面图标(.ico)格式。

## 功能特点

- 支持多种图片格式（PNG、JPG、JPEG、BMP、GIF、WEBP）
- 自动生成多种尺寸的图标（16x16, 32x32, 48x48, 64x64, 128x128, 256x256）
- 简洁的图形界面
- 支持拖拽操作
- 转换后的图标保存在桌面

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方式1：图形界面（推荐）

```bash
python img2ico_gui.py
```

### 方式2：命令行

```bash
python img2ico.py 图片路径
```

例如：
```bash
python img2ico.py "C:\Users\Pictures\myimage.png"
```

## 输出位置

转换后的 `.ico` 文件将保存在桌面的 `ConvertedIcons` 文件夹中。

## 文件说明

- `img2ico.py` - 核心转换库
- `img2ico_gui.py` - 图形界面程序
- `requirements.txt` - 依赖列表
- `README.md` - 说明文档

## 支持的图标尺寸

- 16x16 - 任务栏小图标
- 32x32 - 文件夹图标
- 48x48 - 桌面图标
- 64x64 - 开始菜单图标
- 128x128 - 大图标视图
- 256x256 - 高DPI显示
