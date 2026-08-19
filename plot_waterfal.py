import matplotlib.pyplot as plt
import sys
import numpy as np
import sigpyproc.readers as sigread

filename = str(sys.argv[1])
on1 = float(sys.argv[2])
on2 = float(sys.argv[3])
dm = float(sys.argv[4])

fil=sigread.FilReader(filename)
tsamp = fil.header.tsamp
nchans = fil.header.nchans
nsamples = fil.header.nsamples

print("sampling time: "+str(tsamp)+"\n")

on_samp1 = int(on1/tsamp)
on_samp2 = int(on2/tsamp)

fil1 = fil.read_dedisp_block(on_samp1,on_samp2 - on_samp1, dm)

fil1.downsample(ffactor=32, tfactor=4)

tsamp = fil1.header.tsamp

nchan = fil1.header.nchans
nsamples = fil1.header.nsamples

print(nchan, nsamples)
chan_start = int(0.1*nchan)
chan_end = int(0.9*nchan)

samp_start = int(0.2*nsamples)
samp_end = int(0.8*nsamples)

data = fil1.data[chan_start:chan_end, samp_start:samp_end]

profile = np.mean(data, axis=0)

fig, ax = plt.subplots(2,1)

#plt.plot(profile)
#plt.show()

ax[1].imshow(data, aspect='auto', origin='lower', cmap="YlGnBu")
ax[0].plot(profile)
plt.show()
new_on1 = int(input("Enter new start: "))
new_on2 = int(input("End new end: "))

profile = profile[new_on1:new_on2]
data = data[:, new_on1:new_on2]
freq1 = fil1.header.fmin
freq2 = fil1.header.fmax
delta_f = freq2 - freq1
freq1 = freq1 + 0.1*delta_f
freq2 = freq2 - 0.1*delta_f
time_axis = np.arange(0,len(profile))*tsamp*1000.0
print(freq1, freq2)

#profile = profile - np.median(profile)
#data = data - np.median(data)

np.savetxt("Single_pulse_frequency_time.txt", data)

fig=plt.figure(figsize=(4.5,4),dpi=200)
ax1=fig.add_axes([0.15,0.12,0.8,0.6],title=' dm: '+str(dm), xlabel='Time (ms)',ylabel='Frequency (MHz)')
ax2 = fig.add_axes([0.15,0.72,0.8,0.2],ylabel = 'Intensity',xticks=[])
subband=ax1.imshow(data, aspect='auto', extent=[0.0, time_axis[-1], freq1, freq2], cmap="YlGnBu")
#ax2.set_xlim(new_on1, new_on2)
ax2.plot(profile)
plt.show()
