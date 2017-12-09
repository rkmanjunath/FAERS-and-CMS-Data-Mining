import requests
import pandas as pd
import numpy as np
from suds.client import Client
import multiprocessing


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
        response = requests.get(url + ndc + '?history=false', headers=header).json()
        if response.status_code == 200:  # status code 200 implies that the request has succeeded in which case,
            return ndc, response['rxcui']  # if yes returns ndc and corresponding rxcui
        else:  # for status codes other than 200, the status code
            print response.status_code, response.raise_for_status()  # and the message are returned.
    except requests.exceptions.RequestException as e:
        return "Error: " + str(e)


# def getrx(ndc):
#     url = 'https://ndc.terminology.tools/rxnorm/ndc/'
#     header = {'Authorization': 'guest', }
#     getRXCUI = requests.get(url + ndc + '?history=false', headers=header).json()
#     #rxcuiJSON = json.loads(getRXCUI.text, encoding="utf-8")
#     rxCUI = getRXCUI['rxcui']
#     # store[ndc] = rxCUI
#     print "inhere"
#     return ndc, rxCUI


def get_rxcui_string(s):
    """
    Uses Rxnav SOAP api to get rxcui by string/drug names using RxNorm_SOAP_getApproximateMatch
    https://ndc.terminology.tools/#/ndc#top
    https://rxnav.nlm.nih.gov/RxNormAPISOAP.html#uLink=RxNorm_SOAP_getApproximateMatch
    https://rxnav.nlm.nih.gov/RxNormAPISOAP.html#uLink=RxNorm_SOAP_findRxcuiByString
    :param s: the search string/drug name
    :return: an array of RxNorm identifiers
    """
    _url = "http://rxnav.nlm.nih.gov/RxNormDBService.xml"
    _rxnav = Client(_url)
    # 2 - maxEntries - the maximum amount of entries to be returned
    # 1 - return only information for terms contained in valid RxNorm concepts
    rx = _rxnav.service.getApproximateMatch(s, 2, 1)
    # rx = _rxnav.service.getApproximateMatch("Yaz", 2, 1)
    # print rx
    return rx


def read_csv(filename, col_names=None, cols=None, nas=None):
    """
    Reads the input file using Pandas read.csv
    :param filename: cms file with comma separated values
    :return: data, a pandas dataframe
    """
    data = pd.read_csv(filename, usecols=cols, na_values=nas, names=col_names, header=0,
                       converters={'PROD_SRVC_ID': lambda x: str(x)})
    # ndc_codes = data.iloc[:, 4:5]  # extract product service id/column holding ndc codes
    return data


def multiprocess(data):
    """
    Makes multiple api requests for the list of unique ndc codes using python multiprocessing.Pool.
    Creates a dictionary having ndc codes as keys and corresponding rxcuis as values
    :param data: pandas data frame/cms data
    :return: rx_dict a dictionary
    """
    ndc_list = data['PROD_SRVC_ID'].unique()
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
    :return: new data frame with an additional column for rxcuis
    """
    data['RXCUI'] = data.apply(lambda row: rx_dict[row['PROD_SRVC_ID']], axis=1)  # (axis = 1) row wise
    return data


if __name__ == "__main__":
    filename = r"C:\Users\Gowri-Nidhi\IdeaProjects\rkmanjunath-final-project\data\data.csv"
    names = ('DESYNPUF_ID', 'BENE_BIRTH_DT', 'BENE_DEATH_DT', 'BENE_SEX_IDENT_CD', 'PROD_SRVC_ID', 'QTY_DSPNSD_NUM',
             'ADMTNG_ICD9_DGNS_CD', 'ICD9_DGNS_CD_1', 'ICD9_DGNS_CD_2', 'ICD9_DGNS_CD_3', 'ICD9_DGNS_CD_4',
             'ICD9_DGNS_CD_5', 'ICD9_DGNS_CD_6', 'ICD9_DGNS_CD_7', 'ICD9_DGNS_CD_8', 'ICD9_DGNS_CD_9', 'ICD9_DGNS_CD_10'
             )
    cms_data = read_csv(filename, names)
    # ndc = "00456155001"
    # getrx(ndc)
    # len_df = len(cms_data['PROD_SRVC_ID'])
    # cms_data['RXCUI'] = pd.Series(np.random.randn(len_df), index=cms_data.index)
    ndc_rx_dict = multiprocess(cms_data)
    data = create_rx_column(cms_data, ndc_rx_dict)
    data.to_csv("final_cms.csv")
