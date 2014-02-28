# coding=utf-8
"""
LEX è un modulo che costituisce una base di dati per le legislature italiane.
Deve essere aggiornato manualmente ogni volta che inizia un nuova legislatura.
"""
from collections import namedtuple
from datetime import date

__author__ = 'daniele'

Lex = namedtuple('Legislatura', ['number', 'name', 'voting_date', 'start_date', 'end_date', 'database'])

LEGISLATURE = [
    Lex(0, 'Assemblea Costituente', date(1946, 6, 2),   date(1946, 6, 25),  date(1948, 1, 31),  None),
    Lex(1, 'I Legislatura',         date(1948, 4, 18),  date(1948, 5, 8),   date(1953, 6, 24),  None),
    Lex(2, 'II Legislatura',        date(1953, 6, 7),   date(1953, 6, 25),  date(1958, 6, 11),  None),
    Lex(3, 'III Legislatura',       date(1958, 5, 25),  date(1958, 6, 12),  date(1963, 5, 15),  None),
    Lex(4, 'IV Legislatura',        date(1963, 4, 28),  date(1963, 5, 16),  date(1968, 6, 4),   None),
    Lex(5, 'V Legislatura',         date(1968, 5, 19),  date(1968, 6, 5),   date(1972, 5, 24),  None),
    Lex(6, 'VI Legislatura',        date(1972, 5, 7),   date(1972, 5, 25),  date(1976, 7, 4),   None),
    Lex(7, 'VII Legislatura',       date(1976, 6, 20),  date(1976, 7, 5),   date(1979, 6, 19),  None),
    Lex(8, 'VIII Legislatura',      date(1979, 6, 3),   date(1979, 6, 20),  date(1983, 7, 11),  None),
    Lex(9, 'IX Legislatura',        date(1983, 6, 26),  date(1983, 7, 12),  date(1987, 7, 1),   None),
    Lex(10, 'X Legislatura',        date(1987, 6, 14),  date(1987, 7, 2),   date(1992, 4, 22),  None),
    Lex(11, 'XI Legislatura',       date(1992, 4, 5),   date(1992, 4, 23),  date(1994, 4, 14),  None),
    Lex(12, 'XII Legislatura',      date(1994, 3, 27),  date(1994, 4, 15),  date(1996, 5, 8),   None),
    Lex(13, 'XIII Legislatura',     date(1996, 4, 21),  date(1996, 5, 9),   date(2001, 5, 29),  None),
    Lex(14, 'XIV Legislatura',      date(2001, 5, 13),  date(2001, 5, 30),  date(2006, 4, 27),  None),
    Lex(15, 'XV Legislatura',       date(2006, 4, 9),   date(2006, 4, 28),  date(2008, 4, 28),  None),
    Lex(16, 'XVI Legislatura',      date(2008, 4, 13),  date(2008, 4, 29),  date(2013, 3, 14),  'parlamento16'),
    Lex(17, 'XVII Legislatura',     date(2013, 2, 24),  date(2013, 3, 15),  None,               'parlamento17')
]


def get_legislature():
    """
    This method returns all legislature instances.
    """
    return LEGISLATURE


def get_legislatura(number=None):
    """
    prova a recuperare una legislatura per dato il numero.
    per convenzione l'assemblea costituente è 0
    """
    if number is None:
        number = -1
    return get_legislature()[int(number)]


def get_legislatura_per_data(day):
    """
    cerca una legislatura in cui ricade il giorno fornito come parametro.
    se non esiste ritorna None
    """
    for lex in get_legislature():
        if lex['start_date'] > day:
            continue
        if lex['end_date'] and lex['end_date'] < day:
            continue
        return lex
    return None