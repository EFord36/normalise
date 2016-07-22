# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 15:48:10 2016

@author: Elliot
"""
import re


def expand_NORD(n):
    """Return n as an ordinal in words."""
    ones_C = [
             "zero", "one", "two", "three", "four", "five", "six", "seven",
             "eight", "nine", "ten", "eleven", "twelve", "thirteen",
             "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
             "nineteen"
             ]

    ones_O = [
              "zero", "first", "second", "third", "fourth", "fifth", "sixth",
              "seventh", "eighth", "nineth", "tenth", "eleventh", "twelveth",
              "thirteenth", "fourteenth", "fifteenth", "sixteenth",
              "seventeenth", "eighteenth", "nineteenth"
              ]

    tens_C = [
              "zero", "ten", "twenty", "thirty", "forty", "fifty", "sixty",
              "seventy", "eighty", "ninety"
              ]

    tens_O = [
              "zero", "tenth", "twentieth", "thirtieth", "fortieth",
              "fiftieth", "sixtieth", "seventieth", "eightieth", "ninetieth"
              ]

    large = [
             "", "thousand", "million", "billion", "trillion", "quadrillion",
             "quintillion", "sextillion", "septillion", "octillion",
             "nonillion", "decillion", "undecillion", "duodecillion",
             "tredecillion", "quattuordecillion", "sexdecillion",
             "septendecillion", "octodecillion", "novemdecillion",
             "vigintillion"
             ]

    def subThousand_O(n):
        """Convert an ordinal to words for numbers less than a thousand."""
        if n <= 19:
            return ones_O[n]
        elif n <= 99:
            q, r = divmod(n, 10)
            if r == 0:
                return tens_O[q]
            else:
                return tens_C[q] + "-" + ones_O[r]
        else:
            q, r = divmod(n, 100)
            if r == 0:
                return ones_C[q] + " hundredth"
            else:
                return ones_C[q] + " hundred" + " and " + subThousand_O(r)

    def subThousand_C(n):
        """Convert a cardinal to words for numbers less than a thousand."""
        if n <= 19:
            return ones_C[n]
        elif n <= 99:
            q, r = divmod(n, 10)
            return tens_C[q] + ("-" + subThousand_C(r) if r else "")
        else:
            q, r = divmod(n, 100)
            return (ones_C[q] +
                    " hundred" +
                    (" and " + subThousand_C(r) if r else ""))

    def thousandUp(n):
        """Return cardinal greater than a thousand in words."""
        list1 = []
        for i, z in enumerate(splitByThousands(n)):
            if i and z:
                list1.insert(0, subThousand_C(z) + " " + large[i])
            elif z:
                    list1.insert(0, subThousand_C(z))
        return ", ".join(list1)

    def splitByThousands(n):
        "Return reversed digits of n in groups of 3."""
        res = []
        while n:
            n, r = divmod(n, 1000)
            res.append(r)
        return res

    n_clean = ''
    for i in range(len(n)):
        if i == 0:
            if n[i].isdigit() or n[i] == '-':
                n_clean += n[i]
        else:
            if n[i].isdigit():
                n_clean += n[i]
    num = int(n_clean)
    if num == 0:
        return "Zero"
    else:
        w = thousandUp(num)
        if len(n_clean) < 4:
            pen = subThousand_O(num)
        elif n_clean[-3] == '0':
            if n_clean[-2] == '0' and n_clean[-1] != '0':
                ind = w.rfind(" ")
                end_num = int(n_clean[-1])
                f = w[:ind - 1] + " and " + subThousand_O(end_num)
            elif n_clean[-2:] != '00':
                ind = w.rfind(" ")
                end_num = int(n_clean[-2:])
                f = w[:ind - 1] + " and " + subThousand_O(end_num)
            elif n_clean[-3:] == '000':
                ind = w.rfind(" ")
                f = w[:ind - 1]
            else:
                f = w
            while not f[-1].isalpha():
                f = f[:-1]
            pen = f
        elif n_clean[-3] != '0':
            if n_clean[-2] == '0' and n_clean[-1] != '0':
                ind = w.rfind(" ")
                end_num = int(n_clean[-1])
                f = w[:ind] + " " + subThousand_O(end_num)
            elif n_clean[-2:] != '00':
                ind = w.rfind(" ")
                end_num = int(n_clean[-2:])
                f = w[:ind] + " " + subThousand_O(end_num)
            else:
                f = w
            while not f[-1].isalpha():
                f = f[:-1]
            pen = f
        if ' , ' in pen:
            pen2 = re.sub('(?<= ), ', '', pen)
            pen2 = re.sub('  ', ' ', pen2)
            pen = pen2
        if pen[-3:] == 'ion' or pen[-3:] == 'and':
            return pen + "th"
        else:
            return pen
