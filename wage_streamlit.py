import pandas as pd
import streamlit as st
import pydeck as pdk

import plotly.express as px


st.title('日本の賃金データダッシュボード')

path = 'municipality-wages_20200827\\雇用_医療福祉_一人当たり賃金_'

df_jp_ind   = pd.read_csv(f'{path}全国_全産業.csv', encoding='shift_jis')
df_jp_cat   = pd.read_csv(f'{path}全国_大分類.csv', encoding='shift_jis')
df_pref_ind = pd.read_csv(f'{path}都道府県_全産業.csv', encoding='shift_jis')

# df_jp_ind
# df_jp_cat
# df_pref_ind

st.header('■ 2019年: 一人当たり平均賃金のヒートマップ')

df_jp_lat_lon = pd.read_csv('pref_lat_lon.csv', encoding='utf-8')
tgt_index = df_jp_lat_lon.query('pref_name == "京都県"').index[0]
df_jp_lat_lon.loc[tgt_index,'pref_name'] = '京都府'
# df_jp_lat_lon

df_pref_map = df_pref_ind[(df_pref_ind['年齢'] == '年齢計') & (df_pref_ind['集計年'] == 2019)]
# df_pref_map
df_pref_map = pd.merge(left=df_pref_map, right=df_jp_lat_lon, how='left', left_on='都道府県名', right_on='pref_name').drop('pref_name', axis=1)
# df_pref_map

Xmin = df_pref_map['一人当たり賃金（万円）'].min()
Xmax = df_pref_map['一人当たり賃金（万円）'].max()
# print(Xmin, Xmax)

df_pref_map['一人当たり賃金（相対値）'] = (df_pref_map['一人当たり賃金（万円）'] - Xmin) / (Xmax - Xmin)
# df_pref_map


tokyo_lon = df_pref_map[df_pref_map['都道府県名'] == '東京都'].loc[:,'lon']
tokyo_lat = df_pref_map[df_pref_map['都道府県名'] == '東京都'].loc[:,'lat']
# print(tokyo_lon)
# print(tokyo_lat)

view = pdk.ViewState(
    longitude=float(tokyo_lon),
    latitude=float(tokyo_lat),
    # longitude=139.691648,
    # latitude=35.689185,
    zoom=4,
    pitch=40.5
)

layer = pdk.Layer(
    type="HeatmapLayer",
    data=df_pref_map,
    opacity=0.4,
    get_position=["lon", "lat"],
    threshold=0.3,
    get_weight='一人当たり賃金（相対値）'
)

layer_map = pdk.Deck(
    layers=layer,
    initial_view_state=view,
)

st.pydeck_chart(layer_map)

show_df = st.checkbox(label='Show DataFrame')
if show_df == True:
    st.write(df_pref_map)


st.header('■ 集計年別の一人当たり賃金（万円）の推移')

df_ts_mean = df_jp_ind[df_jp_ind['年齢'] == '年齢計']
df_ts_mean = df_ts_mean.rename(columns={'一人当たり賃金（万円）': '全国_一人当たり賃金（万円）'})
# df_ts_mean

df_pref_mean = df_pref_ind[df_pref_ind['年齢'] == '年齢計']
pref_list = df_pref_mean['都道府県名'].unique()
option_pref = st.selectbox(
    label='都道府県',
    options=(pref_list)
)
df_pref_mean = df_pref_mean[df_pref_mean['都道府県名'] == option_pref]

df_mean_line = pd.merge(left=df_ts_mean, right=df_pref_mean, on='集計年')
df_mean_line = df_mean_line[['集計年', '全国_一人当たり賃金（万円）', '一人当たり賃金（万円）']]
df_mean_line = df_mean_line.set_index(keys='集計年')
# df_mean_line

st.line_chart(data=df_mean_line)


st.header('■ 年齢階級別の全国一人当たり平均賃金（万円）')

df_mean_bubble = df_jp_ind[df_jp_ind['年齢'] != '年齢計']
df_mean_bubble

fig = px.scatter(
    data_frame=df_mean_bubble,
    x='一人当たり賃金（万円）',
    y='年間賞与その他特別給与額（万円）',
    range_x=[150, 700],
    range_y=[0, 150],
    size='所定内給与額（万円）',
    size_max=38,
    color='年齢',
    animation_frame='集計年',
    animation_group='年齢'
)

st.plotly_chart(figure_or_data=fig)


st.header('■ 産業別の賃金推移')

year_list = df_jp_cat['集計年'].unique()
option_year = st.selectbox(
    label='集計年',
    options=(year_list)
)

temp_list = list(df_jp_cat.columns)[4:]
wage_list = []
indexs = [2, 0, 1]
for index in indexs:
    wage_list.append(temp_list[index])
option_wage = st.selectbox(
    label='賃金の種類',
    options=(wage_list)
)

df_mean_cat = df_jp_cat[df_jp_cat['集計年'] == option_year]

max_x = df_mean_cat[option_wage].max() * 1.05

height = 500
width = height * 1.6
# width = height * (1 + np.sqrt(5)) / 2
fig = px.bar(
    data_frame=df_mean_cat,
    x=option_wage,
    y='産業大分類名',
    color='産業大分類名',
    animation_frame='年齢',
    range_x=[0, max_x],
    orientation='h',
    height=height,
    width=width,
)
st.plotly_chart(figure_or_data=fig)

