from pyuvdata import UVCal
import numpy as np

JD2SEC = 1.*24.*60.*60.
class HERACal(UVCal):
    '''Class that loads in hera omnical data,'''
    def __init__(self, meta, gains, flags=None, DELAY=False, ex_ants=[], appendhist=''):
        '''given meta and gain dictionary from omni_run.py before to_npz() call,
           to reshuffle data and populating the UVCal class.'''

        super(HERACal, self).__init__()

        str2pol = {'x': -5, 'y': -6}
        pol2str = {-5: 'x', -6: 'y'}

        chisqdict = {}
        datadict = {}
        flagdict = {}
        ants = []
        for pol in gains:
            for ant in np.sort(gains[pol].keys()):
                datadict['%d%s' % (ant, pol)] = gains[pol][ant]
                if flags:
                    flagdict['%d%s' % (ant, pol)] = flags[pol][ant]
                if ant not in ants:
                    ants.append(ant)

        # drop antennas that are not solved for.
        allants = ants + ex_ants
        ants = np.sort(ants)
        allants = np.sort(allants)
        time = meta['jds']
        freq = meta['freqs']  # in GHz
        pols = [str2pol[p] for p in gains.keys()]
        npol = len(pols)
        ntimes = time.shape[0]
        nfreqs = freq.shape[0]
        nants = len(ants)
        antnames = ['ant' + str(ant) for ant in ants]
        datarray = []
        flgarray = []
        # import IPython; IPython.embed()
        for ii in range(npol):
            dd = []
            fl = []
            for ant in ants:
                try:
                    dd.append(datadict[str(ant) + pol2str[pols[ii]]])
                    if flags:
                        fl.append(flagdict[str(ant) + pol2str[pols[ii]]])
                    else:
                        fl.append(np.zeros_like(dd[-1], dtype=bool))
                # if antenna not in data dict (aka, a bad antenna)
                except(KeyError):
                    print "Can't find antenna {0}".format(ant)
            datarray.append(dd)
            flgarray.append(fl)

        datarray = np.array(datarray)
        datarray = datarray.swapaxes(0, 3).swapaxes(0, 1)

        flgarray = np.array(flgarray)
        flgarray = flgarray.swapaxes(0, 3).swapaxes(0, 1)

        tarray = time
        parray = np.array(pols)
        farray = np.array(freq)
        numarray = np.array(list(ants))
        namarray = np.array(antnames)

        chisqarray = []
        for ii in range(npol):
            ch = []
            for ant in ants:
                try:
                    ch.append(meta['chisq'+str(ant)+pol2str[pols[ii]]])
                except:
                    ch.append(np.ones_like(dd[-1]))  # array of ones
            chisqarray.append(ch)
        chisqarray = np.array(chisqarray).swapaxes(0, 3).swapaxes(0, 1)

        self.telescope_name = 'HERA'
        self.observer = 'Zaki Ali (zakiali@berkeley.edu)'
        try:
            self.pipeline = meta['pipeline']
        except KeyError:
            self.pipeline = 'unknown'
        self.Nfreqs = nfreqs
        self.Njones = len(pols)
        self.Ntimes = ntimes
        try:
            self.history = meta['history'].replace('\n', ' ') + appendhist
        except KeyError:
            self.history = appendhist
        self.Nants_data = len(ants)  # only ants with data
        self.antenna_names = namarray[:self.Nants_data]
        self.antenna_numbers = numarray[:self.Nants_data]
        self.Nants_telescope = nants  # total number of antennas
        self.Nspws = 1

        self.freq_array = farray[:self.Nfreqs].reshape(self.Nspws, -1)
        self.channel_width = np.diff(self.freq_array)[0][0]
        self.jones_array = parray[:self.Njones]
        self.time_array = tarray[:self.Ntimes]
        self.integration_time = meta['inttime']
        self.gain_convention = 'divide'
        self.x_orientation = 'east'
        self.time_range = [self.time_array[0], self.time_array[-1]]
        self.freq_range = [self.freq_array[0], self.freq_array[-1]]
        if DELAY:
            self.set_delay()
            self.delay_array = datarray
            self.quality_array = chisqarray
            self.flag_array = flgarray.astype(np.bool)

        else:
            self.set_gain()
            self.gain_array = datarray
            self.quality_array = chisqarray
            self.flag_array = flgarray.astype(np.bool)
