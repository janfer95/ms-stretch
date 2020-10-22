import pandas as pd
import os
import glob
import re

from msnoise.api import *

def ask_stations(dir):
    """
    Asks which forcing stations to be used for plotting. Applies only if
    default option was not chosen.

    Input:
        :type dir: str
        :param dir: The directory to look for the stations.

    Output:
        :type stas: List of str
        :param stas: List of file names with stations to be plotted.
    """

    stas = []
    print("--------------------------------------------")
    print("Choose any number of stations to be included.")
    print("Type in the name without the '.csv' ending.")
    print("Available stations:")
    print("\n")
    os.system("ls %s" % dir)
    print("\n")
    print("You can also choose 'all'. End the list ")
    print("with hitting Enter without entering a station.")
    print("--------------------------------------------")
    i = 1
    while(1):
        sta = input("%i. Station: " % i)
        if not sta:
            break
        stas.append(sta)
        if sta.lower() == 'all':
            break
        i += 1

    return stas


# TODO: Rewrite this in a better way
def get_pgv():
    df_pgv = pd.read_csv("PGV_data/WANRONG_EQ_INFO_LIST_PGV.txt")
    s = df["yy_jjul_hh_min"]
    date_list = []
    for date in s:
        fmt = '%y-%j-%H-%M'
        year, jday, hour, mts = date.split("_")
        jdate = year + "-" + jday + "-" + hour + "-" + mts
        date_list.append(datetime.datetime.strptime(jdate, fmt))

    df_pgv['Dates'] = date_list
    df_pgv.sort_values(by='Dates', inplace=True)


    #Find out which PGV stations to plot
    if pairs[0] == 'all':
        stas = ["1", "2", "3", "4", "5", "6", "7"]
    #Get all numbers from nice pairs string, convert to set for duplicates
    else:
        stas = list(set(re.findall(r'\d+', str(nice_pairs))))

    for sta in stas:
        #Extract the rows with respective station data
        df_sta = df.loc[df_pgv['sta'] == 'St' + sta]
        plt.plot(df_sta['Dates'], df_sta['PGV '], ".", label='G' + sta)


def get_data(dir, stas):
    """
    Get the specified forcing data, average it and return the data as a
    pandas DataFrame along with the corresponding dates.

    Input:
        :type dir: str
        :param dir: The directory to look for the stations.

        :type stas: List of strings
        :param stas: List of file names with stations to be plotted.


    Output:
        :type data: pandas DataFrame
        :param data: Daily averaged forcing DataFrame.
    """

    if 'all' in stas:
        file_list = glob.glob("%s/*.csv" % dir)
    else:
        file_list = []
        for sta in stas:
            path = os.path.join(dir, sta + ".csv")
            file_list.append(path)

    print("Getting data in %s directory." % dir)
    print("Stations: %s" % str(stas)[1:-1])
    first = True
    for file in file_list:
        try:
            data_med = pd.read_csv(file, index_col=0, parse_dates=True)
        except:
            print("{} was not found".format(path))
            data_med = None

        # The first file can't be concatenated with anything
        if first:
            data = data_med
            continue
        data = pd.concat([data, data_med])

    # Average if there are multiple values for one day
    data = data.groupby('Date').mean()
    data.sort_index()

    return data


