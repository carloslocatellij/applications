# -*- coding: utf-8 -*-
import unittest
import sys
import os

# Add paths for testing
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'modules'))
sys.path.insert(0, r'C:\Users\clocatelli\web2py')
sys.path.insert(0, r'C:\Users\clocatelli\web2py\site-packages')

from wiki_helper import (
    slugify,
    estimate_reading_time,
    generate_excerpt,
    process_callouts,
    render_markdown,
    extract_toc,
    highlight_search_terms,
    can_read_page,
    can_edit_page
)


class DummyUser:
    def __init__(self, uid, email="user@example.com"):
        self.id = uid
        self.email = email


class DummyPage:
    def __init__(self, created_by=1, can_read=None, can_edit=None):
        self.created_by = created_by
        self.can_read = can_read or ["everybody"]
        self.can_edit = can_edit or ["everybody"]


class TestWikiHelper(unittest.TestCase):

    def test_slugify(self):
        self.assertEqual(slugify("Olá Mundo!"), "ola-mundo")
        self.assertEqual(slugify("Guia de Instalação & Configuração: Viveiro 2026"), "guia-de-instalacao-configuracao-viveiro-2026")
        self.assertEqual(slugify("  Espaços   Múltiplos  "), "espacos-multiplos")
        self.assertEqual(slugify(""), "")

    def test_estimate_reading_time(self):
        short_text = "Esta é uma página de exemplo com poucas palavras."
        self.assertEqual(estimate_reading_time(short_text), "1 min de leitura")

        long_text = "palavra " * 450
        self.assertEqual(estimate_reading_time(long_text), "2 min de leitura")

    def test_generate_excerpt(self):
        md = "# Título Principal\n\nEste é um **parágrafo** introdutório com [um link](https://exemplo.com) e `código`."
        excerpt = generate_excerpt(md, max_chars=100)
        self.assertNotIn("#", excerpt)
        self.assertNotIn("**", excerpt)
        self.assertIn("Este é um parágrafo introdutório", excerpt)

    def test_process_callouts(self):
        text = "> [!NOTE]\n> Esta é uma nota importante."
        processed = process_callouts(text)
        self.assertIn("wiki-callout-note", processed)
        self.assertIn("Esta é uma nota importante.", processed)

        text_tip = "> [!TIP]\n> Dica de ouro para usuários."
        processed_tip = process_callouts(text_tip)
        self.assertIn("wiki-callout-tip", processed_tip)

    def test_render_markdown(self):
        md = "# Meu Título\n\nTexto com **negrito** e [link](https://test.com).\n\n| A | B |\n|---|---|\n| 1 | 2 |"
        html = render_markdown(md)
        self.assertIn("<h1", html)
        self.assertIn("<strong>negrito</strong>", html)
        self.assertIn("wiki-table", html)

    def test_extract_toc(self):
        html = '<h1 id="intro">Introdução</h1><p>Texto</p><h2 id="config">Configuração</h2><p>Mais texto</p>'
        toc = extract_toc(html)
        self.assertEqual(len(toc), 2)
        self.assertEqual(toc[0]["level"], 1)
        self.assertEqual(toc[0]["id"], "intro")
        self.assertEqual(toc[0]["title"], "Introdução")
        self.assertEqual(toc[1]["level"], 2)
        self.assertEqual(toc[1]["id"], "config")
        self.assertEqual(toc[1]["title"], "Configuração")

    def test_highlight_search_terms(self):
        text = "O sistema Viveiro permite realizar análises completas."
        highlighted = highlight_search_terms(text, "Viveiro análises")
        self.assertIn('<mark class="wiki-highlight">Viveiro</mark>', highlighted)
        self.assertIn('<mark class="wiki-highlight">análises</mark>', highlighted)

    def test_permissions(self):
        user_author = DummyUser(1)
        user_other = DummyUser(2)
        user_admin = DummyUser(3)

        # Public page
        public_page = DummyPage(created_by=1, can_read=["everybody"], can_edit=["everybody"])
        self.assertTrue(can_read_page(public_page, None))
        self.assertTrue(can_read_page(public_page, user_other))
        self.assertTrue(can_edit_page(public_page, user_author))
        self.assertTrue(can_edit_page(public_page, user_other))

        # Restricted page
        restricted_page = DummyPage(created_by=1, can_read=["analistas"], can_edit=["analistas"])
        self.assertFalse(can_read_page(restricted_page, None))
        self.assertTrue(can_read_page(restricted_page, user_author))  # Author can read
        self.assertFalse(can_read_page(restricted_page, user_other, user_groups=["visitantes"]))
        self.assertTrue(can_read_page(restricted_page, user_other, user_groups=["analistas"]))
        self.assertTrue(can_read_page(restricted_page, user_admin, user_groups=["admin"]))


if __name__ == '__main__':
    unittest.main()
