## --- Inicializando as bibliotecas ---
import pandas as pd
import os
from utils.file_manager import listagem_arquivos, carregamento_arquivos
import numpy as np
import plotly.express as px
import streamlit as st

## --- Definindo os diretórios ---
caminho_nome = os.path.dirname(os.path.abspath(__file__))
caminho_corporativo = os.path.join(caminho_nome, 'corporativo')
caminho_cliente = os.path.join(caminho_nome, 'cliente')

## --- Processamento dos dados do Corporativo ---

# listando os arquivos para importação
lista_arquivos_corporativo = listagem_arquivos(caminho_corporativo, 'csv')
df_corporativo = carregamento_arquivos(lista_arquivos_corporativo, 'Totalbus')

lista_arquivos_j3 = listagem_arquivos(caminho_cliente, 'xlsx')
df_j3 = carregamento_arquivos(lista_arquivos_j3, 'J3')

# definindo o nome das empresas
criterio_empresa = {
    1: 'Viacao Garcia',
    3: 'Princesa do Ivai',
    6: 'Brasil Sul',
    17: 'Santo Anjo'
}

df_corporativo['Nome_Empresa'] = df_corporativo['EMPRESA'].map(criterio_empresa)

# filtrando os dados diferentes do código PCA 254 (Substituição de passagem)
df_corporativo = df_corporativo[df_corporativo['CODIGO PCA'] != 254]

## mantendo as principais colunas do df_corporativo

# colunas originais
col_corporativo_original = ['EMPRESA', 'NUMERO BILHETE', 'NUMERO BPE', 'DATA HORA VENDA',
       'STATUS BILHETE', 'TIPO_VENDA', 'TARIFA', 'PEDAGIO', 'TAXA_EMB',
       'TOTAL DO BILHETE', 'FORMA PAGAMENTO 1', 'VALOR PAGAMENTO 1',
       'FORMA PAGAMENTO 2', 'VALOR PAGAMENTO 2', 'FORMA PAGAMENTO 3',
       'VALOR PAGAMENTO 3', 'NSU 1', 'NSU 2', 'NSU 3', 'AGENCIA ORIGINAL',
       'CODIGO PCA', 'ID TRANSACAO', 'ID TRANSACAO ORIGINAL',
       'NOME PASSAGEIRO', 'POLTRONA', 'AUTORIZAÇÃO', 'FORMA PAGTO. MULTA',
       'VALOR MULTA', 'NSU MULTA', 'FORMA PAGTO. SEGURO OPCIONAL 1',
       'VALOR SEGURO OPCIONAL 1', 'FORMA PAGTO. SEGURO OPCIONAL 2',
       'VALOR SEGURO OPCIONAL 2', 'FORMA PAGTO. SEGURO OPCIONAL 3',
       'VALOR SEGURO OPCIONAL 3', 'FORMA PAGTO. DIF.MENOR', 'VALOR DIF. MENOR',
       'NSU DIF.MENOR', 'DATA HORA VIAGEM', 'DATA HORA VENDA PARA CANC.',
       'AGENCIA EMISSORA', 'CODIGO PCA.1', 'VALOR PCA', 'QTD. PARCELAS',
       'DATA/HORA CANCELAMENTO', 'Nome_Empresa']

# definindo as colunas essenciais
df_corporativo = df_corporativo[['Origem', 'Base', 'Nome_Empresa', 'STATUS BILHETE', 'DATA HORA VENDA', 'DATA HORA VENDA PARA CANC.', 'NUMERO BILHETE', 'ID TRANSACAO ORIGINAL', 'TARIFA',
                  'PEDAGIO', 'TAXA_EMB', 'TOTAL DO BILHETE', 'VALOR MULTA', 'AGENCIA ORIGINAL', 
                  'NOME PASSAGEIRO', 'POLTRONA', 'DATA HORA VIAGEM'
       ]]

