"""
图片转Windows图标核心模块
新增：自定义分辨率选择功能
"""
import os
import sys
from pathlib import Path
from PIL import Image

# 兼容新旧版 PIL
try:
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_FILTER = Image.ANTIALIAS

# 标准Windows图标尺寸（默认）
DEFAULT_ICON_SIZES = [16, 32, 48, 64, 128, 256]
# 可选分辨率（供GUI调用）
OPTIONAL_SIZES = [16, 32, 48, 64, 128, 256, 512]


def get_desktop_path():
    """获取桌面路径"""
    if sys.platform == 'win32':
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    else:
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    return Path(desktop)


def ensure_output_dir():
    """确保输出目录存在"""
    output_dir = get_desktop_path() / 'ConvertedIcons'
    output_dir.mkdir(exist_ok=True)
    return output_dir


def convert_to_ico(image_path, output_name=None, sizes=None):
    """
    将图片转换为Windows图标格式
    新增：sizes - 自定义生成的图标尺寸列表，None则使用默认尺寸

    参数:
        image_path: 输入图片路径
        output_name: 输出文件名（不含扩展名），默认为原文件名
        sizes: 自定义分辨率列表，如[32, 64, 256]，None则用DEFAULT_ICON_SIZES

    返回:
        输出文件的完整路径
    """
    image_path = Path(image_path)
    # 若未指定尺寸，使用默认标准尺寸
    if sizes is None:
        sizes = DEFAULT_ICON_SIZES
    # 尺寸去重并按从大到小排序（保证主图标为最大尺寸）
    sizes = sorted(list(set(sizes)), reverse=True)

    if not image_path.exists():
        raise FileNotFoundError(f'找不到文件: {image_path}')

    # 支持的格式
    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff', '.tif')
    if image_path.suffix.lower() not in supported_formats:
        raise ValueError(f'不支持的文件格式: {image_path.suffix}. 支持的格式: {supported_formats}')

    # 打开图片
    img = Image.open(image_path)

    # 转换为RGBA模式（支持透明）
    if img.mode != 'RGBA':
        if img.mode in ('P', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert('RGBA')
        else:
            # 纯色背景的图片，添加白色背景
            background = Image.new('RGBA', img.size, (255, 255, 255, 255))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            img = Image.alpha_composite(background, img)

    # 如果图片不是正方形，添加透明边距使其变为正方形
    width, height = img.size
    if width != height:
        max_dim = max(width, height)
        new_img = Image.new('RGBA', (max_dim, max_dim), (0, 0, 0, 0))
        # 居中放置
        offset_x = (max_dim - width) // 2
        offset_y = (max_dim - height) // 2
        new_img.paste(img, (offset_x, offset_y))
        img = new_img

    # 确保输出目录存在
    output_dir = ensure_output_dir()

    # 确定输出文件名
    if output_name is None:
        output_name = image_path.stem
    output_path = output_dir / f'{output_name}.ico'

    # 生成指定尺寸的图标 - 从大到小排序，最大的作为主图标
    icon_images = []
    for size in sizes:
        # 若原图尺寸小于目标尺寸，仍生成（保留插值逻辑，与原逻辑一致）
        resized = img.resize((size, size), RESAMPLE_FILTER)
        icon_images.append(resized)

    # 保存为ico文件 - 第一个图标（最大的）作为主图标
    icon_images[0].save(
        output_path,
        format='ICO',
        append_images=icon_images[1:],
        sizes=[(img.width, img.height) for img in icon_images]
    )

    return output_path


def batch_convert(image_paths, sizes=None):
    """
    批量转换图片
    新增：sizes - 自定义生成的图标尺寸列表

    参数:
        image_paths: 图片路径列表
        sizes: 自定义分辨率列表，None则使用默认尺寸

    返回:
        (成功列表, 失败列表)
    """
    success = []
    failed = []
    # 传递自定义尺寸参数
    for path in image_paths:
        try:
            output = convert_to_ico(path, sizes=sizes)
            success.append((path, output))
        except Exception as e:
            failed.append((path, str(e)))

    return success, failed


if __name__ == '__main__':
    # 命令行新增分辨率参数支持，用法：python img2ico.py <图片路径> [尺寸1,尺寸2,...]
    if len(sys.argv) < 2:
        print('用法: python img2ico.py <图片路径> [可选：自定义分辨率，用逗号分隔]')
        print('示例1（默认尺寸）: python img2ico.py "myimage.png"')
        print('示例2（自定义尺寸）: python img2ico.py "myimage.png" 32,64,256,512')
        sys.exit(1)

    image_path = sys.argv[1]
    custom_sizes = None
    # 解析自定义分辨率参数
    if len(sys.argv) >= 3:
        try:
            custom_sizes = [int(s.strip()) for s in sys.argv[2].split(',')]
            # 校验尺寸为正整数
            for s in custom_sizes:
                if s <= 0:
                    raise ValueError
            print(f'✅ 自定义分辨率：{sorted(custom_sizes, reverse=True)}')
        except ValueError:
            print('❌ 分辨率格式错误，请输入正整数，用逗号分隔（如32,64,256）')
            sys.exit(1)

    try:
        output_path = convert_to_ico(image_path, sizes=custom_sizes)
        print(f'✓ 转换成功!')
        print(f'  输入: {image_path}')
        print(f'  输出: {output_path}')
    except Exception as e:
        print(f'✗ 转换失败: {e}')
        sys.exit(1)