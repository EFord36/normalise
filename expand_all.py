from expand_NUMB import expand_NUM, expand_NDIG, expand_NORD, expand_NYER, expand_PRCT, expand_MONEY, expand_NTIME # , expand_RANGE
from expand_EXPN import expand_EXPN
from expand_LSEQ import expand_LSEQ
from expand_NONE import expand_NONE
from expand_WDLK import expand_WDLK


def expand_URL(word):
    return word


def expand_HTAG(word):
    return word


def expand_NDATE(word):
    return word

def expand_NRANGE(word):
    return word
func_dict = {
             'EXPN': 'expand_EXPN(nsw, ind, text)',
             'LSEQ': 'expand_LSEQ(w)',
             'WDLK': 'expand_WDLK(nsw)',
             'NUM': 'expand_NUM(nsw)',
             'NORD': 'expand_NORD(nsw)',
             'NRANGE': 'expand_NRANGE(nsw)',
             'NTIME': 'expand_NTIME(nsw)',
             'NDATE': 'expand_NDATE(nsw)',
             'NYER': 'expand_NYER(nsw)',
             'MONEY': 'expand_MONEY(nsw)',
             'PRCT': 'expand_PRCT(nsw)',
             'PROF': 'expand_WDLK(nsw)',
             'URL': 'expand_URL(nsw)',
             'HTAG': 'expand_HTAG(nsw)',
             'NONE': 'expand_NONE(nsw)'
            }


def expand_all(dic, text):
    for ind, (nsw, tag, ntag) in dic.items():
        dic.update({ind: (nsw, tag, ntag, (eval(func_dict[ntag])))})
    return dic
