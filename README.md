# RL Challenge Config

从相关CSV，导出刷怪波次的详细配置json文件

## 使用步骤

1. 安装python3（如果没有安装过的话）
2. 在本目录中，安装python依赖
    ``` bash
    pip3 install -r requirements.txt
    ```
3. 在本目录新建文件夹：workspace
4. 将templates目录中的所有csv文件复制到workspace目录中
5. 对workspace目录中的csv文件进行修改，使其符合要求
6. 运行python脚本
    ``` bash
    python3 dump.py
    ```
    将在workspace中生成json文件`monster_config.json`

## BOSS的子怪物配置

因为boss涉及到刷小怪，所以如果boss的csv中有monsters字段，则可以按照如下要求直接从monster.csv配置中复用已经注册的波次的怪物：

``` csv
l1w4
```

表示：使用 monster.csv 配置中的`第1关(level1)`的`第4波(wave4)`的怪物的配置