
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


def put_excel_payroll_pay_setup(job_id, task_id):
    logging = log_config(job_id)
    try:
        dbname = get_mongodb_database()
        collection = dbname["put_excel_reckon_payroll_paysetup"]
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        paysetup_data = pd.read_excel(path, 'Put Pay Setup')
        grouped_data = paysetup_data

        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/payroll/payrollitems"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_payrollitems_from_api--> url-->{url} response status-->{response.status_code}")
        JsonResponse1 = response.json()


        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url1 = f"{base_url}/contacts"
        response = requests.request("GET", url1, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_contacts details_from_api--> url1-->{url1} response status-->{response.status_code}")
        JsonResponse2 = response.json()


        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        book_Id=base_url[27:]
        superfunds_url=f"https://api-v2.reckonone.com/{book_Id}/superfunds"
        response = requests.request("GET", superfunds_url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_superfunds_from_api--> url1-->{superfunds_url} response status-->{response.status_code}")
        data = response.json()


        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url1 = f"{base_url}/payroll/superitems"
        response = requests.request("GET", url1, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_superitems details_from_api--> url1-->{url1} response status-->{response.status_code}")
        data2 = response.json()


        
        instance_name = None
        for index, row in paysetup_data.iterrows():
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            QuerySet["employee_id"]=str(row['Employee Id'])
            
            base_rate_amt_val=None
            if str(row["Pay rate basis Hourly"])!="nan" and str(row["Base rate"])!="nan":
                base_rate_amt_val=row["Base rate"]
            else:
                base_rate_amt_val=row["Annual Rate"]

            amount_type=0
            if str(row["Pay rate basis Hourly"]) !="nan":
                amount_type=2
            else:
                amount_type=1


            QuerySet["BaseRateAmount"]=base_rate_amt_val
            QuerySet["BaseRateAmountType"]=amount_type

            Earnings=[]
            Allowance=[]
            Deductions=[]
            CompanyContributions=[]

            # Earning related payload creation
            earning1={}

            pay_item_Id=None
            for i in range(0, len(JsonResponse1)):
                if JsonResponse1[i]["FullName"]==str(row["Earnings Pay item"]):
                     pay_item_Id=JsonResponse1[i]["Id"]
                     break

            earning1["PayItemName"]=str(row["Earnings Pay item"])
            earning1["PayItemsEarningsId"]=pay_item_Id
            earning1["Qty"]=str(row["Earnings Quantity"])
            earning1["Rate"]=str(row["Earnings Rate"])
            if str(row["Earnings Pay item"]) != "nan":
                Earnings.append(earning1)

            pay_item_Id=None
            for i in range(0, len(JsonResponse1)):
                if JsonResponse1[i]["FullName"]==str(row["Earnings Pay item 2"]):
                     pay_item_Id=JsonResponse1[i]["Id"]
                     break

            earning2={}
            earning2["PayItemName"]=str(row["Earnings Pay item 2"])
            earning2["PayItemsEarningsId"]=pay_item_Id
            earning2["Qty"]=str(row["Earnings Quantity 2"])
            earning2["Rate"]=str(row["Earnings Rate 2"])
            if str(row["Earnings Pay item 2"]) != "nan":
                Earnings.append(earning2)
            

            pay_item_Id=None
            for i in range(0, len(JsonResponse1)):
                if JsonResponse1[i]["FullName"]==str(row["Earnings Pay item 3"]):
                     pay_item_Id=JsonResponse1[i]["Id"]
                     break

            earning3={}
            earning3["PayItemName"]=str(row["Earnings Pay item 3"])
            earning3["PayItemsEarningsId"]=pay_item_Id
            earning3["Qty"]=str(row["Earnings Quantity 3"])
            earning3["Rate"]=str(row["Earnings Rate 3"])
            if str(row["Earnings Pay item 3"]) != "nan":
                Earnings.append(earning3)

            pay_item_Id=None
            for i in range(0, len(JsonResponse1)):
                if JsonResponse1[i]["FullName"]==str(row["Earnings Pay item 4"]):
                     pay_item_Id=JsonResponse1[i]["Id"]
                     break

            earning4={}
            earning4["PayItemName"]=str(row["Earnings Pay item 4"])
            earning4["PayItemsEarningsId"]=pay_item_Id
            earning4["Qty"]=str(row["Earnings Quantity 4"])
            earning4["Rate"]=str(row["Earnings Rate 4"])
            if str(row["Earnings Pay item 4"]) != "nan":
                Earnings.append(earning4)

            pay_item_Id=None
            for i in range(0, len(JsonResponse1)):
                if JsonResponse1[i]["FullName"]==str(row["Earnings Pay item 5"]):
                     pay_item_Id=JsonResponse1[i]["Id"]
                     break

            earning5={}
            earning4["PayItemName"]=str(row["Earnings Pay item 5"])
            earning4["PayItemsEarningsId"]=pay_item_Id
            earning4["Qty"]=str(row["Earnings Quantity 5"])
            earning4["Rate"]=str(row["Earnings Rate 5"])
            if str(row["Earnings Pay item 5"]) != "nan":
                Earnings.append(earning5)

            pay_item_Id=None
            for i in range(0, len(JsonResponse1)):
                if JsonResponse1[i]["FullName"]==str(row["Earnings Pay item 6"]):
                     pay_item_Id=JsonResponse1[i]["Id"]
                     break

            earning6={}
            earning4["PayItemName"]=str(row["Earnings Pay item 6"])
            earning4["PayItemsEarningsId"]=pay_item_Id
            earning4["Qty"]=str(row["Earnings Quantity 6"])
            earning4["Rate"]=str(row["Earnings Rate 6"])
            if str(row["Earnings Pay item 6"]) != "nan":
                Earnings.append(earning6)


            #Allowance related payload creation
            allowance1={}

            pay_item_allowance_Id=None
            for i in range(0, len(JsonResponse1)):
                if JsonResponse1[i]["FullName"]==str(row["Allowance Pay item"]):
                     pay_item_allowance_Id=JsonResponse1[i]["Id"]
                     break

            allowance1["PayItemName"]=str(row["Allowance Pay item"])
            allowance1["PayItemsAllowancesId"]=pay_item_allowance_Id
            allowance1["Qty"]=str(row["Allowance Quantity"])
            allowance1["Rate"]=str(row["Allowance Rate"])
            if str(row["Allowance Pay item"]) != "nan":
                Allowance.append(allowance1)


            allowance2={}

            pay_item_allowance_Id=None
            for i in range(0, len(JsonResponse1)):
                if JsonResponse1[i]["FullName"]==str(row["Allowance Pay item 2"]):
                     pay_item_allowance_Id=JsonResponse1[i]["Id"]
                     break

            allowance2["PayItemName"]=str(row["Allowance Pay item 2"])
            allowance2["PayItemsAllowancesId"]=pay_item_allowance_Id
            allowance2["Qty"]=str(row["Allowance Quantity 2"])
            allowance2["Rate"]=str(row["Allowance Rate 2"])
            if str(row["Allowance Pay item"]) != "nan":
                Allowance.append(allowance2)

            earning_val=len(Earnings)
            

            #Deduction payload creation
            contact_Id1=None
            if str(row['Deductions Payee']) != "nan":
                for i in range(0, len(JsonResponse2)):
                    if JsonResponse2[i]["Description"]==str(row['Deductions Payee']):
                        contact_Id1=JsonResponse2[i]["ContactId"]
                        break

            deduction1={}

            deduction_pay_item_Id=None
            if str(row["Deductions Pay item"]) != "nan":
                for i in range(0, len(JsonResponse1)):
                    if JsonResponse1[i]["FullName"]==str(row["Deductions Pay item"]):
                        deduction_pay_item_Id=JsonResponse1[i]["Id"]
                        break

            deduction1["PayItemName"]=str(row["Deductions Pay item"])
            deduction1["PayItemsDeductionsId"]=deduction_pay_item_Id
            deduction1["Qty"]=str(row["Deductions Quantity"])
            deduction1["Rate"]=str(row["Deductions Rate"])
            deduction1["PayeeId"]=contact_Id1
            if str(row["Deductions Pay item"]) != "nan":
                Deductions.append(deduction1)


            deduction2={}

            contact_Id2=None
            if str(row['Deductions Payee 2']) != "nan":
                for i in range(0, len(JsonResponse2)):
                    if JsonResponse2[i]["Description"]==str(row['Deductions Payee 2']):
                        contact_Id2=JsonResponse2[i]["ContactId"]
                        break

            deduction_pay_item_Id=None
            for i in range(0, len(JsonResponse1)):
                if JsonResponse1[i]["FullName"]==str(row["Deductions Pay item 2"]):
                     deduction_pay_item_Id=JsonResponse1[i]["Id"]
                     break

            deduction2["PayItemName"]=str(row["Deductions Pay item 2"])
            deduction2["PayItemsDeductionsId"]=deduction_pay_item_Id
            deduction2["Qty"]=str(row["Deductions Quantity 2"])
            deduction2["Rate"]=str(row["Deductions Rate 2"])
            deduction2["PayeeId"]=contact_Id2
            if str(row["Deductions Pay item 2"]) != "nan":
                Deductions.append(deduction2)

            deduction_val=len(Deductions)


            #Company contributionss
            
            companycontributions1={}

            companycontributions_item_pay_item_Id=None
            if str(row["Company contributions Pay item"]) != "nan":
                for i in range(0, len(JsonResponse1)):
                    if JsonResponse1[i]["FullName"]==str(row["Company contributions Pay item"]):
                        companycontributions_item_pay_item_Id=JsonResponse1[i]["Id"]
                        break

            contact_Id_contribution_1=None
            if str(row['Company contributions Payee']) != "nan":
                for i in range(0, len(JsonResponse2)):
                    if JsonResponse2[i]["Description"]==str(row['Company contributions Payee']):
                        contact_Id_contribution_1=JsonResponse2[i]["ContactId"]
                        break

            companycontributions1["PayItemName"]=str(row["Company contributions Pay item"])
            companycontributions1["PayItemsCompanyContributionsId"]=companycontributions_item_pay_item_Id
            companycontributions1["Qty"]=str(row["Company contributions Quantity"])
            companycontributions1["Rate"]=str(row["Company contributions Rate"])
            companycontributions1["PayeeId"]=contact_Id_contribution_1
            if str(row["Deductions Pay item"]) != "nan":
                CompanyContributions.append(companycontributions1)


            companycontributions2={}

            companycontributions_item_pay_item_Id=None
            if str(row["Company contributions Pay item"]) != "nan":
                for i in range(0, len(JsonResponse1)):
                    if JsonResponse1[i]["FullName"]==str(row["Company contributions Pay item"]):
                        companycontributions_item_pay_item_Id=JsonResponse1[i]["Id"]
                        break

            contact_Id_contribution_2=None
            if str(row['Company contributions Payee 2']) != "nan":
                for i in range(0, len(JsonResponse2)):
                    if JsonResponse2[i]["Description"]==str(row['Company contributions Payee 2']):
                        contact_Id_contribution_2=JsonResponse2[i]["ContactId"]
                        break

            companycontributions2["PayItemName"]=str(row["Company contributions Pay item 2"])
            companycontributions2["PayItemsCompanyContributionsId"]=companycontributions_item_pay_item_Id
            companycontributions2["Qty"]=str(row["Company contributions Quantity 2"])
            companycontributions2["Rate"]=str(row["Company contributions Rate 2"])
            companycontributions2["PayeeId"]=contact_Id_contribution_2
            if str(row["Deductions Pay item 2"]) != "nan":
                CompanyContributions.append(companycontributions2)

            company_contributions_val=len(CompanyContributions)


            
            pay_setup={}
            if earning_val>=1:
                pay_setup["Earnings"]=Earnings
            else:
                pay_setup["Earnings"]=None

            allowance_val=len(Allowance)

            if allowance_val>=1:
                pay_setup["Allowances"]=Allowance
            else:
                pay_setup["Allowances"]=None

            if deduction_val>=1:
                pay_setup["Deductions"]=Deductions
            else:
                pay_setup["Deductions"]=None

            if company_contributions_val>=1:
                pay_setup["CompanyContributions"]=CompanyContributions
            else:
                pay_setup["CompanyContributions"]=None


            SuperAccounts=[]
            QuerySet4={}
            QuerySet5={}
            QuerySet6={}

            
            #for Super guarantee object
            if str(row["SUPERANNUATION ITEMS Super guarantee"]) != "nan" and str(row['Join date']) != "nan":
            
                QuerySet4['SuperFund']=row['Superannuation fund']
                for k in range(0,len(data['list'])):
                    if QuerySet4['SuperFund'] == data['list'][k]["organisationName"]:
                        print("sucessfully match")
                        QuerySet4['SuperFundId'] = data['list'][k]["id"]
                        break

                if str(row["Fund product"]) != "nan" or str(row["Fund product"]) !=" ":
                    QuerySet4['FundProduct']=str(row['Fund product'])
                else:
                    QuerySet4['FundProduct'] = None
                        
                if row['Member number'] != "nan" or row['Member number'] !=" ":
                    QuerySet4['Reference'] = int(row['Member number'])
                else:
                    QuerySet4['Reference'] = None
                    break
                
                QuerySet4['JoinDate'] = str(row['Join date']).split(" ")[0]
                QuerySet4["RateType"] = 2               

                QuerySet4['PayItemName']=row["SUPERANNUATION ITEMS Super guarantee"]
                for k in range(0,len(data2)):
                    if  QuerySet4['PayItemName'] ==data2[k]['Name']:
                        QuerySet4['PayItemsSupersId'] = data2[k]['PayItemId']
                        break
            
            if str(row["SUPERANNUATION ITEMS Super guarantee"]) != "nan" and str(row['Join date']) != "nan":
                SuperAccounts.append(QuerySet4)


            #for Salary sacrifice for super object
            if str(row["SUPERANNUATION ITEMS Salary sacrifice for super"]) != "nan" and str(row['Join date']) != "nan":
            
                QuerySet5['SuperFund']=row['Superannuation fund']
                for k in range(0,len(data['list'])):
                    if QuerySet5['SuperFund'] == data['list'][k]["organisationName"]:
                        print("sucessfully match")
                        QuerySet5['SuperFundId'] = data['list'][k]["id"]
                        break

                if str(row["Fund product"]) != "nan" or str(row["Fund product"]) !=" ":
                    QuerySet5['FundProduct']=str(row['Fund product'])
                else:
                    QuerySet5['FundProduct'] = None
                        
                if row['Member number'] != "nan" or row['Member number'] !=" ":
                    QuerySet5['Reference'] = int(row['Member number'])
                else:
                    QuerySet5['Reference'] = None
                    break
                
                QuerySet5['JoinDate'] = str(row['Join date']).split(" ")[0]
                QuerySet5["RateType"] = 2               

                QuerySet5['PayItemName']=row["SUPERANNUATION ITEMS Salary sacrifice for super"]
                for k in range(0,len(data2)):
                    if  QuerySet5['PayItemName'] ==data2[k]['Name']:
                        QuerySet5['PayItemsSupersId'] = data2[k]['PayItemId']
                        break
            
            if str(row["SUPERANNUATION ITEMS Salary sacrifice for super"]) != "nan" and str(row['Join date']) != "nan":
                SuperAccounts.append(QuerySet5)


            #for Salary sacrifice for super object
            if str(row["SUPERANNUATION ITEMS Other"]) != "nan" and str(row['Join date']) != "nan":
            
                QuerySet6['SuperFund']=row['Superannuation fund']
                for k in range(0,len(data['list'])):
                    if QuerySet6['SuperFund'] == data['list'][k]["organisationName"]:
                        print("sucessfully match")
                        QuerySet6['SuperFundId'] = data['list'][k]["id"]
                        break

                if str(row["Fund product"]) != "nan" or str(row["Fund product"]) !=" ":
                    QuerySet6['FundProduct']=str(row['Fund product'])
                else:
                    QuerySet6['FundProduct'] = None
                        
                if row['Member number'] != "nan" or row['Member number'] !=" ":
                    QuerySet6['Reference'] = int(row['Member number'])
                else:
                    QuerySet6['Reference'] = None
                    break
                
                QuerySet6['JoinDate'] = str(row['Join date']).split(" ")[0]
                QuerySet6["RateType"] = 2               

                QuerySet6['PayItemName']=row["SUPERANNUATION ITEMS Other"]
                for k in range(0,len(data2)):
                    if  QuerySet6['PayItemName'] ==data2[k]['Name']:
                        QuerySet6['PayItemsSupersId'] = data2[k]['PayItemId']
                        break
            
            if str(row["SUPERANNUATION ITEMS Other"]) != "nan" and str(row['Join date']) != "nan":
                SuperAccounts.append(QuerySet6)


            super_value={"SuperAccounts":SuperAccounts}
            pay_setup["Supers"]=super_value

         
            QuerySet["PaySetup"]=pay_setup

            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()






