import numpy as np
import pandas as pd
import calendar
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from PIL import Image

from paths import DATA_PATH


def max_min_analysis():
    st.title("Temeprature Extremes at Geneva Observatory")

    st.header("Dataset")

    st.markdown(
        "The data we propose to work with is the series of maximum temperature at Geneva Observatory during the period 1901-2021. We will first perform our analysis on the daily maxima series. Below, a box-plot of the monthly temepratures has been performed, showing the variability of the temperatures for each month."
    )

    data_max = pd.read_csv(DATA_PATH / "generated" / "DailyEVA" / "Daily_max.csv")

    N = 12
    c = ["hsl(" + str(h) + ",50%" + ",50%)" for h in np.linspace(0, 360, N)]

    fig = go.Figure(
        data=[
            go.Box(
                y=data_max[data_max.Month == float(i + 1)].Max, marker_color=c[i], name=calendar.month_name[int(i + 1)]
            )
            for i in range(N)
        ]
    )

    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(zeroline=False, gridcolor="white"),
    )

    fig["layout"].update(
        {
            "title": "Daily Maxima at Geneva Observatory",
            "title_x": 0.5,
            "xaxis": {"title": "Month", "zeroline": False},
            "yaxis": {"title": "Daily mean temperature (°C)"},
            "width": 1200,
            "height": 600,
        }
    )

    st.plotly_chart(fig)

    st.markdown(
        "In the box plot, we can see that the variability of maxima seems to be the same over the year: there does not seems to be more variability in the winter months compare to the summer months."
    )

    st.markdown(
        "In order to be able to apply the POT method, the observations need to be independent identically distributed. However, one can observe that the temperatures follow a seasonal pattern: the temperature increases from january until it reaches a peak during summer and then decreases until it reaches a minimum at the end of the year. To illustrate this, we have plotted below the maximum temperature curve from 1901 to 2021."
    )

    fig = px.line(data_max, x="Date", y="Max")

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=6, label="6 months", step="month", stepmode="backward"),
                    dict(count=1, label="1 year", step="year", stepmode="backward"),
                    dict(count=5, label="5 year", step="year", stepmode="backward"),
                    dict(count=10, label="10 years", step="year", stepmode="backward"),
                    dict(count=30, label="30 years", step="year", stepmode="backward"),
                    dict(count=50, label="50 years", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        ),
    )

    fig["layout"].update(
        {
            "title": "Daily maximum 1901-2021",
            "title_x": 0.5,
            "xaxis": {"zeroline": False},
            "yaxis": {"title": "Maximum temperature (°C)"},
            "width": 1200,
            "height": 500,
            "legend": {"title": ""},
        }
    )

    st.plotly_chart(fig)

    st.markdown(
        "To avoid these seasonal variations, a  first common approach in an analysis is to consider different series for each month of the year. In our analysis, the temperatures of January from 1901 to 2021, the temperatures of February from 1901 to 2021, etc. A small trend could be observed for certain months, as in our previous study, but it was not taken into account in this first  extreme value analasis. Then, the selection of a fixed threshold for each month was made possible."
    )

    st.header("Choice of Threshold")

    st.markdown("""The choice of threshold is very crucial when one wants to apply the POT method and estimate the GPD parameters. Furthermore, this choice is not straightforward; indeed, a compromise has to be found: a high threshold value reduces the bias as this satisfies es the convergence towards the extreme value theory but however increases the variance for the estimators of the parameters of the GPD, as there will be fewer data from which to estimate parameters. A low threshold value results in the opposite i.e. a high bias but a low variance of the estimators, there is more data with which to estimate the parameters.
    """)

    st.markdown(
        r"""Mean residual life plots have been performed but they were diffcult to interpret. It was quite hard to choose a threshold from such a plot, as all the graph are approximately linear from a very small threshold, exept perhaps the months of June, October, November and December, where the respective mean residual life plots make us think that a threshold above ,respectively , 30.5 ,23 ,17 and 14 $\degree$C appears correct."""
    )

    SELECTED_MONTH1 = st.selectbox(
        "Choose a month to view its Mean Residual  Life plot", calendar.month_name[1:], index=0
    )

    image = Image.open(DATA_PATH / "generated" / "DailyEVA" / "Mean_Residual_Life" / f"{SELECTED_MONTH1}.png")
    st.image(image)

    st.markdown(r"""
    The parameter stability plots involves plotting the modifed scale parameter and the shape parameter against the threshold $u$ for a range of threshold which has been chosen to go from the 80% quantile to the 99% quantile. The parameter estimates should be stable (i.e. constant) above the threshold at which the GPD model becomes valid. In practise, the mean excess values and parameter estimates are calculated from relatively small amounts of data, so the plots will not look either linear or constant even when the GPD model becomes valid. Confidence intervals are included, so that we can evaluate whether the plots look linear or constant once we have accounted for the effects of estimation uncertainty. This is not easy to do by eye, and the interpretation of these plots often requires a good deal of subjective judgement.
    """)

    SELECTED_MONTH2 = st.selectbox(
        "Choose a month to view its Parameters Stability plot", calendar.month_name[1:], index=0
    )

    image = Image.open(DATA_PATH / "generated" / "DailyEVA" / "Parameters_stability" / f"{SELECTED_MONTH2}.png")
    st.image(image)

    parameter_stability_plot_estimate_threshold = pd.read_csv(
        DATA_PATH / "generated" / "DailyEVA" / "Parameters_stability" / "visual_estimate.csv", dtype="a"
    )
    th_thumb = pd.read_csv(DATA_PATH / "generated" / "DailyEVA" / "th_thumb.csv", dtype="a")
    threshold_estimate = parameter_stability_plot_estimate_threshold.append(th_thumb)
    threshold_estimate.rename(columns={"Unnamed: 0": ""}, index={"estimate": "Visual estimate"}, inplace=True)

    st.markdown(
        "On the following table, we can see a estimation of the threshold for each month, according to the visual inspection of the parameters stability plots and according to some rules of thumb describe below."
    )

    st.table(threshold_estimate)

    with st.expander("Rules of Thumb"):
        st.markdown(r"""The differents rules of thumb consists in choosing ine of the sample points as a threshold: the choice is pratically equivalent to estimation of the $k$th upper order statistic $X_{n-k+1}$ from the ordered sequence $X_{(1)}, ...,X_{(n)}$. Frequently used is the 90%  quantile. Other rules can be used, such as the square root $k = \sqrt{n}$ (rules of thumb 2 in the above table) or again the rule $k = n^{\frac{2}{3}}/\log(\log(n))$ (rules of thumb 3 in the above table).
        """)

    st.markdown(r"""Then we applied the multiple-threshold diagnostic. To do this, we used $m = 41$ threholds from the $85\%$ quantile for each month to the threshold which is such that only 30 observations of each month are above this threshold. We calculated the p-values using the score test based on the $\chi_{m-i}^2$ null distribution, $i = 1,... ,m-1$. Our selection method consists of choosing, for each month, the smallest threshold that does not allow us to reject the null hypothesis at a significance level of $\alpha = 0.05$. However, as we can see in the figure below, this method allows us, for some months, to reject our null hypothesis for any threshold above the 80% quantile of each month. This would mean that for these months, we would have to consider thresholds below the 80% quantile, but this would introduce too much bias in our model. In cases where our method allows us to select a threshold, it can be seen that this is generally higher than the 90% quantile. Although this method allows us to choose a threshold more objectively than the graphical methods based on the evaluation of mean residuals life plots and parameters stability plots, it still tends to choose too low thresholds.
    """)

    th_score = pd.read_csv(DATA_PATH / "generated" / "DailyEVA" / "th_score.csv")
    # th_cvm = pd.read_csv("DataGenerated/DailyEVA/th_cvm.csv")
    th_th = pd.read_csv(DATA_PATH / "generated" / "DailyEVA" / "th_th.csv")

    def create_button(label, n_visible):
        return dict(label=label, method="update", args=[{"visible": [bool(n_visible == m) for m in np.arange(1, 13)]}])

    fig = go.Figure()

    for i in range(1, 13):
        fig.add_trace(
            go.Scatter(
                x=th_th[calendar.month_name[i]],
                y=th_score[calendar.month_name[i]],
                name=calendar.month_name[int(i)],
                marker=dict(color=px.colors.qualitative.G10[(i - 1) % 9], size=8),
                mode="lines+markers",
            )
        )
    # for i in range(1,13):
    # fig.add_trace(
    # go.Scatter(x=th_th[calendar.month_name[i]],
    # y=th_cvm[calendar.month_name[i]],
    # name=calendar.month_name[int(i)]+" (Likelihood Ratio Test)",
    # marker=dict(color=px.colors.qualitative.G10[(i)%9],
    # symbol="square",size = 8),
    # mode = 'lines+markers'))

    fig.add_hline(y=0.05, line_dash="dash", line_color="red", name="alpha = 0.05")

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=0,
                x=0.87,
                y=1.12,
                buttons=list([create_button(calendar.month_name[int(m)], m) for m in np.arange(1, 13)]),
            )
        ]
    )
    fig.update_layout(title_text="P-value of the Score Test", title_x=0.5, title_y=1, xaxis_domain=[0.05, 1.0])

    fig["layout"].update(
        {
            "xaxis": {"title": "Thresholds", "zeroline": False},
            "yaxis": {"title": "P-value"},
            "width": 1200,
            "height": 600,
        }
    )

    st.plotly_chart(fig)

    with st.expander("Score Tests"):
        st.markdown("For more details on the [Score Test](https://link.springer.com/article/10.1007/s10687-014-0183-z)")

    st.markdown(r"""For the rest of this study we will therefore take our thresholds as the 90% quantile of each month, as it seems to be accurate.
    """)

    st.header("Declustering and fit of the POT")

    st.markdown(r"""The POT method requires the exceedances to be mutually independent.
    However, for the temperatures data, threshold exceedances are seen to occur
    in groups: an extremely warm day is likely to be followed by another. In order to deal with independent variables and be able to apply the POT method, a commonly used technique is declustering, which  filters the dependent observations to obtain a set of threshold excesses that are approximately independent.
    """)
    st.markdown(
        "The clusters are defined as follows. First, a threshold is  fixed and clusters of exceedances  are consecutive exceedances of this threshold. Then, a run length (minimum  separation) $r$ is set between each cluster: a cluster is terminated whenever the separation between two threshold exceedances is greater than the run length $r$. The maximum excess in each cluster is identified, and these cluster maxima can be assumed to be independent. Then, the GPD can be  fitted to the cluster maxima."
    )
    st.markdown(
        r"Thus, it is necessary for the temperature data to perform a declustering in order to estimate the parameters $\sigma$  and $\xi$ . A run period of $r = 2$ days was chosen, and the threshold was set to the 90% quantile, as it seems to be quite accurate. In the figures below, we have the diagnostic plots for each month."
    )

    SELECTED_MONTH3 = st.selectbox(
        "Choose a month to view the diagnostic plot of the POT fit", calendar.month_name[1:], index=0
    )

    image = Image.open(DATA_PATH / "generated" / "DailyEVA" / "Diag_plot" / f"{SELECTED_MONTH3}.png")
    st.image(image)

    st.markdown(r"""The  fit seems to be good since the probability and quantile plots are fairly linear (confidence intervals taken into account) for each month except for the months. In addition, it would appear that there are too few points to obtain a good agreement between the fitted density and the estimated core density. \n
    La table ci-dessous regroupe les estimations des paramètres $\sigma$  et $\xi$ pour chaque mois, dans les colonnes "sigma" and "shape". In addition, we also have in this table, the standard deviations of our estimates, as well as some normal-based 95% confidence intervals for the both parameters.

    """)

    POT_coef_estimation = pd.read_csv(DATA_PATH / "generated" / "DailyEVA" / "POT_estimation.csv")
    POT_coef_estimation.rename(columns={"Unnamed: 0": ""}, inplace=True)
    POT_coef_estimation = POT_coef_estimation.set_index("", drop=True)

    st.table(
        POT_coef_estimation.style.apply(
            lambda x: [
                "background-color: lightsteelblue" if (0 > x.iloc[6] and 0 > x.iloc[7]) else "" for i, v in enumerate(x)
            ],
            axis=1,
        )
    )

    st.markdown(
        r"The confidence intervals for the shape parameter all contain $\xi = 0$, except for the estimate for February and April. This suggests that a Gumbel distribution ($\xi$ fixed at $0$) could be at the origin of the extremes patterns underlying these ten months. To investigate this further, we calculated and plotted the profiles likelihood of the parameters with 95% confidence intervals (which are represented on the plots by the values of the parameters whose log-likelihood profile is above the horizontal dotted line)."
    )

    dd = np.array([1, 3, 5, 6, 7, 8, 9, 10, 11, 12])
    SELECTED_MONTH4 = st.selectbox(
        "Choose a month to view its profile likelihood plot", [calendar.month_name[i] for i in dd], index=0
    )

    image = Image.open(DATA_PATH / "generated" / "DailyEVA" / "Prof_likelihood" / f"{SELECTED_MONTH4}.png")
    st.image(image)

    st.markdown(
        r"For these ten months, the plot of the log-likelihood profiles suggests that the hypothesis $\xi = 0$ is plausible. It is therefore interesting to explore this possibility further."
    )

    st.header("Gumbel fit")

    st.markdown(r"""On the plots below we have the Gumbel fit plots for all months except February and April.
    """)

    SELECTED_MONTH5 = st.selectbox(
        "Choose a month to view the diagnostic plot of the Gumbel fit", [calendar.month_name[i] for i in dd], index=0
    )

    image = Image.open(DATA_PATH / "generated" / "DailyEVA" / "Diag_plot_gumbel" / f"{SELECTED_MONTH5}.png")
    st.image(image)

    st.markdown(r"""The diagnostic plots seem to indicate an equally good, if not better, fit than the POT model. To decide whether to consider the two-parameter or the one-parameter model, we performed a log-likelihood ratio test for each of the months concerned, in order to find out whether we can significantly assume that $\xi = 0$. The results of these tests are presented in the table below. It can be seen that the null hypothesis, $\xi = 0$, cannot be rejected for each month. In the rest of this study we will therefore consider the one parameter model for each of these months.
    """)

    p_val = pd.read_csv(DATA_PATH / "generated" / "DailyEVA" / "Likelihood_ratio_p_val.csv")
    p_val.rename(columns={"Unnamed: 0": "", "dev": "Deviance", "p_val": "p_value"}, inplace=True)
    p_val = p_val.set_index("", drop=True)

    c1, c2, c3 = st.columns([2, 2, 2])
    with c2:
        st.table(p_val.style.set_caption("P-values of the likelihood ratio test"))

    st.header("Return Levels and Return Periods")

    return_levels = pd.read_csv(DATA_PATH / "generated" / "DailyEVA" / "return_levels.csv")

    st.markdown(r"""In the table below, we have estimates of return levels for return periods of 10, 20, 50, 100, 200 and 1000 years, as well as the maximum temperature observe in each month during the study period.
     """)

    return_levels.rename(columns={"Unnamed: 0": ""}, inplace=True)
    return_levels = return_levels.set_index("", drop=True)
    st.table(return_levels)

    st.markdown(
        "It can be seen that except for the months of February and April where the returns levels are underestimated compared to the maximum temperatures observed over the period 1901-2021, we have that the observed maximum temperatures correspond to a returns period of 100 to 200 years."
    )

    st.header("Discussion")

    st.markdown(
        "The aim of this work was to study the series of maximal temperatures at Geneva Observatory by using the peaks-over-threshold method. A particular interest was given to the choice of the threshold to perform such an analysis. Indeed, the choice of the threshold affects the estimation of the GPD parameters. Different method were used to help the choice of the threshold: graphical diagnostics, rules of thumbs and statistical tests. Rules of thumb are easy to use since they choose one particular value from the series as the threshold. Graphical diagnostics consist in analysisng different plots, but are often very difficult to interpret as they usually require a lot of subjectivity. Finally, a other method using statistical tets was used, which is more demanding computationally, but gave results easier to interpret as the comparison od p-values is more straightforward. Nevertheless, in our case this method tended to give us much too low thresholds. Lastly, we chose to use the rule of thumb with the 90% quantile, as it gave us thresholds close to those found with the diagnostic plots. "
    )

    st.markdown(
        "Concerning the data, a strong seasonal variation is present in the temperature series, as temperature fluctuate along the year. To perform our study, we decided to avoidthis seasonnal variations and cut the data into different series for each month. In addition, in order to work with data that are not dependent we performed a declustering on our data. However, after further analysis of what exactly this declustering did, we realised that it was more or less the same as considering the maximum temperature of each month. This would lead us to change our approach in a future study and to use a block-maxima approach instead of a point-over-threshold approach. As for the results of our modelling, we ended up modelling the extremes of each month with a Gumbel distribution, except for February and April for which a model with negative shape parameters seemed more appropriate. As for the returns levels, we observed that those of February and April seemed to underestimate the maximum temperatures observed over the period under consideration, nevertheless for the other months the calculated returns levels are quite consistent with the observed maximums."
    )
    st.markdown(
        "For further work, it could be possible to use a time-varying threshold and perform the analysis on the whole time series. This would take into account the effect of seasonality."
    )
