import streamlit as st 
import plotly.express as px

st.header("Maiores valores ")

if 'dados' not in st.session_state:
    st.error("Os dados não foram carregados")
else:
    top_n = st.session_state.get('top_n', 10)
    dados = st.session_state['dados']

    col1,col2,col3 = st.columns(3)

    with col1:
        Mempenho = dados.nlargest(top_n,'VALOREMPENHO')
        fig1 = px.bar(Mempenho,x='MUNICIPIO',y='VALOREMPENHO', title='Maiores Empenhos')
        st.plotly_chart(fig1,use_container_width=True)
    with col2:
        MPIB = dados.nlargest(top_n,'PIB')
        fig2 = px.pie(MPIB,values='PIB',names='MUNICIPIO',title='Maiores PIB')
        st.plotly_chart(fig2,use_container_width=True)
    with col3:
        Mprop = dados.nlargest(top_n,'PROPORCAO')
        fig3 = px.bar(Mprop,x='MUNICIPIO',y='PROPORCAO', title='Maiores Gastos em proporcao ao PIB')
        st.plotly_chart(fig3,use_container_width=True)