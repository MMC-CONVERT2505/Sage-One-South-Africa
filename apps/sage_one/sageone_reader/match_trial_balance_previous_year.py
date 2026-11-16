import traceback
from ast import Break
import requests
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import get_job_details
from apps.util.log_file import log_config
import datetime
from datetime import datetime, timedelta

def trial_balance_previous_report(job_id,task_id):
    print("trial_balance_previous_report=============")
    logging=log_config(job_id)
    
    try:

        logging.info(f"{job_id} inside trial_balance_final_report")
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()

        sage_trial_balance = dbname['sage_report_trial_balance']
        reckon_trial_balance = dbname['reckon_report_trial_balance']
        matched_trial_balance = dbname['matched_trial_previous_year_balance']
        
        sage_trial_balance = dbname["sage_report_trial_balance"].find({"job_id":job_id})
        sage_trial_balance1 = []
        for p4 in sage_trial_balance:
            sage_trial_balance1.append(p4)

        reckon_trial_balance = dbname["reckon_report_trial_balance"].find({"job_id":job_id})
        reckon_trial_balance1 = []
        for p4 in reckon_trial_balance:
            reckon_trial_balance1.append(p4)

        sage_coa = dbname["sage_coa"].find({"job_id":job_id})
        sage_coa1 = []
        for p7 in sage_coa:
            sage_coa1.append(p7)


        reckon_coa = dbname["reckon_coa"].find({"job_id":job_id})
        reckon_coa1 = []
        for p9 in reckon_coa:
            reckon_coa1.append(p9)

        
        for i in range(0,len(sage_trial_balance1)):
  
            for j in range(0,len(sage_coa1)):
                if sage_trial_balance1[i]['AccountId'] == sage_coa1[j]['ID']:
                    for m in range(0,len(reckon_coa1)):
                        if sage_coa1[j]['Name'].lower().strip() == reckon_coa1[m]['Name'].lower().strip():
                            
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["Income"]:
                                    for item in entry["ReportData"]["Income"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                if entry["ReportData"]["OtherIncome"]:
                                    for item in entry["ReportData"]["OtherIncome"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                if entry["ReportData"]["COGS"]:
                                    for item in entry["ReportData"]["COGS"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                     
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                if entry["ReportData"]["CurrentAssets_AccountsReceivable"]:
                                    for item in entry["ReportData"]["CurrentAssets_AccountsReceivable"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
                                
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                     
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                if entry["ReportData"]["Expenses"]:
                                    for item in entry["ReportData"]["Expenses"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                   "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                   "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                     
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                
                                if entry["ReportData"]["OtherExpenses"]:
                                    for item in entry["ReportData"]["OtherExpenses"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                
                                if entry["ReportData"]["CurrentAssets_Bank"]:
                                    for item in entry["ReportData"]["CurrentAssets_Bank"]:
                                        if reckon_coa1[m]['Name'].lower().strip() == item['Name'].lower().strip():
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                
                                if entry["ReportData"]["CurrentAssets_Other"]:
                                    for item in entry["ReportData"]["CurrentAssets_Other"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                            
                                
                                if entry["ReportData"]["NonCurrentAssets_Fixed"]:
                                    for item in entry["ReportData"]["NonCurrentAssets_Fixed"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                
                                if entry["ReportData"]["NonCurrentAssets_Other"]:
                                    for item in entry["ReportData"]["NonCurrentAssets_Other"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                    
                                if entry["ReportData"]["CurrentLiabilities_CreditCard"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_CreditCard"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                
                                if entry["ReportData"]["CurrentLiabilities_AccountsPayable"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_AccountsPayable"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                   "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                     
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                
                                if entry["ReportData"]["CurrentLiabilities_Other"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_Other"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                if entry["ReportData"]["NonCurrentLiabilities"]:
                                    for item in entry["ReportData"]["NonCurrentLiabilities"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                   "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                     
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                    
                                if entry["ReportData"]["CurrentLiabilities_Other"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_Other"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                   "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                     
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                    
                                if entry["ReportData"]["Equity"]:
                                    for item in entry["ReportData"]["Equity"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                    
                                

                                        # logging.info("Inserted")
                                        
                            
                            # elif 'Accounts Receivable' in xero_trial_balance1[i]['bankname']:
                            #     if 'Accounts Receivable' in qbo_coa1[m]['Name']:
                            #         document_to_insert = {
                            #             "AccountName": qbo_coa1[m]['FullyQualifiedName'],
                            #             "qbo_balance": float(qbo_coa1[m]['CurrentBalance']),
                            #             "xero_balance": -float(xero_trial_balance1[i]['credit']) if float(xero_trial_balance1[i]['credit']) != 0 else float(xero_trial_balance1[i]['debit']),
                            #             "job_id": f"{job_id}"
                            #         }

                            #         # Check if the document already exists in the collection
                            #         existing_document = matched_trial_balance.find_one({"AccountName": document_to_insert["AccountName"]})
                            #         logging.info(existing_document)
                            #         # Insert the document only if it doesn't exist in the collection
                            #         if existing_document is None:
                            #             matched_trial_balance.update_one(
                            #                 {"AccountName": document_to_insert["AccountName"]},
                            #                 {"$set": document_to_insert},
                            #                 upsert=True
                            #             )
                            #             logging.info("Document inserted successfully.")
                            #         else:
                            #             logging.info("Document already exists, skipping insertion.")

                            
                            # elif 'Accounts Payable' in xero_trial_balance1[i]['bankname']:
                            #     if 'Accounts Payable' in qbo_coa1[m]['Name']:
                            #         document_to_insert = {
                            #             "AccountName": qbo_coa1[m]['FullyQualifiedName'],
                            #             "qbo_balance": float(qbo_coa1[m]['CurrentBalance']),
                            #             "xero_balance": -float(xero_trial_balance1[i]['credit']) if float(xero_trial_balance1[i]['credit']) != 0 else float(xero_trial_balance1[i]['debit']),
                            #             "job_id": f"{job_id}"
                            #         }

                            #         # Check if the document already exists in the collection
                            #         existing_document = matched_trial_balance.find_one({"AccountName": document_to_insert["AccountName"]})
                            #         logging.info(existing_document)
                            #         # Insert the document only if it doesn't exist in the collection
                            #         if existing_document is None:
                            #             matched_trial_balance.update_one(
                            #                 {"AccountName": document_to_insert["AccountName"]},
                            #                 {"$set": document_to_insert},
                            #                 upsert=True
                            #             )
                            #             logging.info("Document inserted successfully.")
                            #         else:
                            #             logging.info("Document already exists, skipping insertion.")
        

                if sage_trial_balance1[i]['Name']== "Opening Balance and Tax Adjustments":
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "Opening Balance Equity":
                            print("Opening Balance Equity==============")
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["Equity"]:
                                    for item in entry["ReportData"]["Equity"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": "Opening Balance Equity","job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":"Opening Balance and Tax Adjustments",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                
                
                tax_provision_data = dbname["sage_report_trial_balance"].find_one({"job_id": job_id, "Name": "Tax Provision"})
                if tax_provision_data: 
                    if sage_trial_balance1[i]['Name'] == "Tax Provision":
                        for m in range(0,len(reckon_coa1)):
                            if reckon_coa1[m]["Name"]  == "GST Collected":
                                for entry in reckon_trial_balance1:
                                    if entry["ReportData"]["CurrentLiabilities_Other"]:
                                        for item in entry["ReportData"]["CurrentLiabilities_Other"]:
                                            if item['Name'] ==  "GST Collected":
                                                if not matched_trial_balance.find_one({"ReckonAccountName": "GST Collected","job_id": f"{job_id}"}):


                                                    matched_trial_balance.insert_one(
                                                        {
                                                        "ReckonAccountName": "GST Collected",
                                                        "SageAccountName":"Tax Provision",
                                                        "reckon_credit_balance": item['Credit'],
                                                        "reckon_debit_balance":item['Debit'],
                                                        "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                        "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                        "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                        "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                        "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                        
                                                        "job_id" :f"{job_id}"
                                                        }
                                                        )
                                                

                else:
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "GST Collected":
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["CurrentLiabilities_Other"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_Other"]:
                                        if item['Name'] ==  "GST Collected":
                                            if not matched_trial_balance.find_one({"ReckonAccountName": "GST Collected","SageAccountName":"Tax Provision","job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": "GST Collected",
                                                    "SageAccountName":"Tax Provision",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": 0,
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-0,2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )

                
                if sage_trial_balance1[i]['Name']== "Tax Payable":
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "GST Paid":
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["CurrentLiabilities_Other"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_Other"]:
                                        if item['Name'] == "GST Paid":
                                            if not matched_trial_balance.find_one({"ReckonAccountName": "GST Paid","job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": "GST Paid",
                                                    "SageAccountName":"Tax Payable",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                if sage_trial_balance1[i]['Name']== "Retained Income":
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "Retained Earnings Surplus/(Accumulated Losses)":
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["Equity"]:
                                    for item in entry["ReportData"]["Equity"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": "Retained Earnings Surplus/(Accumulated Losses)","job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":"Retained Income",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )

                if sage_trial_balance1[i]['Name']== "Retained Income (Opening Balance)":
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "Retained Earnings Surplus/(Accumulated Losses)":
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["Equity"]:
                                    for item in entry["ReportData"]["Equity"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            retail_data= matched_trial_balance.find_one({"ReckonAccountName": "Retained Earnings Surplus/(Accumulated Losses)","job_id": f"{job_id}"})
                                            if retail_data != None:
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":"Retained Income (Opening Balance)",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": retail_data.get("Diff"),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round(retail_data.get("Diff")-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                if sage_trial_balance1[i]['Name']== "Trade Receivables":
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "Accounts Receivable":
                            print("Opening Balance Equity==============")
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["CurrentAssets_AccountsReceivable"]:
                                    for item in entry["ReportData"]["CurrentAssets_AccountsReceivable"]:
                                        if item['Name']== "Accounts Receivable":
                                            if not matched_trial_balance.find_one({"ReckonAccountName": "Accounts Receivable","job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":"Trade Receivables",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                
                if sage_trial_balance1[i]['Name']== "Trade Payables":
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "Accounts Payable":
                            print("Opening Balance Equity==============")
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["CurrentLiabilities_AccountsPayable"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_AccountsPayable"]:
                                        if item['Name']=="Accounts Payable":
                                            if not matched_trial_balance.find_one({"ReckonAccountName": "Accounts Payable","job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":"Trade Payables",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                


                




    except Exception as ex:
        print(ex)
        logging.error(ex, exc_info=True)
        

def trial_balance_current_report(job_id,task_id):
    print("trial_balance_current_report=============")
    logging=log_config(job_id)
    
    try:

        logging.info(f"{job_id} inside trial_balance_final_report")
        start_date, end_date = get_job_details(job_id)
        dbname=get_mongodb_database()

        sage_trial_balance = dbname['sage_report_trial_balance_current']
        reckon_trial_balance = dbname['reckon_report_trial_balance_current']
        matched_trial_balance = dbname['matched_trial_current_year_balance']
        
        sage_trial_balance = dbname["sage_report_trial_balance_current"].find({"job_id":job_id})
        sage_trial_balance1 = []
        for p4 in sage_trial_balance:
            sage_trial_balance1.append(p4)

        reckon_trial_balance = dbname["reckon_report_trial_balance_current"].find({"job_id":job_id})
        reckon_trial_balance1 = []
        for p4 in reckon_trial_balance:
            reckon_trial_balance1.append(p4)

        sage_coa = dbname["sage_coa"].find({"job_id":job_id})
        sage_coa1 = []
        for p7 in sage_coa:
            sage_coa1.append(p7)


        reckon_coa = dbname["reckon_coa"].find({"job_id":job_id})
        reckon_coa1 = []
        for p9 in reckon_coa:
            reckon_coa1.append(p9)

        
        for i in range(0,len(sage_trial_balance1)):
  
            for j in range(0,len(sage_coa1)):
                if sage_trial_balance1[i]['AccountId'] == sage_coa1[j]['ID']:
                    for m in range(0,len(reckon_coa1)):
                        if sage_coa1[j]['Name'].lower().strip() == reckon_coa1[m]['Name'].lower().strip():
                            
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["Income"]:
                                    for item in entry["ReportData"]["Income"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                if entry["ReportData"]["OtherIncome"]:
                                    for item in entry["ReportData"]["OtherIncome"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                if entry["ReportData"]["COGS"]:
                                    for item in entry["ReportData"]["COGS"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                     
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                if entry["ReportData"]["CurrentAssets_AccountsReceivable"]:
                                    for item in entry["ReportData"]["CurrentAssets_AccountsReceivable"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
                                
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                     
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                if entry["ReportData"]["Expenses"]:
                                    for item in entry["ReportData"]["Expenses"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                   "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                   "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                     
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                
                                if entry["ReportData"]["OtherExpenses"]:
                                    for item in entry["ReportData"]["OtherExpenses"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                
                                if entry["ReportData"]["CurrentAssets_Bank"]:
                                    for item in entry["ReportData"]["CurrentAssets_Bank"]:
                                        if reckon_coa1[m]['Name'].lower().strip() == item['Name'].lower().strip():
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                
                                if entry["ReportData"]["CurrentAssets_Other"]:
                                    for item in entry["ReportData"]["CurrentAssets_Other"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                            
                                
                                if entry["ReportData"]["NonCurrentAssets_Fixed"]:
                                    for item in entry["ReportData"]["NonCurrentAssets_Fixed"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                
                                if entry["ReportData"]["NonCurrentAssets_Other"]:
                                    for item in entry["ReportData"]["NonCurrentAssets_Other"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                    
                                if entry["ReportData"]["CurrentLiabilities_CreditCard"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_CreditCard"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                                
                                if entry["ReportData"]["CurrentLiabilities_AccountsPayable"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_AccountsPayable"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                   "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                     
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                
                                if entry["ReportData"]["CurrentLiabilities_Other"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_Other"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                if entry["ReportData"]["NonCurrentLiabilities"]:
                                    for item in entry["ReportData"]["NonCurrentLiabilities"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                   "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                     
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                    
                                if entry["ReportData"]["CurrentLiabilities_Other"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_Other"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                   "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                     
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                    
                                if entry["ReportData"]["Equity"]:
                                    for item in entry["ReportData"]["Equity"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": reckon_coa1[m]['Name'],"job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":sage_coa1[j]['Name'],
            
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                    
                                

                                        # logging.info("Inserted")
                                        
                            
                            # elif 'Accounts Receivable' in xero_trial_balance1[i]['bankname']:
                            #     if 'Accounts Receivable' in qbo_coa1[m]['Name']:
                            #         document_to_insert = {
                            #             "AccountName": qbo_coa1[m]['FullyQualifiedName'],
                            #             "qbo_balance": float(qbo_coa1[m]['CurrentBalance']),
                            #             "xero_balance": -float(xero_trial_balance1[i]['credit']) if float(xero_trial_balance1[i]['credit']) != 0 else float(xero_trial_balance1[i]['debit']),
                            #             "job_id": f"{job_id}"
                            #         }

                            #         # Check if the document already exists in the collection
                            #         existing_document = matched_trial_balance.find_one({"AccountName": document_to_insert["AccountName"]})
                            #         logging.info(existing_document)
                            #         # Insert the document only if it doesn't exist in the collection
                            #         if existing_document is None:
                            #             matched_trial_balance.update_one(
                            #                 {"AccountName": document_to_insert["AccountName"]},
                            #                 {"$set": document_to_insert},
                            #                 upsert=True
                            #             )
                            #             logging.info("Document inserted successfully.")
                            #         else:
                            #             logging.info("Document already exists, skipping insertion.")

                            
                            # elif 'Accounts Payable' in xero_trial_balance1[i]['bankname']:
                            #     if 'Accounts Payable' in qbo_coa1[m]['Name']:
                            #         document_to_insert = {
                            #             "AccountName": qbo_coa1[m]['FullyQualifiedName'],
                            #             "qbo_balance": float(qbo_coa1[m]['CurrentBalance']),
                            #             "xero_balance": -float(xero_trial_balance1[i]['credit']) if float(xero_trial_balance1[i]['credit']) != 0 else float(xero_trial_balance1[i]['debit']),
                            #             "job_id": f"{job_id}"
                            #         }

                            #         # Check if the document already exists in the collection
                            #         existing_document = matched_trial_balance.find_one({"AccountName": document_to_insert["AccountName"]})
                            #         logging.info(existing_document)
                            #         # Insert the document only if it doesn't exist in the collection
                            #         if existing_document is None:
                            #             matched_trial_balance.update_one(
                            #                 {"AccountName": document_to_insert["AccountName"]},
                            #                 {"$set": document_to_insert},
                            #                 upsert=True
                            #             )
                            #             logging.info("Document inserted successfully.")
                            #         else:
                            #             logging.info("Document already exists, skipping insertion.")
        

                if sage_trial_balance1[i]['Name']== "Opening Balance and Tax Adjustments":
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "Opening Balance Equity":
                            print("Opening Balance Equity==============")
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["Equity"]:
                                    for item in entry["ReportData"]["Equity"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": "Opening Balance Equity","job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":"Opening Balance and Tax Adjustments",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                                                
                
                
                tax_provision_data = dbname["sage_report_trial_balance"].find_one({"job_id": job_id, "Name": "Tax Provision"})
                if tax_provision_data: 
                    if sage_trial_balance1[i]['Name'] == "Tax Provision":
                        for m in range(0,len(reckon_coa1)):
                            if reckon_coa1[m]["Name"]  == "GST Collected":
                                for entry in reckon_trial_balance1:
                                    if entry["ReportData"]["CurrentLiabilities_Other"]:
                                        for item in entry["ReportData"]["CurrentLiabilities_Other"]:
                                            if item['Name'] ==  "GST Collected":
                                                if not matched_trial_balance.find_one({"ReckonAccountName": "GST Collected","job_id": f"{job_id}"}):


                                                    matched_trial_balance.insert_one(
                                                        {
                                                        "ReckonAccountName": "GST Collected",
                                                        "SageAccountName":"Tax Provision",
                                                        "reckon_credit_balance": item['Credit'],
                                                        "reckon_debit_balance":item['Debit'],
                                                        "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                        "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                        "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                        "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                        "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                        
                                                        "job_id" :f"{job_id}"
                                                        }
                                                        )
                                                

                else:
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "GST Collected":
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["CurrentLiabilities_Other"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_Other"]:
                                        if item['Name'] ==  "GST Collected":
                                            if not matched_trial_balance.find_one({"ReckonAccountName": "GST Collected","SageAccountName":"Tax Provision","job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": "GST Collected",
                                                    "SageAccountName":"Tax Provision",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": 0,
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-0,2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )

                
                if sage_trial_balance1[i]['Name']== "Tax Payable":
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "GST Paid":
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["CurrentLiabilities_Other"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_Other"]:
                                        if item['Name'] == "GST Paid":
                                            if not matched_trial_balance.find_one({"ReckonAccountName": "GST Paid","job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": "GST Paid",
                                                    "SageAccountName":"Tax Payable",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                if sage_trial_balance1[i]['Name']== "Retained Income":
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "Retained Earnings Surplus/(Accumulated Losses)":
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["Equity"]:
                                    for item in entry["ReportData"]["Equity"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            if not matched_trial_balance.find_one({"ReckonAccountName": "Retained Earnings Surplus/(Accumulated Losses)","job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":"Retained Income",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )

                if sage_trial_balance1[i]['Name']== "Retained Income (Opening Balance)":
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "Retained Earnings Surplus/(Accumulated Losses)":
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["Equity"]:
                                    for item in entry["ReportData"]["Equity"]:
                                        if reckon_coa1[m]['AccountCode'] == item['Code']:
                                            retail_data= matched_trial_balance.find_one({"ReckonAccountName": "Retained Earnings Surplus/(Accumulated Losses)","job_id": f"{job_id}"})
                                            if retail_data != None:
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":"Retained Income (Opening Balance)",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": retail_data.get("Diff"),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round(retail_data.get("Diff")-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                if sage_trial_balance1[i]['Name']== "Trade Receivables":
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "Accounts Receivable":
                            print("Opening Balance Equity==============")
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["CurrentAssets_AccountsReceivable"]:
                                    for item in entry["ReportData"]["CurrentAssets_AccountsReceivable"]:
                                        if item['Name']== "Accounts Receivable":
                                            if not matched_trial_balance.find_one({"ReckonAccountName": "Accounts Receivable","job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":"Trade Receivables",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )
                
                if sage_trial_balance1[i]['Name']== "Trade Payables":
                    for m in range(0,len(reckon_coa1)):
                        if reckon_coa1[m]["Name"]  == "Accounts Payable":
                            print("Opening Balance Equity==============")
                            for entry in reckon_trial_balance1:
                                if entry["ReportData"]["CurrentLiabilities_AccountsPayable"]:
                                    for item in entry["ReportData"]["CurrentLiabilities_AccountsPayable"]:
                                        if item['Name']=="Accounts Payable":
                                            if not matched_trial_balance.find_one({"ReckonAccountName": "Accounts Payable","job_id": f"{job_id}"}):
                                                matched_trial_balance.insert_one(
                                                    {
                                                    "ReckonAccountName": reckon_coa1[m]['Name'],
                                                    "SageAccountName":"Trade Payables",
                                                    "reckon_credit_balance": item['Credit'],
                                                    "reckon_debit_balance":item['Debit'],
                                                    "sage_credit_balance": sage_trial_balance1[i]['Credit'],
                                                    "sage_debit_balance": sage_trial_balance1[i]['Debit'],
                                                    "reckon_balance": round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2),
                                                    "sage_balance": round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2),
                                                    "Diff":round((round(float(item['Debit']),2) if round(float(item['Debit']),2) !=0 else round(-float(item['Credit']),2))-(round(float(sage_trial_balance1[i]['Debit']), 2) if round(float(sage_trial_balance1[i]['Debit']), 2)!=0 else round(-float(sage_trial_balance1[i]['Credit']), 2)),2),
                                                    
                                                    "job_id" :f"{job_id}"
                                                    }
                                                    )                

    except Exception as ex:
        print(ex)
        logging.error(ex, exc_info=True)
        
