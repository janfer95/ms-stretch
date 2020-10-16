"""
This plot shows the final output of MSNoise.
Velocity variation gets plotted with Precipitation,
temperature, and NDVI forcings. Multiple pairs or
filters allowed.


.. include:: clickhelp/msnoise-plot-dvv.rst


Example:

``msnoise plot dvv`` will plot all defaults:

.. image:: .static/dvv.png

"""

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

from matplotlib.dates import DateFormatter
from matplotlib.dates import MonthLocator

from msnoise.api import *
from ..datautilities import get_dvv, get_filter_info, nicen_up_pairs


def main(mov_stack=10, components='ZZ', filterid='1', pairs=None,
         forcings=['prec'], ask=False, type='points', show=True, outfile=None):
    db = connect()

    start, end, datelist = build_movstack_datelist(db)
    filterids, lows, highs, minlags, endlags = get_filter_info(filterid)
    pairs, nice_pairs = nicen_up_pairs(pairs)

    if components.count(","):
        components = components.split(",")
    else:
        components = [components, ]

    # Plot either one forcing with dvv curve or multiple forcings
    if len(forcings) == 1:
        gs = gridspec.GridSpec(1, 1)
    else:
        gs = gridspec.Gridspec(2,1)
    fig = plt.figure(figsize=(12, 9))
    plt.subplots_adjust(bottom=0.06, hspace=0.3)
    first_plot = True
    filter_len = len(filterids)
    for i, filterid in enumerate(filterids):
        dflist = []
        for pair in pairs:
            dvv_data = get_dvv(mov_stack=mov_stack, comps=comps,
                               filterid=filterid, pairs=pair)
            dflist.append(dvv_data)

        # Plot dvv mean and median or multiple dvv
        if first_plot:
            ax = plt.subplot(gs[0])
            first_plot = False

        # TODO: Maybe check for same filter, so that label can be shortened
        if "all" in pairs and filter_len == 1:
            tmp = dflist[0]["mean"]
            plt.plot(tmp.index, tmp.values, ".", markersize=11, label="mean")
            tmp = dflist[0]["median"]
            plt.plot(tmp.index, tmp.values, ".", markersize=11, label="median")
        elif "all" in pairs and filter_len > 1:
            # TODO: Maybe add option to choose mean or median
            tmp = dflist[0]["mean"]
            label = "Filter %i, %i-%is" % (int(filter), minlags[i], endlags[i])
            plt.plot(tmp.index, tmp.values, ".", markersize=11, label=label)
        elif "all" not in pairs and filter_len == 1:
            max_len = 0
            for df, pair in zip(dflist, nice_pairs):
                tmp = df["mean"]
                #Find out longest time series to plot
                if len(tmp) > max_len:
                    max_len = len(tmp)
                    id = tmp.index
                plt.plot(tmp.index, tmp, label=pair)
        else:
            max_len = 0
            for df, pair in zip(dflist, nice_pairs):
                tmp = df["mean"]
                #Find out longest time series to plot
                if len(tmp) > max_len:
                    max_len = len(tmp)
                    id = tmp.index
                label = ("Filter %i, %i-%is, %s" %
                        (int(filter), minlags[i], endlags[i], pair))
                plt.plot(tmp.index, tmp, label=pair)

    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4,
               ncol=2, borderaxespad=0.)
    plt.ylabel('dv/v (%)')
    left, right = id[0], id[-1]
    if mov_stack == 1:
       plt.title('1 Day Smoothing')
    else:
       plt.title('%i Days Smoothing' % mov_stack)
    plt.xlim(left, right)
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))
    fig.autofmt_xdate()


    ax2 = ax.twinx()

    forcing = forcings[0]
    # load forcing default values
    defaults = pd.read_csv("defaults.csv", header=1, index_col=1)
    dir = defaults.at[forcing, 'folder_name']
    name = defaults.at[forcing, 'forcing']
    unit = defaults.at[forcing, 'unit']
    type = defaults.at[forcing, 'plot_type']

    if ask:
        stas = ask_stations(dir)
    else:
        stas = [defaults.at[forcing, 'default_station']]

    if forcing == 'PGV':
        data = get_pgv()
    else:
        data = get_data(dir, stas)


    # TODO: Pass the color as argument?
    color = 'tab:green'
    # Plot configurations
    if type == 'points':
        ax2.plot(data.index, data, ".", markersize=8, color=color)
    elif type == 'bars':
        ax2.bar(data.index, data, color=color)
    elif type == 'cumsum':
        ax2.bar(data.index, data.cumsum(), color=color)
        name = "Cumulative " + name.lower()
    elif type == 'errorbars':
        # TODO: Maybe find more elegant way? For now, data in first, errors
        # in second column
        data_err = data.iloc[1]
        ax2.errorbar(data.index, data.iloc[0], yerr=data_err, fmt='o',
                     color=color)
    else:
        print("Unknown type parameter, using default.")
        ax2.plot(data.index, data, ".", markersize=8, color=color)

    ax2.set_ylabel(name, unit)
    ax2.tick_params(axis='y', labelcolor=color)
    # Forcing y-limit is maximal value plus 10% for extra space
    # TODO: Don't hardwire 10%
    max_val = data.loc[left:right].values.max()
    ax2.set_ylim(0, max_val*1.1)


    if len(forcings) > 1:

        # Plot forcing
        ax3 = fig.add_subplot(gs[1], sharex=ax)

        forcing = forcings[1]
        # load forcing default values
        defaults = pd.read_csv("defaults.csv", header=1, index_col=1)
        dir = defaults.at[forcing, 'folder_name']
        name = defaults.at[forcing, 'forcing']
        unit = defaults.at[forcing, 'unit']
        type = defaults.at[forcing, 'plot_type']

        if ask:
            stas = ask_stations(dir)
        else:
            stas = [defaults.at[forcing, 'default_station']]

        if forcing == 'PGV':
            data = get_pgv()
        else:
            data = get_data(dir, stas)

        # TODO: Pass the color as argument?
        color = 'tab:orange'
        # Plot configurations
        if type == 'points':
            ax3.plot(data.index, data, ".", markersize=8, color=color)
        elif type == 'bars':
            ax3.bar(data.index, data, color=color)
        elif type == 'cumsum':
            ax3.bar(data.index, data.cumsum(), color=color)
            name = "Cumulative " + name.lower()
        elif type == 'errorbars':
            # TODO: Maybe find more elegant way? For now, data in first, errors
            # in second column
            data_err = data.iloc[1]
            ax3.errorbar(data.index, data.iloc[0], yerr=data_err, fmt='o',
                         color=color)
        else:
            print("Unknown type parameter, using default.")
            ax3.plot(data.index, data, ".", markersize=8, color=color)

        ax3.set_ylabel(name, unit)
        ax3.tick_params(axis='y', labelcolor=color)

        plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))
        fig.autofmt_xdate()

        # For the case of two subplots with two y-axes
        if len(forcings) == 3:

            ax4 = ax3.twinx()

            forcing = forcings[2]
            # load forcing default values
            defaults = pd.read_csv("defaults.csv", header=1, index_col=1)
            dir = defaults.at[forcing, 'folder_name']
            name = defaults.at[forcing, 'forcing']
            unit = defaults.at[forcing, 'unit']
            type = defaults.at[forcing, 'plot_type']

            if ask:
                stas = ask_stations(dir)
            else:
                stas = [defaults.at[forcing, 'default_station']]

            if forcing == 'PGV':
                data = get_pgv()
            else:
                data = get_data(dir, stas)

            # TODO: Pass the color as argument?
            color = 'tab:orange'
            # Plot configurations
            if type == 'points':
                ax4.plot(data.index, data, ".", markersize=8, color=color)
            elif type == 'bars':
                ax4.bar(data.index, data, color=color)
            elif type == 'cumsum':
                ax4.bar(data.index, data.cumsum(), color=color)
                name = "Cumulative " + name.lower()
            elif type == 'errorbars':
                # TODO: Maybe find more elegant way? For now, data in first, errors
                # in second column
                data_err = data.iloc[1]
                ax4.errorbar(data.index, data.iloc[0], yerr=data_err, fmt='o',
                             color=color)
            else:
                print("Unknown type parameter, using default.")
                ax4.plot(data.index, data, ".", markersize=8, color=color)

            ax4.set_ylabel(name, unit)
            ax4.tick_params(axis='y', labelcolor=color)
            # Forcing y-limit is maximal value plus 10% for extra space
            # TODO: Don't hardwire 10%
            max_val = data.loc[left:right].values.max()
            ax4.set_ylim(0, max_val*1.1)


    # Prepare plot title
    title = 'Stretching, %s \n' % ",".join(components)
    for i, filterid in enumerate(filterids):
        title += ('Filter %d (%.2f - %.2f Hz), Lag time window %.1f - %.1fs \n' % (
                  int(filterid[0:2]), lows[i], highs[i], minlags[i], endlags[i]))
    if "all" in pairs:
        title += "Average over all pairs"
    else:
        title += "Pairs: %s" % str(nice_pairs)[1:-1]

    plt.suptitle(title)

    if outfile:
        if outfile.startswith("?"):
            if len(mov_stacks) == 1:
                outfile = outfile.replace('?', '%s-f%i-m%i-M%s' % (components,
                                                                   filterid,
                                                                   mov_stack,
                                                                   dttname))
            else:
                outfile = outfile.replace('?', '%s-f%i-M%s' % (components,
                                                               filterid,
                                                               dttname))
        outfile = "dvv_" + outfile
        print("output to:", outfile)
        plt.savefig(outfile)
    if show:
        plt.show()


if __name__ == "__main__":
    main()
