#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Copyright 2018 the HERA Project
# Licensed under the MIT License

from hera_cal import reflections
import sys
import os
import glob

parser = reflections.auto_reflection_argparser()
a = parser.parse_args()

# initialize reflection fitter
RF = reflections.ReflectionFitter(a.datafile, filetype=a.filetype, input_cal=a.input_cal)

# get antennas if possible
if a.ants is None and hasattr(RF, 'ants'):
    bls = zip(RF.ants, RF.ants)
elif a.ants is not None:
    bls = zip(a.ants, a.ants)
else:
    bls = []

# read data
RF.read(bls=bls, polarizations=a.pols)

# get all autocorr keys
keys = [k for k in RF.data if k[0] == k[1]]

# assign Containers
data = RF.data
flags = RF.flags
nsamples = RF.nsamples
times = RF.times

# time average file
if a.time_avg:
    RF.timeavg_data(1e10, data=data, flags=flags, nsamples=nsamples)
    data = RF.avg_data
    flags = RF.avg_flags
    nsamples = RF.avg_nsamples

# clean data
RF.vis_clean(data=data, flags=flags, keys=keys, ax='freq', window=a.window, alpha=a.alpha,
             horizon=a.horizon, standoff=a.standoff, min_dly=a.min_dly, tol=a.tol, maxiter=a.maxiter,
             gain=a.gain, skip_wgt=a.skip_wgt, edgecut_low=a.edgecut_low, edgecut_hi=a.edgecut_hi)

# model auto reflections in clean data
RF.model_auto_reflections(RF.clean_data, a.dly_range, flags=RF.clean_flags, edgecut_low=a.edgecut_low,
                          edgecut_hi=a.edgecut_hi, Nphs=a.Nphs, window=a.window, alpha=a.alpha,
                          zeropad=a.zeropad, fthin=a.fthin, ref_sig_cut=a.ref_sig_cut)

# write reflections
RF.write_auto_reflections(a.outfname, overwrite=a.overwrite, add_to_history=a.add_to_history,
                          write_npz=a.write_npz)
