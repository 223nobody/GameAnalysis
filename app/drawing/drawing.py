import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
# 使用pandas读取数据
agg1 = pd.read_csv(
    '../data/agg_match_stats_1.csv')
# 丢弃重复数据
agg1.drop_duplicates(inplace=True)
# 添加是否成功吃鸡列
agg1['won'] = agg1['team_placement'] == 1
# 添加是否搭乘过车辆列
agg1['drove'] = agg1['player_dist_ride'] != 0
agg1.loc[agg1['player_kills'] < 40, ['player_kills', 'won']].groupby('player_kills').won.mean().plot.bar(figsize=(15,6), rot=0)
plt.xlabel('击杀人数', fontsize=14)
plt.ylabel("吃鸡概率", fontsize=14)
plt.title('击杀人数与吃鸡概率的关系', fontsize=14)
plt.show()

g = sns.FacetGrid(
    agg1.loc[agg1['player_kills']<=10, ['party_size', 'player_kills']],
    row="party_size",
    height=4,       # 修复这里：使用height替代size
    aspect=2
)
g.map(sns.countplot, "player_kills", order=sorted(agg1['player_kills'].unique()))
plt.tight_layout()
plt.show()

agg1.loc[agg1['party_size']!=1, ['player_assists', 'won']].groupby('player_assists').won.mean().plot.bar(figsize=(15,6), rot=0)
plt.xlabel('助攻次数', fontsize=14)
plt.ylabel("吃鸡概率", fontsize=14)
plt.title('助攻次数与吃鸡概率的关系', fontsize=14)
plt.show()

dist_ride = agg1.loc[agg1['player_dist_ride']<12000, ['player_dist_ride', 'won']]
labels=["0-1k", "1-2k", "2-3k", "3-4k","4-5k", "5-6k", "6-7k", "7-8k", "8-9k", "9-10k", "10-11k", "11-12k"]
dist_ride['drove_cut'] = pd.cut(dist_ride['player_dist_ride'], 12, labels=labels)
dist_ride.groupby('drove_cut', observed=False).won.mean().plot.bar(rot=60, figsize=(8,4))
plt.xlabel("搭乘车辆里程", fontsize=14)
plt.ylabel("吃鸡概率", fontsize=14)
plt.title('搭乘车辆里程与吃鸡概率的关系', fontsize=14)
plt.show()

match_unique = agg1.loc[agg1['party_size'] == 1, 'match_id'].unique()
# 先把玩家被击杀的数据导入进来并探索数据
death1 = pd.read_csv('../data/kill_match_stats_final_1.csv')
death1_solo = death1[death1['match_id'].isin(match_unique)]
# 只统计单人模式，筛选存活不超过180秒的玩家数据
death_180_seconds_erg = death1_solo.loc[(death1_solo['map'] == 'ERANGEL')&(death1_solo['time'] < 180)&(death1_solo['victim_position_x']>0), :].dropna()
death_180_seconds_mrm = death1_solo.loc[(death1_solo['map'] == 'MIRAMAR')&(death1_solo['time'] < 180)&(death1_solo['victim_position_x']>0), :].dropna()
# 选择存活不过180秒的玩家死亡位置
data_erg = death_180_seconds_erg[['victim_position_x', 'victim_position_y']].values
data_mrm = death_180_seconds_mrm[['victim_position_x', 'victim_position_y']].values
# 重新scale玩家位置
data_erg = data_erg*4096/800000
data_mrm = data_mrm*1000/800000
from scipy.ndimage import gaussian_filter
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from PIL import Image
def heatmap(x, y, s, bins=100):
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=bins)
    heatmap = gaussian_filter(heatmap, sigma=s)

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    return heatmap.T, extent

fig, axes = plt.subplots(1, 2, figsize=(24, 12))  # 整体宽度24，高度12

# 第一张图：Erangel
# ------------------------------------------------
bg_erg = np.array(Image.open('../data/erangel.jpg'))
ax = axes[0]  # 第一个子图

# 计算Erangel热力图
hmap_erg, extent_erg = heatmap(data_erg[:,0], data_erg[:,1], 4.5)

