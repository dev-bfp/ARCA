'''
ARCA = Algorithm for Risk and Credit Analytics

by: dev-bfp
'''
import time
import datetime
import requests
import pprint
import gspread # LIB DO GOOGLE SHEETS
import pprint
from oauth2client.service_account import ServiceAccountCredentials # LIB DE AUTENTICAÇÃO DA GOOGLE
from datetime import datetime
from Tokens import *
from SCPC_API import *
from Serasa_API import *


# Configuração credencial GoogleApis
scope = ["https://www.googleapis.com/auth/drive"]
credentials_google = ServiceAccountCredentials.from_json_keyfile_name(caminho_local_credentials, scope)
client = gspread.authorize(credentials_google)
# Endereçamento GoogleSheets
#nmSheets = "VENDAS REDFIBRA"
nmSheets = "Vendas Automaticas"
sheet = client.open(nmSheets).worksheet("Consulta de CPF")

def pp(*args):
    pprint.pp(args)
    
def telegram_send(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token2 + '/sendMessage?chat_id=' + bot_chatID2 + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    res = response.json()
    if res['ok']:
        status_msg = 'Sim'
        return f'Mensagem enviada: {status_msg}  -  Mensagem ID:',res['result']['message_id']
    else:
        return 0

def telegram_delete(id):
    if id != 0:
        send_text = 'https://api.telegram.org/bot' + bot_token2 + '/deleteMessage?chat_id=' + bot_chatID2 + '&message_id=' + str(id)
        response = requests.get(send_text)
        res = response.json()
        if res['ok']:
            status_msg = 'Sim'
            return f'Mensagem apagada: {status_msg}'
        else:
            return f'Not deleted  -  {res['description']}'


def get_info_sheets():
    row = sheet.get_all_values()
    last_row = len(row)
    array = {}
    for i in range(1,last_row):
        array2 = []
        dados_zip = dict(zip(row[0],row[i]))
        if dados_zip['Resultado SCPC'] == '':
            dados_zip['ID Linha'] = i
            array[dados_zip['CPF - Sem pontos ou traços']] = dados_zip

    #pprint.pp(array)
    return array if array else None




msg_start = telegram_send('Starting check')
dados_sheets = get_info_sheets()
if dados_sheets is None:
    print('End code')
    msg_noCPF = telegram_send('Sem CPF para consulta')
    time.sleep(2)
    telegram_delete(msg_start[1])
    telegram_delete(msg_noCPF[1])
    #exit()
else:
    for x in dados_sheets.items():
        CPF = x[0]
        solicitante = x[1]['Solicitante']
        cliente = x[1]['Nome Cliente']
        data_nascimento = x[1]['Data de Nascimento']
        id_linha = x[1]['ID Linha']
        
        msg_consult = ("*CONSULTANDO...* 🔎" + "\n" + "\n" +
                        "Solicitante: " + solicitante + "\n" +
                        "Cliente: " + cliente + "\n" +
                        "Data de Nascimento: " + data_nascimento + "\n" +
                        "CPF: " + CPF)
        print(msg_consult)
        telegram_send(msg_consult)
        msg_tele_scpc = telegram_send('🔎 Consultando SCPC...')
        dados_SCPC = SCPC_result(solicitante,CPF)
        data_nasc_SCPC = dados_SCPC['Cadastro']['SPCA-500-NASC']
        nome_cliente = dados_SCPC['Cadastro']['SPCA-500-NOME']
        restricao = dados_SCPC['Resumo Débitos']

        if restricao[0]:
            result_SCPC = '🚫🚫🚫 Com restrição 🚫🚫🚫'
            resultado = restricao[1]
        else:
            result_SCPC = '✅✅✅ Sem restrição ✅✅✅'
            resultado = restricao[1]

        sheet.update_acell('F' + str(id_linha+1), result_SCPC)
        sheet.update_acell('G' + str(id_linha+1), datetime.today().strftime('%d/%m/%Y %H:%M'))

        telegram_delete(msg_tele_scpc[1])
        msg_SCPC = ("Consulta *1* de *2* - *SCPC*" + "\n" + "\n" +
                    "Cliente: " + nome_cliente + "\n" +
                    "CPF: " + CPF + "\n" +
                    "Data de Nascimento: " + data_nasc_SCPC + "\n" +
                    "Resultado: " + result_SCPC + "\n" + "\n" +
                    resultado)
        telegram_send(msg_SCPC)

        if restricao[0] == False:
            msg_tele_serasa = telegram_send('🔎 Consultando Serasa...')
            print('Inicia Serasa')
            # inicia Serasa
            # apaga telegram
        else:
            msg_tele_serasa = telegram_send('Fim da consulta')
            
        
    

