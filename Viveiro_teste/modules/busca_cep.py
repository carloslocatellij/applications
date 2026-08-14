from urllib import request as req
import json
import re

# cep = '15075350'
# logr = req.urlopen('https://viacep.com.br/ws/'+cep+'/json/').read( )
# dic = json.loads(logr.decode('utf-8') )
# print(dic)


class Busca_CEP():
        def __init__(self, error_message='Erro!'):
            self.err = error_message
            self.pattern=pattern
            
        def __call__(self, value):
            self.value = value
            re.sub(self.pattern, '', self.value or '')
            logr = req.urlopen('https://viacep.com.br/ws/'+self.value+'/json/').read()
            dic = json.loads(logr.decode('utf-8'))
            return dic