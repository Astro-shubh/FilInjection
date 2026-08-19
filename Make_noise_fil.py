import modules.FilterbankInjection
import numpy as np
import argparse

parser = argparse.ArgumentParser(description = "This script makes a noise filterbank file.")

parser.add_argument("-f", "--fil-name", type=str, help = "Name of filterbank file.")
parser.add_argument("-nch", "--num-channels", type=int, help = "Number of frequency channels.")
parser.add_argument("-foff", "--channel-width", type=float, help = "Width of a frequency channel (MHz).")
parser.add_argument("-fhi", "--highest-frequency", type=float, help = "Highest observation frequency (MHz).")
parser.add_argument("-tsamp", "--sampling-time", type=float, help = "Sampling time in seconds.")
parser.add_argument("-nsamps", "--number-of-samples", type=int, help = "Number of time samples in file.")

args = parser.parse_args()

fil_name = args.fil_name
nchans = args.num_channels
ch_w = args.channel_width
hifrq = args.highest_frequency
tsamp = args.sampling_time
nsamps = args.number_of_samples
tstart = 60000.0
source = 'fake'
nbits = 8

chunk_size = 50000
nitr = int(nsamps/chunk_size)

header = modules.FilterbankInjection.create_header(fil_name, nchans, ch_w, hifrq, nbits, tsamp, tstart, 0, source)
with modules.FilterbankInjection.IterativeFilterbankWriter(fil_name, header) as writer:
  for itr in range(nitr):
    noise_block = np.random.normal(loc=128.0, scale=25.0, size=(header.nchans, chunk_size))
    writer.append(noise_block, quantize=True)
    print(f"wrote {(itr+1)*chunk_size} samples.")

