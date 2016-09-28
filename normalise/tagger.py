# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import sys
import re
import pickle
from io import open

from normalise.detect import mod_path
from normalise.data.measurements import meas_dict

with open('{}/data/NSW_dict.pickle'.format(mod_path), mode='rb') as file:
    NSWs = pickle.load(file)

curr_list = ['£', '$', '€']
AlPHA_dict, NUMB_dict, MISC_dict = {}, {}, {}


def tagify(dic, verbose=True):
    """Return dictionary with added tag.

    dic: dictionary entry where key is index of word in orig text, value
         is the nsw
    The dictionary returned has the same keys with the values being a tuple
    with nsw and its assigned tag.
    """
    out = {}
    for ind, it in dic.items():
        if verbose:
            sys.stdout.write("\r{} of {} tagged".format(len(out), len(dic)))
            sys.stdout.flush()
        if len(it) > 100:
            out.update({ind: (it, 'MISC')})
        if is_digbased(it):
            out.update({ind: (it, 'NUMB')})
        elif (only_alpha(it) and
              (not mixedcase_pattern.match(it) or
               len(it) <= 3 or (it[-1] == 's' and not
               mixedcase_pattern.match(it[:-1])))):
                    out.update({ind: (it, 'ALPHA')})
        elif it in meas_dict:
            out.update({ind: (it, 'ALPHA')})
        elif is_url(it) or hashtag_pattern.match(it):
            out.update({ind: (it, 'MISC')})
        elif looks_splitty(it):
            out.update({ind: (it, 'SPLT')})
        else:
            out.update({ind: (it, 'MISC')})
    if verbose:
        sys.stdout.write("\r{} of {} tagged".format(len(out), len(dic)))
        sys.stdout.flush()
        print("\n")
    return out


def looks_splitty(w):
    """Return 'True' if w looks like it should be split."""
    if has_digit(w) and has_alpha(w):
        return True
    elif hyphen_pattern.match(w):
        return True
    elif (only_alpha(w) and not w[:2] == 'Mc'and not w[:3] == 'Mac' and
          mixedcase_pattern.match(w)):
        return True
    elif emph_pattern.match(w):
        return True
    else:
        return False


def is_digbased(w):
    """Return 'True' if w is based around digits."""
    if len(w) == 0:
        return False
    if w[-2:] in ["'s", "s'"]:
        return is_digbased(w[:-2])
    elif w[-3:] in ecurr_dict:
        return is_digbased(w[:-3])
    elif w[-2:] in ['st', 'nd', 'rd', 'th']:
        return is_digbased(w[:-2])
    elif w[-1].lower() in end_dict or w[-1] == 's':
        return is_digbased(w[:-1])
    elif w[0] in curr_list:
        return is_digbased(w[1:])
    elif w[0] == "'" and w[1:].isdigit():
        return True
    elif w[0] == '+':
        return is_digbased(w[1:])
    elif w[-1] == '+':
        return is_digbased(w[:-1])
    for lt in w:
        if not lt.isdigit() and lt not in ['/', '.', ',',
                                           '-', '–', '%',
                                           ':', "'", '"',
                                           "°", "—", "′"]:
            return False
    else:
        return True and has_digit(w)


def only_alpha(w):
    """Return 'True' if w is based on alphabetic characters."""
    if len(w) == 0:
        return False
    if w[-2:] in ["'s", "s'"]:
        return only_alpha(w[:-2])
    if is_acr(w):
        return True
    if w[-1] == '.':
        return only_alpha(w[:-1])
    if w[0] == "'":
        return only_alpha(w[1:])
    if w[-1] == "'":
        return only_alpha(w[:-1])
    if w[0] == '"' and w[-1] == '"':
        return only_alpha(w[1:-1])
    return (has_alpha(w) and bool(alpha_pattern.match(w)))


def is_digit(lt):
    """Return 'True' if input letter is a digit."""
    return lt.isdigit()


def is_alpha(lt):
    """Return 'True' if input letter is a letter."""
    return lt.isalpha()


def has_digit(w):
    """Return 'True' if w contains a digit."""
    if list(filter(is_digit, w)):
        return True
    else:
        return False


def has_alpha(w):
    """Return 'True' if w contains a letter."""
    if is_digbased(w):
        return False
    else:
        if list(filter(is_alpha, w)):
            return True
        else:
            return False


def is_acr(w):
    """Return 'True' if w is an acronym (alternates letters and '.')."""
    return bool(acr_pattern.match(w))


def is_url(w):
    """Return 'True' if start or end of w looks like a url."""
    if urlstart_pattern.match(w) or urlend_pattern.match(w):
        return True
    else:
        return False

