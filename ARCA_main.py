'''
ARCA = Algorithm for Risk and Credit Analytics

by: dev-bfp
'''
import time
import datetime
import requests
from pprint import pp as pp
import gspread # LIB DO GOOGLE SHEETS
from oauth2client.service_account import ServiceAccountCredentials # LIB DE AUTENTICAÇÃO DA GOOGLE
from datetime import datetime
from Tokens import *
from SCPC_API import *
from Serasa_API import *

# Configuração credencial GoogleApis
scope = ["https://www.googleapis.com/auth/drive"]
#credentials_google = ServiceAccountCredentials.from_json_keyfile_name(caminho_local_credentials, scope)
credentials_google = ServiceAccountCredentials.from_json_keyfile_dict(credencial_google, scope)
client = gspread.authorize(credentials_google)
# Endereçamento GoogleSheets
#nmSheets = "VENDAS REDFIBRA"
nmSheets = "Vendas Automaticas"
sheet = client.open(nmSheets).worksheet("Consulta de CPF")
#1
    
def telegram_send(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token3 + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    res = response.json()
    if res['ok']:
        status_msg = 'Sim'
        return f'Mensagem enviada: {status_msg}  -  Mensagem ID:',res['result']['message_id'],bot_message
    else:
        return 0
    # -------------------- End --------------------


def telegram_delete(id):
    if id != 0:
        send_text = 'https://api.telegram.org/bot' + bot_token3 + '/deleteMessage?chat_id=' + bot_chatID + '&message_id=' + str(id)
        response = requests.get(send_text)
        res = response.json()
        if res['ok']:
            status_msg = 'Sim'
            return f"Mensagem apagada: {status_msg}"
        else:
            return f"Not deleted  -  {res['description']}"
    # -------------------- End --------------------


def score_rating(score):
    if score >= 800:
        return 'Excelente 🟩'
    elif 740 <= score <= 799:
        return 'Muito bom 🟩'
    elif 600 <= score <= 739:
        return 'Bom 🟨'
    elif 450 <= score <= 559:
        return 'Razoável 🟨'
    elif 300 <= score <= 449:
        return 'Ruim 🟥'
    elif score < 300:
        return 'Muito Ruim ⚠️'
    else:
        return '-'
    # -------------------- End --------------------


def get_info_sheets():
    row = sheet.get_all_values()
    last_row = len(row)
    array = {}
    for i in range(last_row-10,last_row):
        print(sheet.acell('D'+str(i+1)).value)
        dados_zip = dict(zip(row[0],row[i]))
        if dados_zip['Resultado SCPC'] == '':
            dados_zip['ID Linha'] = i
            array[dados_zip['CPF - Sem pontos ou traços']] = dados_zip

    #pprint.pp(array)
    return array if array else None
    # -------------------- End --------------------


def format_name(name):
    word_ignoradas = {'DAS', 'DOS', 'A', 'DA', 'DE', 'DO', 'E',}
    words = name.split()
    formated_name = [word.lower() if word in word_ignoradas
                     else word.capitalize()
                     for word in words]
    formated_names = " ".join(formated_name)
    return formated_names
    # -------------------- End --------------------


def telegram_files(file_path):
    '''Send files to Telegram'''
    url = f'https://api.telegram.org/bot{bot_token}/sendDocument'

    with open(file_path, 'rb') as file:
        files = {'document': file}
        data = {'chat_id': bot_chatID}
        response = requests.post(url, data=data, files=files)

    if response.status_code == 200:
        print('Arquivo enviado com sucesso!')
    else:
        print(f'Falha ao enviar arquivo. Status: {response.status_code}')
    
    # -------------------- End --------------------


def create_json(name, data):
    # Create a HTML file
    agora = datetime.today().strftime('%d-%m-%Y %H %M')
    dir_path = r"C:\Users\DEV\OneDrive\ARCA\html_consultas"
    #dir_path = r"C:\Users\brian\OneDrive\dev-bfp\GitHub\ARCA\html_consultas"
    diretory = f'{dir_path}/{name} {agora}.html'
    with open(diretory, 'w') as archive:
        archive.write(str(data))

    telegram_files(diretory)
        
    # -------------------- End --------------------

# Print timestamp no console
print('Starting',datetime.today().strftime('%d/%m/%Y %H:%M:%S'))

# Coleta id do último timestamp e deleta
id_tel = sheet.acell('L2').value
telegram_delete(id_tel)

# Insere timestamp e id do timestamp no sheets e também envia no telegram
data_hora = datetime.today().strftime('%d/%m/%Y %H:%M:%S')
last_check = telegram_send(f'Última verificação - {data_hora}')
sheet.update_acell('L1', data_hora)
sheet.update_acell('L2', last_check[1])

# Coleta informações do sheets
dados_sheets = get_info_sheets()

# Valida se há dados para consulta e inicia algorítmo
if dados_sheets is None:
    msg_noCPF = telegram_send('Sem CPF para consulta')
    end_msg = telegram_send('End check')
    telegram_delete(msg_noCPF[1])
    telegram_delete(end_msg[1])
    print(end_msg[2], datetime.today().strftime('%d/%m/%Y %H:%M:%S'))
    exit()
    
else:
    # formata dados do GSheets
    for x in dados_sheets.items():
        cpf = x[0]
        solicitante = x[1]['Solicitante']
        cliente = x[1]['Nome Cliente']
        data_nascimento = x[1]['Data de Nascimento']
        id_linha = x[1]['ID Linha']
        
        msg_consult = ("*CONSULTANDO...* 🔎" + "\n" + "\n" +
                        "Solicitante: " + solicitante + "\n" +
                        "Cliente: " + cliente + "\n" +
                        "Data de Nascimento: " + data_nascimento + "\n" +
                        "CPF: " + cpf)
        print(msg_consult)
        telegram_send(msg_consult)
        msg_tele_scpc = telegram_send('🔎 Consultando SCPC...')

        # Inicia consulta no SCPC
        dados_SCPC = SCPC_result(solicitante,cpf)
       
        # processa informações da consulta
        if dados_SCPC[0] == True: # Validação do status da consulta
            # separar def
            data_nasc_SCPC = dados_SCPC[1]['Cadastro']['SPCA-500-NASC']
            nome_cliente = format_name(dados_SCPC[1]['Cadastro']['SPCA-500-NOME'])
            restricao = dados_SCPC[1]['Resumo Débitos']
            cod_resposta = dados_SCPC[1]['Código de resposta']
            try: score = int(dados_SCPC[1]['Score'])
            except: score = dados_SCPC[1]['Score']
            try: valor_restricao = dados_SCPC[1]['Resumo Débitos'][2]['Valor_float']
            except: valor_restricao = 0

            if restricao[0] == True:
                result_SCPC = '🚫🚫🚫 Com restrição 🚫🚫🚫'
                resultado = restricao[1]
                r = resultado.split(' ')
                resumo_restri = result_SCPC + '\n' + f'{r[2]} registro(s) - valor total {r[9]}'
            else:
                result_SCPC = '✅✅✅ Sem restrição ✅✅✅'
                resultado = ''
                resumo_restri = result_SCPC
            score2 = f'{score} - {score_rating(score)}'
            sheet.update_acell('D' + str(id_linha+1), nome_cliente)
            sheet.update_acell('E' + str(id_linha+1), data_nasc_SCPC)
            sheet.update_acell('G' + str(id_linha+1), resumo_restri)
            sheet.update_acell('H' + str(id_linha+1), datetime.today().strftime('%d/%m/%Y %H:%M:%S'))
            sheet.update_acell('K' + str(id_linha+1), score2)

            telegram_delete(msg_tele_scpc[1])
            msg_SCPC = ("Consulta *1* de *2* - *SCPC*" + "\n" + "\n" +
                        "Cliente: *" + nome_cliente + "*" + "\n" +
                        "CPF: " + cpf + "\n" +
                        "Data de Nascimento: " + data_nasc_SCPC + "\n" +
                        "Código resposta: " + cod_resposta + "\n" +
                        "Score: " + score2 + "\n" +
                        "Resultado: " + result_SCPC + "\n" + "\n" +
                        resultado)
            print(msg_SCPC)
            telegram_send(msg_SCPC)

            if restricao[0] == False or valor_restricao < 500:
                msg_tele_serasa = telegram_send('🔎 Consultando Serasa...')
                print('Inicia Serasa')
                dados_Serasa = serasa_result(cpf)
                #pp(dados_Serasa)
                telegram_delete(msg_tele_serasa[1])

                if dados_Serasa[0]:
                    if dados_Serasa[1]['Status Restrição'] == 'Constam Restrições':
                        result_serasa = '🚫🚫🚫 Com restrição 🚫🚫🚫'
                        resumo_serasa = dados_Serasa[1]['Resumo']
                        rs = resumo_serasa.split(' ')
                        resumo_restri_serasa = result_serasa + '\n' + f'{rs[2]} registro(s) - valor total {rs[9]}'

                    else:
                        result_serasa = '✅✅✅ Sem restrição ✅✅✅'
                        resumo_serasa = ''
                        resumo_restri_serasa = result_serasa
                        
                    nome_cliente_serasa = format_name(dados_Serasa[1]['Nome Consultado'])
                    msg_Serasa = ("Consulta *2* de *2* - *SERASA*" + "\n" + "\n" +
                            "Cliente: *" + nome_cliente_serasa + "*" + "\n" +
                            "CPF: " + dados_Serasa[1]['CPF'] + "\n" +
                            "Protocolo: " + dados_Serasa[1]['Protocolo'] + "\n" +
                            "Resultado: " + result_serasa + "\n" + "\n" +
                            resumo_serasa)
                    
                    print(msg_Serasa)
                    telegram_send(msg_Serasa)
                    sheet.update_acell('I' + str(id_linha+1), resumo_restri_serasa)
                    sheet.update_acell('J' + str(id_linha+1), datetime.today().strftime('%d/%m/%Y %H:%M:%S'))
                    print(datetime.today().strftime('%d/%m/%Y %H:%M:%S'))
                else:
                    print('Serasa: ' + dados_Serasa[1])
                    telegram_send(dados_Serasa[1])
                    sheet.update_acell('I' + str(id_linha+1), dados_Serasa[1])
                    sheet.update_acell('J' + str(id_linha+1), datetime.today().strftime('%d/%m/%Y %H:%M:%S'))
                
                title_doc = f'Serasa {nome_cliente} {cpf}'
                dados_html = dados_Serasa[2]['respostaHtml']
                create_json(title_doc, dados_html)

                msg_tele_serasa = telegram_send('Fim da consulta')
                for x in range(5):
                    telegram_send('-')
                    
            else:
                sheet.update_acell('I' + str(id_linha+1), 'Restrição no SCPC')
                sheet.update_acell('J' + str(id_linha+1), '-')
                msg_tele_serasa = telegram_send('Fim da consulta')
                for x in range(5):
                    telegram_send('-')
                print(msg_tele_serasa[2], datetime.today().strftime('%d/%m/%Y %H:%M:%S'))
        
        elif dados_SCPC[0] == 'Erro 500':
            telegram_send('Erro de processamento - favor aguardar nova tentativa')

        else:
            telegram_send(f'SCPC: {dados_SCPC[1]}')
            print(dados_SCPC[1])
            sheet.update_acell('G' + str(id_linha+1), dados_SCPC[1])
            sheet.update_acell('H' + str(id_linha+1), datetime.today().strftime('%d/%m/%Y %H:%M:%S'))


end_msg = telegram_send('End check')
telegram_delete(end_msg[1])
print(end_msg[2], datetime.today().strftime('%d/%m/%Y %H:%M:%S'))
exit()

       
      
    