# renomeando colunas
col_corporativo_renomear = {
    'Nome_Empresa': 'Empresa',
    'NUMERO BILHETE': 'Bilhete',
    'DATA HORA VENDA': 'Data Lancamento',
    'STATUS BILHETE': 'Status',
    'TARIFA': 'Tarifa',
    'PEDAGIO': 'Pedagio',
    'TAXA_EMB': 'Taxa de Embarque',
    'TOTAL DO BILHETE': 'Total do Bilhete',
    'AGENCIA ORIGINAL': 'Agencia',
    'ID TRANSACAO ORIGINAL': 'ID Transacao',
    'NOME PASSAGEIRO': 'Nome Passageiro',
    'POLTRONA': 'Assento',
    'VALOR MULTA': 'Valor Multa',
    'DATA HORA VIAGEM': 'Data Viagem',
    'DATA HORA VENDA PARA CANC.': 'Data Venda'
}

df_corporativo.rename(columns=col_corporativo_renomear, inplace=True)

## --- Tratando o tipo das colunas no Corporativo ---

## definindo as colunas de estorno

# criando as colunas com valor 0.00
df_corporativo['Estorno Tarifa'] = 0.0
df_corporativo['Estorno Taxa'] = 0.0
df_corporativo['Estorno Total'] = 0.0

# ajustando o valor da coluna estorno_tarifa
df_corporativo.loc[df_corporativo['Status'] == 'C', 'Estorno Tarifa'] = df_corporativo.loc[df_corporativo['Status'] == 'C', 'Tarifa']

# ajustando o valor da coluna estorno_taxa
df_corporativo.loc[df_corporativo['Status'] == 'C', 'Estorno Taxa'] = (
    df_corporativo.loc[df_corporativo['Status'] == 'C', 'Pedagio'] + 
    df_corporativo.loc[df_corporativo['Status'] == 'C', 'Taxa de Embarque']
)

# ajustando o valor da coluna estorno_total
df_corporativo.loc[df_corporativo['Status'] == 'C', 'Estorno Total'] = (
    df_corporativo.loc[df_corporativo['Status'] == 'C', 'Estorno Tarifa'] + 
    df_corporativo.loc[df_corporativo['Status'] == 'C', 'Estorno Taxa']
)

# tratando valores vazios da coluna 'Valor Multa'
filtro_multa_null = df_corporativo['Valor Multa'].isna()
df_corporativo.loc[filtro_multa_null, 'Valor Multa'] = 0.0

# tratando a coluna 'Data Venda' vazia em casos de vendas
filtro_vendas = df_corporativo['Status'] == 'V'
df_corporativo.loc[filtro_vendas, 'Data Venda'] = df_corporativo.loc[filtro_vendas, 'Data Lancamento']

# convertendo data de lancamento
df_corporativo['Data Lancamento'] = pd.to_datetime(df_corporativo['Data Lancamento'], dayfirst=True, errors='coerce')

# criando filtro da coluna data venda
filtro_data_venda = df_corporativo['Data Venda'].astype(str).str.strip ()

# convertendo em data do formato dd/mm/yyyy hh:mm
df_corporativo['Data Venda'] = pd.to_datetime(
    filtro_data_venda,
    format='%d/%m/%Y %H:%M',
    errors='coerce'
)

# convertendo em data no formato dd/mm/yyyy hh:mm:ss
mask_nat_1 = df_corporativo['Data Venda'].isna()
df_corporativo.loc[mask_nat_1, 'Data Venda'] = pd.to_datetime(
    filtro_data_venda[mask_nat_1],
    format='%d/%m/%Y %H:%M:%S',
    errors='coerce'
)

# convertendo em data no formato dd/mm/yyyy
mask_nat_2 = df_corporativo['Data Venda'].isna()
df_corporativo.loc[mask_nat_2, 'Data Venda'] = pd.to_datetime(
    filtro_data_venda[mask_nat_2],
    format='%d/%m/%Y',
    errors='coerce'
)

