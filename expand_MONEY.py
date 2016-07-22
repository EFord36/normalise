# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 16:07:07 2016

@author: Elliot
"""
from __future__ import print_function
from expand_NUM import expand_NUM

scurr_dict = {'$': 'dollar', 'Y': 'yen', '€': 'euro',
              '£': 'pound', 'HK$': 'Hong Kong Dollar'}
scurr_dict_pl = {'$': 'dollars', 'Y': 'yen', '€': 'euros',
                 '£': 'pounds', 'HK$': 'Hong Kong Dollars'}
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
                     "ZWD": "Zimbabwe Dollar"
                     }
invariant_plural_curr = ['JPY', 'CNY', 'THB', 'ZAR']
irregular_plural_curr = {'SEK': 'Swedish Kronor', 'NOK': 'Norwegian Kroner',
                         'DKK': 'Danish Kroner', 'ISK': 'Iceland Kronur',
                         'BRL': 'Brazilian Reais', 'LTL': 'litai',
                         'LVL': 'latu', 'RON': 'lei'}


def expand_MONEY(n):
    """Return number and currency of input in words."""
    scurr = ''
    ecurr = ''
    end = ''
    for i in range(len(n)-3):
        if not n[i].isdigit():
            scurr += n[i]
        else:
            num = n[i:-3]
            break
    if n[-3].isalpha():
        ecurr += n[-3:]
    elif n[-1].isalpha():
        num += n[-3:-1]
        end += n[-1]
    else:
        num += n[-3:]

    exp_num = expand_NUM(num)
    if num == '1' and not end:
        if ecurr:
            currency = ecurr_dict[ecurr]
        elif scurr:
            currency = scurr_dict[scurr]
        else:
            currency = ''
    else:
        if ecurr:
            if ecurr in invariant_plural_curr:
                currency = ecurr_dict[ecurr]
            elif ecurr in irregular_plural_curr:
                currency = irregular_plural_curr[ecurr]
            else:
                currency = ecurr_dict[ecurr] + 's'
        elif scurr:
            currency = scurr_dict_pl[scurr]

        else:
            currency = ''
    if end:
        large = end_dict[end.lower()]
    else:
        large = ''
    items = [exp_num]
    if large:
        items.append(large)
    items.append(currency)

    for i in items[:-1]:
        print(i, end=' ')
    print(items[-1])
