import json
import requests
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.qbo_util import instance_check




def add_excel_reckon_chart_of_account(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url1 = f"{base_url}/accounts"
        url2 = f"{base_url}/bankaccounts"

        excel_coa = dbname['excel_reckon_chart_of_account']
      
        x = excel_coa.find({"job_id":job_id})
        excel_coa1 = []
        for k in x:
            excel_coa1.append(k)

        coa1 = dbname['chart_of_account'].find({"job_id":job_id})
        coa = []
        for k1 in coa1:
            coa.append(k1)


        excel_coa1=excel_coa1
        
        for i in range(0,len(excel_coa1)):
            payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
            if excel_coa1[i]['TYPE'] not in ['Bank','Credit card','Credit Card']:
                _id=excel_coa1[i]['_id']
                task_id=excel_coa1[i]['task_id']
                instance_name=None
                excel_coa1[i]['AccountName']== instance_check(instance_name,excel_coa1[i]['AccountName']).replace(":","-")
                excel_coa1[i].pop("_id")
                excel_coa1[i].pop("TYPE")
                excel_coa1[i].pop("job_id")
                excel_coa1[i].pop("task_id")
                excel_coa1[i].pop("is_pushed")
                excel_coa1[i].pop("error")
                excel_coa1[i].pop("payload")
                excel_coa1[i].pop("BankAccountStatus")
                excel_coa1[i].pop("BulkElectronicPaymentSettings")
                excel_coa1[i].pop("Description")
                excel_coa1[i].pop("EFT")
                
                payload = json.dumps(excel_coa1[i])
                asyncio.run(post_data_in_reckon(url1, post_headers, payload,excel_coa,_id, job_id,task_id, excel_coa1[i]["AccountName"]))

            elif excel_coa1[i]['TYPE'] in ['Credit Card','Credit card']:
                excel_coa1[i]['AccountType']=2
                _id=excel_coa1[i]['_id']
                task_id=excel_coa1[i]['task_id']
                excel_coa1[i].pop("_id")
                excel_coa1[i].pop("TYPE")
                excel_coa1[i].pop("job_id")
                excel_coa1[i].pop("task_id")
                excel_coa1[i].pop("is_pushed")
                excel_coa1[i].pop("error")
                excel_coa1[i].pop("payload")
                excel_coa1[i].pop("Status")
                excel_coa1[i].pop("AccountCode")
                excel_coa1[i].pop("ParentAccountingCategoryId")
                excel_coa1[i].pop("BulkElectronicPaymentSettings")
                excel_coa1[i].pop("EFT")
                excel_coa1[i].pop("Hint")
                # excel_coa1[i].pop("TaxGroupId")
                
                payload = json.dumps(excel_coa1[i])
                asyncio.run(post_data_in_reckon(url2, post_headers, payload,excel_coa,_id, job_id,task_id, excel_coa1[i]["AccountName"]))

            elif excel_coa1[i]['TYPE']=='Bank':
                excel_coa1[i]['AccountType']=1

                _id=excel_coa1[i]['_id']
                task_id=excel_coa1[i]['task_id']
                excel_coa1[i].pop("_id")
                excel_coa1[i].pop("TYPE")
                excel_coa1[i].pop("job_id")
                excel_coa1[i].pop("task_id")
                excel_coa1[i].pop("is_pushed")
                excel_coa1[i].pop("error")
                excel_coa1[i].pop("payload")
                excel_coa1[i].pop("Status")
                excel_coa1[i].pop("AccountCode")
                excel_coa1[i].pop("AccountName")
                excel_coa1[i].pop("ParentAccountingCategoryId")
                excel_coa1[i].pop("Hint")
                # excel_coa1[i].pop("TaxGroupId")
                
                payload = json.dumps(excel_coa1[i])
                asyncio.run(post_data_in_reckon(url2, post_headers, payload,excel_coa,_id, job_id,task_id, excel_coa1[i]["BulkElectronicPaymentSettings"]['AccountName']))
    
    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)