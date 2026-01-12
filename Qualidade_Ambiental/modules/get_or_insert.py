def buscar_ou_inserir_logradouro(endereco_obra):
    cep = endereco_obra.get('cep') or endereco_obra.get('Cep') or endereco_obra.get('CEP')
    try:
        cep = int(sub( '[^0-9]','',cep))
    except Exception as e:
        print(f'Problema com CEP:: {e}')
    logradouro = db.executesql(f"SELECT Id, Logradouro FROM Logradouros WHERE Logradouros.Cep = '{cep}' LIMIT 1 ;")
    if logradouro:
        print(f'Logradouro ::{logradouro[0][1]}:: encontrado no banco de dados!')
        return logradouro[0][0]
    else:
        bairro = endereco_obra.get('bairro') or endereco_obra.get('Bairro') or endereco_obra.get('BAIRRO') or ''
        nomebairro = sub(' - .*$', '' , bairro)
        palavra_chave_bairro = ' '.join(nomebairro.split()[ int(len(nomebairro.split())//2): int(len(nomebairro.split())/2+2) ])
        try:
            if len(palavra_chave_bairro) > 1:
                idbairro = db.executesql(f"SELECT Bairros.Id, Bairros.Bairro FROM Bairros WHERE Bairros.Bairro LIKE '%{palavra_chave_bairro}%';", as_dict= True)
            else:
                idbairro = {}
            if len(idbairro) > 0:
                idbairro, nomebairro = idbairro[0].get('Id'),  idbairro[0].get('Bairro')
                print(f'Bairro :: {nomebairro}:: encontrado no banco de dados com id [{idbairro}]!')
            else:
                print(f"Bairro {bairro} não encontrado")
                bairro_id = db.Bairros.validate_and_insert(
                    Bairro = bairro,
                    Cor = '', IdCidade= 9999
                    )

        except Exception as e:
                    session.flash = "Erro ao cadastrar Bairro"
                    print(e)
                    print('Redirecionando para form de Logradouros')
                    redirect(URL('default', 'Logradouros'))

        logradouro = endereco_obra.get('Logradouro') or endereco_obra.get('LOGRADOURO')
        elementos_de_logradouro = logradouro.split()
        if elementos_de_logradouro[0].upper().startswith('R'):
            denomin = 'RUA'
        elif elementos_de_logradouro[0].upper().startswith('AV'):
            denomin = 'AVENIDA'
        else:
            denomin = '-'
        try:
            logradouro = db.Logradouros.validate_and_insert(
                            Logradouro = ' '.join(logradouro.split()[1:] if denomin != '-' else logradouro),
                            Cep = cep,
                            Denominacao = denomin,
                            Prefixo='-',
                            IdBairro= idbairro if idbairro else bairro_id,
                            IdCidade=9999)
            print(f'Logradouro ::{logradouro}:: inserido no banco de dados!')

            db.commit()
            return logradouro.id
        except Exception as e:
                    session.flash = f"Erro ao cadastrar Logradouro: {e}"
                    print(f'erro ao inserir {logradouro} -> {e}')
                    redirect(URL('default', 'Logradouros'))