# convertendo em data no formato dd-mm-yyyy
mask_nat_3 = df_corporativo['Data Venda'].isna()
df_corporativo.loc[mask_nat_3, 'Data Venda'] = pd.to_datetime(
    filtro_data_venda[mask_nat_3],
    format='%d-%m-%Y',
    errors='coerce'
)

# convertendo em data no formato dd-mm-yyyy hh:mm:ss
mask_nat_4 = df_corporativo['Data Venda'].isna()
df_corporativo.loc[mask_nat_4, 'Data Venda'] = pd.to_datetime(
    filtro_data_venda[mask_nat_4],
    format='%d-%m-%Y %H:%M:%S',
    errors='coerce'
)

# normalizando a data
df_corporativo['Data Venda'] = df_corporativo['Data Venda'].dt.normalize()

# tratando tipos diversos das colunas
df_corporativo['ID Transacao'] = df_corporativo['ID Transacao'].astype(str).str.replace('.0', '')
df_corporativo['Bilhete'] = df_corporativo['Bilhete'].astype(str)
df_corporativo['Assento'] = df_corporativo['Assento'].astype(str)
df_corporativo['Total do Bilhete'] = df_corporativo['Total do Bilhete'].astype(float)

## definindo a coluna de comissao
# posteriormente, verificar a variação feita com métricas de incentivo
df_corporativo['Comissao'] = 0.08
df_corporativo['Comissao_vlr'] = df_corporativo['Total do Bilhete'] * df_corporativo['Comissao']

## definindo a coluna de repasse
df_corporativo['Repasse'] = df_corporativo['Total do Bilhete'] - df_corporativo['Comissao_vlr']

# ajustando para negativo os valores cancelados
df_corporativo.loc[df_corporativo['Status'] == 'C', 'Repasse'] = -df_corporativo.loc[df_corporativo['Status'] == 'C', 'Repasse']

## --- Tratando as colunas da J3 ---

## mantendo a coluna original
col_j3_original = ['Origem', 'Destino', 'Serviço ', 'Assento', 'Tarifa', 'Taxas', 'Seguro',
       'Pedágio', 'Taxa de Embarque', 'Outros', 'Nome Passageiro', 'Documento',
       'Data Venda', 'Numero Bilhete', 'Id Transação', 'Data Viagem',
       'Data Cancelamento', 'Agência Cancelamento', 'Estorno Tarifa',
       'Estorno Taxa', 'Estorno Total', 'Base', 'Status']

## renomeando colunas
col_j3_renomear = {
    'Pedágio': 'Pedagio'
}

df_j3.rename(columns=col_j3_renomear, inplace=True)

## criando a coluna data_lancamento
df_j3['Data Lancamento'] = df_j3['Data Venda']
df_j3.loc[df_j3['Status'] != 'V', 'Data Lancamento'] = df_j3.loc[df_j3['Status'] != 'V', 'Data Cancelamento']

## criando a coluna numero_bilhete, vazio
df_j3['Bilhete'] = 0

## ajustando a coluna id_transacao
df_j3['ID Transacao'] = df_j3['Numero Bilhete']
df_j3 = df_j3.drop(columns='Numero Bilhete')

## incluindo a coluna total_do_bilhete
df_j3['Total do Bilhete'] = df_j3['Tarifa'] + df_j3['Pedagio'] + df_j3['Taxa de Embarque']

## incluindo a coluna de valor_multa
df_j3['Valor Multa'] = 0.0

## incluindo a coluna agencia
df_j3['Agencia'] = '999-97'
df_j3.loc[df_j3['Origem'].str.contains('EMBARCA', na=False), 'Agencia'] = '999-81'

## definindo a coluna de empresas
condicao_empresa = [
    df_j3['Origem'].str.contains('VGL', na=False).copy(),
    df_j3['Origem'].str.contains('EPIL', na=False).copy(),
    df_j3['Origem'].str.contains('BS', na=False).copy(),
    df_j3['Origem'].str.contains('ESA', na=False).copy()
]

