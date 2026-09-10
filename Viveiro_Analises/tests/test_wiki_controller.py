# -*- coding: utf-8 -*-
import unittest
import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'modules'))
sys.path.insert(0, r'C:\Users\clocatelli\web2py')
sys.path.insert(0, r'C:\Users\clocatelli\web2py\site-packages')

import wiki_helper


class TestWikiIntegration(unittest.TestCase):

    def test_full_markdown_rendering(self):
        sample_doc = """# Procedimento Operacional Padrão - Viveiro de Mudas

> [!NOTE]
> Este documento é mantido pela equipe técnica.

## 1. Introdução

O Viveiro Municipal de São José do Rio Preto realiza a produção e distribuição de mudas nativas.

> [!TIP]
> Utilize sempre equipamentos de proteção individual (EPI).

### Tabela de Espécies

| Espécie | Nome Científico | Tempo de Germinação |
|---|---|---|
| Ipê Amarelo | Handroanthus albus | 15 a 20 dias |
| Jacarandá | Jacaranda mimosifolia | 20 a 30 dias |

### Checklist Diário
* [x] Checagem do sistema de irrigação
* [ ] Adubação dos canteiros do setor B
"""
        html = wiki_helper.render_markdown(sample_doc)
        
        # Verify callouts rendered
        self.assertIn('wiki-callout wiki-callout-note', html)
        self.assertIn('wiki-callout wiki-callout-tip', html)
        self.assertIn('Este documento é mantido pela equipe técnica.', html)
        self.assertIn('Utilize sempre equipamentos de proteção individual', html)

        # Verify Table
        self.assertIn('table table-bordered table-hover table-striped wiki-table', html)
        self.assertIn('Ipê Amarelo', html)
        self.assertIn('Handroanthus albus', html)

        # Verify Headings
        self.assertIn('Procedimento Operacional Padrão - Viveiro de Mudas', html)

        # Verify TOC extraction
        toc = wiki_helper.extract_toc(html)
        self.assertTrue(len(toc) >= 3)
        self.assertEqual(toc[0]['level'], 1)
        self.assertEqual(toc[1]['level'], 2)
        self.assertEqual(toc[2]['level'], 3)
        self.assertIn('procedimento-operacional-padrao', toc[0]['id'])

    def test_slugify_portuguese_accents(self):
        tests = [
            ("Análise de Qualidade da Água & Solo 2026", "analise-de-qualidade-da-agua-solo-2026"),
            ("Instalação / Configuração / Atualização", "instalacao-configuracao-atualizacao"),
            ("Mudas de Espécies Nativas - Guia Rápido!", "mudas-de-especies-nativas-guia-rapido"),
        ]
        for inp, expected in tests:
            self.assertEqual(wiki_helper.slugify(inp), expected)

    def test_search_snippet_and_highlight(self):
        text = "O Viveiro Municipal produz mudas nativas de qualidade com irrigação automatizada."
        query = "mudas nativas irrigação"
        highlighted = wiki_helper.highlight_search_terms(text, query)
        self.assertIn('<mark class="wiki-highlight">mudas</mark>', highlighted)
        self.assertIn('<mark class="wiki-highlight">nativas</mark>', highlighted)
        self.assertIn('<mark class="wiki-highlight">irrigação</mark>', highlighted)


if __name__ == '__main__':
    unittest.main()
