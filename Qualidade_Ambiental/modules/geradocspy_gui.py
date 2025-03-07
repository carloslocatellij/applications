#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================#
#---          Geradocs          ---#
#--- AUTOMATIZADOR de DOCUMENTOS --#
#---     Interface Grafica      ---#
#==================================#

# %%
'''
    "(C)" Carlos Augusto Locatelli Júnior 2022
    Este programa é um software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da GNU General Public License conforme publicada pela Free Software Foundation.
    Este programa é distribuído na esperança de que seja útil, mas SEM QUALQUER GARANTIA; Consulte <https://www.gnu.org/licenses/>.
'''

from geradocspy import ler_o_arq_modelo, pegar_campos_do_modelo, preencher_arquivo_novo


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import filedialog
    
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