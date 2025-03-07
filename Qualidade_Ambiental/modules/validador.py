



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