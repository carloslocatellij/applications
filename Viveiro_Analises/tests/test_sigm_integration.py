# -*- coding: utf-8 -*-
import unittest
import sys
import os
import re
from pathlib import Path
path_user = Path.home()

# Add paths for web2py imports
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'modules'))
sys.path.insert(0, f'{path_user}\web2py')
sys.path.insert(0, f'{path_user}\web2py\site-packages')

from gluon.utils import secure_dumps, secure_loads


def normalizar_logradouro_test(logr):
    if not logr:
        return ""
    logr = str(logr).strip()
    padroes = [
        r'^(rua|r\.)\s+(rua|r\.)\s+',
        r'^(avenida|av\.|av)\s+(avenida|av\.|av)\s+',
        r'^(alameda|al\.)\s+(alameda|al\.)\s+',
        r'^(travessa|tv\.)\s+(travessa|tv\.)\s+',
        r'^(praca|praça|pc\.)\s+(praca|praça|pc\.)\s+',
        r'^(rodovia|rod\.)\s+(rodovia|rod\.)\s+',
    ]
    for padrao in padroes:
        m = re.match(padrao, logr, re.IGNORECASE)
        if m:
            primeiro = m.group(1).capitalize()
            logr = re.sub(padrao, f"{primeiro} ", logr, count=1, flags=re.IGNORECASE)
            break
    return logr.upper()


class TestSigmIntegration(unittest.TestCase):

    def test_normalizar_logradouro_duplicado(self):
        # Exemplo real fornecido pelo usuário
        entrada = "rua Rua Aparecido Balbino Pereira entre as ruas Monteiro Lobato"
        esperado = "RUA APARECIDO BALBINO PEREIRA ENTRE AS RUAS MONTEIRO LOBATO"
        self.assertEqual(normalizar_logradouro_test(entrada), esperado)

    def test_normalizar_logradouro_avenida(self):
        entrada = "avenida av. Alberto Andaló"
        esperado = "AVENIDA ALBERTO ANDALÓ"
        self.assertEqual(normalizar_logradouro_test(entrada), esperado)

    def test_normalizar_logradouro_sem_duplicidade(self):
        entrada = "Rua Bernardino de Campos"
        esperado = "RUA BERNARDINO DE CAMPOS"
        self.assertEqual(normalizar_logradouro_test(entrada), esperado)

    def test_normalizar_logradouro_vazio_ou_nulo(self):
        self.assertEqual(normalizar_logradouro_test(None), "")
        self.assertEqual(normalizar_logradouro_test(""), "")

    def test_criptografia_credenciais_sessao(self):
        key = "chave_de_teste_segura_12345"
        payload = {"user": "fiscal.meioambiente", "pass": "SenhaForte#2026"}
        
        token = secure_dumps(payload, key)
        self.assertTrue(isinstance(token, (str, bytes)))
        
        token_str = token.decode("utf-8") if isinstance(token, bytes) else str(token)
        decrypted = secure_loads(token_str, key)
        
        self.assertIsInstance(decrypted, dict)
        self.assertEqual(decrypted["user"], "fiscal.meioambiente")
        self.assertEqual(decrypted["pass"], "SenhaForte#2026")

    def test_criptografia_credenciais_invalida(self):
        key = "chave_de_teste_segura_12345"
        payload = {"user": "fiscal.meioambiente", "pass": "SenhaForte#2026"}
        token = secure_dumps(payload, key)
        token_str = token.decode("utf-8") if isinstance(token, bytes) else str(token)

        # Tentativa com chave errada deve retornar None por falha na assinatura HMAC
        resultado = secure_loads(token_str, "chave_errada_99999")
        self.assertIsNone(resultado)

    def test_mapeamento_regras_negocio_poda(self):
        dados_sigm = {
            "protocolo": "2026000344344",
            "data_abertura": "11/09/2026",
            "solicitante": "bispado de rio preto",
            "dados_descricao": {
                "logradouro": "rua Rua Aparecido Balbino Pereira entre as ruas Monteiro Lobato",
                "cep": None,
                "número_da_casa": None,
                "quantidade_de_árvores": None,
                "tipo_de_solicitação": "que seja feita a poda"
            }
        }

        solicitante = str(dados_sigm.get("solicitante") or "").strip().upper()
        self.assertEqual(solicitante, "BISPADO DE RIO PRETO")

        dados_desc = dados_sigm.get("dados_descricao") or {}
        num_casa = dados_desc.get("número_da_casa")
        numero = "" if num_casa is None else str(num_casa).strip()
        self.assertEqual(numero, "")

        tipo_solic = str(dados_desc.get("tipo_de_solicitação") or "").lower()
        is_poda = "poda" in tipo_solic
        self.assertTrue(is_poda)

        qtd_arvores = dados_desc.get("quantidade_de_árvores")
        quantidade = "" if qtd_arvores is None else str(qtd_arvores).strip()
        self.assertEqual(quantidade, "")

    def test_mapeamento_regras_negocio_supressao(self):
        dados_sigm = {
            "protocolo": "2026000999888",
            "data_abertura": "15/09/2026",
            "solicitante": "JOÃO DA SILVA",
            "dados_descricao": {
                "logradouro": "Rua XV de Novembro",
                "cep": "15010-000",
                "número_da_casa": "1234",
                "quantidade_de_árvores": 2,
                "tipo_de_solicitação": "Solicito a remoção / supressão de árvore seca"
            }
        }

        dados_desc = dados_sigm.get("dados_descricao") or {}
        num_casa = dados_desc.get("número_da_casa")
        numero = "" if num_casa is None else str(num_casa).strip()
        self.assertEqual(numero, "1234")

        tipo_solic = str(dados_desc.get("tipo_de_solicitação") or "").lower()
        is_poda = "poda" in tipo_solic
        self.assertFalse(is_poda)

        qtd_arvores = dados_desc.get("quantidade_de_árvores")
        quantidade = "" if qtd_arvores is None else str(qtd_arvores).strip()
        self.assertEqual(quantidade, "2")


if __name__ == "__main__":
    unittest.main()
