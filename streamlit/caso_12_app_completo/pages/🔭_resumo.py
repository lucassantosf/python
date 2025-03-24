import streamlit as st 

st.header("Resumo dos dados")

if 'dados' not in st.session_state:
    st.error("Os dados não foram carregados")
else:
    dados = st.session_state['dados'].describe().reset_index()
    st.write(dados)
    