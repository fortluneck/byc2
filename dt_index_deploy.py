import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# 设置页面配置
st.set_page_config(
    page_title="数字化转型指数分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 数据加载与处理
@st.cache_data
def load_data():
    """加载并处理数字化转型指数数据"""
    try:
        # 支持多种文件路径
        import os
        possible_paths = [
            "合并后的数字化转型指数数据.xlsx",
            "./合并后的数字化转型指数数据.xlsx",
            "/app/合并后的数字化转型指数数据.xlsx"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                df = pd.read_excel(path)
                st.success(f"成功加载数据文件: {path}")
                break
        else:
            st.error("未找到数据文件")
            return None
        
        # 数据处理
        df['股票代码'] = df['股票代码'].astype(str)
        df['年份'] = df['年份'].astype(int)
        
        # 确保行业名称不为空
        df['行业名称'] = df['行业名称'].fillna('未知行业')
        df['行业代码'] = df['行业代码'].fillna('未知')
        
        return df
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        import traceback
        st.error(f"详细错误: {traceback.format_exc()}")
        return None

# 加载数据
df = load_data()

if df is not None:
    # 应用标题
    st.title("数字化转型指数分析平台")
    st.markdown("---")
    
    # 侧边栏筛选器
    st.sidebar.header("数据筛选")
    
    # 年份筛选（默认选择有完整行业数据的年份）
    years = sorted(df['年份'].unique())
    # 查找有完整行业数据的年份
    default_year = 2021  # 已知有完整数据的年份
    default_index = years.index(default_year) if default_year in years else len(years)-1
    
    selected_year = st.sidebar.selectbox("选择年份", years, index=default_index)
    
    # 年份提示
    if selected_year > 2021:
        st.sidebar.warning("⚠️ 提示：2022年后行业数据不完整，建议查看2021年及之前的数据")
    
    # 行业筛选
    industries = ['全部'] + sorted(df['行业名称'].unique())
    selected_industry = st.sidebar.selectbox("选择行业", industries)
    
    # 企业名称搜索
    company_name = st.sidebar.text_input("企业名称")
    
    # 股票代码搜索
    stock_code = st.sidebar.text_input("股票代码")
    
    # 筛选数据
    filtered_df = df.copy()
    filtered_df = filtered_df[filtered_df['年份'] == selected_year]
    
    if selected_industry != '全部':
        filtered_df = filtered_df[filtered_df['行业名称'] == selected_industry]
    
    if company_name:
        filtered_df = filtered_df[filtered_df['企业名称'].str.contains(company_name, case=False)]
    
    if stock_code:
        filtered_df = filtered_df[filtered_df['股票代码'].str.contains(stock_code, case=False)]
    
    # 主内容区域
    with st.container():
        # 数据概览
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("企业数量", len(filtered_df))
        
        if filtered_df.empty:
            st.warning("当前筛选条件下没有数据")
        else:
            avg_index = filtered_df['数字化转型指数(0-100分)'].mean()
            max_index = filtered_df['数字化转型指数(0-100分)'].max()
            min_index = filtered_df['数字化转型指数(0-100分)'].min()
            
            with col2:
                st.metric("平均指数", f"{avg_index:.1f}")
            with col3:
                st.metric("最高指数", int(max_index))
            with col4:
                st.metric("最低指数", int(min_index))
        
        # 指数分布直方图
        st.subheader("数字化转型指数分布")
        if not filtered_df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.histplot(filtered_df['数字化转型指数(0-100分)'], bins=20, kde=True, ax=ax, color='skyblue')
            ax.set_title(f"{selected_year}年数字化转型指数分布")
            ax.set_xlabel("数字化转型指数")
            ax.set_ylabel("企业数量")
            st.pyplot(fig)
        
        # 企业排名表格
        st.subheader("企业排名")
        if not filtered_df.empty:
            ranked_df = filtered_df.sort_values(by='数字化转型指数(0-100分)', ascending=False)
            display_df = ranked_df[['股票代码', '企业名称', '行业名称', '数字化转型指数(0-100分)', '总词频数']].head(20)
            display_df.insert(0, '排名', range(1, len(display_df) + 1))
            st.dataframe(display_df, use_container_width=True)
        
        # 行业对比分析
        st.subheader("行业对比分析")
        year_data = df[df['年份'] == selected_year]
        industry_avg = year_data.groupby('行业名称')['数字化转型指数(0-100分)'].mean().sort_values(ascending=False).reset_index()
        
        if len(industry_avg) > 1:
            # 只显示非未知行业的数据
            industry_avg_non_unknown = industry_avg[industry_avg['行业名称'] != '未知行业']
            
            if len(industry_avg_non_unknown) > 0:
                fig = px.bar(
                    industry_avg_non_unknown.head(10),
                    x='行业名称',
                    y='数字化转型指数(0-100分)',
                    title=f"{selected_year}年各行业平均指数Top10",
                    color='数字化转型指数(0-100分)',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("当前年份没有非未知行业数据")
