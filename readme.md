## 致谢

感谢[jmcomic](https://github.com/JMasann/JMComic)提供的漫画下载服务

## 部署

1.克隆仓库

```
git clone https://github.com/miiiiiint/jmbot.git
```

2.部署环境

**linux**

```
cd jmbot
sudo chmod +x envset.sh
./envset.sh
```

**windows**

首先安装python，然后安装requirements

```
pip install -r requirements.txt
```

3.运行

```
python bot.py
```

4.连接onebot

_添加反向ws连接，端口为6700，消息段改为string_

## 已知问题

1.pdf转换函数未使用异步，会造成进程堵塞，在下载时无法接收消息

2.不同onebot协议端的消息转法构造格式，目前仅支持napcat，lagrange需要手动到bot.py注释代码

## 使用

1.使用 **/jm [id]** 命令可以下载对应id的pdf

2.使用 **/s [关键词] [页码]** 命令可以搜索相关的本子信息（不带图，只有名字和id）

## 更新
jmcomic自带pdf生成插件所需的 **img2pdf** 库在安装时需要c++运行库，对环境部署极不友好，重新实现了pdf生成逻辑，仅使用pillow库。

## 说明

欢迎提pr，代码十分混乱，但是其实也没有几行，大部分使用ai生成，目前没有迁移为插件的想法

已有nb插件[nonebot_plugin_jmcomic](https://github.com/zhulinyv/nonebot_plugin_jmcomic/tree/main)，可以尝试使用
