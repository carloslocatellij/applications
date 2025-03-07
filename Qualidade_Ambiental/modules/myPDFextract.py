#!/usr/bin/python
# -*- coding: utf-8 -*-
#==================================#
#---          Extrator          ---#
#---       de DOCUMENTOS        ---#
#---           PDF              ---#
#==================================#

from io import StringIO
from typing import List, Generator
from pdfminer.pdfminer.converter import TextConverter
from pdfminer.pdfminer.pdfpage import PDFPage
from pdfminer.pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter


def extract_text_by_page(pdf_path: str) -> Generator[str, None, None]:
    ''' A função extract_text_by_page é uma função Python que utiliza a biblioteca pdfminer para extrair o texto de um
    arquivo PDF página por página. Ele cria um objeto PDFResourceManager para gerenciar os recursos compartilhados
    entre as páginas do PDF, um objeto StringIO para armazenar o texto extraído de cada página e um objeto TextConverter
    que converte o conteúdo da página em texto. A função itera sobre cada página do documento PDF usando o método get_pages
    da classe PDFPage e retorna um gerador contendo o texto extraído de cada página.

    '''
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
                resource_manager = PDFResourceManager()
                fake_file_handle = StringIO()
                converter = TextConverter(resource_manager,
                                      fake_file_handle)
                page_interpreter = PDFPageInterpreter(resource_manager,
                                                  converter)
                page_interpreter.process_page(page)
                text = fake_file_handle.getvalue()
                yield text
                converter.close()
        fake_file_handle.close()

def extract_text(pdf_path: str) -> List[str]:
    """Extrai o texto de um arquivo PDF (Argumento: pdf_path: O caminho para o arquivo PDF.)
       Retorna uma lista de strings, uma string para cada página do arquivo PDF.
     Levanta:
         FileNotFoundError: se o arquivo PDF especificado não existir.

        >>>extract_text('exeplo.pdf')

    """
    # Check if the file exists
    try:
        with open(pdf_path, 'rb'):
            pass
    except FileNotFoundError:
        raise

    # Extract text from each page and append it to a list
    pages = []
    for page in extract_text_by_page(pdf_path):
        pages.append(page)

    return pages
