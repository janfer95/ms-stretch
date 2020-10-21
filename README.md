# ms-stretch
A Stretching Method (plot) plugin for MSNoise

[![Join the chat at https://gitter.im/ROBelgium/MSNoise](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/ROBelgium/MSNoise?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

MSNoise possesses the possibility of computing relative velocity variation
curves, but a way to plot the results in the 'standard MSNoise way' was
missing.

This plugin contains a command to plot the stretching data in the same
format as for the MCWS method. Moreover, some other scripts are included
to plot the stretching data along with forcings like precipitation,
temperature, pressure, etc. The dvv curves can also be plotted with
their respective correlation coefficients to quickly check for low
correlation parts of the curve.

Examples can be found ([here]())

For questions, comments and bugs please contact jfkuehn@gfz-potsdam.de.

## Installation
* Follow the MSNoise installation instructions ([here](http://msnoise.org/doc/installation.html))
* Install ms-stretch. One way to do it is to copy it into the folder where 
msnoise and other python packages are saved, type ``cd ms-stretch`` and then 
run ``python setup.py install``. 

## Running ms-stretch

After installing the plugin make sure to add "ms_stretch" to the plugin
parameter in the web admin. Alternatively ``msnoise config set plugins=ms_stretch``
works too. Note in both cases that an underscore is needed, not a dash.

To just plot the stretching data in the typical MSNoise fashion with all
the defaults simply type: ``msnoise p plot dvv -f 1``.
In contrast to the ``msnoise plot dvv`` command the explicit declaration of
the filter is highly recommended. Reason for this is that the plugin command also
supports plotting of multiple filters and different lag time windows (LTW)
within the same filter.

### Plotting multiple filters

While working with the stretching method one often tries out different lag
time windows for the same filters. To better compare this results they can be
plotted together by simply calling the filter argument multiple times.

* ``msnoise p plot dvv -f 1 -f 2`` plots the dvv curves corresponding to
the two filters with otherwise default values.

* ``msnoise p plot dvv -f 1_2_4 -f 1_4_8`` plots two dvv curves corresponding
to the same filter, BUT for different LTW. In this case, 2s-4s and 4s-8s.

### Setting up LTW data

MSNoise outputs by default the stretching data in a folder called STR, where
the results for the different filters are saved. If you already have computed
some STR data, but still want to have plots with various LTW then you can
change the folder names of the filters from e.g. ``STR/01`` to ``STR/01_2_4``
or similar. Naturally, you have to remember in which LTW you computed the data.

Another option is to run the command ``msnoise p compute_stretching``. A script
is executed that is identical to the original MSNoise one with the only
difference that the output folder is changed to the format mentioned above, i.e.
``STR/filterid_startlag_endlag``. This also has the (nice) side effect that if
data for the same filter with another LTW is computed, it does not overwrite
the previous data.

### Plot dvv curves with forcings

This plugin also supports the possibility of plotting forcings like
precipitation, temperature and pressure alongside the dvv curves. To get
started one must at first "install" another table called DefaultStations.

The command ``msnoise p plot install`` takes care of that. Now this table
should appear and be editable in the MSNoise web admin (run ``msnoise admin``).  

As a default a precipitation entry is given. Further forcings can be added at
will. The columns of the table should be self-explaining*. The following commands
extract information from that table so it is advised to regularly check the
settings.  

* ``msnoise p plot forcing -f 1`` plots a dvv curve with the default of
plotting the first forcing in the DefaultStations table. Multiple filters or
different LTW are possible.

* ``msnoise p plot mforcing -f 1`` is the same as the command before only
that multiple forcings are possible. Check out the ([examples]()) to get an idea.


*Note: In the column Default Station 'all' can be passed and this takes the
average of all the stations in the forcing folder. Otherwise, write the
name of the station without the '.csv'-ending. Additionally, click on examples
above to find out more about the expected file and folder structure for the
forcing commands to work properly.

### Other commands

* ``msnoise p plot corr -f 1`` plots the dvv curve with defaults and adds a
subplot with the corresponding correlation coefficients.

* ``msnoise p plot uninstall`` deletes the DefaultStations table from the
database.

## Miscellaneous

If questions arise it can be helpful to use the ``--help`` argument after
the command to see which parameters are needed or optional. Furthermore,
the Python Code has generally a docstring for each function so that sometimes
extra information can be found there. Otherwise don't hesitate to contact me
under the E-mail address given before.

## Outlook

Some further modifications are planned for this plugin including:

* an alternative stacking method to improve noisy dvv curves in some cases

* corresponding plots

* computing and plotting Signal-to-Noise ratios 
