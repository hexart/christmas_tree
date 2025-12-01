#!/bin/bash
# macOS/Linux 编译脚本
# 使用方法：./build.sh

set -e  # 遇到错误立即退出

echo "========================================"
echo "圣诞树应用编译脚本 for macOS/Linux"
echo "========================================"
echo ""

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "错误：未在虚拟环境中"
    echo "请先运行: source .venv/bin/activate"
    exit 1
fi

echo "步骤 1/3: 清理旧文件..."
rm -rf dist build

echo "步骤 2/3: 使用 PyInstaller 打包..."
pyinstaller build.spec --clean

if [ $? -ne 0 ]; then
    echo "错误：打包失败"
    exit 1
fi

echo "步骤 3/3: 验证输出..."
if [ "$(uname)" = "Darwin" ]; then
    # macOS
    if [ -d "dist/Christmas_Tree.app" ]; then
        echo ""
        echo "========================================"
        echo "编译成功！"
        echo "========================================"
        echo ""
        echo "应用位置："
        echo "  $(pwd)/dist/Christmas_Tree.app"
        echo ""
        echo "运行方法："
        echo "  双击 Christmas_Tree.app"
        echo "  或命令行: open dist/Christmas_Tree.app"
        echo ""
    else
        echo "错误：未找到生成的应用"
        exit 1
    fi
else
    # Linux
    if [ -d "dist/Christmas_Tree" ]; then
        echo ""
        echo "========================================"
        echo "编译成功！"
        echo "========================================"
        echo ""
        echo "应用位置："
        echo "  $(pwd)/dist/Christmas_Tree/"
        echo ""
        echo "运行方法："
        echo "  ./dist/Christmas_Tree/Christmas_Tree"
        echo ""
    else
        echo "错误：未找到生成的可执行文件"
        exit 1
    fi
fi
