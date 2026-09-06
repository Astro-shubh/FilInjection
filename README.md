# A tool to inject band-limited dispersed signals in filterbank files

This is a sigpyproc-based injection tool. This was specifically designed to inject band-limited signals and RFI into filterbank data. The generated files are only compatible with sigpyproc at the moment.

## Dependencies
This requires sigpyproc to be installed.

## Usage
1. Generate a noise filterbank file:
   ```text
   Make_noise_fil.py -f <noise_file_name> -nch <number_of_channels> -foff <channel_width (MHz)> -fhi <highest_frequency (MHz)> -tsamp <sampling_time (s)> -nsamps <number_of_samples>
2. Inject a signal in a noise filterbank file:
   ```text
   python Inject_signal.py -if <input_noise_filterbank> -of <output_fitlerbank> -p <period (s)> -w <width (s)> -dm <DM> -cf <signal_central_frequency> -bf <band_occupancy> -snr <input_snr>
   ```
