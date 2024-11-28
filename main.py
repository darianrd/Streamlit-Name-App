import numpy as np
import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from my_plots import *
import streamlit as st

@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

@st.cache_data
def ohw(df):
    nunique_year = df.groupby(['name', 'sex'])['year'].nunique()
    one_hit_wonders = nunique_year[nunique_year == 1].index
    one_hit_wonder_data = df.set_index(['name', 'sex']).loc[one_hit_wonders].reset_index()
    return one_hit_wonder_data

data = load_name_data()
ohw_data = ohw(data)

st.title("Name Popularity App")

with st.sidebar:
    input_name = st.text_input('Enter a name:', 'Mary')
    toggle = st.toggle('Recent History')
    year_input = st.slider('Year', min_value=1880, max_value=2023, value=2000)
    n_names = st.radio('Number of names per sex', [3, 5, 10])

tab1, tab2 = st.tabs(['Names', 'Year'])

with tab1:
    if toggle:
        max_year = data['year'].max()
        name_data = data[(data['name'] == input_name) & (data['year'] >= max_year - 9)].copy()
    else:
        name_data = data[data['name'] == input_name]
    st.write("**Count of Names by Year and Sex**")
    fig = px.line(name_data, x = 'year', y = 'count', color = 'sex')
    st.plotly_chart(fig)

    fig2 = name_trend_plot(name_data, name = input_name)
    st.plotly_chart(fig2)

with tab2:
    col1, col2 = st.columns([2,1])
    with col1:
        fig3 = top_names_plot(data, year = year_input, n = n_names)
        st.plotly_chart(fig3) 

    with col2:
        with st.popover("Unique Names Table"):
            st.write('Count of Unique Names for Selected Year')
            output_table = unique_names_summary(data, year_input)
            st.dataframe(output_table)