hyphen_pattern = re.compile('''
(([\'\.]?                       # optional "'" or "."
[A-Za-z]                        # letter
[\'\.]?)                        # optional "'" or "."
+                               # lines 1-3 repeated one or more times
(-|–|—|/|\s|(-&-))              # followed by '-', '–', '—', '/', or '-&-'
)+                              # all of the above repeated 1+ times
([\'\.]?[A-Za-z][\.\']?)*       # optional final 'word' (same as lines 1-3)
$                               # end of string
    ''', re.VERBOSE)

mixedcase_pattern = re.compile('''
([A-Z]{2,}[a-z]) |    # 2 or more capitals, a lowercase OR
(.*[a-z][A-Z])        # any number of chars, a lowercase, an uppercase
''', re.VERBOSE)

emph_pattern = re.compile('''
[\*~<:]+                          # '*' or '~' repeated one or more times
([A-Za-z]+[-/\']?)+[A-Za-z]+    # optionally hyphenated 'word'
[\*~>:]+                          # '*' or '~' repeated one or more times
$                               # end of string
''', re.VERBOSE)

acr_pattern = re.compile('''
([A-Za-z]\.)+           # letter followed by '.' 1 or more times
[A-Za-z]?               # optional final letter
$                       # end of string
''', re.VERBOSE)

alpha_pattern = re.compile('''
([A-Za-z]+\'?)*         # (1 or more letter, optional apostrophe) repeated
$                       # end of string
''', re.VERBOSE)

urlstart_pattern = re.compile('''
(https?://)|            #'http' followed by optional 's', then '://' OR
(www\.)                 #'www.'
''', re.VERBOSE | re.IGNORECASE)

urlend_pattern = re.compile('''
.*                      #any number of characters
\.                      # '.'
((com)|                 # 'com' OR
(org(\.uk)?)|           # 'org' followed optionally by '.uk' OR
(co\.uk))               # 'co.uk'
$                       #end of string
''', re.VERBOSE | re.IGNORECASE)

hashtag_pattern = re.compile('''
\#
[A-Za-z0-9]+
[_-]?
[A-Za-z0-9]*
''', re.VERBOSE)

