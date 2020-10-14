import pandas as pd
import os
import glob
import re

def ask_stations(dir):
    stas = []

    print("Choose any number of stations to be included.")
    print("Type in the name without the '.csv' ending.")
    os.system("ls %s" % forcing)
    print("You can also choose 'all'. End the list ")
    print("with hitting Enter without entering a station.")
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
    # TODO: Update doc string
    """
    Return specified daily precipitation data for the Hualien
    region. Files must be stored in the 'precipitation' folder.

    input:
        source: String indicating source of precipitation data
            'CWB' = Taiwanese Central Weather Bureau data
            'Cal' = Calibration data from NASA
            'HQ'  = High quality precipitation data from NASA

    output:
        Array with the precipitation data
    """
    if 'all' in stas:
        file_list = glob.glob("/%s/*.csv" % dir)
    else:
        file_list = []
        for sta in stas:
            path = os.path.join(dir, sta + ".csv")

    first = True
    for file in file_list:
        try:
            data_med = pd.read_csv(file, index_col=0, parse_dates=True,
                               header=None)
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


def get_dvv(mov_stack=10, comps="ZZ", filterid="1", pairs=None):
    """
    Return dvv data, already averaged over the specified parameters. Data
    structure has to be as in the standard msnoise settings.

    input:
        comps: List with components to average over
        mov_stack: Moving Stack Days used
        filterid: Filter used

    output:
        Array with the averaged dvv values
    """

    db = ms.connect()
    # Treat components and pairs input
    if pairs:
        pairs = pairs.split(",")
    else:
        pairs = ["all"]

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
    for pair in pairs:
        first = True
        for comp in comps:
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


def get_corr(mov_stack=10, comps="ZZ", filterid="1", pairs=None):
    """
    Return the correlation coefficients, averaged over the specified
    parameters. Data structure has to be as in the standard msnoise settings.

    input:
        comps: List with components to average over
        mov_stack: Moving Stack Days used
        filterid: Filter used

    output:
        Array with the averaged dvv values
    """

    db = ms.connect()
    # Treat components and pairs input
    if pairs:
        pairs = pairs.split(",")
    else:
        pairs = ["all"]

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
    for pair in pairs:
        first = True
        for comp in comps:
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


def get_dvv_mat(mov_stack=10, comps="ZZ", filterid="1", pairs=None):
    """
    Return dvv data, already averaged over the specified parameters. Input
    data is saved as coefficient matrices over time.

    input:
        comps: List with components to average over
        mov_stack: Moving Stack Days used
        filterid: Filter used
        pairs: Which station pairs to compute

    output:
        dvv_data: Relative velocity variation time series in Dataframe
        coeff_mat: Coefficient matrix averaged over given comps and pairs
    """

    db = ms.connect()
    #Treat components and pairs input
    if pairs:
        pairs = pairs.split(",")
    else:
        pairs = ["all"]

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

    for pair in pairs:
        first = True
        for comp in comps:
            filedir = os.path.join("STR_Mat","%s" % filterid,
                               "%03i_DAYS" % mov_stack, comp)
            #Either get all stations or only selected pairs
            if "all" in pairs:
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
    str_range = float(ms.get_config(db, "stretching_max"))
    nstr = int(ms.get_config(db, "stretching_nsteps"))
    alldeltas = []
    allcoeffs = coeff_mat.values
    deltas = 1 + np.linspace(-str_range, str_range, nstr)

    for i in range(allcoeffs.shape[0]):
        alldeltas.append(deltas[np.argmax(allcoeffs[i,:])])

    dvv_data = pd.DataFrame(alldeltas, index=coeff_mat.index)
    return dvv_data, coeff_mat


def get_filter_info(filterid):
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

    for filter in filterids:
        for filterdb in get_filters(db, all=True):
            if int(filterid[0:2]) == filterdb.ref:
                lows.append(float(filterdb.low))
                highs.append(float(filterdb.high))
                break

    return filterids, lows, highs, minlags, endlags


def nicen_up_pairs(pairs):
    """ Formats the pairs list into a better
    human-readable format for plotting.

    input:
        pairs: List of station pairs

    output:
        String of station pairs
    """
    #If there is no pair passed, pass keyword "all", else nicen them up
    if len(pairs) == 0:
        pairs = ["all"]
    else:
        nice_pairs = []
        for pair in pairs:
            new_pair = pair.replace("5K_","")
            #Get rid of SW0 part, for less crammed visuals
            new_pair = new_pair.replace("SW0", "")
            nice_pairs.append(new_pair)

    return pairs, nice_pairs
