"""
图片转Windows图标 - 图形界面
新增：分辨率可视化选择功能
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import traceback

# 尝试导入 tkinterdnd2
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
    print("[DEBUG] tkinterdnd2 loaded successfully")
except ImportError:
    HAS_DND = False
    print("[DEBUG] tkinterdnd2 not available, drag and drop disabled")
    print("[DEBUG] To enable: pip install tkinterdnd2")

# 导入核心模块（新增了自定义尺寸）
try:
    from img2ico import convert_to_ico, batch_convert, get_desktop_path, DEFAULT_ICON_SIZES, OPTIONAL_SIZES
    print("[DEBUG] img2ico module loaded")
except Exception as e:
    print(f"[ERROR] Failed to load img2ico: {e}")
    traceback.print_exc()
    sys.exit(1)


class Img2IcoApp:
    def __init__(self, root):
        self.root = root
        self.root.title('图片转Windows图标工具 - 支持自定义分辨率')
        self.root.geometry('700x650')
        self.root.minsize(600, 550)

        # 存储选中的文件
        self.selected_files = []
        # 分辨率勾选状态（默认全选DEFAULT_ICON_SIZES）
        self.size_vars = {size: tk.IntVar(value=1 if size in DEFAULT_ICON_SIZES else 0) for size in OPTIONAL_SIZES}

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面 - 新增分辨率选择区域"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding='20')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text='图片转Windows图标',
            font=('Microsoft YaHei', 18, 'bold')
        )
        title_label.pack(pady=(0, 10))

        # 说明文字
        if HAS_DND:
            desc_text = '拖拽图片到下方区域，或点击"选择图片"按钮 | 可自定义勾选需要的分辨率'
        else:
            desc_text = '点击"选择图片"按钮添加文件（拖放需安装tkinterdnd2） | 可自定义勾选需要的分辨率'

        desc_label = ttk.Label(
            main_frame,
            text=desc_text,
            font=('Microsoft YaHei', 10),
            foreground='gray'
        )
        desc_label.pack(pady=(0, 15))

        # 新增：分辨率选择区域
        size_frame = ttk.LabelFrame(main_frame, text='选择生成的分辨率（多选）', padding='10')
        size_frame.pack(fill=tk.X, pady=(0, 10))
        # 分辨率按钮布局（一行显示，均匀分布）
        for idx, size in enumerate(OPTIONAL_SIZES):
            ttk.Checkbutton(
                size_frame,
                text=f'{size}x{size}',
                variable=self.size_vars[size],
                command=self.update_size_status  # 勾选后更新状态栏
            ).grid(row=0, column=idx, padx=8, pady=5)

        # 文件列表区域
        drop_frame = ttk.LabelFrame(main_frame, text='文件列表', padding='10')
        drop_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 创建 Listbox
        self.file_listbox = tk.Listbox(
            drop_frame,
            selectmode=tk.MULTIPLE,
            font=('Microsoft YaHei', 11),
            height=10,
            bg='#f8f9fa'
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = ttk.Scrollbar(drop_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # 绑定拖放事件（仅在 tkinterdnd2 可用时）
        if HAS_DND:
            self.file_listbox.drop_target_register(DND_FILES)
            self.file_listbox.dnd_bind('<<Drop>>', self.on_drop)

        # 插入提示文字
        self.file_listbox.insert(tk.END, '>>> 等待添加图片文件 <<<')
        self.file_listbox.insert(tk.END, '')
        self.file_listbox.insert(tk.END, '点击"选择图片"按钮添加文件')

        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=15)

        self.select_btn = ttk.Button(
            btn_frame,
            text='+ 选择图片',
            command=self.select_files,
            width=15
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(
            btn_frame,
            text='清空列表',
            command=self.clear_files,
            width=15
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        self.convert_btn = ttk.Button(
            btn_frame,
            text='开始转换',
            command=self.start_convert,
            width=20
        )
        self.convert_btn.pack(side=tk.RIGHT, padx=5)

        # 信息区域
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=5)

        desktop_path = get_desktop_path() / 'ConvertedIcons'
        output_label = ttk.Label(
            info_frame,
            text=f'输出位置: {desktop_path}',
            font=('Microsoft YaHei', 9),
            foreground='gray'
        )
        output_label.pack(anchor=tk.W)

        # 分辨率状态标签（初始显示默认尺寸）
        self.size_status_label = ttk.Label(
            info_frame,
            text=f'当前选择分辨率: {", ".join([f"{s}x{s}" for s in DEFAULT_ICON_SIZES])}',
            font=('Microsoft YaHei', 9),
            foreground='gray'
        )
        self.size_status_label.pack(anchor=tk.W)

        # 状态栏
        self.status_label = ttk.Label(
            main_frame,
            text='就绪 - 请拖放图片或点击选择 | 可自定义分辨率',
            font=('Microsoft YaHei', 9),
            foreground='blue'
        )
        self.status_label.pack(anchor=tk.W, pady=(10, 0))

    def update_size_status(self):
        """更新分辨率选择状态标签"""
        selected_sizes = self.get_selected_sizes()
        if not selected_sizes:
            self.size_status_label.config(text='当前选择分辨率: 未选择（请至少勾选一个）')
        else:
            size_text = ', '.join([f"{s}x{s}" for s in sorted(selected_sizes, reverse=True)])
            self.size_status_label.config(text=f'当前选择分辨率: {size_text}')

    def get_selected_sizes(self):
        """获取用户勾选的分辨率列表"""
        return [size for size, var in self.size_vars.items() if var.get() == 1]

    def on_drop(self, event):
        """处理拖放的文件"""
        data = event.data
        # 处理花括号包裹的路径（Windows 常见格式）
        files = []
        if '{' in data:
            import re
            files = re.findall(r'\{([^}]+)\}', data)
            if not files:
                files = data.strip('{}').split('} {')
        else:
            files = data.split()
        # 清理提示文字
        if self.file_listbox.get(0) == '>>> 拖拽图片文件到这里 <<<<':
            self.file_listbox.delete(0, tk.END)
        self.add_files(files)

    def select_files(self):
        """打开文件选择对话框"""
        files = filedialog.askopenfilenames(
            title='选择图片文件',
            filetypes=[
                ('图片文件', '*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff *.tif'),
                ('PNG图片', '*.png'),
                ('JPEG图片', '*.jpg *.jpeg'),
                ('所有文件', '*.*')
            ]
        )
        if files:
            if self.file_listbox.get(0) == '>>> 拖拽图片文件到这里 <<<<':
                self.file_listbox.delete(0, tk.END)
            self.add_files(files)

    def add_files(self, files):
        """添加文件到列表"""
        supported_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff', '.tif')
        added_count = 0
        for file in files:
            try:
                path = Path(file.strip())
                if path.suffix.lower() in supported_exts:
                    file_str = str(path)
                    if file_str not in self.selected_files:
                        self.selected_files.append(file_str)
                        self.file_listbox.insert(tk.END, path.name)
                        added_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to add file {file}: {e}")
        if added_count > 0:
            self.status_label.config(
                text=f'已添加 {added_count} 个文件，共 {len(self.selected_files)} 个 - 点击"开始转换"',
                foreground='green'
            )

    def clear_files(self):
        """清空文件列表"""
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.file_listbox.insert(tk.END, '>>> 拖拽图片文件到这里 <<<')
        self.file_listbox.insert(tk.END, '')
        self.file_listbox.insert(tk.END, '或点击下方"选择图片"按钮')
        self.status_label.config(text='列表已清空 | 可自定义分辨率', foreground='blue')

    def start_convert(self):
        """开始转换 - 传递自定义分辨率"""
        if not self.selected_files:
            messagebox.showwarning('提示', '请先选择或拖放图片文件！')
            return
        # 获取用户勾选的分辨率
        selected_sizes = self.get_selected_sizes()
        if not selected_sizes:
            messagebox.showwarning('提示', '请至少勾选一个分辨率！')
            return

        self.convert_btn.config(state=tk.DISABLED)
        self.status_label.config(text='正在转换...', foreground='orange')
        self.root.update()

        try:
            # 传递自定义分辨率参数给批量转换
            success, failed = batch_convert(self.selected_files, sizes=selected_sizes)
            output_dir = get_desktop_path() / 'ConvertedIcons'

            if success:
                size_text = ', '.join([f"{s}x{s}" for s in sorted(selected_sizes, reverse=True)])
                message = f'转换完成!\n\n成功: {len(success)} 个\n失败: {len(failed)} 个\n\n生成分辨率: {size_text}\n\n输出位置: {output_dir}'
                if failed:
                    message += '\n\n失败详情:\n'
                    for path, error in failed:
                        message += f'  - {Path(path).name}: {error}\n'
                messagebox.showinfo('转换完成', message)
                # 打开输出文件夹
                if output_dir.exists():
                    os.startfile(output_dir)
                self.status_label.config(
                    text=f'转换完成 - 成功:{len(success)} 失败:{len(failed)}',
                    foreground='green'
                )
            else:
                messagebox.showerror('错误', f'所有文件转换失败:\n{failed[0][1] if failed else "未知错误"}')
                self.status_label.config(text='转换失败', foreground='red')

        except Exception as e:
            error_msg = f'转换过程中出现错误:\n{str(e)}'
            print(f"[ERROR] {error_msg}")
            traceback.print_exc()
            messagebox.showerror('错误', error_msg)
            self.status_label.config(text='转换失败', foreground='red')

        finally:
            self.convert_btn.config(state=tk.NORMAL)


def main():
    """主函数"""
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    # 设置DPI感知
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')

    app = Img2IcoApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()