end_dict = {'k': 'thousand', 'm': 'million', 'b': 'billion'}
ecurr_dict = {
              "US$": "U S Dollar",
              "AFN": "Afghanistan Afghani",
              "ALL": "Albanian Lek",
              "DZD": "Algerian Dinar",
              "AOA": "Angolan Kwanza",
              "ARS": "Argentine Peso",
              "AMD": "Armenian Dram",
              "AWG": "Aruban Florin",
              "AUD": "Australian Dollar",
              "AZN": "Azerbaijan New Manat",
              "BSD": "Bahamian Dollar",
              "BHD": "Bahraini Dinar",
              "BDT": "Bangladeshi Taka",
              "BBD": "Barbados Dollar",
              "BYR": "Belarusian Ruble",
              "BZD": "Belize Dollar",
              "BMD": "Bermudian Dollar",
              "BTN": "Bhutan Ngultrum",
              "BOB": "Bolivian Boliviano",
              "BAM": "Bosnian Mark",
              "BWP": "Botswana Pula",
              "BRL": "Brazilian Real",
              "BND": "Brunei Dollar",
              "BGN": "Bulgarian Lev",
              "BIF": "Burundi Franc",
              "XOF": "CFA Franc BCEAO",
              "XAF": "CFA Franc BEAC",
              "XPF": "CFP Franc",
              "KHR": "Cambodian Riel",
              "CAD": "Canadian Dollar",
              "CHF": "Swiss Franc",
              "CVE": "Cape Verde Escudo",
              "KYD": "Cayman Islands Dollar",
              "CLP": "Chilean Peso",
              "CNY": "Chinese Yuan",
              "COP": "Colombian Peso",
              "KMF": "Comoros Franc",
              "CDF": "Congolese Franc",
              "CRC": "Costa Rican Colon",
              "HRK": "Croatian Kuna",
              "CUC": "Cuban Convertible Peso",
              "CUP": "Cuban Peso",
              "CYP": "Cyprus Pound",
              "CZK": "Czech Koruna",
              "DKK": "Danish Krone",
              "DJF": "Djibouti Franc",
              "DOP": "Dominican Republic Peso",
              "XCD": "East Caribbean Dollar",
              "EGP": "Egyptian Pound",
              "SVC": "El Salvador Colon",
              "EEK": "Estonian Kroon",
              "ETB": "Ethiopian Birr",
              "EUR": "Euro",
              "FKP": "Falkland Islands Pound",
              "FJD": "Fiji Dollar",
              "GMD": "Gambian Dalasi",
              "GEL": "Georgian Lari",
              "GHS": "Ghanaian New Cedi",
              "GIP": "Gibraltar Pound",
              "XAU": "Gold (oz)",
              "GTQ": "Guatemalan Quetzal",
              "GNF": "Guinea Franc",
              "GYD": "Guyanese Dollar",
              "HTG": "Haitian Gourde",
              "HNL": "Honduran Lempira",
              "HKD": "Hong Kong Dollar",
              "HUF": "Hungarian Forint",
              "ISK": "Iceland Krona",
              "INR": "Indian Rupee",
              "IDR": "Indonesian Rupiah",
              "IRR": "Iranian Rial",
              "IQD": "Iraqi Dinar",
              "ILS": "Israeli New Shekel",
              "JMD": "Jamaican Dollar",
              "JPY": "Japanese Yen",
              "JOD": "Jordanian Dinar",
              "KZT": "Kazakhstan Tenge",
              "KES": "Kenyan Shilling",
              "KWD": "Kuwaiti Dinar",
              "KGS": "Kyrgyzstanian Som",
              "LAK": "Lao Kip",
              "LVL": "Latvian Lats",
              "LBP": "Lebanese Pound",
              "LSL": "Lesotho Loti",
              "LRD": "Liberian Dollar",
              "LYD": "Libyan Dinar",
              "LTL": "Lithuanian Litas",
              "MOP": "Macau Pataca",
              "MKD": "Macedonian Denar",
              "MGA": "Malagasy Ariary",
              "MWK": "Malawi Kwacha",
              "MYR": "Malaysian Ringgit",
              "MVR": "Maldive Rufiyaa",
              "MTL": "Maltese Lira",
              "MRO": "Mauritanian Ouguiya",
              "MUR": "Mauritius Rupee",
              "MXN": "Mexican Peso",
              "MDL": "Moldovan Leu",
              "MNT": "Mongolian Tugrik",
              "MAD": "Moroccan Dirham",
              "MZN": "Mozambique New Metical",
              "MMK": "Myanmar Kyat",
              "ANG": "NL Antillian Guilder",
              "NAD": "Namibia Dollar",
              "NPR": "Nepalese Rupee",
              "NZD": "New Zealand Dollar",
              "NIO": "Nicaraguan Cordoba Oro",
              "NGN": "Nigerian Naira",
              "KPW": "North Korean Won",
              "NOK": "Norwegian Krone",
              "OMR": "Omani Rial",
              "PKR": "Pakistan Rupee",
              "PAB": "Panamanian Balboa",
              "PGK": "Papua New Guinea Kina",
              "PYG": "Paraguay Guarani",
              "PEN": "Peruvian Nuevo Sol",
              "PHP": "Philippine Peso ",
              "PLN": "Polish Zloty",
              "QAR": "Qatari Rial",
              "RON": "Romanian New Leu",
              "RUB": "Russian Rouble",
              "RWF": "Rwandan Franc",
              "WST": "Samoan Tala",
              "STD": "Sao Tome/Principe Dobra",
              "SAR": "Saudi Riyal",
              "RSD": "Serbian Dinar",
              "SCR": "Seychelles Rupee",
              "SLL": "Sierra Leone Leone",
              "XAG": "Silver oz",
              "SGD": "Singapore Dollar",
              "SKK": "Slovak Koruna",
              "SIT": "Slovenian Tolar",
              "SBD": "Solomon Islands Dollar",
              "SOS": "Somali Shilling",
              "ZAR": "South African Rand",
              "KRW": "South-Korean Won",
              "LKR": "Sri Lanka Rupee",
              "SHP": "St Helena Pound",
              "SDG": "Sudanese Pound",
              "SRD": "Suriname Dollar",
              "SZL": "Swaziland Lilangeni",
              "SEK": "Swedish Krona",
              "CHF": "Swiss Franc",
              "SYP": "Syrian Pound",
              "TWD": "Taiwan Dollar",
              "TZS": "Tanzanian Shilling",
              "THB": "Thai Baht",
              "TOP": "Tonga Pa'anga",
              "TTD": "Trinidad/Tobago Dollar",
              "TND": "Tunisian Dinar",
              "TRY": "Turkish New Lira",
              "TMM": "Turkmenistan Manat",
              "USD": "US Dollar",
              "UGX": "Uganda Shilling",
              "UAH": "Ukraine Hryvnia",
              "UYU": "Uruguayan Peso",
              "AED": "United Arab Emir Dirham",
              "VUV": "Vanuatu Vatu",
              "VEB": "Venezuelan Bolivar",
              "VND": "Vietnamese Dong",
              "YER": "Yemeni Rial",
              "ZMK": "Zambian Kwacha",
              "ZWD": "Zimbabwe Dollar",
              "£": "pound",
              "$": "dollar",
              "€": "euro"
              }
