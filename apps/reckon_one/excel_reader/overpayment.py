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
import collections
from apps.util.qbo_util import instance_check



def get_excel_reckon_invoice_overpayment(job_id,task_id):
    print("inside overpayment script")
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_invoice_overpayment"]

        file_prefix = str(job_id)
        files_directory = os.path.join(get_root_path('apps'), 'files/')
        filename = next((f for f in os.listdir(files_directory) if f.startswith(file_prefix)), None)
        if filename is None:
            return

        path = os.path.join(files_directory, filename)
        workbook = openpyxl.load_workbook(path)
        sheet_names = workbook.sheetnames
        receivemoney_data = pd.read_excel(path, 'Invoice Over Payment')

        grouped_data = receivemoney_data.groupby(["Reference"])

        reckon_coa1 = dbname["reckon_coa"].find({"job_id":job_id})
        reckon_coa = []
        for p1 in reckon_coa1:
            reckon_coa.append(p1)

        reckon_payment_method1 = dbname["reckon_payment_method"].find({"job_id":job_id})
        reckon_payment_method = []
        for p1 in reckon_payment_method1:
            reckon_payment_method.append(p1)


        coa1 = dbname['reckon_bank_account'].find({"job_id":job_id})
        coa = []
        for i2 in coa1:
            coa.append(i2)
 
        reckon_contact1 = dbname['reckon_contact'].find({"job_id":job_id})
        reckon_contact = []
        for i3 in reckon_contact1:
            reckon_contact.append(i3)

        
        reckon_item1 = dbname['reckon_item'].find({"job_id":job_id})
        reckon_item = []
        for i5 in reckon_item1:
            reckon_item.append(i5) 
        
        taxcode_reckon1 = dbname["taxcode_reckon"].find({"job_id":job_id})
        taxcode_reckon = []
        for p1 in taxcode_reckon1:
            taxcode_reckon.append(p1)
        
        for group_name, df_group in grouped_data:
            QuerySet={}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            instance_name=None
            
            for row_index, row in df_group.iterrows():
                date1=str(row['Date*']).split(" ")[0]
                transactiondate = datetime.strptime(date1, "%Y-%m-%d")
                transactiondate1=transactiondate.strftime("%Y-%m-%d")

                mainaccountuid=None
                for j1 in range(0,len(coa)):
                    if str(row["Bank Account*"]) == coa[j1]['BankName']:
                        mainaccountuid=coa[j1]["BankAccountID"]
                        break

                lineaccountuid=None
                
                for j2 in range(0,len(reckon_coa)):
                    if reckon_coa[j2]['Name'] == 'Accounts Receivable':
                        lineaccountuid=reckon_coa[j2]["Id"]
                        break
                        
                contactuid=None
                for s1 in range(0, len(reckon_contact)):
                    if row["Contact*"] == reckon_contact[s1]['FirstNameBranchName']:
                        contactuid = reckon_contact[s1]["ContactId"]
                        break
                    elif row["Contact*"] == reckon_contact[s1]['Description']:
                        contactuid = reckon_contact[s1]["ContactId"]
                        break
               
                QuerySet["BankAccountId"]= mainaccountuid
                QuerySet["ContactId"]= contactuid
                QuerySet["Reference"]= str(row['Reference']) if instance_check(instance_name,row['Reference'])!=None else None
                QuerySet["TransDate"]= transactiondate1
                QuerySet["Amount"]=instance_check(instance_name,row['Amount*'])
                QuerySet['AccountsReceivableCategoryId'] = lineaccountuid
                QuerySet['AllocateFullAmount']=False
                
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
        

def get_excel_reckon_bill_overpayment(job_id,task_id):
    print("inside overpayment script")
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_bill_overpayment"]

        file_prefix = str(job_id)
        files_directory = os.path.join(get_root_path('apps'), 'files/')
        filename = next((f for f in os.listdir(files_directory) if f.startswith(file_prefix)), None)
        if filename is None:
            return

        path = os.path.join(files_directory, filename)
        workbook = openpyxl.load_workbook(path)
        sheet_names = workbook.sheetnames
        receivemoney_data = pd.read_excel(path, 'Bill Over Payment')

        grouped_data = receivemoney_data.groupby(["Reference"])

        reckon_coa1 = dbname["reckon_coa"].find({"job_id":job_id})
        reckon_coa = []
        for p1 in reckon_coa1:
            reckon_coa.append(p1)

        reckon_payment_method1 = dbname["reckon_payment_method"].find({"job_id":job_id})
        reckon_payment_method = []
        for p1 in reckon_payment_method1:
            reckon_payment_method.append(p1)


        coa1 = dbname['reckon_bank_account'].find({"job_id":job_id})
        coa = []
        for i2 in coa1:
            coa.append(i2)
 
        reckon_contact1 = dbname['reckon_contact'].find({"job_id":job_id})
        reckon_contact = []
        for i3 in reckon_contact1:
            reckon_contact.append(i3)

        
        reckon_item1 = dbname['reckon_item'].find({"job_id":job_id})
        reckon_item = []
        for i5 in reckon_item1:
            reckon_item.append(i5) 
        
        taxcode_reckon1 = dbname["taxcode_reckon"].find({"job_id":job_id})
        taxcode_reckon = []
        for p1 in taxcode_reckon1:
            taxcode_reckon.append(p1)
        
        for group_name, df_group in grouped_data:
            QuerySet={}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            instance_name=None
            
            for row_index, row in df_group.iterrows():
                date1=str(row['Date*']).split(" ")[0]
                transactiondate = datetime.strptime(date1, "%Y-%m-%d")
                transactiondate1=transactiondate.strftime("%Y-%m-%d")

                mainaccountuid=None
                for j1 in range(0,len(coa)):
                    if str(row["Bank Account*"]) == coa[j1]['BankName']:
                        mainaccountuid=coa[j1]["BankAccountID"]
                        break

                lineaccountuid=None
                
                for j2 in range(0,len(reckon_coa)):
                    if reckon_coa[j2]['Name'] == 'Accounts Payable':
                        lineaccountuid=reckon_coa[j2]["Id"]
                        break
                        
                contactuid=None
                for s1 in range(0, len(reckon_contact)):
                    if row["Contact*"] == reckon_contact[s1]['FirstNameBranchName']:
                        contactuid = reckon_contact[s1]["ContactId"]
                        break
                    elif row["Contact*"] == reckon_contact[s1]['Description']:
                        contactuid = reckon_contact[s1]["ContactId"]
                        break
               
                QuerySet["BankAccountId"]= mainaccountuid
                QuerySet["ContactId"]= contactuid
                QuerySet["Reference"]= str(row['Reference']) if instance_check(instance_name,row['Reference'])!=None else None
                QuerySet["TransDate"]= transactiondate1
                QuerySet["Amount"]=instance_check(instance_name,row['Amount*'])
                QuerySet['AccountsPayableCategoryId'] = lineaccountuid
                QuerySet['AllocateFullAmount']=False
                
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
        