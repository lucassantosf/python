# importar libs
import streamlit as st 
import pandas as pd 
from statsmodels.tsa.statespace.sarimax import SARIMAX 
from statsmodels.tsa.seasonal import seasonal_decompose 
import matplotlib.pyplot as plt 
from datetime import date 
from io import StringIO

# começar configurações da pagina 
st.set_page_config(page_title="Sistema de análise e previsão de séries temporais",layout="wide")
st.title("Sistema de análise e previsão de séries temporais")

with st.sidebar:
    uploaded_file = st.file_uploader("Escolha o arquivo : ",type=['csv'])
    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        data = pd.read_csv(stringio,header=None)
        data_inicio = date(2000,10,1)
        periodo = st.date_input("Periodo inicial da série", data_inicio)
        periodo_previsao = st.number_input("Informe quantos meses quer prever",min_value=1,max_value=48,value=12)
        processar = st.button("Processar")

if uploaded_file is not None and processar:
    try: 
        # transformar dados importados em uma série temporal
        ts_data = pd.Series(data.iloc[:,0].values,index=pd.date_range(
            start=periodo,periods=len(data),freq='M'))

        # decompor
        decomposicao = seasonal_decompose(ts_data,model='additive')
        
        # criar figura da decomposicao
        fig_decomposicao = decomposicao.plot()
        fig_decomposicao.set_size_inches(10,8)

        # criar modelo arima 
        modelo = SARIMAX(ts_data,order=(2,0,0),seasonal_order=(0,1,1,12))
        modelo_fit = modelo.fit()

        # fazer previsão
        previsao = modelo_fit.forecast(steps=periodo_previsao)

        # criar figura da previsao
        fig_previsao, ax = plt.subplots(figsize=(10,5))
        ax = ts_data.plot(ax=ax)
        previsao.plot(ax=ax, style='r--')

        # mostrar na tela o resultado 
        col1, col2, col3 = st.columns([3,3,2]) #parametros de proporção das colunas na tela 

        with col1:
            st.write("Decomposição")
            st.pyplot(fig_decomposicao)

        with col2:
            st.write("Previsão")
            st.pyplot(fig_previsao)

        with col3:
            st.write("Dados da Previsão")
            st.dataframe(previsao)

    except Exception as e:
        st.error(f"Erro ao processar os dados : {e}")



