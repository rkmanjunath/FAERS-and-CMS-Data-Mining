# FAERS Data Mining #

The objective is to identify adverse drug events (ADEs) in the CMS claims data 
with the aid of information from the US Food and Drug Administration (FDA) 
Adverse Event Reporting System (FAERS) database. This effort will evaluate the 
utility of CMS claims data for identifying potential adverse drug events and 
if successful will improve the timeliness of ADE detection. Some of the studies 
such as detecting association between Statin Use and Cancer (Mai Fujimoto, 2015), 
Retrospective Detection of Drug Safety Signals and Adverse Events in Electronic 
General Practice Records (Andrew Tomlin, 2012), Drug safety surveillance using 
de-identified EMR and claims data (PM, 2010) and Leveraging Food and Drug 
Administration Adverse Event Reports for the Automated Monitoring of Electronic 
Health Records in a Pediatric Hospital (Tang H, 2017) present several approaches 
that can be used.

## Data Used ##
* CMS 2008-2010 Data Entrepreneurs’ Synthetic Public Use Files (DE-SynPUF) for 
  Beneficiary Summary, Inpatient Claims and Prescription Drug events downloaded from 
  https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs/DE_Syn_PUF.html  
  The pdf *Centers for Medicare and Medicaid Services (CMS) Linkable 2008–2010 Medicare Data
  Entrepreneurs’ Synthetic Public Use File (DE-SynPUF)* has information regarding the files, 
  data elements and their descriptions.  
* FAERS quarterly ASCII files with demographic, drug and reaction information for the 
  years 2014 – 2017 downloaded from the following link.
  https://www.fda.gov/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/ucm082193.htm
  The pdf *ASC_NTS* has information regarding file and data element descriptions.
    
## Methods ##
The CMS files are in csv format and the FAERS are "$" delimited text files. The preprocessing 
is done using a sequence of bash commands. These are included in cms_cmds.txt and faers_cmds.txt. 
In brief, preprocessing for each category includes 
* Extracting the necessary features
* Merging the individual files, for example (all drug files to one final drug file)
* Sorting and eliminating duplicates (row wise)
* Joining the relevant files to get one file each in CMS and FAERS
* Sample files cms_diab_100.csv and faers_100.csv are in the data folder.

### Processing for individual diseases ###
The NDC codes list for different disease consitions can be obtained from data.gov. ndcdisease.csv
contains the diabetes NDC codes. The CMS master file (output of cms_cmds.txt) is processed using 
cms_diab_cmds.txt. This gives a sunset of CMS master file, that has beneficiaries who have been 
prescribed at least one of the diabetes drugs from the data.gov diabetes NDC codes list. The same
process can be followed to get data corresponding to several other conditions like, hypertension, 
depression, anxiety etc. The CMS file that results from this process and the final FAERS file become
input to the next step. 

### Creating files for data analysis ###
These files are then read in python via pandas. The code/pipeline is in preprocess_cms.py and 
preprocess_faers.py. The goal here is to match the two files on drug codes. The drug information 
in CMS/PDE file is represented as NDC codes whereas in FAERS, text strings are used to represent 
drug names. The conversion of NDC codes into Rx concepts/rxcui is achieved as below,
* For CMS data, the api used is NDC/RXNORM Transformer (https://ndc.terminology.tools/) from
  West Coast Informatics LLC. The code/pipeline is in preprocess_cms.py. A unique list of NDC 
  codes is created and multiple api calls are made to get the corresponding rxcuis. The output
  of this pipeline is a csv file containing beneficiary id and rxcuis. 
* For FAERS data, the api used is Rxnav Approximate Matching is used. More information is available 
  in https://rxnav.nlm.nih.gov/RxNormApproxMatch.html. The code/pipeline is in preprocess_faers.py.
  From FEARS data,the dosage and unit information is extracted from dose_vbm column using regex. 
  This information is concatenated with drugname and then api calls are made to the corresponding 
  rxcui. The output is a csv file that has primaryid and corresponding rxcuis. A sample output file,
  final_faers.csv is in the data folder.
  
### Data Analysis ###
* The two files can be joined to get matching patients with respect to drug combinations using bash
  join commands.   
* This file can then be input to any downstream analysis such as clustering, to see if the CMS 
  beneficiaries get clustered along with the FAERS patients that had an ADE. 
  
  

  






