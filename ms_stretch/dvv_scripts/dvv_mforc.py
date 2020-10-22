"""
Plot dvv curves with up to 3 forcings.

Plot dvv velocity curves obtained by the stretching method with multiple
forcings defined in the arguments and configurations. The first
forcing is plotted together with the dvv curve. The two other ones
are displayed in a subplot.

Example:

``msnoise plugin plot mforcing -f 1_2_4`` will plot a dvv curve with all defaults,
where filter 1 was used and the stretching window was 2s-4s.

"""

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

from matplotlib.dates import DateFormatter
from matplotlib.dates import MonthLocator

from msnoise.api import *
from ..api import *


def main(mov_stack=10, components='ZZ', filterid='1', pairs=None, custom=False,
         forcings=[], ask=False, show=True, outfile=None):
    db = connect()
    start, end, datelist = build_movstack_datelist(db)
    filterids, lows, highs, minlags, endlags = get_filter_info(filterid)
    pairs, nice_pairs = nicen_up_pairs(pairs, custom)

    if components.count(","):
        components = components.split(",")
    else:
        components = [components, ]

    # Plot either one forcing with dvv curve or multiple forcings
    if len(forcings) <= 1:
        gs = gridspec.GridSpec(1, 1)
    else:
        gs = gridspec.GridSpec(2,1)
    fig = plt.figure(figsize=(12, 9))
    plt.subplots_adjust(bottom=0.06, hspace=0.3)
    first_plot = True
    filter_len = len(filterids)
    for i, filterid in enumerate(filterids):
        dflist = []
        for pair in pairs:
            dvv_data = get_dvv(mov_stack=mov_stack, comps=components,
                               filterid=filterid, pairs_av=pair)
            dflist.append(dvv_data)

        # Plot dvv mean and median or multiple dvv
        if first_plot:
            ax = plt.subplot(gs[0])
            first_plot = False

        # TODO: Maybe check for same filter, so that label can be shortened
        if "all" in pairs and filter_len == 1:
            tmp = dflist[0]["mean"]
            id = tmp.index
            plt.plot(tmp.index, tmp.values, ".", markersize=11, label="mean")
            tmp = dflist[0]["median"]
            plt.plot(tmp.index, tmp.values, ".", markersize=11, label="median")
        elif "all" in pairs and filter_len > 1:
            # TODO: Maybe add option to choose mean or median
            tmp = dflist[0]["mean"]
            id = tmp.index
            filter = int(filterid[0:2])
            label = "Filter %i, %i-%is" % (filter, minlags[i], endlags[i])
            plt.plot(tmp.index, tmp.values, ".", markersize=11, label=label)
        elif "all" not in pairs and filter_len == 1:
            max_len = 0
            for df, pair in zip(dflist, nice_pairs):
                tmp = df["mean"]
                #Find out longest time series to plot
                if len(tmp) > max_len:
                    max_len = len(tmp)
                    id = tmp.index
                plt.plot(tmp.index, tmp, ".", markersize=11, label=pair)
        else:
            max_len = 0
            for df, pair in zip(dflist, nice_pairs):
                tmp = df["mean"]
                #Find out longest time series to plot
                if len(tmp) > max_len:
                    max_len = len(tmp)
                    id = tmp.index
                label = ("Filter %i, %i-%is, %s" %
                        (int(filterid[0:2]), minlags[i], endlags[i], pair))
                plt.plot(tmp.index, tmp, label=label)

    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4,
               ncol=1, borderaxespad=0.)
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

    if not forcings:
        forcing = get_config_p(db, isref=True, name=1,
                               value='short_name', plugin='DefaultStations')
    else:
        forcing = forcings[0]
    dir = get_config_p(db, name=forcing, value='folder_name',
                       plugin='DefaultStations')
    name = get_config_p(db, name=forcing, value='forcing',
                        plugin='DefaultStations')
    unit = get_config_p(db, name=forcing, value='unit',
                        plugin='DefaultStations')
    type = get_config_p(db, name=forcing, value='plot_type',
                        plugin='DefaultStations')

    if ask:
        stas = ask_stations(dir)
    else:
        stas = [get_config_p(db, name=forcing, value='default_station',
                             plugin='DefaultStations')]

    data = get_data(dir, stas)
    data = data.loc[left:right]

    # TODO: Pass the color as argument?
    color = 'tab:blue'
    # Plot configurations
    if type == 'points':
        ax2.plot(data.index, data["Data"], ".", markersize=8, color=color)
    elif type == 'bars':
        ax2.bar(data.index, data["Data"], color=color)
    elif type == 'cumsum':
        ax2.bar(data.index, data["Data"].cumsum(), color=color)
        name = "Cumulative " + name.lower()
    elif type == 'errorbars':
        ax2.errorbar(data.index, data["Data"], yerr=data["Error"], fmt='o',
                     color=color)
    else:
        print("Unknown type parameter, using default.")
        ax2.plot(data.index, data["Data"], ".", markersize=8, color=color)

    if unit:
        ax2.set_ylabel(name + " in " + unit, color=color)
    else:
        ax2.set_ylabel(name, color=color)
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
        dir = get_config_p(db, name=forcing, value='folder_name',
                           plugin='DefaultStations')
        name = get_config_p(db, name=forcing, value='forcing',
                            plugin='DefaultStations')
        unit = get_config_p(db, name=forcing, value='unit',
                            plugin='DefaultStations')
        type = get_config_p(db, name=forcing, value='plot_type',
                            plugin='DefaultStations')

        if ask:
            stas = ask_stations(dir)
        else:
            stas = [get_config_p(db, name=forcing, value='default_station',
                                 plugin='DefaultStations')]

        data = get_data(dir, stas)
        data = data.loc[left:right]

        # TODO: Pass the color as argument?
        color = 'tab:green'
        # Plot configurations
        if type == 'points':
            ax3.plot(data.index, data["Data"], ".", markersize=8, color=color)
        elif type == 'bars':
            ax3.bar(data.index, data["Data"], color=color)
        elif type == 'cumsum':
            ax3.bar(data.index, data["Data"].cumsum(), color=color)
            name = "Cumulative " + name.lower()
        elif type == 'errorbars':
            ax3.errorbar(data.index, data["Data"], yerr=data["Error"], fmt='o',
                         color=color)
        else:
            print("Unknown type parameter, using default.")
            ax3.plot(data.index, data["Data"], ".", markersize=8, color=color)

        if unit:
            ax3.set_ylabel(name + " in " + unit, color=color)
        else:
            ax3.set_ylabel(name, color=color)
        ax3.tick_params(axis='y', labelcolor=color)
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))
        fig.autofmt_xdate()

        # Station list without the brackets
        stas_string = str(stas)[1:-1]
        if "all" in stas:
            subtitle = "%s data for all the stations" % name
        elif len(stas) == 1:
            subtitle = "%s data for station: %s" % (name, stas_string)
        else:
            subtitle = "%s data for stations: %s" % (name, stas_string)

        # For the case of two subplots with two y-axes
        if len(forcings) == 3:

            ax4 = ax3.twinx()

            forcing = forcings[2]
            # load forcing default values
            dir = get_config_p(db, name=forcing, value='folder_name',
                               plugin='DefaultStations')
            name = get_config_p(db, name=forcing, value='forcing',
                                plugin='DefaultStations')
            unit = get_config_p(db, name=forcing, value='unit',
                                plugin='DefaultStations')
            type = get_config_p(db, name=forcing, value='plot_type',
                                plugin='DefaultStations')

            if ask:
                stas = ask_stations(dir)
            else:
                stas = [get_config_p(db, name=forcing, value='default_station',
                                     plugin='DefaultStations')]

            data = get_data(dir, stas)
            data = data.loc[left:right]

            # TODO: Pass the color as argument?
            color = 'tab:red'
            # Plot configurations
            if type == 'points':
                ax4.plot(data.index, data["Data"], ".", markersize=8, color=color)
            elif type == 'bars':
                ax4.bar(data.index, data["Data"], color=color)
            elif type == 'cumsum':
                ax4.bar(data.index, data["Data"].cumsum(), color=color)
                name = "Cumulative " + name.lower()
            elif type == 'errorbars':
                ax4.errorbar(data.index, data["Data"], yerr=data["Error"], fmt='o',
                             color=color)
            else:
                print("Unknown type parameter, using default.")
                ax4.plot(data.index, data["Data"], ".", markersize=8, color=color)

            if unit:
                ax4.set_ylabel(name + " in " + unit, color=color)
            else:
                ax4.set_ylabel(name, color=color)
            ax4.tick_params(axis='y', labelcolor=color)
            # Forcing y-limit is maximal value plus 10% for extra space
            # TODO: Don't hardwire 10%
            max_val = data.loc[left:right].values.max()
            ax4.set_ylim(0, max_val*1.1)
            plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))
            fig.autofmt_xdate()

            # Station list without the brackets
            stas_string = str(stas)[1:-1]
            if "all" in stas:
                subtitle += "\n%s data for all the stations" % name
            elif len(stas) == 1:
                subtitle += "\n%s data for station: %s" % (name, stas_string)
            else:
                subtitle += "\n%s data for stations: %s" % (name, stas_string)
        plt.title(subtitle)


    # Prepare plot title
    title = 'Stretching, %s, ' % ",".join(components)
    if pairs[0] == 'all':
        title += "Average over all pairs\n"
    else:
        title += "Pairs: %s\n" % str(nice_pairs)[1:-1]
    for i, filterid in enumerate(filterids):
        title += ('Filter %d (%.2f - %.2f Hz), Lag time window %.1f - %.1fs \n' % (
                  int(filterid[0:2]), lows[i], highs[i], minlags[i], endlags[i]))

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
