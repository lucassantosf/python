import streamlit as st 
import pandas as pd 
from sklearn.model_selection import train_test_split 
from sklearn.preprocessing import OrdinalEncoder  
from sklearn.naive_bayes import CategoricalNB 
from sklearn.metrics import accuracy_score

st.set_page_config(
    page_title="Classificação de veiculos",
    layout="wide"
)

## Criar modelo 
@st.cache_data
def load_data_and_model():
    carros = pd.read_csv("car.csv",sep=",")

    ## Tratamento dos dados 
    encoder = OrdinalEncoder()

    for col in carros.columns.drop('class'):
        carros[col] = carros[col].astype('category')

    ## Encoder -> Mudar dados categoricos nominais para ordinais
    X_encoded = encoder.fit_transform(carros.drop('class',axis=1)) 

    y = carros['class'].astype('category').cat.codes

    ## Separar dados de treino e teste
    X_train,X_test, y_train, y_test = train_test_split(X_encoded,y,test_size=0.3,random_state=42)
    
    ## Treinar modelo
    modelo = CategoricalNB()
    modelo.fit(X_train,y_train)

    y_pred = modelo.predict(X_test)
    acuraria = accuracy_score(y_test,y_pred)

    return encoder, modelo, acuraria, carros

encoder, modelo, acuraria, carros = load_data_and_model()

st.title("Previsão de Qualidade de Veiculo")
st.write(F"Acurário do modelo : {acuraria:2f}")

input_features = [
                st.selectbox("Preço : ",carros['buying'].unique()),
                st.selectbox("Manutenção : ",carros['maint'].unique()),
                st.selectbox("Portas : ",carros['doors'].unique()),
                st.selectbox("Capacidade de passageiros : ",carros['persons'].unique()),
                st.selectbox("Portamalas : ",carros['lug_boot'].unique()),
                st.selectbox("Segurança : ",carros['safety'].unique()),
            ]

## Se botao for pressionado/clicado
if st.button("Processar"):
    input_df = pd.DataFrame([input_features],columns=carros.columns.drop('class'))
    input_encoded = encoder.transform(input_df)
    predict_encoded = modelo.predict(input_encoded)
    ## Transformar o encoded para a classficacao nominal e não ordinal
    previsao = carros['class'].astype('category').cat.categories[predict_encoded][0]
    st.header(F"Resultado da previsão : {previsao}")