def get_dvv(mov_stack=10, comps="ZZ", filterid="1", pairs_av=None):
    """
    Get the dvv data computed by the msnoise compute_stretch,
    average it over the specified parameters and return the data
    as a pandas DataFrame along with the corresponding dates.

    Note: The pairs_av argument does not quite correspond to the
    pairs argument in the plotting scripts. Here it stands for
    the pairs to average over, in the plotting script the pairs
    are the pairs to be plotted.

    Input:
        :type mov_stack: int
        :param mov_stack: Number of days that data is smoothed.

        :type comps: str
        :param comps: List of strings of components to be included.

        :type filterid: str
        :param filterid: Filter results to be plotted. Can contain
        stretching time window information.

        :type pairs_av: List of strings
        :param pairs_av: List of pairs to be averaged over.


    Output:
        :type dvv_data: pandas DataFrame
        :param dvv_data: Daily mean and median dvv data.
    """

    db = connect()
    # Treat components and pairs input
    if pairs_av:
        pairs_av = pairs_av.split(",")
    else:
        pairs_av = ["all"]

    # Accepts also string divided by commas
    if type(comps) is not list:
        if len(comps) == 1:
            comps = [comps]
        else:
            comps = comps.split(",")

    # Norm the filterid, add a 0 when needed
    idx = filterid.find("_")
    if len(filterid[:idx]) == 2:
        pass
    else:
        filterid = "0" + filterid

    # Average over certain pairs or over all
    # Usually only one pair or all are used
    for pair in pairs_av:
        first = True
        for comp in comps:
            filedir = os.path.join("STR","%s" % filterid,
                               "%03i_DAYS" % mov_stack, comp)
            #Either get all stations or only selected pairs
            if "all" in pairs_av:
                listfiles = os.listdir(path=filedir)
            else:
                file = pair + ".csv"
                listfiles = [file]

            for file in listfiles:
                rf = os.path.join("STR","%s" % filterid,
                                  "%03i_DAYS" % mov_stack, comp, file)

                # Save the first df to be the reference
                if first:
                    df = pd.read_csv(rf, index_col=0,
                                     parse_dates=True).iloc[:,0].to_frame()
                    first = False
                    continue

                # Merge Dataframes for later averaging
                df_temp = pd.read_csv(rf, index_col=0,
                                     parse_dates=True).iloc[:,0].to_frame()
                df = pd.merge(df, df_temp, left_index=True,
                              right_index=True, how='outer')

    df.sort_values(by=['Date'])
    col1 = ((df.mean(axis=1)-1)*100).values
    col2 = ((df.median(axis=1)-1)*100).values
    data = {"mean": col1, "median": col2}
    dvv_data = pd.DataFrame(data, index=df.index)
    return dvv_data


def get_dvv_mat(mov_stack=10, comps="ZZ", filterid="1", pairs_av=None):
    """
    Return dvv data, already averaged over the specified parameters. Input
    data is saved as coefficient matrices over time.

    Get the dvv data computed by the msnoise compute_stretch,
    average it over the specified parameters and return the data
    as a pandas DataFrame along with the corresponding dates. The
    averaging is done by first stacking each stretching
    coefficient matrix and then extract the dvv values.

    Note: The pairs_av argument does not quite correspond to the
    pairs argument in the plotting scripts. Here it stands for
    the pairs to average over, in the plotting script the pairs
    are the pairs to be plotted.

    Input:
        :type mov_stack: int
        :param mov_stack: Number of days that data is smoothed.

        :type comps: str
        :param comps: List of strings of components to be included.

        :type filterid: str
        :param filterid: Filter results to be plotted. Can contain
        stretching time window information.

        :type pairs_av: List of strings
        :param pairs_av: List of pairs to be averaged over.


    Output:
        :type dvv_data: pandas DataFrame
        :param dvv_data: Daily mean and median dvv data.

        :type coeff_mat: pandas DataFrame
        :param coeff_mat: Coefficient matrix averaged over given parameters.
    """

    db = connect()
    #Treat components and pairs input
    if pairs_av:
        pairs_av = pairs_av.split(",")
    else:
        pairs_av = ["all"]

    # Accepts also string divided by commas
    if type(comps) is not list:
        if len(comps) == 1:
            comps = [comps]
        else:
            comps = comps.split(",")

    #Norm the filterid, add a 0 when needed
    idx = filterid.find("_")
    if len(filterid[:idx]) == 2:
        pass
    else:
        filterid = "0" + filterid

    for pair in pairs_av:
        first = True
        for comp in comps:
            filedir = os.path.join("STR_Mat","%s" % filterid,
                               "%03i_DAYS" % mov_stack, comp)
            #Either get all stations or only selected pairs
            if "all" in pairs_av:
                listfiles = os.listdir(path=filedir)
            else:
                file = pair + ".csv"
                listfiles = [file]

            for file in listfiles:
                rf = os.path.join("STR_Mat","%s" % filterid,
                                  "%03i_DAYS" % mov_stack, comp, file)

                #Save the first df to be the reference
                if first:
                    df_med = pd.read_csv(rf, index_col=0,
                                        parse_dates=True)
                    first = False
                    continue

                #Start averaging over all components
                df_temp = pd.read_csv(rf, index_col=0,
                                     parse_dates=True)
                df_med = pd.concat([df_med, df_temp])

    coeff_mat = df_med.groupby('Date').mean()
    #Compute dvv from averaged coefficient matrix
    str_range = float(get_config(db, "stretching_max"))
    nstr = int(get_config(db, "stretching_nsteps"))
    alldeltas = []
    allcoeffs = coeff_mat.values
    deltas = 1 + np.linspace(-str_range, str_range, nstr)

    for i in range(allcoeffs.shape[0]):
        alldeltas.append(deltas[np.argmax(allcoeffs[i,:])])

    dvv_data = pd.DataFrame(alldeltas, index=coeff_mat.index)
    return dvv_data, coeff_mat