# 处理Erangel透明度
alphas_erg = np.clip(Normalize(0, hmap_erg.max(), clip=True)(hmap_erg) * 4.5, 0.0, 1.)
colors_erg = Normalize(0, hmap_erg.max(), clip=True)(hmap_erg)
colors_erg = cm.Reds(colors_erg)
colors_erg[..., -1] = alphas_erg

# 绘制Erangel
ax.set_title('Erangel - 玩家死亡位置分布', fontsize=16)
ax.set_xlim(0, 4096)
ax.set_ylim(0, 4096)
ax.imshow(bg_erg)
ax.imshow(colors_erg, extent=extent_erg, origin='lower', cmap=cm.Reds, alpha=0.9)
ax.invert_yaxis()  # 反转Y轴

# 第二张图：Miramar
# ------------------------------------------------
bg_mrm = np.array(Image.open('../data/miramar.jpg'))
ax = axes[1]  # 第二个子图

# 计算Miramar热力图
hmap_mrm, extent_mrm = heatmap(data_mrm[:,0], data_mrm[:,1], 4)

# 处理Miramar透明度
alphas_mrm = np.clip(Normalize(0, hmap_mrm.max(), clip=True)(hmap_mrm) * 4, 0.0, 1.)
colors_mrm = Normalize(0, hmap_mrm.max(), clip=True)(hmap_mrm)
colors_mrm = cm.Reds(colors_mrm)
colors_mrm[..., -1] = alphas_mrm

# 绘制Miramar
ax.set_title('Miramar - 玩家死亡位置分布', fontsize=16)
ax.set_xlim(0, 1000)
ax.set_ylim(0, 1000)
ax.imshow(bg_mrm)
ax.imshow(colors_mrm, extent=extent_mrm, origin='lower', cmap=cm.Reds, alpha=0.9)
ax.invert_yaxis()  # 反转Y轴

# 整体调整
plt.tight_layout()  # 自动调整子图间距
plt.suptitle('游戏热力图 - 玩家死亡位置分布', fontsize=20)  # 总标题
plt.subplots_adjust(top=0.85)  # 为总标题留出空间
plt.show()

death_final_circle_erg = death1_solo.loc[(death1_solo['map'] == 'ERANGEL')&(death1_solo['victim_placement'] == 2)&(death1_solo['victim_position_x']>0)&(death1_solo['killer_position_x']>0), :].dropna()
death_final_circle_mrm = death1_solo.loc[(death1_solo['map'] == 'MIRAMAR')&(death1_solo['victim_placement'] == 2)&(death1_solo['victim_position_x']>0)&(death1_solo['killer_position_x']>0), :].dropna()


final_circle_erg = np.vstack([death_final_circle_erg[['victim_position_x', 'victim_position_y']].values,
                                    death_final_circle_erg[['killer_position_x', 'killer_position_y']].values])*4096/800000
final_circle_mrm = np.vstack([death_final_circle_mrm[['victim_position_x', 'victim_position_y']].values,
                                    death_final_circle_mrm[['killer_position_x', 'killer_position_y']].values])*1000/800000
# 创建1行2列的子图布局
fig, axs = plt.subplots(1, 2, figsize=(28, 14))  # 整体宽度28英寸，高度14英寸

# 第一幅图：Erangel热力图
# ----------------------------------------------------------
bg_erg = np.array(Image.open('../data/erangel.jpg'))
hmap_erg, extent_erg = heatmap(final_circle_erg[:,0], final_circle_erg[:,1], 1.5)

# 处理Erangel透明度
alphas_erg = np.clip(Normalize(0, hmap_erg.max(), clip=True)(hmap_erg)*1.5, 0.0, 1.)
colors_erg = Normalize(0, hmap_erg.max(), clip=True)(hmap_erg)
colors_erg = cm.Reds(colors_erg)
colors_erg[..., -1] = alphas_erg

