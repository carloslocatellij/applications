# %%
'''
    "(C)" Carlos Augusto Locatelli Júnior 2022
    Este programa é um software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da GNU General Public License conforme publicada pela Free Software Foundation,
     seja a versão 3 da Licença, ou (a seu critério) qualquer versão posterior.
    Este programa é distribuído na esperança de que seja útil, mas SEM QUALQUER GARANTIA;
     Veja a Licença Pública Geral GNU para mais detalhes.
    Você deve ter recebido uma cópia da Licença Pública Geral GNU junto com este programa. Caso contrário, consulte <https://www.gnu.org/licenses/>.
'''

# %%
#Imports
import zipfile
import os
from pathlib import Path
from xml.dom.minidom import parseString
import tempfile
dir = tempfile.mkdtemp(prefix='criaodttmpd')

# %%
#if __name__ != '__main__':
#pasta = os.getcwd()
#arquivo_mod = Path(pasta, Path("modelo2022_1.odt"))

# %%
def ler_o_arq_modelo(arquivo_mod):
    with zipfile.ZipFile(arquivo_mod, 'r') as modelo:
        conteudo = modelo.read('content.xml')
    modelo.close()
    return conteudo

# %%
def pegar_campos_do_modelo(conteudo):
    
    dom = parseString(conteudo)
    vars = dom.getElementsByTagName('text:variable-set')
    return [val.childNodes[0].data for val in vars]

# %%
def preencher_conteudo(conteudo, entradas_dos_campos):
    conteudot = conteudo.decode('utf-8')
    return f'{conteudot.format(**entradas_dos_campos)}'


# %%
def cria_arquivo_novo(path_arquivo_mod, nome_do_arq='Novo_arquivo'):
    arquivo_novo = Path(path_arquivo_mod, nome_do_arq+ '.odt')
    with open(arquivo_novo , 'w') as arq:
        arq.close()
    return arquivo_novo

# %%
def transferencia_de_esqueleto_do_modelo(arquivo_mod, pasta_arq_mod, campo_p_nome):
    with zipfile.ZipFile(arquivo_mod, 'r') as zip:
        lst_arqvs = zip.infolist()
        for arq in lst_arqvs:
            if arq.filename != 'content.xml':
                zip.extract(arq, dir)
    with zipfile.ZipFile(str(pasta_arq_mod) + f'\\{campo_p_nome}.odt', 'a') as zipfinal:
        for file in Path(dir).iterdir():
            if file.is_dir():
                for root, dirs, files in os.walk(file):
                    for f in files:
                        basedir = os.path.dirname(dir) 
                        dirname = root.replace(basedir, '').replace('\\'+Path(dir).name, '')
                        tmpdir = Path(dir).name
                        if Path(f).is_dir():
                            zipfinal.write(Path(dir, f), os.path.join(dirname , f))
                        else:
                            zipfinal.write(Path(root, f), arcname=Path(dirname,f))
            else:
                zipfinal.write(file, file.name)
        
        zipfinal.close()

    return Path(zipfinal.filename)


# %%
#print(os.listdir(dir))
#transferencia_de_esqueleto_do_modelo()

# %%
def preencher_arquivo_novo(campo_p_nome, conteudo, entradas_dos_campos, arquivo_mod):
    path_arquivo_mod = arquivo_mod.parent.absolute()
    arquivo_a_ser_criado = transferencia_de_esqueleto_do_modelo(arquivo_mod, path_arquivo_mod, campo_p_nome)   



    with zipfile.ZipFile(arquivo_a_ser_criado, 'a') as zip:
        #content = zip.getinfo('content.xml')
        #with zip.open( content, 'w') as contentxml:
        zip.writestr('content.xml' ,preencher_conteudo(conteudo, entradas_dos_campos).encode())

# %%
if __name__ == '__main__':
    import tkinter as tk
    from tkinter import filedialog
    import time
    
    arquivo_mod = None

    def Janela_do_form(arquivo_mod):
        form = tk.Toplevel(root)

        conteudo = ler_o_arq_modelo(arquivo_mod)
        campos = pegar_campos_do_modelo(conteudo)

        frame = tk.Frame(
                        master=form,
                        relief=tk.RAISED,
                        borderwidth=1)
        frame.grid(column=0, row=0, columnspan=3, rowspan=2)

        campos_numerados = {k:v for v, k in enumerate(campos)}
        entradas_dos_campos = {}
        for campo, num in campos_numerados.items():
            label = tk.Label(master=form, text=f"{campo.replace('{','').replace('}','')}")
            label.grid(column=0, row=num)
            entrada_campo = f"{campo.replace('{','').replace('}','')}"
            var_entrada = tk.StringVar() 
            entradas_dos_campos[entrada_campo] = tk.Entry(master=form, textvariable=var_entrada)
            entradas_dos_campos[entrada_campo].grid(column=1, row=num)

        def pega_tudo():
            valores_de_entrada = {}
            for campo, valor in entradas_dos_campos.items():
                valores_de_entrada[campo] = valor.get()
            
            campo_p_nome = None
            for k,v in entradas_dos_campos.items():
                if k == 'proprietario':
                    campo_p_nome = v.get()
                
            
            print(campo_p_nome)
            print(valores_de_entrada)

            if campo_p_nome:
                preencher_arquivo_novo(campo_p_nome, conteudo, valores_de_entrada, arquivo_mod)
                print('Feito!')
                
        criar =tk.Button(master=form, text='Criar', command=pega_tudo )
        criar.grid(column=2, row=len(campos)+1, padx=5)

    class App:

        def __init__(self, master=None):
            self.widget0 = tk.Frame(master)
            self.widget0.pack()
            self.msg = tk.Label(self.widget0, text='Buscar arquivo')
            self.msg["font"] = ("Calibri", "9", "italic")
            self.msg.pack()
            self.btnSearch = tk.Button(self.widget0)
            self.btnSearch['text'] = 'Buscar'
            self.btnSearch['command'] = self.search
            self.btnSearch.pack()
            self.file = None

        def search(self):
            file = filedialog.askopenfilename()
            file = Path(file)
            return Janela_do_form(file)

    root = tk.Tk()
    App(root)
    root.geometry("300x150")
    root.mainloop()

else:
    pass




