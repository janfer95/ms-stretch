"""
This plot shows the final output of MSNoise.


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



def main(mov_stack=None, components='ZZ', filterid='1', pairs=None,
         show=False, outfile=None):

    db = connect()

    start, end, datelist = build_movstack_datelist(db)

    if mov_stack != 0:
        mov_stacks = [mov_stack, ]
    else:
        mov_stack = get_config(db, "mov_stack")
        if mov_stack.count(',') == 0:
            mov_stacks = [int(mov_stack), ]
        else:
            mov_stacks = [int(mi) for mi in mov_stack.split(',')]

    filterids, lows, highs, minlags, endlags = get_filter_info(filterid)
    pairs, nice_pairs = nicen_up_pairs(pairs)

    if components.count(","):
        components = components.split(",")
    else:
        components = [components, ]

    gs = gridspec.GridSpec(len(mov_stacks), 1)
    fig = plt.figure(figsize=(12, 9))
    plt.subplots_adjust(bottom=0.06, hspace=0.3)


    for i, mov_stack in enumerate(mov_stacks):
        first_plot = True
        filter_len = len(filterids)
        for j, filterid in enumerate(filterids):
            dflist = []
            for pair in pairs:
                dvv_data = get_dvv(mov_stack=mov_stack, comps=components,
                                   filterid=filterid, pairs=pair)
                dflist.append(dvv_data)

            # Plot dvv mean and median or multiple dvv
            if first_plot:
                ax = plt.subplot(gs[i])
                first_plot = False

            # TODO: Maybe check for same filter, so that label can be shortened
            if pairs[0] == "all" and filter_len == 1:
                tmp = dflist[0]["mean"]
                id = tmp.index
                plt.plot(tmp.index, tmp.values, ".", markersize=11, label="mean")
                tmp = dflist[0]["median"]
                plt.plot(tmp.index, tmp.values, ".", markersize=11, label="median")
            elif pairs[0] == "all" and filter_len > 1:
                # TODO: Maybe add option to choose mean or median
                tmp = dflist[0]["mean"]
                id = tmp.index
                label = "Filter %i, %i-%is" % (int(filter), minlags[j], endlags[j])
                plt.plot(tmp.index, tmp.values, ".", markersize=11, label=label)
            elif pairs[0] != "all" and filter_len == 1:
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
                            (int(filter), minlags[j], endlags[j], pair))
                    plt.plot(tmp.index, tmp, label=pair)

        # Coordinate labels and grids
        left, right = id[0], id[-1]
        plt.xlim(left, right)
        plt.ylabel('dv/v (%)')
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))
        fig.autofmt_xdate()
        # Title and legend
        if mov_stack == 1:
            plt.title('1 Day Smoothing')
        else:
            plt.title('%i Days Smoothing' % mov_stack)
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4,
                   ncol=2, borderaxespad=0.)

    # Prepare plot title
    title = 'Stretching, %s \n' % ",".join(components)
    for i, filterid in enumerate(filterids):
        title += ('Filter %d (%.2f - %.2f Hz), Lag time window %.1f - %.1fs \n' % (
                  int(filterid[0:2]), lows[i], highs[i], minlags[i], endlags[i]))
    if pairs[0] == 'all':
        title += "Average over all pairs"
    else:
        title += "Pairs: %s" % str(nice_pairs)[1:-1]


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