# 绘制Erangel子图
ax = axs[0]  # 第一个子图
ax.set_title('Erangel 决赛圈分布热力图', fontsize=18)
ax.set_xlim(0, 4096)
ax.set_ylim(0, 4096)
ax.imshow(bg_erg)
ax.imshow(colors_erg, extent=extent_erg, origin='lower', cmap=cm.Reds, alpha=0.9)
ax.invert_yaxis()

# 第二幅图：Miramar热力图
# ----------------------------------------------------------
bg_mrm = np.array(Image.open('../data/miramar.jpg'))
hmap_mrm, extent_mrm = heatmap(final_circle_mrm[:,0], final_circle_mrm[:,1], 1.5)

# 处理Miramar透明度
alphas_mrm = np.clip(Normalize(0, hmap_mrm.max(), clip=True)(hmap_mrm)*1.5, 0.0, 1.)
colors_mrm = Normalize(0, hmap_mrm.max(), clip=True)(hmap_mrm)
colors_mrm = cm.Reds(colors_mrm)
colors_mrm[..., -1] = alphas_mrm

# 绘制Miramar子图
ax = axs[1]  # 第二个子图
ax.set_title('Miramar 决赛圈分布热力图', fontsize=18)
ax.set_xlim(0, 1000)
ax.set_ylim(0, 1000)
ax.imshow(bg_mrm)
ax.imshow(colors_mrm, extent=extent_mrm, origin='lower', cmap=cm.Reds, alpha=0.9)
ax.invert_yaxis()

# 整体设置
plt.suptitle('PUBG决赛圈位置分布热力图对比', fontsize=24)
plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为总标题留出空间
plt.show()

erg_died_of = death1.loc[(death1['map']=='ERANGEL')&(death1['killer_position_x']>0)&(death1['victim_position_x']>0)&(death1['killed_by']!='Down and Out'),:].copy()
mrm_died_of = death1.loc[(death1['map']=='MIRAMAR')&(death1['killer_position_x']>0)&(death1['victim_position_x']>0)&(death1['killed_by']!='Down and Out'),:].copy()
plt.figure(figsize=(18, 8))  # 整体尺寸调整为18×8英寸

# 第一幅图：绝地海岛艾伦格武器击杀统计
plt.subplot(1, 2, 1)  # 第一个子图
erg_died_of['killed_by'].value_counts()[:10].plot.barh()
plt.xlabel("被击杀人数", fontsize=14)
plt.ylabel("击杀的武器", fontsize=14)
plt.title('武器跟击杀人数的统计(绝地海岛艾伦格)', fontsize=14)
plt.yticks(fontsize=12)

# 第二幅图：热情沙漠米拉玛武器击杀统计
plt.subplot(1, 2, 2)  # 第二个子图
mrm_died_of['killed_by'].value_counts()[:10].plot.barh()
plt.xlabel("被击杀人数", fontsize=14)
plt.ylabel("")  # 删除第二个子图的Y轴标签，避免重复
plt.title('武器跟击杀人数的统计(热情沙漠米拉玛)', fontsize=14)
plt.yticks(fontsize=12)

# 添加整体标题并调整布局
plt.suptitle('PUBG地图武器击杀统计对比', fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])  # 为总标题留出空间
plt.subplots_adjust(wspace=0.3)  # 增加子图间距，防止重叠
plt.show()

erg_distance = np.sqrt(((erg_died_of['killer_position_x']-erg_died_of['victim_position_x'])/100)**2
                       + ((erg_died_of['killer_position_y']-erg_died_of['victim_position_y'])/100)**2)
mrm_distance = np.sqrt(((mrm_died_of['killer_position_x']-mrm_died_of['victim_position_x'])/100)**2
                       + ((mrm_died_of['killer_position_y']-mrm_died_of['victim_position_y'])/100)**2)
plt.figure(figsize=(10, 6))
sns.histplot(erg_distance.loc[erg_distance<400], kde=True, bins=50)
plt.title('Erangel 击杀距离分布 (<400米)', fontsize=14)
plt.xlabel('击杀距离 (米)', fontsize=12)
plt.ylabel('频次', fontsize=12)
plt.show()

# 创建2×2的子图布局
fig, axes = plt.subplots(2, 2, figsize=(20, 16))

