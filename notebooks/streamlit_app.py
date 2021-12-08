import matplotlib
import matplotlib.pyplot as plt
import streamlit as st
#from pyvis.network import Network
import numpy as np
import pandas as pd
from datetime import datetime
import os
import matplotlib
import base64
from paths import paths

from streamlit_functions import *
from streamlit_forecasting import st_forecasting
from streamlit_monthly import monthly_analysis
from streamlit_EVA import max_min_analysis

# STREAMLIT STRUCTURAL CONFIGURATION

st.set_page_config(layout='wide')

#-----


#-----

st.markdown("<h1 style='text-align: center;'> Meteorological data visualization</h1>",
            unsafe_allow_html=True)


MODES = ['Descriptive Statistics','Time Series Analysis','Extreme Value Analysis', 'Time Series Visualization', 'Time Series Analysis']
MODES_TS = ["Annual Mean Temperature at Geneva Observatory","Monthly Mean Temperature at Geneva Observatory"]
MODES_EVA = ["Max-Min temeprature extreme analysis at Geneva Observatory"]

st.sidebar.header('Options')

INFO = st.sidebar.radio("Content",('Project description', 'Mean Temperature at Geneva Observatory','Extreme Value Analysis', 'Data Visualization'))
    

# PROJECT DESCRIPTION

if INFO == 'Project description':
    
    introduction()
    
# Written analysis with time series
elif INFO == "Mean Temperature at Geneva Observatory":
    
    SELECTED_MODE = st.sidebar.selectbox("Part", MODES_TS, index=0)
    #if SELECTED_MODE == MODES_TS[0]:
     #   annual_intro()
    if SELECTED_MODE == MODES_TS[0]:
        annual_analysis()
    elif SELECTED_MODE == MODES_TS[1]:
        monthly_analysis()

elif INFO == 'Extreme Value Analysis':

    SELECTED_MODE = st.sidebar.selectbox("Part", MODES_EVA, index=0)
        
    if SELECTED_MODE == MODES_EVA[0]:
        max_min_analysis()
    
# INTERACTIVE AND STATIC DATA VISUALIZATION

elif INFO == 'Data Visualization':

    SELECTED_MODE = st.sidebar.selectbox("Visualization mode", MODES, index=0)
    if SELECTED_MODE == MODES[0]:
        
        elt = st.radio("What do you want to observe?",('Mean temperature', 'Sunshine duration'))
        
        station = st.radio("What station are you interested in?",('Geneva Observatory', 'All stations in Switzerland'))
        
        st.header("Descriptive Statistics - Interactive Visualization")
        st.sidebar.header("Descriptive Data visualization")
        
        path = paths(elt)
        
        
        df = pd.read_table(path, sep = ',', names = ['SOUID','DATE','TG','Q_TG'], skiprows = range(0,20))

        if station == 'Geneva Observatory':
            
            if st.checkbox("Descriptive statistics summary"):

                plot_stats_window_st(df,elt)

            elif st.checkbox("Display time-window feature"):

                multiple_curves_window(df,elt)

            elif st.checkbox("Display correlation network feature"):

                correlation_net(df, elt)

            elif st.checkbox("Display animated circular temperature evolution"):

                st_circular_vision()
                
        elif station == 'All stations in Switzerland':
            
            st.markdown("Processing the data from all stations may take a few seconds...")
            
            dfs, dfs_M, names = multiple_data_processing()
            
            if st.checkbox("Display temperature curves on all observatories"):

                st_all_obs_curves(dfs, dfs_M, names)
                
            elif st.checkbox("Display geographic correlation network"):
                
                st_geo_correlation_net(dfs, names)
            
            


    #elif SELECTED_MODE == MODES[1]:

    elif SELECTED_MODE == MODES[2]:
        
        results_display()
            
        
# SIDEBAR BONUS OPTIONS

if st.sidebar.button("Data"):

    datasets()

if st.sidebar.button("GitHub"):

    github()

if st.sidebar.button("Contacts"):
    
    contacts()
    

                
