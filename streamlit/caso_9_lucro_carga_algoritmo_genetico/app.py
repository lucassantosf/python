#importacao libs
import streamlit as st
import pandas as pd
from geneticalgorithm import geneticalgorithm as ga 

#definir titulo da pagina
st.set_page_config(page_title="Otimização de transporte de carga", layout="wide")
st.title("Otimização de transporte de carga")

def load_data(file):
    return pd.read_csv(file, sep=";")

def fitness_function(X,data,max_volume,max_weight):
    selected_items = data.iloc[X.astype(bool),:]
    total_weight = selected_items['PESO'].sum()
    total_volume = selected_items['VOLUME'].sum()

    if total_weight > max_weight or total_volume > max_volume:
        return -1 
    else:
        return -selected_items['VALOR'].sum()

data = None 

col1,col2 = st.columns(2)

with col1.expander("Dados"):
    uploaded_file = st.file_uploader("Selecione o arquivo",type='csv')
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        calculated_button = st.button("Calcular Totais")

        if calculated_button:
            st.write(data)
            st.write(f"Quantidade de itens : {len(data)}")
            st.write(f"Peso Total : {data['PESO'].sum()}")
            st.write(f"Volume Total : {data['VOLUME'].sum()}")
            st.write(f"Valor Total : {data['VALOR'].sum()}")

with col2.expander("Processamento"):
    if data is not None:
        sobra_peso = st.number_input("Informe a sobra de peso", value=6000)
        sobra_volume = st.number_input("Informe a sobra de volume", value=350)
        iteracao = st.number_input("Informe a quantidade de iterações",value=10)
        process_button = st.button("Processar")

        if process_button:
            algorithm_param = {
                'max_num_iteration':iteracao,
                'population_size':10,
                'mutation_probability':0.1,
                'elit_ratio':0.01,
                'parents_portion':0.3,
                'crossover_probability':0.5,
                'crossover_type':'uniform',
                'max_iteration_without_improv': None,
            }

            varbound = [[0,1]] * len(data)
            model = ga(
                function=lambda X:fitness_function(X,data,sobra_volume, sobra_peso),
                dimension=len(data),
                variable_type='bool',
                variable_boundaries=varbound,
                algorithm_parameters=algorithm_param
            )
            model.run()
            solution = data.iloc[model.output_dict['variable'].astype(bool),:]
            st.write(solution)
            st.write(f"Quantidade final {len(solution)}")
            st.write(f"Peso final {solution['PESO'].sum()}")
            st.write(f"Volume final {solution['VOLUME'].sum()}")
            st.write(f"Valor final {solution['VALOR'].sum()}")
