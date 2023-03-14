import streamlit as st
st.set_page_config(layout="wide")
from st_aggrid import AgGrid
from app import (create_connection, DB_FILE, TABLE, initialize_ss_var)
import pandas as pd

def on_edit_click(ss, idx):
    ss.edit[idx] = True

def on_save_click(ss, idx):
    ss.edit[idx] = False
    ss.df.loc[
            idx, 
            ['team1', 'team2', 'winner', 'odd', 'bet_amount']
            ] = ss.changes

def save_changes():
    _conn = create_connection(DB_FILE)
    r = st.session_state.df.to_sql(
        TABLE,
        _conn,
        index=False, 
        if_exists='replace'
        )

'''
# History
'''

st.sidebar.markdown("# History")


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
    st.session_state.first_load = True
    initialize_ss_var('df', df)

else:
    df = st.session_state.df

initialize_ss_var('edit', dict.fromkeys(df.index, False))

with st.expander("Default book"):
#with st.container():
    # columns of table
    # 1: bet_id
    # 2: team1
    # 3: team2
    # 4: winner (1=team1, 2=team2)
    # 5: odd
    # 6: bet_amount
    # 7: select_slider (pick winner; 0=undefined; 1=Lost; 2=Won)
    # 8: edit button
    columns = st.columns(
        (1, 3, 3, 3, 1, 1, 3, 1)
        )
    fields = ["id", "Team 1", "Team 2", "Winner", "Odd", "Amount", "Result", "Action"]
    for col, field_name in zip(columns, fields):
        col.write(f"**{field_name}**")

    for index, row in st.session_state.df.iloc[::-1].iterrows():
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(
            (1, 3, 3, 3, 1, 1, 3, 1)
            )
        col1.write(row.bet_id)
        col2.write(row.team1)
        col3.write(row.team2)
        winner = {1: row.team1, 2: row.team2}[row.winner]
        col4.write(winner)
        col5.write(row.odd)
        col6.write(row.bet_amount)
        prev_result = {0: 'Undefined', 1: 'Lost', 2: 'Won'}[row.result]

        with col7:
            result_slider = st.select_slider(
                "",
                options=('Lost', 'Undefined', 'Won'),
                value=prev_result,
                key=f"slider-{index}"
                )
        
        if result_slider != row.result:
            new_result = {'Undefined': 0, 'Lost': 1, 'Won': 2}[result_slider]
            st.session_state.df.loc[index, 'result'] = new_result
        
        placeholder = col8.empty()

        if st.session_state.edit[index]:
            initialize_ss_var('changes', ['', '', '', 0, 0])
            placeholder.button("💾",
            key=f'save-{index}',
            type='primary',
            on_click=on_save_click,
            args=[st.session_state, index,]
            )

            new_team1, new_team2, = row.team1, row.team2
            new_winner = {1: row.team1, 2: row.team2}[row.winner]
            new_odd, new_bet = row.odd, row.bet_amount

            c1, c2 = st.columns(2)
            with c1:
                new_team1 = st.text_input("", new_team1)
            with c2:
                new_team2 = st.text_input("", new_team2)

            c3, c4, c5 = st.columns((1, 1, 2))
            with c3:
                new_odd = st.number_input(
                    "Odd",
                    value=new_odd,
                    min_value=1.0,
                    max_value=None,)
            with c4:
                new_bet = st.number_input(
                    "Bet Amount",
                    value=new_bet,
                    min_value=1.0,
                    max_value=None,)
            with c5:
                new_winner = st.selectbox(
                    "Picked winner",
                    (new_team1, new_team2))
                    
            # col2.write(new_team1)
            # col3.write(new_team2)
            # col4.write(new_winner)
            # col5.write(new_odd)
            # col6.write(new_bet)
            winner = {new_team1: 1, new_team2:2}[new_winner]
            st.session_state.changes = [new_team1, new_team2, winner, new_odd, new_bet]

        else:
            placeholder.button("✏️",
                key=f'edit-{index}',
                type='primary',
                on_click=on_edit_click,
                args=[st.session_state, index]
                )

    
    AgGrid(df)


_, save_col, _ = st.columns(3)
with save_col:
    save_button = st.button("Save changes",
    on_click=save_changes,
    type='primary',
    key='save_btn')