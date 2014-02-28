# coding=utf-8
"""
Dati relativi alla repubblica italiana.
"""

import re
from datetime import date

__author__ = 'daniele'


#Define exceptions
class RomanError(Exception): pass
class OutOfRangeError(RomanError): pass
class NotIntegerError(RomanError): pass
class InvalidRomanNumeralError(RomanError): pass


#Define digit mapping
romanNumeralMap = (('M',  1000),
                   ('CM', 900),
                   ('D',  500),
                   ('CD', 400),
                   ('C',  100),
                   ('XC', 90),
                   ('L',  50),
                   ('XL', 40),
                   ('X',  10),
                   ('IX', 9),
                   ('V',  5),
                   ('IV', 4),
                   ('I',  1))


#Define pattern to detect valid Roman numerals
romanNumeralPattern = re.compile("""
    ^                   # beginning of string
    M{0,4}              # thousands - 0 to 4 M's
    (CM|CD|D?C{0,3})    # hundreds - 900 (CM), 400 (CD), 0-300 (0 to 3 C's),
                        #            or 500-800 (D, followed by 0 to 3 C's)
    (XC|XL|L?X{0,3})    # tens - 90 (XC), 40 (XL), 0-30 (0 to 3 X's),
                        #        or 50-80 (L, followed by 0 to 3 X's)
    (IX|IV|V?I{0,3})    # ones - 9 (IX), 4 (IV), 0-3 (0 to 3 I's),
                        #        or 5-8 (V, followed by 0 to 3 I's)
    $                   # end of string
    """, re.VERBOSE)


def roman_to_int(s):
    """convert Roman numeral to integer"""
    if not s:
        raise InvalidRomanNumeralError('Input can not be blank')
    if not romanNumeralPattern.search(s):
        raise InvalidRomanNumeralError('Invalid Roman numeral: %s' % s)

    result = 0
    index = 0
    for numeral, integer in romanNumeralMap:
        while s[index:index+len(numeral)] == numeral:
            result += integer
            index += len(numeral)
    return result


class Repubblica(object):

    LEGISLATURE = {
        0: {
            'name': u"Assemblea Costituente",
            'voting_date': date(1956, 6, 2),
            'start_date': date(1946, 6, 25),
            'end_date': date(1948, 1, 31),
        },

        1: {
            'name': u"I Legislatura",
            'voting_date': date(1948, 4, 18),
            'start_date': date(1948, 5, 8),
            'end_date': date(1953, 6, 24),
        },

        2: {
            'name': u"II Legislatura",
            'voting_date':  date(1953, 6, 7),
            'start_date':  date(1953, 6, 25),
            'end_date':  date(1958, 6, 11)
        },

        3: {
            'name': u"III Legislatura",
            'voting_date':  date(1958, 5, 25),
            'start_date':  date(1958, 6, 12),
            'end_date':  date(1963, 5, 15)
        },

        4: {
            'name': u"IV Legislatura",
            'voting_date':  date(1963, 4, 28),
            'start_date':  date(1963, 5, 16),
            'end_date':  date(1968, 6, 4)
        },

        5: {
            'name': u"V Legislatura",
            'voting_date':  date(1968, 5, 19),
            'start_date':  date(1968, 6, 5),
            'end_date':  date(1972, 5, 24)
        },

        6: {
            'name': u"VI Legislatura",
            'voting_date':  date(1972, 5, 7),
            'start_date':  date(1972, 5, 25),
            'end_date':  date(1976, 7, 4)
        },

        7: {
            'name': u"VII Legislatura",
            'voting_date':  date(1976, 6, 20),
            'start_date':  date(1976, 7, 5),
            'end_date':  date(1979, 6, 19)
        },

        8: {
            'name': u"VIII Legislatura",
            'voting_date':  date(1979, 6, 3),
            'start_date':  date(1979, 6, 20),
            'end_date':  date(1983, 7, 11)
        },

        9: {
            'name': u"IX Legislatura",
            'voting_date':  date(1983, 6, 26),
            'start_date':  date(1983, 7, 12),
            'end_date':  date(1987, 7, 1)
        },

        10: {
            'name': u"X Legislatura",
            'voting_date':  date(1987, 6, 14),
            'start_date':  date(1987, 7, 2),
            'end_date':  date(1992, 4, 22)
        },

        11: {
            'name': u"XI Legislatura",
            'voting_date':  date(1992, 4, 5),
            'start_date':  date(1992, 4, 23),
            'end_date':  date(1994, 4, 14)
        },

        12: {
            'name': u"XII Legislatura",
            'voting_date':  date(1994, 3, 27),
            'start_date':  date(1994, 4, 15),
            'end_date':  date(1996, 5, 8)
        },

        13: {
            'name': u"XIII Legislatura",
            'voting_date':  date(1996, 4, 21),
            'start_date':  date(1996, 5, 9),
            'end_date':  date(2001, 5, 29)
        },

        14: {
            'name': u"XIV Legislatura",
            'voting_date':  date(2001, 5, 13),
            'start_date':  date(2001, 5, 30),
            'end_date':  date(2006, 4, 27)
        },

        15: {
            'name': u"XV Legislatura",
            'voting_date':  date(2006, 4, 9),
            'start_date':  date(2006, 4, 28),
            'end_date':  date(2008, 4, 28)
        },

        16: {
            'name': u"XVI Legislatura",
            'voting_date':  date(2008, 4, 13),
            'start_date':  date(2008, 4, 29),
            'end_date':  date(2013, 3, 14),
            'database': 'parlamento16',
        },

        17: {
            'name': u"XVII Legislatura",
            'voting_date':  date(2013, 2, 24),
            'start_date':  date(2013, 3, 15),
            'end_date': None,
            'database': 'parlamento17',
        },

    }

    @classmethod
    def get_legislature(cls):
        """
        lista di tutte le legislature inserite
        """
        return cls.LEGISLATURE

    @classmethod
    def get_legislatura(cls, key):
        """
        prova a recuperare una legislatura per dato il numero.
        per convenzione l'assemblea costituente è 0
        """
        try:
            key = int(key)
        except ValueError:
            try:
                key = roman_to_int(key)
            except InvalidRomanNumeralError:
                return None

        try:
            return Repubblica.get_legislature()[key]
        except KeyError:
            return None

    @classmethod
    def get_legislatura_per_data(cls, day):
        """
        cerca una legislatura in cui ricade il giorno fornito come parametro.
        se non esiste ritorna None
        """
        for key, lex in cls.get_legislature().items():
            if lex['start_date'] > day:
                continue
            if lex['end_date'] and lex['end_date'] < day:
                continue
            return lex
        return None

    @classmethod
    def get_legislatura_corrente(cls):
        """
        Chiama get_legislatura_per_data passandogli la data di oggi
        """
        return cls.get_legislatura_per_data(date.today())
