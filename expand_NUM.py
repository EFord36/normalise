# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 16:05:33 2016

@author: Elliot
"""


def expand_NUM(n):
    """Return n as an cardinal in words."""
    ones_C = [
             "zero", "one", "two", "three", "four", "five", "six", "seven",
             "eight", "nine", "ten", "eleven", "twelve", "thirteen",
             "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
             "nineteen"
             ]

    tens_C = [
             "zero", "ten", "twenty", "thirty", "forty", "fifty", "sixty",
             "seventy", "eighty", "ninety"
             ]

    large = [
              "", "thousand", "million", "billion", "trillion", "quadrillion",
              "quintillion", "sextillion", "septillion", "octillion",
              "nonillion", "decillion", "undecillion", "duodecillion",
              "tredecillion", "quattuordecillion", "sexdecillion",
              "septendecillion", "octodecillion", "novemdecillion",
              "vigintillion"
              ]

    def subThousand(n):
        """Convert a cardinal to words for numbers less than a thousand."""
        if n <= 19:
            return ones_C[n]
        elif n <= 99:
            q, r = divmod(n, 10)
            return tens_C[q] + ("-" + subThousand(r) if r else "")
        else:
            q, r = divmod(n, 100)
            return (ones_C[q]
                    + " hundred"
                    + (" and " + subThousand(r) if r else ""))

    def splitByThousands(n):
        "Return reversed digits of n in groups of 3."""
        res = []
        while n:
            n, r = divmod(n, 1000)
            res.append(r)
        return res

    def thousandUp(n):
        """Return cardinal greater than a thousand in words."""
        list1 = []
        for i, z in enumerate(splitByThousands(n)):
            if i and z:
                list1.insert(0, subThousand(z) + " " + large[i])
            elif z:
                    list1.insert(0, subThousand(z))
        return ", ".join(list1)

    def decimal(n):
        """Returns pronounced words with n as rhs of a decimal"""
        out = ' point'
        for lt in n:
            out += ' {}'.format(ones_C[int(lt)])
        return out

    n_clean = ''
    for i in range(len(n)):
        if not i:
            if n[i].isdigit() or n[i] == '-':
                n_clean += n[i]
        else:
            if n[i].isdigit() or n[i] == '.':
                n_clean += n[i]
    if '.' in n_clean:
        dot = n_clean.find('.')
        whole, part = n_clean[:dot], n_clean[dot+1:]
        return expand_NUM(whole) + decimal(part)
    num = int(n_clean)
    if num == 0:
        return "zero"
    else:
        w = ("minus " if num < 0 else "") + thousandUp(abs(num))
        if len(n) < 4:
            return w
        else:
            if n[-3] == '0' and n[-1] != '0':
                ind = w.rfind(" ")
                return w[:ind-1] + " and" + w[ind:]
            else:
                return w
