import requests
import pandas as pd
import multiprocessing


def read_csv(filename, col_names=None, cols=None, nas=None):
    """
    Reads the input file using Pandas read.csv
    :param filename: cms file with comma separated values
    :return: data, a pandas dataframe
    """
    data = pd.read_csv(filename, usecols=cols, na_values=nas, names=col_names, header=0,
                       converters={'PROD_SRVC_ID': lambda x: str(x)})
    return data


def getrx(ndc):
    """
    Uses Rxnorm Tranformer api to convert the NDC codes to rxcuis
    This helps in matching the two datasets on drug names.
    :param ndc: The NDC code (string format)
    :return: rxcui along with the ndc
    """
    url = 'https://ndc.terminology.tools/rxnorm/ndc/'
    header = {'Authorization': 'guest', }
    try:
        response = requests.get(url + ndc + '?history=false', headers=header)
        if response.status_code == 200:  # status code 200 implies that the request has succeeded in which case,
            rx = response.json()
            rxCUI = rx['rxcui']
            return ndc, rxCUI  # if yes returns ndc and corresponding rxcui
        else:  # for status codes other than 200, the status code
            return
    except requests.exceptions.RequestException as e:
        return


def multiprocess(data):
    """
    Makes multiple api requests at a time for the list of unique ndc codes using python
    multiprocessing.Pool.
    Creates a dictionary having ndc codes as keys and corresponding rxcuis as values
    :param data: pandas data frame/cms data
    :return: rx_dict a dictionary
    """
    pool = multiprocessing.Pool(processes=4)
    rx_dict = dict(pool.map(getrx, (ndc_list)))
    pool.close()
    pool.join()
    return rx_dict


def create_rx_column(data, rx_dict):
    """
    Using the ndc code dictionary, creates an additional column to hold the rxnorm codes for the
    corresponding ndc codes.
    :param data: cms data as a pandas data frame
    :param rx_dict: ndc dictionary
    :return: data frame with just the two columns 'DESYNPUF_ID', 'RXCUI'
    """
    data['RXCUI'] = data.apply(lambda row: rx_dict[row['PROD_SRVC_ID']], axis=1)  # (axis = 1) row wise
    return data[['DESYNPUF_ID', 'RXCUI']]


if __name__ == "__main__":
    filename = r"data\cms_diab_100.csv"
    cms_data = read_csv(filename)
    # create a list with unique NDC codes
    ndc_list = cms_data['PROD_SRVC_ID'].unique()
    # create a dictionary with the NDC codes as keys and rxcuis as values
    ndc_rx_dict = multiprocess(ndc_list)
    # create an additional column that will hold the respective rxcuis and drop duplicate rows
    data = create_rx_column(cms_data, ndc_rx_dict).drop_duplicates
    # write the dataframe to a csv file to use for further analysis
    data.to_csv(r"data\final_cms.csv", index=False)
