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



def get_excel_reckon_receive_money(job_id,task_id):
    print("inside receive money script")
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_receive_money"]

        file_prefix = str(job_id)
        files_directory = os.path.join(get_root_path('apps'), 'files/')
        filename = next((f for f in os.listdir(files_directory) if f.startswith(file_prefix)), None)
        if filename is None:
            return

        path = os.path.join(files_directory, filename)
        workbook = openpyxl.load_workbook(path)
        sheet_names = workbook.sheetnames
        receivemoney_data = pd.read_excel(path, 'Receive Money')

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
            QuerySet={'AllocationSplit':[]}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            instance_name=None
            totalamount=0
            totaltax=0
            
            for row_index, row in df_group.iterrows():
                if instance_check(instance_name,row['Tax Amount']) == None:
                    totalamount=totalamount+(row['Amount']+0)
                elif instance_check(instance_name,row['Tax Amount']) != None:
                    totalamount=totalamount+(row['Amount']+row['Tax Amount'])
                
                date1=str(row['Date*']).split(" ")[0]
                transactiondate = datetime.strptime(date1, "%Y-%m-%d")
                transactiondate1=transactiondate.strftime("%Y-%m-%d")

                if row_index == 0:
                    line_row=1
                else:
                    line_row=row_index+1 
                
                mainaccountuid=None
                for j1 in range(0,len(coa)):
                    if str(row["Bank Account*"]) == coa[j1]['BankName']:
                        mainaccountuid=coa[j1]["BankAccountID"]
                        break

                lineaccountuid=None
                
                for j2 in range(0,len(reckon_coa)):
                    if str(int(row["Account"])) == reckon_coa[j2]['AccountCode']:
                        lineaccountuid=reckon_coa[j2]["Id"]
                        break
                        
                contactuid=None
                for s1 in range(0, len(reckon_contact)):
                    if row["Contact*"] == reckon_contact[s1]['FirstNameBranchName']:
                        print(row["Contact*"] == reckon_contact[s1]['FirstNameBranchName'])
                        contactuid = reckon_contact[s1]["ContactId"]
                        print(contactuid,"if")
                        break
                    elif row["Contact*"] == reckon_contact[s1]['Description']:
                        contactuid = reckon_contact[s1]["ContactId"]
                        print("elif")
                        break
               
                itemid=None
                for s11 in range(0, len(reckon_item)):
                    if row["Item"] == reckon_item[s11]['FullName']:
                        itemid = reckon_item[s11]["Id"]

                line_tax= None
                for j in range(0, len(taxcode_reckon)):
                    if row["Tax code"] == taxcode_reckon[j]['Name']:
                        line_tax = taxcode_reckon[j]['ID']
                        break
                    # elif taxcode_reckon[j]['Name'] == 'NTD':
                    #     line_tax = taxcode_reckon[j]['ID']
                    #     continue

                paymentmethodid= None
                for j2 in range(0, len(reckon_payment_method)):
                    if row["Payment method"] == reckon_payment_method[j2]['Description']:
                        paymentmethodid = reckon_payment_method[j2]['Id']
                        break
                    if row["Payment method"] == 'Check':
                        if reckon_payment_method[j2]['Description'] == 'Cheque':
                            paymentmethodid = reckon_payment_method[j2]['Id']
                            break
                

                QuerySet["BankAccountId"]= mainaccountuid
                QuerySet["ContactId"]= contactuid
                QuerySet["Reference"]= str(row['Reference']) if instance_check(instance_name,row['Reference'])!=None else None
                QuerySet["TransDate"]= transactiondate1
                QuerySet["Amount"]=instance_check(instance_name,row['Amount'])
                QuerySet["PaymentMethodId"] = paymentmethodid
                QuerySet["Details"] = instance_check(instance_name,row['Details'])
                
                QuerySet1={}

                QuerySet1["ChargeableItemId"]=itemid

                QuerySet1["Description"]=instance_check(instance_name,row['Description'])

                QuerySet1["Quantity"]=instance_check(instance_name,row['Qty']) if instance_check(instance_name,row['Qty'])!=None else 1

                QuerySet1["DiscountPercent"]=instance_check(instance_name,row['Discount'])

                QuerySet1["TaxAmount"]=round(row["Tax Amount"],2) if instance_check(instance_name,row['Tax Amount'])!=None else 0

                QuerySet1["TaxGroupId"]=line_tax if QuerySet1['TaxAmount']!=0 else None

                QuerySet1["Amount"]=round(QuerySet1["Quantity"]*instance_check(instance_name,row['Amount']),4)

                QuerySet1["AmountExTax"]=round(QuerySet1["Quantity"]*instance_check(instance_name,row['Amount']),4)

                QuerySet1["LineNo"]=line_row
                QuerySet1["UnitPricePrecision"]=2.0
                QuerySet1["AccountId"]=lineaccountuid
                
                QuerySet['AllocationSplit'].append(QuerySet1)

                QuerySet["Amount"]= round(totalamount,4)

                print(QuerySet,"QuerySet-----------------------")
                
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
        