# 设置整体标题
plt.suptitle('PUBG不同距离武器击杀统计对比', fontsize=20)

# 第一行：狙击武器统计
# ----------------------------------------------------
# Erangel 狙击武器统计 (800-1500米)
ax = axes[0, 0]
erg_sniper_data = erg_died_of.loc[(erg_distance > 800) & (erg_distance < 1500), 'killed_by'].value_counts()[:10]
if len(erg_sniper_data) > 0:
    erg_sniper_data.plot.bar(ax=ax, rot=30)
    ax.set_xlabel("狙击武器", fontsize=14)
    ax.set_ylabel("被击杀人数", fontsize=14)
    ax.set_title('艾伦格(800-1500米)狙击武器统计', fontsize=16)
else:
    ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes, fontsize=16)
    ax.set_title('艾伦格(800-1500米)狙击武器统计 - 无数据', fontsize=16)

# Miramar 狙击武器统计 (800-1000米)
ax = axes[0, 1]
mrm_sniper_data = mrm_died_of.loc[(mrm_distance > 800) & (mrm_distance < 1500), 'killed_by'].value_counts()[:10]
if len(mrm_sniper_data) > 0:
    mrm_sniper_data.plot.bar(ax=ax, rot=30)
    ax.set_xlabel("狙击武器", fontsize=14)
    ax.set_ylabel("")  # 隐藏右侧图的Y轴标签
    ax.set_title('米拉玛(800-1000米)狙击武器统计', fontsize=16)
else:
    ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes, fontsize=16)
    ax.set_title('米拉玛(800-1000米)狙击武器统计 - 无数据', fontsize=16)

# 第二行：近战武器统计
# ----------------------------------------------------
# Erangel 近战武器统计 (<10米)
ax = axes[1, 0]
erg_melee_data = erg_died_of.loc[erg_distance < 10, 'killed_by'].value_counts()[:10]
if len(erg_melee_data) > 0:
    erg_melee_data.plot.bar(ax=ax, rot=30)
    ax.set_xlabel("近战武器", fontsize=14)
    ax.set_ylabel("被击杀人数", fontsize=14)
    ax.set_title('艾伦格(<10米)近战武器统计', fontsize=16)
else:
    ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes, fontsize=16)
    ax.set_title('艾伦格(<10米)近战武器统计 - 无数据', fontsize=16)

# Miramar 近战武器统计 (<10米)
ax = axes[1, 1]
mrm_melee_data = mrm_died_of.loc[mrm_distance < 10, 'killed_by'].value_counts()[:10]
if len(mrm_melee_data) > 0:
    mrm_melee_data.plot.bar(ax=ax, rot=30)
    ax.set_xlabel("近战武器", fontsize=14)
    ax.set_ylabel("")  # 隐藏右侧图的Y轴标签
    ax.set_title('米拉玛(<10米)近战武器统计', fontsize=16)
else:
    ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes, fontsize=16)
    ax.set_title('米拉玛(<10米)近战武器统计 - 无数据', fontsize=16)

# 调整布局和间距
plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为总标题留出空间
plt.subplots_adjust(hspace=0.3, wspace=0.2)  # 增加行和列间距
plt.show()

from bokeh.models.tools import HoverTool
from bokeh.palettes import brewer
from bokeh.plotting import figure, show, output_file
from bokeh.models.sources import ColumnDataSource
from bokeh.layouts import row
erg_died_of = erg_died_of.copy()
erg_died_of['erg_dist'] = erg_distance
erg_died_of = erg_died_of.loc[erg_died_of['erg_dist']<800, :]
top_weapons_erg = list(erg_died_of['killed_by'].value_counts()[:10].index)
top_weapon_kills = erg_died_of[np.isin(erg_died_of['killed_by'], top_weapons_erg)].copy()
top_weapon_kills['bin'] = pd.cut(top_weapon_kills['erg_dist'], np.arange(0, 800, 10), include_lowest=True, labels=False)
top_weapon_kills_wide = top_weapon_kills.groupby(['killed_by', 'bin']).size().unstack(fill_value=0).transpose()
top_weapon_kills_wide = top_weapon_kills_wide.div(top_weapon_kills_wide.sum(axis=1), axis=0)

