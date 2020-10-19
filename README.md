# ms-stretch
A Stretching Method (plot) plugin for MSNoise

MSNoise possesses the possibility of computing relative velocity variation
curves, but a way to plot the results in the 'standard MSNoise way' was
missing. 

This plugin contains a command to plot the stretching data in the same 
format as for the MCWS method. Moreover, some other scripts are included
to plot the stretching data along with forcings like precipitation, 
temperature, pressure, etc. The dvv curves can also be plotted with 
their respective correlation coefficients to quickly check for low
correlation parts of the curve. 

## Documentation

### Installation
TODO: Be more precise.
* Follow the MSNoise installation instructions ([here](http://msnoise.org/doc/installation.html))
* Install ms-stretch  

### Running ms-stretch

After installing the plugin make sure to add "ms_stretch" to the plugin
parameter in the web admin. Alternatively ``msnoise config set plugins=ms_stretch``
works too.
