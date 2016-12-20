#!/usr/bin/env python
# encoding: utf-8
r"""
Simple convenience script for setting up and running an interactive plotting
sesssion.
"""

from __future__ import absolute_import
import sys
import clawpack.visclaw.Iplotclaw as Iplotclaw

def run_iplotclaw(setplot='setplot.py',outdir='./_output'):
    ip = Iplotclaw.Iplotclaw(setplot=setplot,outdir=outdir)
    ip.plotloop()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_iplotclaw(*sys.argv[1:])
    else:
        run_iplotclaw()
