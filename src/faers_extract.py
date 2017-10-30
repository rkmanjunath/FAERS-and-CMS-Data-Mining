import requests
import json
import os
from pymongo import MongoClient


def get_faers_data(text=" ", api_key="xBxthPuqSle59AwWI3GZZeaFOYZXrg2xxVh4BLBn"):
    """

    :param test:
    :param params:
    :return:
    """
    params = {
        'apikey': api_key,
        'text': text,
        'format': 'json'
    }

    # URL = "https://api.fda.gov/drug/event.json?limit=1"
    URL = 'https://api.fda.gov/drug/event.json?search=receivedate:[20080101+TO+20080201]&count=receivedate'
    # URL = 'https://api.fda.gov/drug/event.json?search=receivedate:[20080101+TO+20080201]&limit=2'

    data = requests.get(URL).json()

    for result in data.get('results', []):
        print json.dumps(result, indent=2)
    pass


def read_json(json_file):
    """

    :param json_file:
    :return:
    """
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.faersdb
    with open(json_file, 'r') as infile:
        data = json.load(infile)
    print data.keys()
    if "results" in data.keys():
        db.ade_reports.insert(data["results"])
    return


def filter_data():
    """

    :param db:
    :param collection:
    :return:
    """
    client = MongoClient('localhost', 27017)
    db = client.faersdb

    cur = db.ade_reports.find(
        {"patient.drug.patientonsetage": {"$exists": True},
         "patient.drug.patientonsetageunit": {"$exists": True},
         "patient.patientsex": {"$exists": True},
         "patient.drug.openfda": {"$exists": True},
         "primarysource.qualification": {"$in": ["1", "2", "3"]},
         "patient.drug.drugcharacterization": "1",
         "patient.drug.drugdosagetext": {"$exists": True},
         })
    for elem in cur:
        db.nlp_ade_reports.insert(elem)
    return


def extract_data():
    """

    :return:
    """
    client = MongoClient('localhost', 27017)
    db = client.faersdb
    cur = db.nlp_ade_reports.find(
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
    """

    :param path:
    :return:
    """
    file_lst = []
    for name in os.listdir(dir_path):
        file_lst.append(os.path.join(dir_path, name))
    return file_lst


if __name__ == "__main__":
    # get_faers_data()
    # dir = r"C:\Users\Gowri-Nidhi\IdeaProjects\rkmanjunath-final-project\Drugevents"
    # files = get_files(dir)
    # for file in files:
    #     read_json(file)
    filter_data()
    #extract_data()
