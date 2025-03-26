#!/bin/bash
set -e

if ! command -v python3 &> /dev/null
then
    echo "Python 3 未安装，开始安装..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
    echo "Python 3, pip 和 venv 安装完成。"
else
    echo "Python 3 已安装。"
fi

if [ -f "requirements.txt" ]; then
    echo "找到 requirements.txt 文件，开始创建虚拟环境并安装依赖..."

    if [ -d "venv" ]; then
        echo "检测到已存在的 venv 目录，删除旧的虚拟环境..."
        rm -rf venv
    fi

    if command -v python &> /dev/null; then
        echo "使用 'python' 命令创建虚拟环境..."
        python -m venv venv
    elif command -v python3 &> /dev/null; then
        echo "使用 'python3' 命令创建虚拟环境..."
        python3 -m venv venv
    else
        echo "既没有找到 'python' 命令，也没有找到 'python3' 命令，无法创建虚拟环境。请确保 Python 已安装并添加到 PATH。"
        exit 1
    fi
    echo "虚拟环境创建完成。"

    source venv/bin/activate

    echo "虚拟环境已激活，开始安装 requirements.txt 中的依赖..."
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    echo "requirements.txt 中的依赖安装完成。"

    deactivate
    echo "虚拟环境已退出。"
else
    echo "当前目录下未找到 requirements.txt 文件，跳过依赖安装。"
fi

echo "脚本执行完毕，即将关闭。"
exit 0