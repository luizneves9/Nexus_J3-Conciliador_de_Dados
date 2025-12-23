## --- Inicializando as bibliotecas ---
import pandas as pd
import os

## --- Definindo os diretórios ---
caminho_nome = os.path.dirname(os.path.abspath(__file__))
caminho_corporativo = os.path.join(caminho_nome, 'corporativo')
caminho_cliente = os.path.join(caminho_nome, 'cliente')

## --- Processamento dos dados do Corporativo ---

# definindo os arquivos da pasta
caminhos_arquivos = [
    os.path.join(caminho_corporativo, f) for f in os.listdir(caminho_corporativo) if f.endswith(('.csv'))
]

# processando os arquivos
lista_arquivos = []

for arquivo in caminhos_arquivos:

    nome_arquivo = os.path.basename(arquivo)
    print(f'Sistema: Processando o arquivo "{nome_arquivo}".')

    try:
        arquivo_temporario = pd.read_csv(arquivo, sep=';', decimal=',', encoding='latin-1')
        if arquivo_temporario is not None:
            arquivo_temporario['Origem'] = nome_arquivo
            lista_arquivos.append(arquivo_temporario)
    except Exception as e:
        print(f'Aviso: Erro ao processar o arquivo "{nome_arquivo}".')
    
if lista_arquivos:
    try:
        df_corporativo = pd.concat(lista_arquivos)
    except Exception as e:
        print(f'Aviso: Erro ao concatenar os arquivos da "lista_arquivos".')

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

## mantendo as principais colunas do df

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
df_corporativo = df_corporativo[['Origem', 'Nome_Empresa', 'STATUS BILHETE', 'DATA HORA VENDA', 'DATA HORA VENDA PARA CANC.', 'NUMERO BILHETE', 'ID TRANSACAO ORIGINAL', 'TARIFA',
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
    'TAXA_EMB': 'Taxa_Emb',
    'TOTAL DO BILHETE': 'Total do Bilhete',
    'AGENCIA ORIGINAL': 'Agencia',
    'ID TRANSACAO ORIGINAL': 'ID Transacao',
    'NOME PASSAGEIRO': 'Nome Passageiro',
    'POLTRONA': 'Poltrona',
    'VALOR MULTA': 'Valor Multa',
    'DATA HORA VIAGEM': 'Data Viagem',
    'DATA HORA VENDA PARA CANC.': 'Data Venda'
}

df_corporativo.rename(columns=col_corporativo_renomear, inplace=True)

# tratando valores vazios da coluna 'Valor Multa'
filtro_multa_null = df_corporativo['Valor Multa'].isna()
df_corporativo.loc[filtro_multa_null, 'Valor Multa'] = 0

# tratando a coluna 'Data Venda' vazia em casos de vendas
filtro_vendas = df_corporativo['Status'] == 'V'
df_corporativo.loc[filtro_vendas, 'Data Venda'] = df_corporativo.loc[filtro_vendas, 'Data Lancamento']

## tratando datas

# convertendo data de lancamento
df_corporativo['Data Lancamento'] = pd.to_datetime(df_corporativo['Data Lancamento'], dayfirst=True, errors='coerce')

# criando filtro da coluna data venda
filtro_data_venda = df_corporativo['Data Venda'].astype(str).str.strip()

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