def get_corr(mov_stack=10, comps="ZZ", filterid="1", pairs_av=None):
    """
    Return the correlation coefficients, averaged over the specified
    parameters.

    Input:
        :type mov_stack: int
        :param mov_stack: Number of days that data is smoothed.

        :type comps: str
        :param comps: List of strings of components to be included.

        :type filterid: str
        :param filterid: Filter results to be plotted. Can contain
        stretching time window information.

        :type pairs_av: List of strings
        :param pairs_av: List of pairs to be averaged over.


    Output:
        :type corr_data: pandas DataFrame
        :param corr_data: Daily mean and median dvv data.
    """

    db = connect()
    # Treat components and pairs input
    if pairs_av:
        pairs_av = pairs_av.split(",")
    else:
        pairs_av = ["all"]

    # Accepts also string divided by commas
    if type(comps) is not list:
        if len(comps) == 1:
            comps = [comps]
        else:
            comps = comps.split(",")

    # Norm the filterid, add a 0 when needed
    idx = filterid.find("_")
    if len(filterid[:idx]) == 2:
        pass
    else:
        filterid = "0" + filterid

    # Average over certain pairs or over all
    # Usually only one pair or all are used
    for pair in pairs_av:
        first = True
        for comp in comps:
            filedir = os.path.join("STR","%s" % filterid,
                               "%03i_DAYS" % mov_stack, comp)
            #Either get all stations or only selected pairs
            if "all" in pairs_av:
                listfiles = os.listdir(path=filedir)
            else:
                file = pair + ".csv"
                listfiles = [file]

            for file in listfiles:
                rf = os.path.join("STR","%s" % filterid,
                                  "%03i_DAYS" % mov_stack, comp, file)

                # Save the first df to be the reference
                if first:
                    df = pd.read_csv(rf, index_col=0,
                                     parse_dates=True).iloc[:,1].to_frame()
                    first = False
                    continue

                # Merge Dataframes for later averaging
                df_temp = pd.read_csv(rf, index_col=0,
                                     parse_dates=True).iloc[:,1].to_frame()
                df = pd.merge(df, df_temp, left_index=True,
                              right_index=True, how='outer')

    df.sort_values(by=['Date'])
    col1 = df.mean(axis=1).values
    col2 = df.median(axis=1).values
    data = {"mean": col1, "median": col2}
    corr_data = pd.DataFrame(data, index=df.index)
    return corr_data


