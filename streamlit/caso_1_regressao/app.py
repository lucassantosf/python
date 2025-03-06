import streamlit as st 
import pandas as pd 
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt 

dados = pd.read_csv('slr12.csv', sep=";")

## Separar previsor e alvo da regressao 

X = dados[['FrqAnual']]
y = dados['CusInic']

## Criação do modelo de regressão
model = LinearRegression().fit(X,y)

## Criar titulo para a página
st.title('Previsão inicial de custo para franquia')

## Construir o App Streamlit
col1,col2 = st.columns(2)

with col1:
    st.header("Dados")
    st.table(dados.head(10))

with col2:
    st.header("Gráfico de Dispersão")
    fig, ax = plt.subplots()
    ax.scatter(X,y, color='blue')
    ax.plot(X, model.predict(X), color='red')
    st.pyplot(fig)

st.header("Valor anual da franquia")
novo_valor = st.number_input("Insira novo valor", min_value=1.0, max_value=99999999999.0,value=1500.0, step=0.01)
processar = st.button("Processar")

## Se clicar no botão processar
if processar:
    dados_novo_valor = pd.DataFrame([[novo_valor]], columns=['FrqAnual'])
    prev = model.predict(dados_novo_valor)
    st.header(f"Previsão de custo inicial R$ {prev[0]:.2f}")