import re

patern = re.compile('([^\d]+)')

def UNMASK(num): 
    return re.sub(patern, '', num or '')


class IS_CHKBOX01:
    def __init__(self, on, off, error_message='Erro!'):
        self._on = on
        self._off = off
        self.e = error_message

    def parsed(self, value):
        return self._on if value == 'on' else self._off

    def __call__(self, value):

        if value in (None, 'on', 'off'):
            return (self.parsed(value), None)

        return (value, self.e)

class MASK_CPF(object):
    """
    Edit the a CPF code mask

    example::

        db.mytable.mycolumn.represent = lambda value, row: MASK_CPF()(value)

        >>> MASK_CPF()('12345678909')
        '123.456.789-09'
        >>> MASK_CPF()('123456797')
        '001.234.567-97'

    """

    def __init__(self):
        pass

    def __call__(self, cpf):
        if not isinstance(cpf, (list, str)):
            cpf = str(cpf)
        if isinstance(cpf, str):
            cpf = UNMASK(cpf)
            cpf = '0' * (11 - len(cpf)) + cpf
        return '{}{}{}.***.***-**'.format(*cpf)


class MASK_CNPJ(object):
    """
    Edit the a CNPJ code mask

    example::

        db.mytable.mycolumn.represent = lambda value, row: MASK_CNPJ()(value)

        >>> MASK_CNPJ()('12345678000195')
        '12.345.678/0001-95'
        >>> MASK_CNPJ()('123456000149')
        '00.123.456/0001-49'
    """

    def __init__(self):
        pass

    def __call__(self, cnpj):
        if not isinstance(cnpj, (list, str)):
            cnpj = str(cnpj)
        if isinstance(cnpj, str):
            cnpj = UNMASK(cnpj)
            cnpj = '0' * (14 - len(cnpj)) + cnpj
        return '{}{}.{}{}{}.{}{}{}/{}{}{}{}-{}{}'.format(*cnpj)


    
class IS_CPF(object):
    def __init__(self, format=True, error_message='Digite apenas os numeros!'):
        self.format = format
        self.error_message = error_message

    def __call__(self, value):

        def valida(value):

            def calcdv(numb):
                result = int()
                seq = reversed(((range(9, id_type[1], -1) * 2)[:len(numb)]))
                #return (value,'to fundo1')
                for digit, base in zip(numb, seq):
                    result += int(digit) * int(base)

                dv = result % 11
                #return (value,'to fundo1'+str(dv))
                return (dv - 10) and dv or 0

            id_type = ['CPF', -1]

            numb, xdv = value[:-2], value[-2:]

            dv1 = calcdv(numb)
            #return (value,'entrei'+str(dv1))
            dv2 = calcdv(numb + str(dv1))
            return (('%d%d' % (dv1, dv2) == xdv and True or False), id_type[0])


        try:
            cpf = str(value)
            #return(cpf,'aquiok'+str(len(cpf)==11))
            if len(cpf) >= 11:

                #return (value, 'cpf acima de 11')
                c = []
                for d in cpf:
                    if d.isdigit():
                        c.append(d)
                cl = str(''.join(c))
                #return (value, 'cpf incorreto'+str(cl))
                if len(cl) == 11:
                    if valida(cl)[0] == True:
                        return (cl, None)
                    else:
                        return (cl, 'cpf invalido')
                elif len(cl) < 11:
                    return (cl, 'cpf incompleto')
                else:
                    return (cl, 'cpf tem mais de 11 digitos')
            else:
                return (value, 'cpf deve estar no formato 000.000.000-00')
                #return(cpf,'aquiok'+str(len(cpf)==11))


        except:
            return (value, 'algum erro' + str(value))

#def formatter(self, value):
        #if value ==11:
#        formatado = value[0:3] + '.' + value[3:6] + '.' + value[6:9] + '-' + value[9:11]
        #else:
        #    formatado=value
        #formatado = value
#	return formatado '''


