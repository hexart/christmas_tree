"""
Windows 屏保包装器
处理 Windows 屏保的命令行参数
"""
import sys
import os

# Windows 屏保命令行参数：
# /s - 运行屏保
# /c - 显示配置对话框
# /p <hwnd> - 在预览窗口中显示
# 无参数 - 当作 /c 处理

def main():
    # 解析命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg == '/s':
            # 运行屏保模式
            run_screensaver()
        elif arg == '/c':
            # 配置对话框（可选实现）
            show_config_dialog()
        elif arg.startswith('/p'):
            # 预览模式（在小窗口中显示）
            # 这个模式比较复杂，通常可以忽略
            print("预览模式暂不支持")
            sys.exit(0)
        else:
            # 默认运行屏保
            run_screensaver()
    else:
        # 无参数，显示配置对话框
        show_config_dialog()


def run_screensaver():
    """运行屏保主程序"""
    # 导入主程序
    import main

    # 强制全屏模式
    main.Config.AUTO_FULLSCREEN = True

    # 运行
    main.main()


def show_config_dialog():
    """显示配置对话框（简单实现）"""
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    messagebox.showinfo(
        "圣诞树屏保",
        "圣诞树粒子动画屏保\n\n"
        "功能说明：\n"
        "• 自动全屏显示3D圣诞树\n"
        "• 鼠标拖拽可旋转\n"
        "• 按ESC键退出\n\n"
        "如需修改配置，请编辑 main.py 中的 Config 类"
    )
    root.destroy()


if __name__ == '__main__':
    main()
