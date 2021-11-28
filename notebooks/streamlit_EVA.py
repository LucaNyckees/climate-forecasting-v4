import streamlit as st
import scipy as sc
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import date
#import statistics as st
from statsmodels.graphics.gofplots import qqplot
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.seasonal import STL
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.distributions.empirical_distribution import ECDF
import calendar
from TimeSerie_fct import create_monthly_avg_time_serie
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.stattools import acf, pacf
from sklearn.utils import resample
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

def max_min_analysis():
    st.title("Temeprature Extremes at Geneva Observatory")
    
    st.header("Dataset")
    
    st.markdown("The data we propose to work with is the series of maximum and minimum temperature at Geneva Observatory during the period 1901-2021. We will first perform our analysis on the daily maxima series, and then on the daily minima series. Below, a box-plot of the monthly temepratures has been performed, showing the variability of the temperatures for each month.")
    
    data_max = pd.read_csv("DataGenerated/DailyEVA/Daily_max.csv")
    
    N=12
    c = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, N)]
    
    fig = go.Figure(data=[go.Box(
        y=data_max[data_max.Month == float(i+1)].Max,
        marker_color=c[i],name=calendar.month_name[int(i+1)]
        ) for i in range(N)])
        
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(zeroline=False, gridcolor='white'),
    )
    
    fig['layout'].update({
        'title': 'Daily Maxima at Geneva Observatory',
        'title_x': 0.5,
        'xaxis': {
            'title': 'Month',
            'zeroline': False
        },
        'yaxis': {
            'title':"Daily mean temperature (°C)"
        },
        
        'width': 1200,
        'height': 600
    })
        
    st.plotly_chart(fig)
    
    st.markdown("In the box plot, we can see that the variability of maxima seems to be the same over the year: there does not seems to be more variability in the winter months compare to the summer months.")
    
    st.markdown("In order to be able to apply the POT method, the observations need to be independent identically distributed. However, one can observe that the temperatures follow a seasonal pattern: the temperature increases from january until it reaches a peak during summer and then decreases until it reaches a minimum at the end of the year. To illustrate this, we have plotted below the maximum temperature curve from 1901 to 2021.")
    
    fig = px.line(data_max, x='Date', y='Max')

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=6, label="6 months", step="month", stepmode="backward"),
                dict(count=1, label="1 year", step="year", stepmode="backward"),
                dict(count=5, label="5 year", step="year", stepmode="backward"),
                dict(count=10, label="10 years", step="year", stepmode="backward"),
                dict(count=30, label="30 years", step="year", stepmode="backward"),
                dict(count=50, label="50 years", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    fig['layout'].update({
        'title': 'Daily maximum 1901-2021',
        'title_x': 0.5,
        'xaxis': {
            'zeroline': False
        },
        'yaxis': {
            'title':"Maximum temperature (°C)"
        },
        
        'width': 1200,
        'height': 500,
        'legend':{
            'title':""
                         }
    })
   
    st.plotly_chart(fig)
    
    st.markdown("To avoid these seasonal variations, a  first common approach in an analysis is to consider different series for each month of the year. In our analysis, the temperatures of January from 1901 to 2021, the temperatures of February from 1901 to 2021, etc. A small trend could be observed for certain months, but it was not taken into account in this first  extreme value analasis. Then, the selection of a fixed threshold for each month was made possible.")


    st.header("Choice of Threshold")
    
    st.markdown('''The choice of threshold is very crucial when one wants to apply the POT method and estimate the GPD parameters. Furthermore, this choice is not straightforward; indeed, a compromise has to be found: a high threshold value reduces the bias as this satisfies es the convergence towards the extreme value theory but however increases the variance for the estimators of the parameters of the GPD, as there will be fewer data from which to estimate parameters. A low threshold value results in the opposite i.e. a high bias but a low variance of the estimators, there is more data with which to estimate the parameters.
    ''')
    
    st.markdown(r'''Mean residual life plots have been performed but they were diffcult to interpret. It was quite hard to choose a threshold from such a plot, as all the graph are approximately linear from a very small threshold, exept perhaps the months of June, October, November and December, where the respective mean residual life plots make us think that a threshold above ,respectively , 30.5 ,23 ,17 and 14 $\degree$C appears correct.''')
    
    SELECTED_MONTH1 = st.selectbox("Choose a month to view its Mean Residual  Life plot",calendar.month_name[1:] , index=0)

    file = "DataGenerated/DailyEVA/Mean_Residual_Life/ "+str(SELECTED_MONTH1)+" .png"
    st.image(file)
    
    st.markdown(r'''
    The parameter stability plots involves plotting the modifed scale parameter and the shape parameter against the threshold u for a range of threshold which has been chosen to go from the 80% quantile to the 99% quantile. The parameter estimates should be stable (i.e. constant) above the threshold at which the GPD model becomes valid. In practise, the mean excess values and parameter estimates are calculated from relatively small amounts of data, so the plots will not look either linear or constant even when the GPD model becomes valid. Confidence intervals are included, so that we can evaluate whether the plots look linear or constant once we have accounted for the effects of estimation uncertainty. This is not easy to do by eye, and the interpretation of these plots often requires a good deal of subjective judgement.
    ''')
    
    SELECTED_MONTH2 = st.selectbox("Choose a month to view its Parameters Stability plot",calendar.month_name[1:] , index=0)

    file = "DataGenerated/DailyEVA/Parameters_stability/ "+str(SELECTED_MONTH2)+" .png"
    st.image(file)
    
    parameter_stability_plot_estimate_threshold = pd.read_csv("DataGenerated/DailyEVA/Parameters_stability/visual_estimate.csv",dtype='a').drop(labels='Unnamed: 0',axis = 1)
    
    st.markdown("On the following table, we can see a estimation of the threshold for each month, according to the visual inspection of the parameters stability plots.")
    
    st.dataframe(parameter_stability_plot_estimate_threshold)


