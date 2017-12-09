import pandas as pd
import re
import numpy as np
from suds.client import Client


def read_csv(filename, col_names=None, cols=None, nas=None):
    """
    Reads the input file using Pandas read.csv
    :param filename: cms file with comma separated values
    :return: data, a pandas dataframe
    """
    data = pd.read_csv(filename, usecols=range(0, 11), na_values=nas,
                       names=col_names, header=0, delimiter='$')
    return data


def split_dose_text(dosage_info):
    """
    Extracts dosage and text information from text using regex
    :param dosage_info: string
    :return: string
    """
    if pd.isnull(dosage_info):
        return
    else:
        unit_mg = "MG"
        s = re.findall(pattern="[\d.]{1,}[( |MILGRASU)]+", string=dosage_info)[:1]
        for i, value in enumerate(s):
            if 'MILLIGRAM' in s[i]:
                s[i] = s[i].replace('MILLIGRAM', unit_mg)
        s1 = ''.join(str(e) for e in s)
    return s1


def get_rxcui_string(s):
    """
    Uses Rxnav SOAP api to get rxcui by string/drug names using RxNorm_SOAP_getApproximateMatch
    https://rxnav.nlm.nih.gov/RxNormAPISOAP.html#uLink=RxNorm_SOAP_getApproximateMatch
    :param s: the search string/drug name
    :return: an array of RxNorm identifiers
    """
    _url = "http://rxnav.nlm.nih.gov/RxNormDBService.xml"
    _rxnav = Client(_url, faults=False)
    # s - the search string
    # 1 - maxEntries - the maximum amount of entries to be returned
    # 0 - return information for Rx terms that may or may not be suppressed
    try:
        rx = _rxnav.service.getApproximateMatch(s, 1, 0) # yeilds a tuple (response codes, rx_concepts)
        if rx[0] == 200 and len(rx[1]['rxMatchInfo']) > 0:
            # returns the first match/Rxcui
            return rx[1]['rxMatchInfo'][0]['RXCUI']
        else:
            return
    except Exception as e:
        print "Error: " + str(e)
        return


if __name__ == "__main__":
    filename = r"data\faers_100.txt"
    faers_data = read_csv(filename)
    # extract dosage and units from dose_vbm
    faers_data['dosage'] = faers_data['dose_vbm'].apply(split_dose_text)
    # extract the relevant features
    faers_drug_data = faers_data[["primaryid", "drugname", "dosage"]]
    # eliminate the duplicates
    faers_drug_data = faers_drug_data.drop_duplicates()
    # concatenate drugname, dosage and units
    faers_drug_data["dosagetxt"] = np.where(faers_drug_data.dosage.notnull(),
                                            faers_drug_data["drugname"] + " " + faers_drug_data["dosage"],
                                            faers_drug_data["drugname"])
    faers_drug_data = faers_drug_data[["primaryid", "dosagetxt"]]
    # convert the drugnames to rxcui via rxnav soap api
    faers_drug_data["rxcui"] = faers_drug_data.apply(lambda row: get_rxcui_string(row["dosagetxt"]), axis=1)
    final_data = faers_drug_data[["primaryid", "rxcui"]]
    # elimate duplicate rows (patient and rxcuis)
    final_data = final_data.drop_duplicates()
    # write to csv and use for further analysis
    final_data.to_csv(r"data\final_faers.csv", index=False)
