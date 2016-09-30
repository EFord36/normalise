from sys import argv
import argparse
import pickle

from normalise import normalise, rejoin, tokenize_basic


def main():
    parser = argparse.ArgumentParser(description="""normalises text in file
     at path given (path/name.extension'), and stores in 'file_normalised' (path/name_normalised.extention). Will use
     simple default tokenizer and general abbrevations: to use custom tokenizer
     and abbreviations import normalise function from the module.""")
    parser.add_argument('text', metavar='P', type=str, nargs='+',
                        help='The path of the text to be normalised')
    parser.add_argument('-E', dest='english', type=str, choices=['BrE', 'AmE'],
                        default='BrE',
                        help='specify the variety as American English or British English (default: British English)')
    parser.add_argument('-A', dest='abbrevs', default=None,
                        help='The path to a pickled custom abbreviation dictionary')
    parser.add_argument('-T', dest='tokenizer', default=None,
                        help='The path to a pickled custom tokenizer')
    parser.add_argument('-V', '--verbose', dest='verbose', action='store_const',
                        const=True, default=False,
                        help='specify verbose output (default: False)')
    args = parser.parse_args()
    if args.abbrevs:
        with open(args.abbrevs, mode='rb') as f:
            user_abbrevs = pickle.load(f)
    else:
        user_abbrevs = {}
    if args.tokenizer:
        with open(args.tokenizer, mode='rb') as f:
            tokenizer = pickle.load(f)
    else:
        tokenizer = tokenize_basic
    for f in args.text:
        print(f)
        with open(f, mode='r') as raw:
            text = raw.read()
        i = f.rfind('.')
        with open('{}_normalised{}'.format(f[:i], f[i:]), mode='w') as out:
            norm = rejoin(normalise(text, verbose=args.verbose, variety=args.english, user_abbrevs=user_abbrevs, tokenizer=tokenizer))
            print(norm)
            out.write(norm)
