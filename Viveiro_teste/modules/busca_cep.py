from urllib import request as req
import unicodedata
import json
import re

# cep = '15075350'
# logr = req.urlopen('https://viacep.com.br/ws/'+cep+'/json/').read( )
# dic = json.loads(logr.decode('utf-8') )
# print(dic)


class Busca_CEP():
        def __init__(self, pattern, error_message='Erro!'):
            self.err = error_message
            self.pattern=pattern
            
        def __call__(self, value):
            self.value = value           
            re.sub(self.pattern, '', self.value or '')
            
            if value.isdigit() and len(value) != 8:
                return 'Mal formatado'
            elif not value.isdigit() and len(value) < 3:
                return 'Tamanho insuficiente'
            elif value.isdigit():
                logr = req.urlopen('https://viacep.com.br/ws/'+self.value+'/json/').read()
                dic = json.loads(logr.decode('utf-8'))
                return dic
            else:
                nfkd = unicodedata.normalize('NFKD', self.value)
                without_acents = ''.join([c for c in nfkd if not unicodedata.combining(c)])
                self.value = without_acents.encode('ascii', 'ignore').decode('utf-8')
                logr = req.urlopen('https://viacep.com.br/ws/SP/Sao%20Jose%20do%20Rio%20Preto/'+'+'.join(self.value.split())+'/json/').read()
                dic = json.loads(logr.decode('utf-8'))
                return dic