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

## 使用

1.使用 **/jm [id]** 命令可以下载对应id的pdf

2.使用 **/s [关键词] [页码]** 命令可以搜索相关的本子信息（不带图，只有名字和id）

## 说明

欢迎提pr，代码十分混乱，但是其实也没有几行，目前没有迁移为插件的想法
已有nb插件[nonebot_plugin_jmcomic](https://github.com/zhulinyv/nonebot_plugin_jmcomic/tree/main)
，可以尝试使用
