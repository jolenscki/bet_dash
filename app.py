import streamlit as st
st.set_page_config(layout="wide")
import random as rd
import pandas as pd
import re
import sqlite3
from sqlite3 import Error
import requests

DB_FILE = "bet_history.db"
TABLE = "matches"



def set_winner(team):
    st.session_state['game_winner'] = team

def get_id_from_link(match_link):
    '''
    Function that retrieves the ID from a HLTV match link
    '''
    # try conversion
    try:
        match_link = int(match_link)
    except:
        pass
    if isinstance(match_link, int):
        return match_link
    pattern = r"(?:https:\/\/)?(?:www.)?hltv.org\/matches\/(\d+)\/?(?:\S+)?"
    match_id = re.match(pattern, match_link).groups()
    if not match_id:
        raise("Invalid link!")
    return match_id[0]

def save_bet():
    st.session_state['confirmation'] = True
    conn = create_connection(DB_FILE)
    update_table(conn, TABLE, df)

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        st.failed(f"conn failed {e}")
    
    return conn

def update_table(_conn, table, df):
    r = df.to_sql(
        table,
        _conn,
        index=False, 
        if_exists='append'
        )
    st.success(f'Bet registered successfully', icon="✅")

    st.session_state.sql_result = r

    return r

@st.cache_resource
def clear_all():
    st.cache_resource.clear()
    for k in st.session_state.keys():
        del st.session_state[k]
    st.write([el for el in st.session_state.keys()])

def initialize_ss_var(key, default_value):
    if key not in st.session_state:
        st.session_state[key] = default_value

initialize_ss_var("game_winner", None)
initialize_ss_var("confirmation", False)
initialize_ss_var("sql_result", 0)
initialize_ss_var("hltv_link", '')
initialize_ss_var("team1_txt_input", '')
initialize_ss_var("team2_txt_input", '')
initialize_ss_var("odd_value", 1.85)
initialize_ss_var("bet_amount", 10.0)


'''
# Betting Dashboard
'''

st.sidebar.markdown("# Add Bet")


hltv_link = st.text_input(
    "Match Page or Match ID (HLTV)",
     st.session_state["hltv_link"],
     key="hltv_link",
     )

if hltv_link:
    hltv_link = get_id_from_link(hltv_link)

team1, vs_str, team2 = st.columns((3, 1, 3))

t1 = team1.text_input(
    "Team 1 Name",
     st.session_state["team1_txt_input"],
     key="team1_txt_input",
     )
vs_str.write('vs')
t2 = team2.text_input(
    "Team 2 Name",
    st.session_state["team2_txt_input"],
    key="team2_txt_input",
    )
team1_btn_col, _, team2_btn_col = st.columns((3, 1, 3))


with team1_btn_col:
    team1_btn = st.button(
        label=t1,
        on_click=lambda: set_winner(t1),
        key='t1'
         )

with team2_btn_col:
    team2_btn = st.button(
        label=t2,
        on_click=lambda: set_winner(t2),
        key='t2'
         )

if st.session_state['game_winner']:
    txt = st.write(f"Betting on {st.session_state['game_winner']}")


odd_col, bet_amount_col = st.columns(2)

with odd_col:
    odd = st.number_input(
        "Odd on winning team",
        min_value=1.0,
        max_value=None,
        # value=st.session_state.odd_value,
        step=.01,
        format='%0.2f',
        key='odd_value',
    )

with bet_amount_col:
    bet_amount = st.number_input(
        "Bet on winning team",
        min_value=0.01,
        max_value=None,
        value=st.session_state.bet_amount,
        step=.01,
        format="%.2f",
        key='bet_amount',
    )



try:
    bet_info = {
        'team1': t1,
        'team2': t2,
        'winner': {t1:1, t2:2}[st.session_state.game_winner],
        'odd': round(odd, 2),
        'bet_amount': round(bet_amount, 2),
        'match_id': hltv_link if hltv_link else 1
    }

    df = pd.DataFrame([bet_info])
except:
    if st.session_state['game_winner']:
        st.write(f"Coudn't create dataframe `df`")
    
confirm = st.button(label='Place bet',
    on_click=save_bet,
    key='confirm')
    

clear_all = st.button(
    label='Clear/Place new bet',
    on_click=clear_all,
    key='clear')