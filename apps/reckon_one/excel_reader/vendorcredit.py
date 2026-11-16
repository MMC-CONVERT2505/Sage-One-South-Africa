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



def get_excel_reckon_vendorcredit(job_id,task_id):
    try:
        print("get_excel_reckon_vendorcredit")
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_vendorcredit"]
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
        
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        bill_data = pd.read_excel(path, 'Supplier return')
        grouped_data = bill_data.groupby(["Reference code"])

        tax1 = dbname['taxcode_reckon'].find({"job_id":job_id})
        tax = []
        for i in tax1:
            tax.append(i) 

        coa1 = dbname['reckon_coa'].find({"job_id":job_id})
        coa = []
        for i in coa1:
            coa.append(i) 

        supplier1 = dbname['reckon_contact'].find({"job_id":job_id})
        supplier = []
        for i in supplier1:
            supplier.append(i) 

        
        item1 = dbname['reckon_item'].find({"job_id":job_id})
        item = []
        for i in item1:
            item.append(i) 
        
        term1 = dbname['reckon_term'].find({"job_id":job_id})
        term = []
        for i in term1:
            term.append(i) 

        template1 = dbname['reckon_vendorcredit_template'].find({"job_id":job_id})
        template = []
        for i in template1:
            template.append(i) 

        instance_name=None
        
        for group_index, df_group in grouped_data:
            QuerySet={'LineItems':[]}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            totaltax=0
            totalamount=0
            for row_index, row in df_group.iterrows():
                
                date1=str(row['Adjustment note date']).split(" ")[0]
                
                supplieruid=None
                for j2 in range(0,len(supplier)):
                    if row["Supplier"] == supplier[j2]['Description']:
                        supplieruid=supplier[j2]["ContactId"]
                        break    
                    elif row["Supplier"] == supplier[j2]['FirstNameBranchName']:
                        supplieruid=supplier[j2]["ContactId"]
                        break    
                        
                accountid=None
                if int(row["Account"])==float(row["Account"]):
                    row["Account"]=str(int(row["Account"]))
                    
                for j3 in range(0,len(coa)):
                    if 'AccountCode' in coa[j3]:
                        if str(row["Account"]) == coa[j3]['AccountCode']:
                            accountid=coa[j3]["Id"]
                            break
                    else:
                        continue
                
                itemid=None
                if instance_check(instance_name,row['Item']) !=None:
                    for j5 in range(0,len(item)):
                        if row["Item"] == item[j5]['FullName']:
                            itemid=item[j5]["Id"]
                            continue
                        elif row["Item"].replace(":","-") == item[j5]['FullName']:
                            itemid=item[j5]["Id"]
                            continue
                        elif row["Item"]+"-"+row["Account"] == item[j5]['FullName']:
                            itemid=item[j5]["Id"]
                            break
                    
                taxgroupid=None
                for j4 in range(0,len(tax)):
                    if row["Tax code"] == tax[j4]['Name']:
                        taxgroupid=tax[j4]["ID"]

                templateid=None
                for t5 in range(0,len(template)):
                    if template[t5]['Name'] == "Standard Supplier Adjustment Note":
                        templateid=template[t5]["ID"]
             
                if row['Amounts*'] == 'Non Taxed':
                    AmountTaxStatus=1
                elif row['Amounts*'] == 'Gross (Tax Inclusive)':
                    AmountTaxStatus=2
                elif row['Amounts*'] == 'Net (Tax Exclusive)':
                    AmountTaxStatus=3
                
                totaltax=totaltax+row['Tax Amount']
                totalamount=totalamount+row['Amount']
                
                QuerySet['SupplierId'] = supplieruid
                QuerySet['AmountTaxStatus'] = AmountTaxStatus
                QuerySet['Reference'] = str(row['Reference code'])
                QuerySet['Tax'] = round(totaltax,4) if totaltax!=0 else 0
                QuerySet['Amount'] = round((totalamount + totaltax),4)
                QuerySet['TemplateId'] = templateid
                # QuerySet['BillAmount'] = None
                # QuerySet['BIllDiscountAmount'] = None
                # QuerySet['BIllDiscountPercentage'] = None
                # QuerySet['BillTax'] = None
                QuerySet['Notes'] = instance_check(instance_name,row['NOTES'])
                QuerySet['SupplierCreditNoteDate'] = date1
                
                QuerySet1={}
                QuerySet1['LineNo'] = row_index+1
                QuerySet1['ChargeableItemId']=itemid
                QuerySet1['Item']=instance_check(instance_name,row['Item'])
                QuerySet1['Account']=instance_check(instance_name,row['Account'])
                # QuerySet1['DiscountPercent']=instance_check(instance_name,row['Discount'])
                QuerySet1['TaxAmount']=None if instance_check(instance_name,row['Tax Amount'])==0 else instance_check(instance_name,row['Tax Amount'])
                QuerySet1['InvoiceDiscountedTaxAmount']=QuerySet1['TaxAmount']
                    
                amount=round(instance_check(instance_name,row['Qty'])*instance_check(instance_name,row['Item price']),4)
                QuerySet1['Amount']=amount
                QuerySet1['InvoiceDiscountedAmountExTax']=QuerySet1['Amount']
                QuerySet1['AmountExTax']=amount
                QuerySet1['TaxIsModified'] =True
                QuerySet1['IsSubTotal']=False
                QuerySet1['AccountingCategoryId']=accountid
                QuerySet1['AccountId']=accountid if itemid==None else None
                QuerySet1['AccountName']=instance_check(instance_name,row['Account Name'])
                QuerySet1['Description']=instance_check(instance_name,row['Description'])
                QuerySet1['Quantity']=instance_check(instance_name,row['Qty'])
                QuerySet1['UnitPriceExTax']=instance_check(instance_name,row['Item price'])
                QuerySet1['UnitPriceTax']=instance_check(instance_name,row['Tax Amount'])
                QuerySet1['UnitPriceIsTaxInclusive']=False
                QuerySet1['TaxGroupId']=taxgroupid if QuerySet1['TaxAmount']!=None else None
                
                QuerySet['LineItems'].append(QuerySet1)
                
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
