def expand_LSEQ(word):
    out = ''
    if word[0].isalpha():
        out += word[0].upper()
    for c in word[1:]:
        if c.isalpha():
            out += ' '
            out += c.upper()
    return out
