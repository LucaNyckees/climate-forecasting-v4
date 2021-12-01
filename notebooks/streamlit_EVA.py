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
from plotly.validators.scatter.marker import SymbolValidator

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
    The parameter stability plots involves plotting the modifed scale parameter and the shape parameter against the threshold $u$ for a range of threshold which has been chosen to go from the 80% quantile to the 99% quantile. The parameter estimates should be stable (i.e. constant) above the threshold at which the GPD model becomes valid. In practise, the mean excess values and parameter estimates are calculated from relatively small amounts of data, so the plots will not look either linear or constant even when the GPD model becomes valid. Confidence intervals are included, so that we can evaluate whether the plots look linear or constant once we have accounted for the effects of estimation uncertainty. This is not easy to do by eye, and the interpretation of these plots often requires a good deal of subjective judgement.
    ''')
    
    SELECTED_MONTH2 = st.selectbox("Choose a month to view its Parameters Stability plot",calendar.month_name[1:] , index=0)

    file = "DataGenerated/DailyEVA/Parameters_stability/ "+str(SELECTED_MONTH2)+" .png"
    st.image(file)
    
    parameter_stability_plot_estimate_threshold = pd.read_csv("DataGenerated/DailyEVA/Parameters_stability/visual_estimate.csv",dtype='a')
    th_thumb = pd.read_csv("DataGenerated/DailyEVA/th_thumb.csv",dtype='a')
    threshold_estimate = parameter_stability_plot_estimate_threshold.append(th_thumb)
    threshold_estimate.rename(columns={'Unnamed: 0': ''}, index={'estimate': 'Visual estimate'}, inplace=True)
    
    st.markdown("On the following table, we can see a estimation of the threshold for each month, according to the visual inspection of the parameters stability plots and according to some rules of thumb describe below.")
    
    st.table(threshold_estimate)
    
    
    with st.expander("Rules of Thumb"):
        st.markdown("h")
        
        
    st.markdown(r'''Then we applied the multiple-threshold diagnostic. To do this, we used $m = 41$ threholds from the $85\%$ quantile for each month to the threshold which is such that only 30 observations of each month are above this threshold. We calculated the p-values using the score test based on the $\chi_{m-i}^2$ null distribution, $i = 1,... ,m-1$. Our selection method consists of choosing, for each month, the smallest threshold that does not allow us to reject the null hypothesis at a significance level of $\alpha = 0.05$. However, as we can see in the figure below, this method allows us, for some months, to reject our null hypothesis for any threshold above the 80% quantile of each month. This would mean that for these months, we would have to consider thresholds below the 80% quantile, but this would introduce too much bias in our model. In cases where our method allows us to select a threshold, it can be seen that this is generally higher than the 90% quantile. Although this method allows us to choose a threshold more objectively than the graphical methods based on the evaluation of mean residuals life plots and parameters stability plots, it still tends to choose too low thresholds.
    ''')
        
    th_score = pd.read_csv("DataGenerated/DailyEVA/th_score.csv")
    #th_cvm = pd.read_csv("DataGenerated/DailyEVA/th_cvm.csv")
    th_th = pd.read_csv("DataGenerated/DailyEVA/th_th.csv")
    
    def create_button(label, n_visible):
        return dict(label=label,
                         method="update",
                         args=[{"visible": [bool(n_visible==m) for m in np.arange(1,13)]}]
                         )
    fig = go.Figure()
    
    for i in range(1,13):
        fig.add_trace(
            go.Scatter(x=th_th[calendar.month_name[i]],
                       y=th_score[calendar.month_name[i]],
                       name=calendar.month_name[int(i)],
                       marker=dict(color=px.colors.qualitative.G10[(i-1)%9],size = 8),
                       mode = 'lines+markers'))
    #for i in range(1,13):
        #fig.add_trace(
            #go.Scatter(x=th_th[calendar.month_name[i]],
                      # y=th_cvm[calendar.month_name[i]],
                       #name=calendar.month_name[int(i)]+" (Likelihood Ratio Test)",
                       #marker=dict(color=px.colors.qualitative.G10[(i)%9],
                       #symbol="square",size = 8),
                      # mode = 'lines+markers'))
        
    fig.add_hline(y=0.05,line_dash="dash", line_color="red", name = 'alpha = 0.05')

    
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=0,
                x=0.87,
                y=1.12,
                buttons=list([create_button(calendar.month_name[int(m)],m) for m in np.arange(1,13)]),
            )
        ])
    fig.update_layout(
    title_text="P-value of the Score Test", title_x= 0.5, title_y= 1,
    xaxis_domain=[0.05, 1.0]
    )
    
    fig['layout'].update({
        'xaxis': {
            'title': 'Thresholds',
            'zeroline': False
        },
        'yaxis': {
            'title':"P-value"
        },
        
        'width': 1200,
        'height': 600
    })
        
    st.plotly_chart(fig)

    with st.expander("SCore and Cramér-Von Mises Tests"):
        st.markdown("")
        
    st.markdown(r'''For the rest of this study we will therefore take our thresholds as the 90% quantile of each month, as it seems to be accurate.
    ''')
    
    st.header("Declustering and fit of the POT")
    
    st.markdown(r'''
    ''')
    
    SELECTED_MONTH3 = st.selectbox("Choose a month to view the diagnostic plot of the POT fit",calendar.month_name[1:] , index=0)

    file = "DataGenerated/DailyEVA/Diag_plot/ "+str(SELECTED_MONTH3)+" .png"
    st.image(file)
    
    POT_coef_estimation = pd.read_csv("DataGenerated/DailyEVA/POT_estimation.csv")
    POT_coef_estimation.rename(columns={'Unnamed: 0': ''}, inplace=True)
    POT_coef_estimation = POT_coef_estimation.set_index('',drop = True)
    
    st.table(POT_coef_estimation.style.apply(lambda x: ["background-color: lightsteelblue"
                          if ((0 > x.iloc[6]
                                                    and 0 > x.iloc[7]))
                          else "" for i, v in enumerate(x)], axis = 1))
    dd = np.array([1,3,5,6,7,8,9,10,11,12])
    SELECTED_MONTH4 = st.selectbox("Choose a month to view its profile likelihood plot",[calendar.month_name[i] for i in dd] , index=0)

    file = "DataGenerated/DailyEVA/Prof_likelihood/ "+str(SELECTED_MONTH4)+" .png"
    st.image(file)
    
    st.header("Gumbel fit")
    
    SELECTED_MONTH5 = st.selectbox("Choose a month to view the diagnostic plot of the Gumbel fit",[calendar.month_name[i] for i in dd] , index=0)

    file = "DataGenerated/DailyEVA/Diag_plot_gumbel/ "+str(SELECTED_MONTH5)+" .png"
    st.image(file)
    
    p_val = pd.read_csv("DataGenerated/DailyEVA/Likelihood_ratio_p_val.csv")
    p_val.rename(columns={'Unnamed: 0': '','dev': 'Deviance','p_val': 'p_value'}, inplace=True)
    p_val = p_val.set_index('',drop = True)
    
    c1,c2,c3 = st.columns([2,2,2])
    with c2:
        st.table(p_val.style.set_caption("P-values of the likelihood ratio test"))
     
     st.hearder("Non-stationarity: Modelling")
     
     