class IS_CPF_OR_CNPJ(object):
    def __init__(self, format=True, error_message='Digite apenas os números!'):
        self.format = format
        self.error_message = error_message

    def __call__(self, value):
        try:
            # return (value, 'cpf incorreto'+str(value))
            # return (value, 'cpf incorreto'+str(cl))
            c = []
            for d in value:
                if d.isdigit():
                    c.append(d)
            cl = str(''.join(c))
            # return (value, 'cpf incorreto'+str(cl))
            if len(cl) == 11:
                cpf = cl
                cnpj = None
            elif len(cl) == 14:
                cpf = None
                cnpj = cl
            else:
                return (value, 'Número de dígitos incorreto para CPF ou CNPJ')

            # return(cpf,'aquiok'+str(len(cpf)==11))
            if cpf:

                def valida(value):

                    def calcdv(numb):
                        result = int()
                        seq = reversed((list(range(9, id_type[1], -1)) * 2)[:len(numb)])
                        # return (value,'to fundo1')
                        for digit, base in zip(numb, seq):
                            result += int(digit) * int(base)

                        dv = result % 11
                        # return (value,'to fundo1'+str(dv))
                        return (dv-10) and dv or 0

                    id_type = ['CPF', -1]

                    numb, xdv = value[:-2], value[-2:]

                    dv1 = calcdv(numb)
                    # return (value,'entrei'+str(dv1))
                    dv2 = calcdv(numb+str(dv1))
                    return (('%d%d' % (dv1, dv2) == xdv and True or False), id_type[0])

                try:
                    cpf = str(value)
                    # return(cpf,'aquiok'+str(len(cpf)==11))
                    if len(cpf) >= 11:

                        # return (value, 'cpf acima de 11')
                        c = []
                        for d in cpf:
                            if d.isdigit():
                                c.append(d)
                        cl = str(''.join(c))
                        # return (value, 'cpf incorreto'+str(cl))
                        if len(cl) == 11:
                            if valida(cl)[0] == True:
                                return (value, None)
                            else:
                                return (value, 'cpf inválido')
                        elif len(cl) < 11:
                            return (value, 'cpf incompleto')
                        else:
                            return (value, 'cpf tem mais de 11 dígitos')
                        if cpf[3] != '.' or cpf[7] != '.' or cpf[11] != '-':
                            return (value, 'cpf deve estar no formato 000.000.000-00'+cpf[11])
                    else:
                        return (value, 'cpf deve estar no formato 000.000.000-00')
                    # return(cpf,'aquiok'+str(len(cpf)==11))
                except:
                    return (value, 'algum erro '+str(value))
            elif cnpj:

                """ Pega apenas os 12 primeiros dígitos do CNPJ e gera os 2 dígitos que faltam """
                inteiros = [int(s) for s in cnpj if s.isdigit()]     
                novoCnpj = inteiros[:12]

                prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
                while len(novoCnpj) < 14:
                    r = sum([x * y for (x, y) in zip(novoCnpj, prod)]) % 11
                    if r > 1:
                        f = 11-r
                    else:
                        f = 0
                    novoCnpj.append(f)
                    prod.insert(0, 6)
                # return(str(novoCnpj),'aquiok')
                """ Se o número gerado coincidir com o número original, é válido """
                if novoCnpj == inteiros:
                    # cnpj = ''.join(novoCnpj)

                    return (str(cnpj), None)

                else:
                    return (value, 'CNPJ não é válido')

        except:
            return (value, 'algum erro'+str(value))

    def formatter(self, value):
        # if len(value) == 11:
        #     formatado = value[0:3]+'.'+value[3:6] + \
        #         '.'+value[6:9]+'-'+value[9:11]
        # elif len(value) == 14:
        #     formatado = value[0:2]+'.'+value[2:5]+'.' + \
        #         value[5:8]+'/'+value[8:12]+'-'+value[12:14]
        # else:
        #     formatado = value
        formatado = value.replace('.', '').replace('/','').replace('-','')

        return formatado

