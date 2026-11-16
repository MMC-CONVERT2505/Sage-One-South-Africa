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

def get_excel_reckon_journal(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_journal"]
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
        
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        journal_data = pd.read_excel(path, 'Journals')
        grouped_data = journal_data.groupby(["Summary"])


        tax1 = dbname["taxcode_reckon"].find({"job_id":job_id})
        tax = []
        for i in tax1:
            tax.append(i) 
        
        coa1 = dbname['reckon_coa'].find({"job_id":job_id})
        coa = []
        for i in coa1:
            coa.append(i) 

        coa2 = dbname['reckon_bank_account'].find({"job_id":job_id})
        bank = []
        for i in coa2:
            bank.append(i) 

        contact1 = dbname['reckon_contact'].find({"job_id":job_id})
        contact = []
        for i in contact1:
            contact.append(i) 

        instance_name=None
        
        for group_name, df_group in grouped_data:
            QuerySet={'Transactions':[]}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            AmountTaxStatus=1
            QuerySet['JournalStatus'] = 2
                
            for row_index, row in df_group.iterrows():
                if row['Amount*'] == 'Net (Tax Exclusive)':
                    AmountTaxStatus=3
                else:
                    AmountTaxStatus = 1
                
                account=None
                # account1=None
                if type(row["Account"]) in [int,float]:
                    if int(row["Account"])==float(row["Account"]):
                        row["Account"]=str(int(row["Account"]))
                    
                    for j3 in range(0,len(coa)):
                        if 'AccountCode' in coa[j3]:
                            if str(row["Account"]) == coa[j3]['AccountCode']:
                                account=coa[j3]["Id"]
                                break
                else:
                    for j3 in range(0,len(coa)):
                        if str(row["Account"]) == coa[j3]['Name']:
                            account=coa[j3]["Id"]
                            break
        
                # for j4 in range(0,len(bank)):
                #     if str(row["Account Name"]) == bank[j4]['BankName']:
                #         account1=bank[j4]["BankAccountID"]
                #         break
                    
                contactid = None
                for j1 in range(0,len(contact)):
                    if str(row['Contact']) == contact[j1]['Description']:
                        contactid = contact[j1]['ContactId']

                TaxGroupId = None
                for j3 in range(0,len(tax)):
                    if str(row['Tax code']) == str(tax[j3]['Name']):
                        TaxGroupId = tax[j3]['ID']

                QuerySet1={}
                date1=str(row['Journal Date*']).split(" ")[0]
                QuerySet['JournalNumber'] = row['Summary']
                QuerySet['Summary'] = row['Summary']
                QuerySet['JournalDate'] = date1
                QuerySet['AmountTaxStatus'] = AmountTaxStatus

                QuerySet1['AccountingCategoryId'] = account
                
                if instance_check(instance_name,row['Tax code']) not in [None,0]:
                    QuerySet1['TaxGroupId'] = TaxGroupId
                    QuerySet1['TransType']=2
                
                line_tax = 0
                if instance_check(instance_name,row['Tax']) not in [None,0]:
                    line_tax=round(instance_check(instance_name,row['Tax']),2)
                
                if row['Amount*'] == 'Net (Tax Exclusive)':
                    if instance_check(instance_name,row['Debit']) not in [None,0]:
                        QuerySet1['Debit'] = round(instance_check(instance_name,row['Debit']),4)
                        QuerySet1['TaxAmount'] = line_tax
                    elif instance_check(instance_name,row['Credit']) not in [None,0]:
                        QuerySet1['Credit'] = round(instance_check(instance_name,row['Credit']),4)
                        QuerySet1['TaxAmount'] = line_tax

                    
                else:
                    if instance_check(instance_name,row['Debit']) not in [None,0]:
                        QuerySet1['Debit'] = round(instance_check(instance_name,row['Debit']) + line_tax,4)
                        QuerySet1['TaxAmount'] = line_tax

                    elif instance_check(instance_name,row['Credit']) not in [None,0]:
                        QuerySet1['Credit'] = round(instance_check(instance_name,row['Credit']) + line_tax,4)
                        QuerySet1['TaxAmount'] = line_tax

                    
                if contactid != None:
                    QuerySet1['ContactId'] = contactid
                    QuerySet1['TransType'] = 1
                    
                QuerySet['Transactions'].append(QuerySet1)
            
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()