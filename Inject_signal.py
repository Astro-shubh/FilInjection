import modules.FilterbankInjection
import numpy
import argparse

parser = argparse.ArgumentParser(description = "This script injects dispersed pulses (full-band/band-limited) in a noise filterbank file.")

parser.add_argument("-if", "--input-file", type=str, help = "Input filterbank file.")
parser.add_argument("-of", "--output-file", type=str, help = "Output filterbank file.")
parser.add_argument("-p", "--period", type=float, help = "Period in second to inject the signal.")
parser.add_argument("-w", "--width", type=float, help = "Pulse width in s to inject.")
parser.add_argument("-dm", "--dispersion-measure", type=float, help = "Dispersion measure to inject the signal.")
parser.add_argument("-cf", "--central-frequency", type=float, help = "Central frequency (MHz) of the signal.")
parser.add_argument("-bf", "--band-occupancy", type=float, help = "Band ocuupancy of the signal (less than or equal to 1).")
parser.add_argument("-snr", "--injection-snr", type=float, help = " S/N for injection.")

args = parser.parse_args()

in_file = args.input_file
out_file = args.output_file
period = args.period
width = args.width
dm = args.dispersion_measure
cf = args.central_frequency
bf = args.band_occupancy
snr = args.injection_snr


modules.FilterbankInjection.inject_filterbank(in_file, out_file, period, width, dm, cf, bf, snr)

