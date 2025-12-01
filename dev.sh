#!/bin/bash
# macOS/Linux 开发热更新脚本
# 使用方法：./dev.sh

set -e  # 遇到错误立即退出

echo "========================================"
echo "圣诞树应用 - 开发模式"
echo "========================================"
echo ""

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  未检测到虚拟环境，正在激活..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        echo "✅ 虚拟环境已激活"
    else
        echo "❌ 错误：未找到虚拟环境"
        echo "请先运行: python3 -m venv .venv"
        echo "然后运行: source .venv/bin/activate"
        echo "最后运行: pip install -r requirements.txt"
        exit 1
    fi
fi

# 检查依赖
echo "检查依赖..."
if ! python -c "import pygame" 2>/dev/null; then
    echo "⚠️  pygame 未安装，正在安装依赖..."
    pip install -r requirements.txt
fi

echo "✅ 依赖检查完成"
echo ""
echo "========================================"
echo "启动应用（热更新模式）"
echo "========================================"
echo "提示：修改 main.py 后，按 Ctrl+C 停止，然后重新运行此脚本"
echo "      或者在代码中使用 pygame.KEYDOWN K_r 实现热重载"
echo ""

# 使用 watch 或循环监听文件变化（可选）
# 这里简单地直接运行，用户可以手动重启
while true; do
    echo "▶️  运行 main.py..."
    echo ""

    python main.py

    exit_code=$?

    echo ""
    echo "========================================"
    if [ $exit_code -eq 0 ]; then
        echo "程序正常退出"
    else
        echo "程序异常退出 (code: $exit_code)"
    fi
    echo "========================================"
    echo ""
    echo "按 Ctrl+C 退出开发模式，或按任意键重新运行..."

    # 等待用户输入
    read -n 1 -s -r

    echo ""
    echo "正在重新启动..."
    echo ""
done
