# -*- coding: utf-8 -*-

#=====================================================#
###     MODULO COM FUNÇOES DE PLOTAGEM DE DADOS     ###
###	     		ENTRADAS DE MATERIAIS NOS 			###
###					PONTOS DE Apoio                 ###
#=====================================================#

#==### Vantagens sobre googlechart: Python puro, simplicidade, conhecimento do codigo
#==### Vantagens sobre Tk e Qt: Interface web totalmente interoperavel, facil e rapida distribuiçao, padrao MVC pronto

#==============================================================================#
### 	Deve ser importado nos controladores de plotagem.				 	 ###
### 											 						   	 ###
### Atualmente em funcionamento a geraçao de um grafico em .png.		   	 ###
###  O retorno devera ser para uma tag <img> html 							 ###
### 																	   	 ###
### how-to em http://www.web2pyslices.com/article/show/1357/matplotlib-howto ###
#==============================================================================#

# IMPORTAÇAO DE BIBLIOTECAS
import numpy as np
import matplotlib.pyplot as plt  
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas #plota o grafico em amb externo
from matplotlib.figure import *  # plota em figura
from io import BytesIO # para transferir o output padrao do grafico para 


# Funçao do modulo gerador de graficos

def plot(title='title',xlab='x',ylab='y',mode='plot', data={}, legendgrau=0):
    fig=Figure(figsize= (7,7), )
    fig.set_facecolor('white')
    ax = fig.add_subplot(111)
    if title: ax.set_title(title)
    if xlab: ax.set_xlabel(xlab)
    if ylab: ax.set_ylabel(ylab)
    legend = []
    keys = sorted(data)
    for key in keys:
        stream = data[key]
        (x,y)=([],[])
        for point in stream:
            x.append(point[0])
            y.append(point[1])
        if mode=='bar':
            ell = ax.bar(range(len(y)), y)
            ell.set_label(x)
            ax.set_xticks(range(len(y)))
            ax.set_xticklabels(x)
            legend.append((ell,key))
        elif mode=='plot':
            ell = ax.plot(x, y)
            legend.append((ell,key))
        else:
            ell = ax.hist(y,35)
    if legend:
        ax.legend([x for (x,y) in legend], [y for (x,y) in legend]) 
    ax.tick_params(labelrotation=legendgrau,width=0.4, length=2   , labelsize=9)
    ax.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.6)
    canvas=FigureCanvas(fig)
    stream= BytesIO()
    canvas.print_png(stream)
    return stream.getvalue()
