import requests
import locale
import datetime
import json
from datetime import datetime
from pprint import pp as pp
from Tokens import keys_serasa as ks

def create_json(name, data):
    agora = datetime.now().strftime('%d-%m-%Y %H %M')
    dir_path = r"C:\Users\DEV\OneDrive\ARCA\logs_json"
    #dir_path = r"C:\Users\financeiro\OneDrive\dev-bfp\GitHub\ARCA\logs_json"
    diretory = f'{dir_path}/Serasa-{name} {agora}.json'
    with open(diretory, 'w') as archive:
        json.dump(data,archive,indent=4)

def get_info_serasa_CPF(CPF):
  url = "https://sistemas.connectsa.com.br/mercurio/ws_consulta/"
  
  headers = {
    'Cookie': 'PHPSESSID=8gas7hs4sqchs9dm10p93rmmf9; ROUTEID=.mercurio3; ROUTEID_mercurio=.mercurio3; sc_actual_lang_MERCURIO=pt_br'
  }
  
  payload = {'login': ks['login'],
            'password': ks['password'],
            'idclient': ks['idclient'],
            'apikey': ks['apikey'],
            'consulta': ks['consulta'],
            'tipodocumento': 'F',
            'documento': CPF,
            'estatica': 'N', # S = Consulta estática (simulação) | N = Consulta real
            'tiporesposta': 'A',
            'agregados': ''}
  
  response = requests.request("POST", url, headers=headers, data=payload)
  dados = response.json()
  pp(dados)
  return dados

def serasa_result(CPF):
  dados_serasa = get_info_serasa_CPF(CPF)

  array = {}
  response_msg = dados_serasa['status']['mensagem'] # mensagem 'Sucesso' para seguir
  if response_msg == 'Sucesso':
    array['Status Restrição'] = dados_serasa['status']['descricaoCodigoResposta']
    array['Protocolo'] = dados_serasa['status']['protocolo']
    array['Nome Consultado'] = dados_serasa['entrada']['nomeConsultado']
    array['CPF'] = dados_serasa['entrada']['documentoConsultado']
    array['Quantidade de Ocorrências'] = dados_serasa['resultado']['quadroResumoConsta']['quantidadeTotalOcorrencias']
    array['Registros'] = dados_serasa['resultado']['quadroResumoConsta']['registros']
    try: create_json(array['Nome Consultado'],dados_serasa)
    except: pass
    if array['Status Restrição'] == 'Constam Restrições':
      valor_total = 0
      for x in array['Registros'].items():
        valor = x[1]['valorTotal'].replace('R$ ','').replace('.','').replace(',','.')
        try: valor_total += float(valor)
        except: pass
      locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
      valor_formatado = locale.currency(valor_total, grouping=True)
      array['Valor Total'] = valor_formatado
      resumo = msg_resumo = (f"Foram encontrados {array['Quantidade de Ocorrências']} registros no valor total de {array['Valor Total']}") 
      array['Resumo'] = resumo
    
    return True, array, dados_serasa
  else:
      print('Serasa: ', dados_serasa['status']['mensagem'])
      return False, 'Serasa: ' + dados_serasa['status']['mensagem']


if __name__ == "__main__":
  dados = serasa_result("12345678910")
  print(dados)