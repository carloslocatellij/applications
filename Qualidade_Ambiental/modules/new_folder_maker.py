import asyncio
import re
from pathlib import Path
#import aiofiles
import aiofiles.os

async def pega_numeracao_da_pasta(caminho_da_pasta: object = 'pathlib.WindowsPath'):

    sub_pastas = []
    pattern = r'\d+_'
    reg = re.compile(pattern)
    async for dir in aiofiles.os.scandir(caminho_da_pasta):
        if Path(caminho_da_pasta, dir[0]).is_dir() and reg.search(str(dir[0])) and reg.match(str(dir[0].split('\\')[-1])):
            await sub_pastas.append(int(reg.match(str(dir[0].split('\\')[-1])).group()[:-1]))
    return str(max(sub_pastas or 0)+1)
    

async def pasta_existe(caminho_da_pasta, protocolo):

    async for entry in aiofiles.os.scandir(caminho_da_pasta):  # Aguardando o resultado de scandir()
        if entry.is_dir() and protocolo in entry.name:
            next(f"para o protoc. {protocolo} em {entry.name}")
    yield False


async def criar_pasta_compartilhada(dados, caminho_da_pasta, numerar=False):
    gerador = dados.get('nome') or dados.get('Nome') or dados.get('dados_gerador').get('Nome') or \
     dados.get('dados_gerador').get('nome') or 'Desconhecido'
    protocolo = dados.get('protocolo') or dados.get('Protocolo')

    pasta_existente = await pasta_existe(caminho_da_pasta, protocolo)

    if __name__ == "__main__":
        op_criar_pasta = str(input('Deseja criar a pasta: Digite(s/n): '))
        if op_criar_pasta == 's':
            if pasta_existente:
                print(f'Já existe a pasta {pasta_existente}')
            else:
                try:
                    if numerar:
                        await aiofiles.os.mkdir(r'F:\{}\{}_{}_{}'.format(caminho_da_pasta, await pega_numeracao_da_pasta(caminho_da_pasta),
                                                        str(gerador.replace('/','-')).upper(), protocolo))
                    else:
                        await aiofiles.os.mkdir(r'F:\{}\{}_{}'.format(caminho_da_pasta,str(gerador.replace('/','-')).upper(), protocolo))

                    print('Pasta criada {}_{} '.format(str(gerador).upper(), protocolo))
                except Exception as e:
                    print (f'Ocorreu um erro ao criar a pasta:: {e}')
    else:
        if pasta_existente:
            print (f'Já existe a pasta {await pasta_existente}')
            return 'Já existe pasta para este protocolo!'
        else:
            try:
                if numerar:
                    await aiofiles.os.mkdir(r'{}\{}_{}_{}'.format(str(caminho_da_pasta), str(await pega_numeracao_da_pasta(str(caminho_da_pasta))),
                                                str(gerador.replace('/','-')).upper(), protocolo))
                else:
                    await aiofiles.os.mkdir(r'{}\{}_{}'.format(str(caminho_da_pasta),str(gerador.replace('/','-')).upper(), protocolo))
                print('Pasta criada {}_{} '.format(str(gerador).upper(), protocolo))

            except Exception as e:
                    print (f'Ocorreu um erro ao criar a pasta:: {e}')
                    return e

# Example usage
async def main():
    nome = input("Nome: ")
    protocolo = input("Protocolo: ")
    dados = {'nome': nome, 'protocolo': protocolo}
    caminho_da_pasta = './Teste/'
    await criar_pasta_compartilhada(dados, caminho_da_pasta, numerar=True)

if __name__ == "__main__":
    asyncio.run(main())