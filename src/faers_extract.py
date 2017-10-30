import requests
import json
import os
from pymongo import MongoClient


def get_faers_data():
    """Uses Python rest api to retrieve documents from the FAERS drug event end point
     and prints out the documents. The function can be used during the initial analysis to understand the
     document structure
    :return: None
    """
    # params = {
    #     'apikey': api_key,
    #     'format': 'json'
    # }

    # URL = "https://api.fda.gov/drug/event.json?limit=1"
    URL = 'https://api.fda.gov/drug/event.json?search=receivedate:[20080101+TO+20080201]&count=receivedate'
    # URL = 'https://api.fda.gov/drug/event.json?search=receivedate:[20080101+TO+20080201]&limit=2'

    data = requests.get(URL).json()

    for result in data.get('results', []):
        print json.dumps(result, indent=2)
    return


def read_json(json_file):
    """Read FAERS ADE json files, creates a mongodb instance "faersdb" and inserts the ADE reports into
    ade_reports collection.
    :param json_file: string/file path. Drug event files in json format (downloaded from FAERS drug event endpoint.
    :return: None
    """
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.faersdb
    with open(json_file, 'r') as infile:
        data = json.load(infile)
    if "results" in data.keys():
        db.ade_reports.insert(data["results"])
    return


def filter_data(db, col_name):
    """Filters Adverse event reports on the following criteria, and inserts the resulting reports into another
    collection nlp_ade_reports.
    * The report contained Drug dosage text
    * Category of individual who submitted the report = health care professional(codes 1,2,3)
    * Drug Characterization = 1 (Suspect - the drug was considered by the reporter to be the cause of ADE)
    * Contains patient information and open fda fields
    :param db: string/name of the database (faersdb)
    :param col_name: string/name of the collection(ade_reports)
    :return: None
    """
    client = MongoClient('localhost', 27017)
    db = client.db
    collection = col_name
    cur = db.collection.find({"$and":
        [
            {"primarysource.qualification": {"$in": ["1", "2", "3"]}},
            {"patient.patientonsetage": {"$exists": True}},
            {"patient.patientonsetageunit": {"$exists": True}},
            {"patient.patientsex": {"$exists": True}},
            {"patient.drug" : {"$elemMatch": {"openfda": {"$exists": True},
                                                                "drugcharacterization": "1",
                                                                "drugdosagetext": {"$exists": True}}}}
        ]
    })
    for elem in cur:
        db.nlp_ade_reports.insert(elem)
    return


def extract_data(db, col):
    """ Extarcts relevant fields from collection nlp_ade_reports and inserts them into ade_fields collection.
    Different collections are used to store the data at different stages to facilitate iterative analysis.
    :param db: string/name of the database (faersdb)
    :param col: string/name of the collection(ade_reports)
    :return: None
    """
    client = MongoClient('localhost', 27017)
    db = client.db
    collection = col
    cur = db.collection.find(
        {}, {"patient.patientonsetage": True,
             "patient.patientonsetageunit": True,
             "patient.patientsex": True,
             "patient.drug.openfda.generic_name": True,
             "patient.drug.drugdosagetext": True,
             "patient.reaction.reactionmeddrapt": True, })

    for elem in cur:
        db.ade_fields.insert(elem)
    return


def get_files(dir_path):
    """Gives a list of all the files given a directory.

    :param dir_path: string/ directory path
    :return:list containing all the file names in the directory
    """
    file_lst = []
    for name in os.listdir(dir_path):
        file_lst.append(os.path.join(dir_path, name))
    return file_lst


if __name__ == "__main__":
    # get_faers_data(key)
     dir = r"C:\Users\Gowri-Nidhi\IdeaProjects\rkmanjunath-final-project\Drugevents"
    # files = get_files(dir)
    # for file in files:
    #     read_json(file)
    # filter_data()
    #extract_data()


