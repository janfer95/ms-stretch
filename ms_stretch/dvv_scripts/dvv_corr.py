"""Plot dvv curves with correlation coefficients.

Plot velocity curves obtained by the stretching method with
their respective correlation coefficients in a subplot.

Example:

``msnoise plugin plot corr`` will plot all defaults.
"""

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

from matplotlib.dates import DateFormatter
from matplotlib.dates import MonthLocator

from msnoise.api import *
from ..api import get_dvv, get_filter_info, nicen_up_pairs


def main(mov_stack=10, components='ZZ', filterid='1', pairs=None, custom=False,
         show=False, outfile=None):

    db = connect()

    start, end, datelist = build_movstack_datelist(db)
    filterids, lows, highs, minlags, endlags = get_filter_info(filterid)
    # Since there is only one filter:
    filterid, low, high = filterids[0], lows[0], highs[0]
    minlag, endlag = minlags[0], endlags[0]

    pairs, nice_pairs = nicen_up_pairs(pairs, custom)

    if components.count(","):
        components = components.split(",")
    else:
        components = [components, ]

    #Plot one mov_stack with correlation data
    gs = gridspec.GridSpec(2, 1)
    fig = plt.figure(figsize=(12, 9))
    plt.subplots_adjust(bottom=0.06, hspace=0.3)
    dflist = []
    dflist_corr = []
    for pair in pairs:
        first = True
        for comp in components:

            filedir = os.path.join("STR","%s" % filterid,
                                   "%03i_DAYS" % mov_stack, comp)

            #Either get all stations or only selected pairs
            if "all" in pairs:
                listfiles = os.listdir(path=filedir)
            else:
               file = pair + ".csv"
               listfiles = [file]

            for file in listfiles:
                rf = os.path.join("STR","%s" % filterid,
                                  "%03i_DAYS" % mov_stack, comp, file)

                #Save the first df to be the reference
                if first:
                    df_med = pd.read_csv(rf, index_col=0,
                                        parse_dates=True).iloc[:,0].to_frame()
                    df_corr = pd.read_csv(rf, index_col=0,
                                         parse_dates=True).iloc[:,1].to_frame()
                    first = False
                    continue

                # Merge all the dataframes for later averaging
                df_temp = pd.read_csv(rf, index_col=0,
                                     parse_dates=True).iloc[:,0].to_frame()
                df_temp2 = pd.read_csv(rf, index_col=0,
                                      parse_dates=True).iloc[:,1].to_frame()
                df_med = pd.merge(df_med, df_temp, left_index=True,
                                 right_index=True, how='outer')
                df_corr = pd.merge(df_corr, df_temp2, left_index=True,
                                  right_index=True, how='outer')

        df_med.sort_values(by=['Date'])
        col1 = ((df_med.mean(axis=1)-1)*100).values
        col2 = ((df_med.median(axis=1)-1)*100).values
        data = {"mean": col1, "median": col2}
        dvv_data = pd.DataFrame(data, index=df.index)

        df_corr.sort_values(by=['Date'])
        col1 = df.mean(axis=1).values
        col2 = df.median(axis=1).values
        data = {"mean": col1, "median": col2}
        corr_data = pd.DataFrame(data, index=df.index)

        dflist.append(dvv_data)
        dflist_corr.append(corr_data)


    # Plot dvv mean and median or multiple dvv
    ax = plt.subplot(gs[0])

    if "all" in pairs:
        tmp = dflist[0]["mean"]
        plt.plot(tmp.index, tmp.values, ".", markersize=11, label="mean")
        tmp = dflist[0]["median"]
        plt.plot(tmp.index, tmp.values, ".", markersize=11, label="median")
    else:
        max_len = 0
        for df, pair in zip(dflist, nice_pairs):
            tmp = df["mean"]
            #Find out longest time series to plot
            if len(tmp) > max_len:
                max_len = len(tmp)
                id = tmp.index
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

    #Plot correlation as subplot
    plt.subplot(gs[1], sharex=ax)
    plt.title("Correlation coefficients for the stretching method ")
    print(df_corr)
    if "all" in pairs:
        tmp = dflist_corr[0]["mean"]
        plt.plot(tmp.index, tmp.values, ".", markersize=11, label="mean")
        tmp = dflist_corr[0]["median"]
        plt.plot(tmp.index, tmp.values, ".", markersize=11, label="median")
    else:
        max_len = 0
        for df, pair in zip(dflist_corr, nice_pairs):
            tmp = df["mean"]
            #Find out longest time series to plot
            if len(tmp) > max_len:
                max_len = len(tmp)
                id = tmp.index
            plt.plot(tmp.index, tmp, label=pair)
    #plt.plot(tmp2.index, df_corr.loc[tmp2.index].values)
    plt.ylabel('Correlation coefficient')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4,
               ncol=2, borderaxespad=0.)
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))
    fig.autofmt_xdate()
    if "all" in pairs:
        #Prepare station strings
        stations = str(nice_pairs)[1:-1]
        title = ('Stretching, %s, Filter %d (%.2f - %.2f Hz), '
                 'Lag time window %.1f - %.1fs') % \
                   (",".join(components), int(filterid[0:2]), low,
                    high, minlag, endlag) \
                + "\n Stations: %s" % stations
    else:
        title = ('Stretching, %s, Filter %d (%.2f - %.2f Hz), '
                 'Lag time window %.1f - %.1fs') % \
                   (",".join(components), int(filterid[0:2]), low,
                    high, minlag, endlag) \
                + "\n Average over all available stations"
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
