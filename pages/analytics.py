import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import numpy as np
from app import (create_connection,
 DB_FILE, TABLE, initialize_ss_var)

import plotly.express as px
import plotly.graph_objects as go

'''
# Analytics
'''
st.sidebar.markdown("# Analytics")


initialize_ss_var('first_load', False)

if not st.session_state.first_load:
    _conn = create_connection(DB_FILE)
    query = f'''SELECT 
        bet_id,
        team1,
        team2,
        winner,
        odd,
        bet_amount,
        match_id,
        result
        FROM {TABLE}
    '''

    df = pd.read_sql_query(query, _conn)
    df = df[df.result != 0]
    st.session_state.first_load = True
    initialize_ss_var('df', df)


initialize_ss_var('analysis_range', (1, st.session_state.df.shape[0]))
st.sidebar.slider(
    "Analyze this matches",
    value=(1, st.session_state.df.shape[0]),
    step=1,
    min_value=1,
    max_value=st.session_state.df.shape[0],
    key='analysis_range',
)

initialize_ss_var('df_range', st.session_state.df)
r = st.session_state.analysis_range
st.session_state.df_range = st.session_state.df.iloc[r[0]:r[1]]

st.dataframe(st.session_state.df_range)

amount_invested = st.session_state.df_range.bet_amount.cumsum().rename("Betted")
revenue = st.session_state.df_range.apply(
    lambda row: row.odd*row.bet_amount if row.result==2 else 0,
     axis=1
     ).cumsum().rename("Return")

profit = (revenue - amount_invested).rename("Profit")

chart_data = pd.concat(
    [amount_invested, revenue, profit],
    axis=1,
)

c1, c2 = st.columns(2, gap='large')

with c1:
    st.write("# Overall results")
    # vertical space for alignemnt
    for i in range(5):
        st.text("")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart_data.index, y=chart_data.iloc[:, 0],
            name='Expenses',
            mode='lines',
            line=dict(width=.5, color="#ff8c8c"),
            stackgroup = 'one'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=chart_data.index, y=chart_data.iloc[:, 1],
            name='Revenue',
            mode='lines',
            line=dict(width=.5, color="#5ce488"),
            stackgroup = 'two'
        )
    )

    st.plotly_chart(fig, theme='streamlit')
        
with c2:
    st.write("# Profits")
    initialize_ss_var('profit_type', 'Absolute')
    st.selectbox(
        "Analysis type",
        options=('Absolute', 'Relative'),
        key='profit_type'
    )
    x = chart_data.index
    if st.session_state.profit_type == 'Absolute':
        y = chart_data.iloc[:, 2]
        layout = go.Layout()
    else:
        y = (chart_data.iloc[:, 2]/chart_data.iloc[:, 0])
        layout = go.Layout(yaxis=dict(tickformat=".2%"))
    
    mask = y >= 0
    y_above = np.where(mask, y, 0)
    y_below = np.where(mask, 0, y)

    fig2 = go.Figure(layout=layout)
    fig2.add_trace(
        go.Scatter(
            x=x, y=y_above,
            name='Profit',
            mode='lines',
            fill='tozeroy',
            line=dict(width=.5, color="#5ce488"),
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=x, y=y_below,
            name='Loss',
            mode='lines',
            fill='tozeroy',
            line=dict(width=.5, color="#ff8c8c"),
        )
    )

    st.plotly_chart(fig2, theme='streamlit')