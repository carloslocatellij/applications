import decimal

def analise_de_residuos_projedatos(pgr=None):
    if not pgr:
        return('Não foi passado um PGR válido')

    obra = db.Pgrcc(db.Pgrcc.id == int(pgr)).idobra
    area = db.Obras(db.Obras.Id == obra).AreaConstrExecutar
    INDICE_MAX_GERACAO = decimal.Decimal(0.12)
    INDICE_MIN_GERACAO = decimal.Decimal(0.05)
    PERCENTIL_RESIDUO_A = decimal.Decimal(0.8)
    PERCENTIL_RESIDUO_B = decimal.Decimal(0.2)
    PERCENTIL_RESIDUO_D = decimal.Decimal(0.006)

    def GERACAO_MAX_A():
        return area * INDICE_MAX_GERACAO * PERCENTIL_RESIDUO_A

    def GERACAO_MIN_A():
        return area * INDICE_MIN_GERACAO * PERCENTIL_RESIDUO_A

    def GERACAO_MAX_B():
        return area * INDICE_MAX_GERACAO * PERCENTIL_RESIDUO_B

    def GERACAO_MIN_B():
        return area * INDICE_MIN_GERACAO * PERCENTIL_RESIDUO_B

    def GERACAO_MAX_D():
        return area * INDICE_MAX_GERACAO * PERCENTIL_RESIDUO_D
    analise_res = {}

    cls_a = db.Pgrcc(db.Pgrcc.id == int(pgr)).cls_a if pgr else None
    cls_b = db.Pgrcc(db.Pgrcc.id == int(pgr)).cls_b if pgr else None
    cls_d = db.Pgrcc(db.Pgrcc.id == int(pgr)).cls_d if pgr else None

    classes = [cls_a, cls_b, cls_d]
    analise = dict(MAX_A=GERACAO_MAX_A(), MIN_A=GERACAO_MIN_A(), MAX_B=GERACAO_MAX_B(), MIN_B=GERACAO_MIN_B(), MAX_D=GERACAO_MAX_D())
    res = ['A','B', 'D']
    clsss = [('MAX_A','MIN_A'), ('MAX_B','MIN_B'), ('MAX_D','MAX_D')]
    for r in range(len(res)):
        if res[r] == 'D':
            if classes[r] > analise[ clsss[r][0]]:
                analise_res[res[r]] = 'ACIMA'
            else:
                analise_res[res[r]] = 'OK'
        elif classes[r] > analise[ clsss[r][0] ]:
             analise_res[res[r]] = 'ACIMA'

        elif classes[r] < analise[clsss[r][1]]:
            analise_res[res[r]] = 'ABAIXO'
        else:
            analise_res[res[r]] = 'OK'



    return dict(MAX_A=GERACAO_MAX_A(), MIN_A=GERACAO_MIN_A(), MAX_B=GERACAO_MAX_B(), MIN_B=GERACAO_MIN_B(), MAX_D=GERACAO_MAX_D(), analise_res=analise_res)
