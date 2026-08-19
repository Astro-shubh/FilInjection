#!/usr/bin/env python3
import numpy as np
import math
from sigpyproc.header import Header
from sigpyproc.readers import FilReader


class IterativeFilterbankWriter:
    """
    A stateful wrapper class around sigpyproc to iteratively stream and write 
    8-bit quantized filterbank blocks (time-frequency numpy arrays).
    """
    def __init__(self, output_filename, header, target_mean=128.0, target_std=25.0):
        self.output_filename = output_filename
        self.header = header
        self.target_mean = target_mean
        self.target_std = target_std
        
        # Initialize the output file stream using sigpyproc's prep_outfile
        self.out_file = self.header.prep_outfile(self.output_filename)
        self.total_written_samps = 0

    def append(self, data_matrix, quantize=True):
        """
        Appends a 2D numpy array of shape (nchans, nsamps) to the filterbank file iteratively.
        """
        nchans, nsamps = data_matrix.shape
        
        if nchans != self.header.nchans:
            raise ValueError(f"Channel mismatch! Expected {self.header.nchans} channels, got {nchans}.")

        if nsamps <= 0:
            return

        if quantize:
            chunk_mean = np.mean(data_matrix)
            chunk_std = np.std(data_matrix)
            if chunk_std == 0:
                chunk_std = 1.0

            normalized = (data_matrix - chunk_mean) / chunk_std
            quantized_floats = (normalized * self.target_std) + self.target_mean
            final_chunk = np.clip(quantized_floats, 0, 255).astype(np.uint8)
        else:
            final_chunk = data_matrix.astype(np.uint8)

        # Column-major flattening requirement for sigpyproc cwrite
        flat_stream_to_write = final_chunk.T.flatten()
        self.out_file.cwrite(flat_stream_to_write)
        self.total_written_samps += nsamps

    def close(self):
        if self.out_file:
            self.out_file.close()
            print(f"\nFilterbank writer closed. Total written time samples: {self.total_written_samps:,}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()




def get_scaling_factors(injection_snr, width, tsamp, band_width, nchans, band_occupancy):
    """ 
    Band width in MHz, width and tsamp in s, and band_occupancy in fraction
    computes scaling factor for median and rms for the fitlebrank pixels 
    """
    channel_width = band_width/nchans
    raw_res = 1.0e-6/channel_width         ## Time resolution in s if band_width was in MHz
    current_downf = tsamp/raw_res   ## tsamp in s
    nbins = width/tsamp
    channel_snr = injection_snr/(band_occupancy*np.sqrt(nchans))

    # channel_snr = (mean_scaling - 1)*sqrt(nbins)

    scaling = 1 + channel_snr/np.sqrt(nbins)

    return scaling



def get_delay_samps(current_frq, highest_frq, tsamp, dm):
    """
    Returns delay in number of samples for the current_frq (MHz) with respect to highest_frq (MHz)
    for the given DM."
    """
    dm_const = 1/241.0
    high_frq = highest_frq/1000.0  # in GHz
    curr_frq = current_frq/1000.0 # in GHz
    # Compute the delay
    delay_s = dm*dm_const*(1/(curr_frq*curr_frq) - 1/(high_frq*high_frq))

    #return delay number of bins for current channel
    return int(delay_s/tsamp)




def inject_signal(buffer_block, chunk_size, period, width, dm, centre_frq, occupancy_frc, injection_snr, injection_phase):
    fmin = buffer_block.header.fmin
    fmax = buffer_block.header.fmax
    bandwidth = buffer_block.header.bandwidth
    tsamp = buffer_block.header.tsamp
    nchans = buffer_block.header.nchans
    chan_freqs = buffer_block.header.chan_freqs
    centrer_chan = np.where(np.abs(chan_freqs - centre_frq) == min(np.abs(chan_freqs - centre_frq)))[0][0]
    side_inj_chans = int(nchans*occupancy_frc/2.0)

    scaling = get_scaling_factors(injection_snr, width, tsamp, bandwidth, nchans, occupancy_frc)
    nbins = int(width/tsamp)
    start_chan = centrer_chan - side_inj_chans
    if(start_chan < 0):
        start_chan = 0
    end_chan = centrer_chan + side_inj_chans
    if(end_chan >= nchans):
        end_chan = nchans-1
    max_delay_samps = get_delay_samps(fmin, fmax, tsamp, dm)
    nperiods = math.floor(chunk_size/period)
    end_phase = (chunk_size - nperiods*period)/period
    if(end_phase > injection_phase):
        nperiods = nperiods+1
        return_phase = 1 - end_phase
    else:
        return_phase = injection_phase - end_phase

    data = buffer_block.data
    for int_p in range(nperiods):
        start_time = (int_p + injection_phase)*period
        if(start_time + max_delay_samps + nbins < chunk_size):
            for chan in range(start_chan, end_chan):
                delay_samps = get_delay_samps(chan_freqs[chan], fmax, tsamp, dm)
                start_samps = int(start_time/tsamp)+delay_samps
                if(start_samps + nbins > len(data[chan,:])):
                        break
                mean = np.mean(data[chan, start_samps:start_samps+nbins])
                rms = np.std(data[chan, start_samps:start_samps+nbins])
                ## First scale the noise conponent by scaling factor
                noise_comp = (data[chan, start_samps:start_samps+nbins] - mean)*scaling
                ## Add rms*(scaling - 1) to the mean
                mean_comp = np.ones(nbins)*mean + rms*(scaling - 1)
                ## Generate injected data
                data[chan, start_samps:start_samps+nbins] = mean_comp + noise_comp
    return data, return_phase




def inject_filterbank(input_file, output_filename, period, width, dm, mid_freq, band_occ)
"""
   Injects signal in the noise filterbank file and writes out a new filterbank. Needs period and width in seconds, frequency in MHz
   Band occupancy of the signal in fraction, and injection SNR. Unfortunately presto can't read filterbank wirtten by sigpyproc.
"""
 
    # Get the header
    fil_in = FilReader(input_file)
    my_header = fil_in.header
    tsamp = my_header.tsamp

    # processing parameters
    start = 0.0
    chunk_to_process = 10.0  # In s
    overlap = 4.0            # seconds

    buffer_size = int((chunk_to_process + overlap)/tsamp)
    chunk_size = int(chunk_to_process/tsamp)
    overlap_size = int(overlap/tsamp)
    nitr = int(my_header.nsamples/chunk_size)
    duration = tsamp*my_header.nsamples
    print(f"Total duration of file: {duration}")
    print(f"number of iterations: {nitr}")
    start_samp = 0
    start_phase = 0.5

    with IterativeFilterbankWriter(output_filename, my_header) as writer:
        for itr in range(nitr):
            print(f"processing itr: {itr}")
            buffer = fil_in.read_block(start_samp, buffer_size)
            data, start_phase = inject_signal(buffer, chunk_size, period, width, dm, mid_freq, band_occ, injection_snr, start_phase)
            writer.append(data, quantize=True)
            start_samp = itr*chunk_size
