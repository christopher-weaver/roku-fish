"""Rebuild complete mesh swim poses in the lateral (model Z) axis."""
import argparse
from lateral_swim import build
from fish_anatomy import WIDTHS
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--species',nargs='+',choices=list(WIDTHS))
    args=parser.parse_args();build(args.species)
