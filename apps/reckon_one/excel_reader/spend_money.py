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



def get_excel_reckon_spend_money(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_spend_money"]

        file_prefix = str(job_id)
        files_directory = os.path.join(get_root_path('apps'), 'files/')
        filename = next((f for f in os.listdir(files_directory) if f.startswith(file_prefix)), None)
        if filename is None:
            return

        path = os.path.join(files_directory, filename)
        workbook = openpyxl.load_workbook(path)
        sheet_names = workbook.sheetnames
        spendmoney_data = pd.read_excel(path, 'Spend Money')

        grouped_data = spendmoney_data.groupby(["Reference"])

        reckon_coa1 = dbname["reckon_coa"].find({"job_id":job_id})
        reckon_coa = []
        for p1 in reckon_coa1:
            reckon_coa.append(p1)
 
        reckon_contact1 = dbname['reckon_contact'].find({"job_id":job_id})
        reckon_contact = []
        for i3 in reckon_contact1:
            reckon_contact.append(i3)

        reckon_item1 = dbname['reckon_item'].find({"job_id":job_id})
        reckon_item = []
        for i5 in reckon_item1:
            reckon_item.append(i5) 
        
        coa1 = dbname['reckon_bank_account'].find({"job_id":job_id})
        coa = []
        for i2 in coa1:
            coa.append(i2)

        
        term1 = dbname['reckon_term'].find({"job_id":job_id})
        reckon_term = []
        for i in term1:
            reckon_term.append(i) 
        
        taxcode_reckon1 = dbname["taxcode_reckon"].find({"job_id":job_id})
        taxcode_reckon = []
        for p1 in taxcode_reckon1:
            taxcode_reckon.append(p1)

        reckon_payment_method1 = dbname["reckon_payment_method"].find({"job_id":job_id})
        reckon_payment_method = []
        for p1 in reckon_payment_method1:
            reckon_payment_method.append(p1)

        
        instance_name=None
        
        for group_name, df_group in grouped_data:
            QuerySet={'Allocations':[],'AllocationSplit':[]}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            instance_name=None
            totalamount=0
            totaltax=0
            
            for row_index, row in df_group.iterrows():
                print(row_index)
                totalamount=totalamount+(row['Amount'])
                totaltax=totaltax+(row['Tax Amount'])

                if row['Amount*'] == 'Non Taxed':
                    AmountTaxStatus=1
                elif row['Amount*'] == 'Gross (Tax Inclusive)':
                    AmountTaxStatus=2
                elif row['Amount*'] == 'Net (Tax Exclusive)':
                    AmountTaxStatus=3

                date1=str(row['Date*']).split(" ")[0]
                transactiondate = datetime.strptime(date1, "%Y-%m-%d")
                transactiondate1=transactiondate.strftime("%Y-%m-%d")

                if row_index == 0:
                    line_row=1
                else:
                    line_row=row_index+1

                
                mainaccountuid=None
                for j1 in range(0,len(coa)):
                    if str(row["Bank Account*"]).replace(":","-") == coa[j1]['BankName'].replace(":","-"):
                        mainaccountuid=coa[j1]["BankAccountID"]

                contactuid=None
                for s1 in range(0, len(reckon_contact)):
                    if row["Contact*"] == reckon_contact[s1]['FirstNameBranchName']:
                        if reckon_contact[s1]["IsSupplier"] == True:
                            contactuid = reckon_contact[s1]["ContactId"]
                            break
                    elif row["Contact*"] == reckon_contact[s1]['Description']:
                        if reckon_contact[s1]["IsSupplier"] == True:
                            contactuid = reckon_contact[s1]["ContactId"]
                            break

                itemid=None
                for s11 in range(0, len(reckon_item)):
                    if row["Item"] == reckon_item[s11]['FullName']:
                        itemid = reckon_item[s11]["ID"]


                accountid=None
                if int(row["Account"])==float(row["Account"]):
                    row["Account"]=str(int(row["Account"]))
                    
                for j3 in range(0,len(reckon_coa)):
                    if 'AccountCode' in reckon_coa[j3]:
                        if str(row["Account"]) == reckon_coa[j3]['AccountCode']:
                            accountid=reckon_coa[j3]["Id"]
                            break
                    else:
                        continue
                
                AccountsPayableCategoryId=None
                
                for s13 in range(0, len(reckon_coa)):
                    if reckon_coa[s13]['Name'] == 'Accounts Payable':
                        AccountsPayableCategoryId=reckon_coa[s13]["Id"]

                # termid=None
                # for s12 in range(0,len(reckon_term)):
                #     if row["project id"]== reckon_term[s12]['Name']:
                #         termid=reckon_term[s12]["Id"]

                line_tax= None
                for j in range(0, len(taxcode_reckon)):
                    if row["Tax code"] == taxcode_reckon[j]['Name']:
                        line_tax = taxcode_reckon[j]['ID']
                        break
                    elif taxcode_reckon[j]['Name'] == 'NTD':
                        line_tax = taxcode_reckon[j]['ID']
                        continue

                paymentmethodid= None
                for j2 in range(0, len(reckon_payment_method)):
                    if row["Payment method"] == reckon_payment_method[j2]['Description']:
                        paymentmethodid = reckon_payment_method[j2]['Id']
                        break
                    if row["Payment method"] == 'Check':
                        if reckon_payment_method[j2]['Description'] == 'Cheque':
                            paymentmethodid = reckon_payment_method[j2]['Id']
                            break
                    # else:
                    #     if reckon_payment_method[j2]['Description'] == 'Cheque':
                    #         paymentmethodid = reckon_payment_method[j2]['Id']
                    #         break
                    
                QuerySet["BankAccountId"]= mainaccountuid
                QuerySet['PaymentMethodId'] = paymentmethodid
                QuerySet["ContactId"]= contactuid if contactuid != None else None
                QuerySet["AllocateFullAmount"]= True
                QuerySet["TransDate"]= transactiondate1
                QuerySet["Reference"]= str(row['Reference'])
                QuerySet["Amount"]= round(totalamount,4)
                QuerySet['AccountsPayableCategoryId'] = AccountsPayableCategoryId
                
                if instance_check(instance_name,row['Amount*']) in ['Net (Tax Exclusive)',None]:
                    QuerySet1={}
                    QuerySet1["ChargeableItemId"]=itemid if itemid !=None else None
                    QuerySet1["AccountId"]=accountid if itemid ==None else None
                    QuerySet1["LineNo"]= row_index+1
                    QuerySet1['Description'] = instance_check(instance_name,row['Description']) 
                    QuerySet1['ProjectId'] = "00000000-0000-0000-0000-000000000000"
                    QuerySet1['UnitPriceIsTaxInclusive'] = False
                    QuerySet1['DiscountAccuracy'] = None
                    QuerySet1['DiscountPercent'] = None
                    QuerySet1['AmountAccuracy'] = None
                    QuerySet1['InvoiceDiscountedAmountExTax'] = None
                    QuerySet1['InvoiceDiscountedTaxAmount'] = None
                    QuerySet1["Quantity"]= instance_check(instance_name,row['Qty'])
                    QuerySet1["UnitPriceExTax"]= 0 if itemid== None else 1
                    QuerySet1["UnitPriceTax"]= 0 if itemid== None else 1
                    QuerySet1["TaxIsModified"]= True
                    QuerySet1["TaxGroupId"]= line_tax
                    QuerySet1["TaxAmount"]= None if instance_check(instance_name,row['Tax Amount'])==None else round(instance_check(instance_name,row['Tax Amount']),2)
                    QuerySet1["Amount"]= round(instance_check(instance_name,row['Amount']),4) if instance_check(instance_name,row['Amount'])!=None else 0
                    QuerySet1["AmountExTax"]= round(instance_check(instance_name,row['Amount'])-instance_check(instance_name,row['Tax Amount']),2) if instance_check(instance_name,row['Tax Amount'])!=None else round(instance_check(instance_name,row['Amount']),2)
                    QuerySet1["HasDataForPosting"]= True
                    QuerySet1["IsSubTotal"]= False
                    QuerySet1["IsParent"]= False
                    QuerySet['AllocationSplit'].append(QuerySet1)

            if QuerySet["ContactId"]!=None:
                collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
        