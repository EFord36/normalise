from sys import argv
import argparse

from normalise import normalise, rejoin


def main():
    parser = argparse.ArgumentParser(description="""normalises text in file
     at path given (path/name.extension'), and stores in 'file_normalised' (path/name_normalised.extention). Will use
     simple default tokenizer and general abbrevations: to use custom tokenizer
     and abbreviations import normalise function from the module.""")
    parser.add_argument('text', metavar='P', type=str, nargs=1,
                        help='The path of the text to be normalised')
    parser.add_argument('--AmE', dest='variety', action='store_const',
                        const='AmE', default='BrE',
                        help='specify the variety as American English (default: British English)')
    parser.add_argument('--V', dest='verbose', action='store_const',
                        const=True, default=False,
                        help='specify verbose output (default: False)')
    args = parser.parse_args()
    f = args.text[0]
    print(f)
    with open(f, mode='r') as raw:
        text = raw.read()
    i = f.rfind('.')
    with open('{}_normalised{}'.format(f[:i], f[i:]), mode='w') as out:
        norm = rejoin(normalise(text, verbose=args.verbose, variety=args.variety))
        print(norm)
        out.write(norm)
