#!/usr/bin/env python
# encoding: utf-8
r"""
Simple convenience script for setting up and running an interactive plotting
sesssion.
"""

from __future__ import absolute_import
import argparse
import clawpack.visclaw.Iplotclaw as Iplotclaw

def run_iplotclaw(**kwargs):
    ip = Iplotclaw.Iplotclaw(**kwargs)
    ip.plotloop()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", default="./_output", type=str, nargs="?")
    parser.add_argument("setplot", default="setplot.py", type=str, nargs="?")
    parser.add_argument("--fname", default=None, type=str, required=False)
    parser.add_argument("--fps", default=None, type=float, required=False)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    run_iplotclaw(**parse_args().__dict__)
