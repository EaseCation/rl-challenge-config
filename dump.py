import pandas as pd
import numpy as np
import json
import re
import glob


def default(o):
    if isinstance(o, np.int64):
        return int(o)
    return o


# 获取所有的CSV文件
csv_files = glob.glob('workspace/*.csv')
print('读取文件: ' + ', '.join(csv_files))

# 初始化一个空的字典来存储所有的数据
data = {"levels": []}

# 初始化一个列表来存储需要后处理的boss
postprocess_bosses = []

# 遍历所有的CSV文件
for csv_file in csv_files:
    # 读取CSV文件
    df = pd.read_csv(csv_file)

    # 将数据按照level、wave和wave_type进行分组
    grouped = df.groupby(['level', 'wave', 'wave_type'])

    # 遍历所有的分组
    for (level, wave, wave_type), group in grouped:
        # 初始化一个空的字典来存储当前分组的数据
        if 'boss' in wave_type:
            wave_data = {"wave": wave, "type": wave_type, "boss": {}}
            # 遍历当前分组的所有行
            for _, row in group.iterrows():
                # 将每一行的数据添加到boss的数据中
                boss_data = row.drop(['level', 'wave', 'wave_type']).to_dict()
                # 如果boss的csv中有monster字段
                if 'monsters' in boss_data:
                    # 将boss添加到需要后处理的列表中
                    postprocess_bosses.append((boss_data, wave_data, level))
                else:
                    # 检查boss的数据，如果有空的或者缺失的字段，将其设置为默认值
                    for key, value in boss_data.items():
                        if pd.isnull(value):
                            boss_data[key] = 0  # 或者其他你想要的默认值
                    wave_data["boss"] = boss_data
        else:
            wave_data = {"wave": wave, "type": wave_type, "monsters": []}
            # 遍历当前分组的所有行
            for _, row in group.iterrows():
                # 将每一行的数据添加到monsters列表中
                wave_data["monsters"].append(row.drop(['level', 'wave', 'wave_type']).to_dict())
        # 将当前分组的数据添加到对应的level中
        if not any(d['level'] == level for d in data["levels"]):
            data["levels"].append({"level": level, "waves": [wave_data]})
        else:
            # 如果发现同level中已经有这个wave了，则打印警报
            if any(d['wave'] == wave for d in data["levels"][level - 1]["waves"]):
                print("警告: level={} wave={} 波次重复 {}!".format(level, wave, wave_type))
            next(d for d in data["levels"] if d['level'] == level)["waves"].append(wave_data)

# 后处理boss
for boss_data, wave_data, level in postprocess_bosses:
    # 获取monsters字段的值
    monster_value = boss_data.pop('monsters')

    # 检查monster_value是否符合格式
    if not re.match(r'l\d+w\d+', monster_value):
        print("警告: monster_value {} 不符合格式!".format(monster_value))
        continue

    # 解析monster字段的值
    monster_level, monster_wave = map(int, monster_value[1:].split('w'))
    # 从data中获取对应的怪物配置
    monster_group = next((d for d in data["levels"] if d['level'] == monster_level), None)

    if monster_group is None:
        print("警告: level={} wave={} {} 的怪物配置不存在!"
              .format(level, wave_data['wave'], monster_value))
        continue

    monster_wave_data = next((d for d in monster_group["waves"] if d['wave'] == monster_wave), None)

    if monster_wave_data is None:
        print("警告: level={} wave={} {} 的怪物配置不存在!"
              .format(level, wave_data['wave'], monster_value))
        continue

    if 'monsters' not in monster_wave_data or len(monster_wave_data['monsters']) == 0:
        print("警告: level={} wave={} {} 的怪物配置不存在或为空!"
              .format(monster_level, monster_wave, monster_value))
        continue

    # 将怪物配置添加到boss的数据中
    boss_data['monsters'] = monster_wave_data.get('monsters', [])
    wave_data["boss"] = boss_data

# 将数据转换为JSON格式，并写入到一个新的JSON文件中
with open('workspace/monster_config.json', 'w') as f:
    json.dump(data, f, default=default, indent=4)

print("导出为json配置完成！")