valores_empresa = [
    'Viacao Garcia',
    'Prinecesa do Ivai',
    'Brasil Sul',
    'Santo Anjo'
]

df_j3['Empresa'] = np.select(condicao_empresa, valores_empresa, 'Nao Identificado')

## definindo colunas essenciais
df_j3 = df_j3[[
    'Origem', 'Base', 'Empresa', 'Status', 'Data Lancamento', 'Data Venda',
    'Bilhete', 'ID Transacao', 'Tarifa', 'Pedagio', 'Taxa de Embarque', 'Total do Bilhete', 
    'Valor Multa', 'Agencia', 'Nome Passageiro', 'Assento', 'Data Viagem', 'Estorno Tarifa', 'Estorno Taxa', 'Estorno Total'
]]

## definindo a coluna de comissao
# posteriormente, verificar a variação feita com métricas de incentivo
df_j3['Comissao'] = 0.08
df_j3['Comissao_vlr'] = df_j3['Total do Bilhete'] * df_j3['Comissao']

## definindo a coluna de repasse
df_j3['Repasse'] = df_j3['Total do Bilhete'] - df_j3['Comissao_vlr']

# ajustando para negativo os valores vendidos
df_j3.loc[df_j3['Status'] == 'V', 'Repasse'] = -df_j3.loc[df_j3['Status'] == 'V', 'Repasse']

## definindo o tipo das colunas str
col_j3_str = ['Bilhete', 'ID Transacao', 'Assento', 'Data Viagem']
df_j3[col_j3_str] = df_j3[col_j3_str].astype(str)

## --- Agrupando dataframes ---
df_agrupado = pd.concat([df_corporativo, df_j3], ignore_index=True)

## --- Streamlit ---

## funções
def formata_inteiros(num):
    num = f'{num:,.0f}'.replace('.', 'x').replace(',', '.').replace('x', ',')
    return num

def formata_valores(num):
    if num >= 1_000_000:
        return f'{num / 1_000_000:.1f} Mi'
    elif num >= 1_000:
        return f'{num / 1_000:.1f} Mil'
    else:
        return f'{num:.2f}'.replace('.', ',')

def formata_numeros(num):
    num = f'{num:,.2f}'.replace('.', 'x').replace(',', '.').replace('x', ',')
    return num

## estruturando métricas

# receita de vendas mensais do totalbus - apenas vendas
receita_vendas_mensal_totalbus = df_agrupado[(df_agrupado['Base'] == 'Totalbus') & (df_agrupado['Status'] == 'V')].set_index('Data Lancamento').groupby(pd.Grouper('Data Lancamento', freq='ME'))['Total do Bilhete'].sum().reset_index()

# valor total de transações no totalbus
receita_total_totalbus = df_agrupado[(df_agrupado['Base'] == 'Totalbus') & (df_agrupado['Status'] == 'V')]['Total do Bilhete'].sum()

# quantidade de transações no totalbus
quantidade_vendas_totalbus = df_agrupado[(df_agrupado['Base'] == 'Totalbus') & (df_agrupado['Status'] == 'V')].shape[0]

# ticket totalbus
ticket_totalbus = receita_total_totalbus / quantidade_vendas_totalbus

## dashboard
st.set_page_config(layout='wide')

st.write('DASHBOARD | J3')

aba1, aba2 = st.tabs(['Resumo', 'Conciliação'])

with aba1:

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric('Total de Vendas', f'R$ {formata_valores(receita_total_totalbus)}')

    with col2:
        st.metric('Quantidade de Vendas', formata_inteiros(quantidade_vendas_totalbus))

    with col3:
        st.metric('Ticket', f'R$ {formata_numeros(ticket_totalbus)}')

with aba2:

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric('Total de Vendas', f'R$ {formata_valores(receita_total_totalbus)}')

    with col2:
        st.metric('Quantidade de Vendas', formata_inteiros(quantidade_vendas_totalbus))

    with col3:
        st.metric('Ticket', f'R$ {formata_numeros(ticket_totalbus)}')
