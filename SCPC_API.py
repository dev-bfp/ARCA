import requests
import json
import pprint
from Tokens import keys_scpc as kc

def pp(*args):
    pprint.pp(args)


def get_info_SCPC_CPF(solicitante,cpf):
    url = "https://api.scpc.inf.br/api/consulta/rest"

    headers = {
        "Content-Type": "application/json",
    }
    body = {
        "SPCA-XML": {
            "VERSAO": "20220225",
            "SOLICITACAO": {
                "S-REGIONAL": kc['REGIONAL'],
                "S-CODIGO": kc['CODIGO'],
                "S-SENHA": kc['SENHA'],
                "S-CONSULTA": kc['CONSULTA'],
                "S-SOLICITANTE": solicitante,
                "S-CPF": cpf,
            }
        }
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(body))
    
    if response.status_code == 200:
        print('Consulta realizada')
        return True, response.json()
    else:
        print(f"Erro na consulta: {response.status_code}")
        print(response.text)
        mensagem_erro = response.json()['SPCA-XML']['RESPOSTA']['RESPOSTA-RETORNO']['MENSAGEM-RESPOSTA']
        return None, mensagem_erro
    # --------------------------- Fim ---------------------------


def SCPC_result(solicitante,cpf):
    dados_cpf = get_info_SCPC_CPF(solicitante,cpf)
    if dados_cpf[0]:
        array = {}
        array['Código de resposta'] = dados_cpf[1]['SPCA-XML']['RESPOSTA']['NUMERO-RESPOSTA']
        matriz = dados_cpf[1]['SPCA-XML']['RESPOSTA']['REGISTRO-ACSP-SPCA']
        array['Cadastro'] = matriz['SPCA-500-IDENTIFICA']
        dt_nas = str(array['Cadastro']['SPCA-500-NASC'])
        array['Cadastro']['SPCA-500-NASC'] = f'{dt_nas[6:8]}/{dt_nas[4:6]}/{dt_nas[0:4]}'
        
        score = matriz['SPCA-601-SCORE-CRED']
        array['Score'] = score[0]['SPCA-601-SCORE']
        try: array['Dados adicionais'] = matriz['SPCA-501-LOCALIZACAO']
        except: array['Dados adicionais'] = "Sem informações adicionais"
        try:
            dados_debitos = {}
            resumo_debitos = dados_cpf[1]['SPCA-XML']['RESPOSTA']['REGISTRO-ACSP-SPCA']['SPCA-108-DEBITO']['SPCA-108-RESUMO']
            dados_debitos['Total de Registros'] = resumo_debitos['SPCA-108-TOTAL']['SPCA-108-DEVEDOR']
            dados_debitos['Valor Total'] = resumo_debitos['SPCA-108-TOTAL']['SPCA-108-VALOR']
            
            dpd = str(resumo_debitos['SPCA-108-PRIMEIRO-DEB']['SPCA-108-P-DATA']) #Data do primeiro débito
            dados_debitos['Data do Primeiro Débito'] = f'{dpd[6:8]}/{dpd[4:6]}/{dpd[0:4]}' # Data do primeiro débito formatado
            dud = str(resumo_debitos['SPCA-108-MAIOR-DEB']['SPCA-108-M-DATA']) # Data do último débito
            dados_debitos['Data do Último Débito'] = f'{dud[6:8]}/{dud[4:6]}/{dud[0:4]}' # Data do último débito formatado
            
            msg_resumo = (f"Foram encontrados {dados_debitos['Total de Registros']} registros no valor total de {dados_debitos['Valor Total']}" + "\n" +
                          f"Primeira negativação em {dados_debitos['Data do Primeiro Débito']} e última negativação em {dados_debitos['Data do Último Débito']}")                       

            array['Resumo Débitos'] = True,msg_resumo, dados_debitos
            
        except: array['Resumo Débitos'] = False,'Sem restrição'

        return array
    else:
        return dados_cpf[1]


