import requests
import pprint
import locale
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
            'estatica': 'N', # S = Consulta estática (simulação) | N = Consulta real
            'tiporesposta': 'J',
            'agregados': ''}
  
  response = requests.request("POST", url, headers=headers, data=payload)
  dados = response.json()
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
    
    return True, array
  else:
      return False, 'Serasa: ' + dados_serasa['status']['mensagem']
