import workalendar.america as america
import datetime as dt
import numpy as np

cal = america.BrazilSaoPauloCity()

def quantidade_dias_uteis(ano, mes):
    mes = int(mes)
    ano = int(ano)
    dias_uteis = 0

    # Verifica se mes e ano são numeros inteiros
    if isinstance(mes, int) and isinstance(ano, int):
        for dia in range(1, 32):
            try:
                data = dt.date(ano, mes, dia)
                if cal.is_working_day(data):
                    dias_uteis += 1
            except:
                break
    return dias_uteis

def dataEhUtil(ano, mes, dia):
    data = dt.date(ano, mes, dia)
    return cal.is_working_day(data)