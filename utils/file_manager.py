## --- Inicializando as bibliotecas ---

import os
import pandas as pd

## --- Listando os arquivos da pasta ---

def listagem_arquivos(caminho, tipo_arquivo='csv'):
    """
    Função com funcionalidade de listar todos os arquivos .csv em uma pasta especifica.
    
    :param caminho: diretório da pasta.
    """
    if tipo_arquivo == 'csv':
        caminhos_arquivos = [
            os.path.join(caminho, f) for f in os.listdir(caminho) if f.endswith(('.csv'))
        ]
    elif tipo_arquivo == 'xlsx':
        caminhos_arquivos = [
            os.path.join(caminho, f) for f in os.listdir(caminho) if f.endswith(('.xlsx'))
        ]
    return caminhos_arquivos

## --- Carregamento dos arquivos ---

def carregamento_arquivos(lista_arquivos, nome_base):
    
    # criando uma lista vazia
    lista_arquivos_processados = []
    
    # looping para processar cada arquivo csv
    if nome_base == 'Totalbus':
        for arquivo in lista_arquivos:

            nome_arquivo = os.path.basename(arquivo)
            print(f'Sistema: Processando o arquivo "{nome_arquivo}".')

            try:
                df_temp = pd.read_csv(arquivo, sep=';', decimal=',', encoding='latin-1')
                if not df_temp.empty:
                    df_temp['Origem'] = nome_arquivo
                    df_temp['Base'] = nome_base
                    lista_arquivos_processados.append(df_temp)
            except Exception as e:
                print(f'Aviso: Erro ao processar o arquivo "{nome_arquivo}". ~~> {e}')
        
    elif nome_base == 'J3':
        for arquivo in lista_arquivos:

            nome_arquivo = os.path.basename(arquivo)
            print(f'Sistema: Processando o arquivo "{nome_arquivo}".')

            try:

                colunas_j3 = ['Origem', 'Destino', 'Serviço ', 'Assento', 'Tarifa', 'Taxas', 'Seguro',
                              'Pedágio', 'Taxa de Embarque', 'Outros', 'Nome Passageiro', 'Documento',
                              'Data Venda', 'Numero Bilhete', 'Id Transação', 'Data Viagem',
                              'Data Cancelamento', 'Agência Cancelamento', 'Estorno Tarifa',
                              'Estorno Taxa', 'Estorno Total']

                df_temp_pago = pd.read_excel(arquivo, sheet_name='Extrato Pago', skiprows=1, engine='calamine')
                if not df_temp_pago.empty:
                    df_temp_pago = df_temp_pago[colunas_j3]
                    df_temp_pago['Origem'] = nome_arquivo
                    df_temp_pago['Base'] = nome_base
                    df_temp_pago['Status'] = 'V'
                    lista_arquivos_processados.append(df_temp_pago)

                df_temp_alterados = pd.read_excel(arquivo, sheet_name='Extrato Alterados', skiprows=1, engine='calamine')
                if not df_temp_alterados.empty:
                    df_temp_alterados = df_temp_alterados[colunas_j3]
                    df_temp_alterados['Origem'] = nome_arquivo
                    df_temp_alterados['Base'] = nome_base
                    df_temp_alterados['Status'] = 'C'
                    lista_arquivos_processados.append(df_temp_alterados)

                df_temp_canc_online = pd.read_excel(arquivo, sheet_name='Extrato Cancelado Online', skiprows=1, engine='calamine')
                if not df_temp_canc_online.empty:
                    df_temp_canc_online = df_temp_canc_online[colunas_j3]
                    df_temp_canc_online['Origem'] = nome_arquivo
                    df_temp_canc_online['Base'] = nome_base
                    df_temp_canc_online['Status'] = 'C'
                    lista_arquivos_processados.append(df_temp_canc_online)

                df_temp_canc_offline = pd.read_excel(arquivo, sheet_name='Extrato Cancelado Offline', skiprows=1, engine='calamine')
                if not df_temp_canc_offline.empty:
                    df_temp_canc_offline = df_temp_canc_offline[colunas_j3]
                    df_temp_canc_offline['Origem'] = nome_arquivo
                    df_temp_canc_offline['Base'] = nome_base
                    df_temp_canc_offline['Status'] = 'E'
                    lista_arquivos_processados.append(df_temp_canc_offline)

            except Exception as e:
                print(f'Aviso: Erro ao processar o arquivo "{nome_arquivo}". ~~> {e}')

    if lista_arquivos_processados:
        try:
            lista_arquivos_processados = [df for df in lista_arquivos_processados if not df.empty]
            df_final = pd.concat(lista_arquivos_processados)
        except Exception as e:
            print(f'Aviso: Erro ao concatenar os arquivos da "lista_arquivos".')

    return df_final