# 定义堆叠函数
def stacked(df):
    df_top = df.cumsum(axis=1)
    df_bottom = df_top.shift(axis=1).fillna(0)[::-1]
    df_stack = pd.concat([df_bottom, df_top], ignore_index=True)
    return df_stack

areas_erg = stacked(top_weapon_kills_wide)
colors_erg = brewer['Spectral'][areas_erg.shape[1]]
x2_erg = np.hstack((top_weapon_kills_wide.index[::-1], top_weapon_kills_wide.index)) / 0.095

# 创建第一幅图表
hover_erg = HoverTool(
    tooltips=[("武器", "@weapon"), ("距离", "$x{0}m"), ("比例", "$y{0.0%}")],
    point_policy='follow_mouse'
)

TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
p1 = figure(x_range=(1, 800), y_range=(0, 1), tools=[TOOLS, hover_erg], width=400)
p1.grid.minor_grid_line_color = '#eeeeee'

source1 = ColumnDataSource(data={
    'x': [x2_erg] * areas_erg.shape[1],
    'y': [areas_erg[c].values for c in areas_erg],
    'weapon': list(top_weapon_kills_wide.columns),
    'color': colors_erg
})

p1.patches('x', 'y', source=source1, legend_field="weapon",
           color='color', alpha=0.8, line_color=None)
p1.title.text = "艾伦格: Top10武器击杀分布"
p1.xaxis.axis_label = "击杀距离 (0-800米)"
p1.yaxis.axis_label = "百分比"
p1.legend.location = "top_left"

# 准备第二幅图：Miramar
# ----------------------------------------------------------
# 复制您的数据处理代码...
mrm_died_of = mrm_died_of.copy()
mrm_died_of['mrm_dist'] = mrm_distance
mrm_died_of = mrm_died_of.loc[mrm_died_of['mrm_dist']<800, :]
top_weapons_mrm = list(mrm_died_of['killed_by'].value_counts()[:10].index)
top_weapon_kills = mrm_died_of[np.in1d(mrm_died_of['killed_by'], top_weapons_mrm)].copy()
top_weapon_kills['bin'] = pd.cut(top_weapon_kills['mrm_dist'], np.arange(0, 800, 10), include_lowest=True, labels=False)
top_weapon_kills_wide_mrm = top_weapon_kills.groupby(['killed_by', 'bin']).size().unstack(fill_value=0).transpose()
top_weapon_kills_wide_mrm = top_weapon_kills_wide_mrm.div(top_weapon_kills_wide_mrm.sum(axis=1), axis=0)

areas_mrm = stacked(top_weapon_kills_wide_mrm)
colors_mrm = brewer['Spectral'][areas_mrm.shape[1]]
x2_mrm = np.hstack((top_weapon_kills_wide_mrm.index[::-1], top_weapon_kills_wide_mrm.index)) / 0.095

# 创建第二幅图表
hover_mrm = HoverTool(
    tooltips=[("武器", "@weapon"), ("距离", "$x{0}m"), ("比例", "$y{0.0%}")],
    point_policy='follow_mouse'
)

p2 = figure(x_range=(1, 800), y_range=(0, 1), tools=[TOOLS, hover_mrm], width=400)
p2.grid.minor_grid_line_color = '#eeeeee'

source2 = ColumnDataSource(data={
    'x': [x2_mrm] * areas_mrm.shape[1],
    'y': [areas_mrm[c].values for c in areas_mrm],
    'weapon': list(top_weapon_kills_wide_mrm.columns),
    'color': colors_mrm
})

p2.patches('x', 'y', source=source2, legend_field="weapon",
           color='color', alpha=0.8, line_color=None)
p2.title.text = "米拉玛: Top10武器击杀分布"
p2.xaxis.axis_label = "击杀距离 (0-800米)"
p2.yaxis.axis_label = ""

# 创建并显示横向布局
output_file("weapon_analysis_compare.html")
layout = row(p1, p2, sizing_mode='stretch_width')

# show(layout)
