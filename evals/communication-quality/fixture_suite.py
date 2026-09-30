import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--list', action='store_true')
parser.add_argument('--run', action='store_true')
parser.add_argument('--short', action='store_true')
args = parser.parse_args()
if args.list:
    print('short: isolated arithmetic regression; synthetic; estimate <1 second' if args.short else
          'full: isolated arithmetic regression + synthetic soak; estimate 8 minutes; budget 10 minutes; '
          'fixture emulates execution immediately, no load')
elif args.run:
    assert 2 + 2 == 4
    print('PASS: synthetic fixture emulation only; no real soak or environment compatibility measured')