def get_filter_info(filterid):
    """
    Extract minlag, endlag, the lower and the higher frequency
    boundary of the given filter. For that either directly the
    input is used or the database. Filterid can be a list of
    filters. Lastly, if needed a fill up 0 is added to the
    filter for further processing.

    Input:
        :type filterid: List of str
        :param filterid: Filters to extract information from.

    Output:
        :type filterids: List of str
        :param filterids: Filter ids without extra info and padded 0.

        :type lows: List of floats
        :param lows: Lower frequency bound corresponding to filters.

        :type highs: List of floats
        :param highs: Higher frequency bound corresponding to filters.

        :type minlags: List of floats
        :param minlags: Start of stretching time window corresponding to filters.

        :type endlags: List of floats
        :param endlags: End of stretching time window corresponding to filters.
    """
    db = connect()

    filterids = []
    minlags = []
    endlags = []
    lows = []
    highs = []
    for filter in filterid:
        #Norm the filterid, add a 0 when needed
        idx = filter.find("_")
        if len(filter[:idx]) == 2:
            pass
        else:
            filterids.append("0" + filter)
        #Get stretching window information (try to get it of filter first)
        if len(filter) > 2:
            idx = filter.find("_")
            idx2 = filter.rfind("_")
            minlag = float(filter[idx+1:idx2])
            endlag = float(filter[idx2+1:])
        else:
            minlag = float(get_config(db, "dtt_minlag"))
            wwidth = float(get_config(db, "dtt_width"))
            endlag = minlag + wwidth
        minlags.append(minlag)
        endlags.append(endlag)

    for filterid in filterids:
        for filterdb in get_filters(db, all=True):
            if int(filterid[0:2]) == filterdb.ref:
                lows.append(float(filterdb.low))
                highs.append(float(filterdb.high))
                break

    return filterids, lows, highs, minlags, endlags


def get_config_p(session, isref=False, name=None, value=None,
                 isbool=False, plugin=None):
    """Get the value of one or all config bits from plugins from the database.
    A more specified version of the MSNoise get_config function

    :type isref: bool
    :param isref: if True, values can be accessed by the reference number
    :type session: :class:`sqlalchemy.orm.session.Session`
    :param session: A :class:`~sqlalchemy.orm.session.Session` object, as
        obtained by :func:`connect`
    :type name: str
    :param name: The name of the config bit to get. If isref, the reference
                 number can be used instead of the short name
    :type isbool: bool
    :param isbool: if True, returns True/False for config `name`. Defaults to
        False
    :type plugin: str
    :param plugin: Gives the name of the Plugin config to use. E.g.
        if "Amazing" is provided, MSNoise will try to load the "AmazingConfig"
        entry point. See :doc:`plugins` for details.

    :rtype: str or bool
    :returns: the value for `name`
    """
    for ep in pkg_resources.iter_entry_points(
            group='msnoise.plugins.table_def'):
        if ep.name.replace("Config", "") == plugin:
            table = ep.load()

    if isref:
        config = session.query(table).filter(table.ref == name).first()
    else:
        config = session.query(table).filter(table.short_name == name).first()
    if config is not None:
        if isbool:
            if config.value in [True, 'True', 'true', 'Y', 'y', '1', 1]:
                config = True
            else:
                config = False
        else:
            config = getattr(config, value)
    else:
        config = ''

    return config


def nicen_up_pairs(pairs, custom=False):
    """
    If no pairs are passed, all is returned to signal that
    it should be averaged over all pairs. Otherwise the
    pairs are nicened up for plotting. Custom options are also
    possible. A csv file "change_pairs.csv" with the substitions
    to be made has to be created.

    Input:
        :type pairs: List of str
        :param pairs: Pairs that are later to be plotted.

        :type custom: Boolean
        :param custom: Check file for custom options.

    Output:
        :type pairs: List of str
        :param pairs: Pairs that are later to be plotted, maybe all.

        :type nice_pairs: List of str
        :param nice_pairs: Pairs that are easier to read and fit better on plot.

    """

    if len(pairs) == 0:
        pairs = ["all"]
        nice_pairs = ["all"]
    elif custom:
        nice_pairs = []
        df = pd.read_csv("change_pairs.csv", header=None)
        df.fillna('', inplace=True)
        for pair in pairs:
            for i in range(len(df)):
                val = df.iloc[i,0]
                sub = df.iloc[i,1]
                if i == 0:
                    new_pair = pair.replace(val, sub)
                    continue
                new_pair = new_pair.replace(val, sub)
            nice_pairs.append(new_pair)
    else:
        nice_pairs = []
        for pair in pairs:
            # Change underscores to dots
            new_pair = pair.replace("_", ".", 1)
            new_pair = new_pair[::-1].replace("_", ".", 1)
            new_pair = new_pair[::-1]
            nice_pairs.append(new_pair)

    return pairs, nice_pairs
