import traceback
from ast import Break
import os
import requests
import pandas as pd
import openpyxl

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from flask.helpers import get_root_path
from datetime import datetime
import math 
from apps.util.qbo_util import instance_check


def get_excel_journal(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_journal"]
        payload, base_url, headers = get_settings_myob(job_id)
        
        tax_url = f"{base_url}/GeneralLedger/TaxCode"
        taxresponse = requests.request("GET", tax_url, headers=headers, data=payload)
        taxJsonResponse = taxresponse.json()
        taxJsonResponse1 = taxJsonResponse["Items"]
        
        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
        
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        journal_data = pd.read_excel(path, 'Journals')
        grouped_data = journal_data.groupby(["Reference number"])


        x = dbname["taxcode_myob"].find({"job_id":job_id})
        arr = []
        for i in x:
            arr.append(i) 
        
        job1 = dbname['job'].find({"job_id":job_id})
        job = []
        for i in job1:
            job.append(i) 

        coa1 = dbname['chart_of_account'].find({"job_id":job_id})
        coa = []
        for i in coa1:
            coa.append(i) 

        instance_name=None
        for group_name, df_group in grouped_data:
            QuerySet={'Lines':[]}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
                
            for row_index, row in df_group.iterrows():
                QuerySet1={}
                date1=str(row['Date']).split(" ")[0]
                transactiondate = datetime.strptime(date1, "%Y-%m-%d")
                transactiondate1=transactiondate.strftime("%Y-%m-%d")
                
                QuerySet['Memo'] = instance_check(instance_name,row["Description of transaction"])
                QuerySet['DisplayID'] = str(instance_check(instance_name,row["Reference number"]))[-13:]
                QuerySet['DateOccurred'] = transactiondate1
                # QuerySet['IsTaxInclusive'] = False if row["Amounts are"] == 'Tax exclusive' else True
                QuerySet['IsTaxInclusive'] = True

                jobuid={}
                for i1 in range(0,len(job)):
                    if job[i1]["Name"]==row['Job']:
                        jobuid["UID"]=job[i1]["UID"]

                tax_code={}
                for i2 in range(0,len(taxJsonResponse1)):
                    if row['Tax Code']==taxJsonResponse1[i2]["Code"]:
                        tax_code["UID"]=taxJsonResponse1[i2]["UID"]
                        break
                    elif row['Tax Code']==taxJsonResponse1[i2]["Description"]:
                        tax_code["UID"]=taxJsonResponse1[i2]["UID"]
                        break
                    else:
                        if taxJsonResponse1[i2]["Code"]=="N-T":
                            tax_code["UID"]=taxJsonResponse1[i2]["UID"]

                mainaccountuid={}
                for j1 in range(0,len(coa)):
                    if str(row["Account"]) == coa[j1]['DisplayId']:
                        mainaccountuid["UID"]=coa[j1]["UID"]


                QuerySet1['Account'] = mainaccountuid
                QuerySet1['Job'] = None if jobuid=={} else jobuid
                QuerySet1['Memo'] = instance_check(instance_name,row["Description"])
                QuerySet1['TaxCode'] = tax_code
                # QuerySet1['Amount'] = float(row["Debit Amount"]) if math.isnan(row["Credit Amount"]) else float(row["Debit Amount"])
                # QuerySet1['IsCredit'] = False if math.isnan(row["Credit Amount"]) else True
                QuerySet1['Amount'] = float(row["Debit Amount"]) if row["Credit Amount"]==0 else float(row["Credit Amount"])
                QuerySet1['IsCredit'] = False if row["Credit Amount"]==0 else True
                QuerySet['Lines'].append(QuerySet1)
            
            collection.insert_one(QuerySet)


    except Exception as ex:
        traceback.print_exc()