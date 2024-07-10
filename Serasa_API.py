import requests
import pprint
from Tokens import keys_serasa as ks

def pp(*args):
  return pprint.pp(args)

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
            'estatica': 'S', # S = Consulta estática (simulação) | N = Consulta real
            'tiporesposta': 'J',
            'agregados': ''}
  
  response = requests.request("POST", url, headers=headers, data=payload)
  dados = response.json()
  return dados

def serasa_result(CPF):
  dados_serasa = get_info_serasa_CPF(CPF)
  response_msg = dados_serasa['status']['mensagem'] # mensagem 'Sucesso' para seguir
  if response_msg == 'Sucesso':
    status_restricao = dados_serasa['status']['descricaoCodigoResposta']
    protocolo = dados_serasa['status']['protocolo']
    nome_consultado = dados_serasa['entrada']['nomeConsultado']
    qtd_ocorrencias = dados_serasa['resultado']['quadroResumoConsta']['quantidadeTotalOcorrencias']
    registros = dados_serasa['resultado']['quadroResumoConsta']['registros']


  return True

  else:
    return False, dados_serasa['status']['mensagem']
  

