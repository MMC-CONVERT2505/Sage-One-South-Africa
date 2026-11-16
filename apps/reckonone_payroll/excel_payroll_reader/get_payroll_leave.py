import traceback
from ast import Break
import os
import requests
import pandas as pd
import openpyxl
import math

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from flask.helpers import get_root_path
from datetime import datetime
import math
import collections
from apps.util.qbo_util import instance_check


def get_excel_payroll_leave(job_id, task_id):
    print("inside get_excel_payroll_leave**********")
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_payroll_leave"]
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        leave_data = pd.read_excel(path, 'Pay Item Leave')
        grouped_data = leave_data
        account_data = list(dbname["reckon_coa"].find({"job_id":job_id}))


        instance_name = None
        for group_index, row in grouped_data.iterrows():
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None

            leaveitemtype_map = {
                    "Annual": 12,
                    "Personal": 13,
                    "LongService": 14,
                    "OtherLeave": 15
                    }
            
            leave_subtype_map = {
                "Paid Parental Leave":48,
                "Workers' Compensation":49,
                "Ancillary and Defence Leave":47,
                "Time off in Lieu":50,
                "Other":51

                }
            
            leaveitemtype= None
            if str(row["Leave type"]).strip() in leaveitemtype_map:
                leaveitemtype = leaveitemtype_map[str(row["Leave type"]).strip()]
            else:
                leaveitemtype = 0

            leave_subtype= None

            if str(row["Leave sub-type"]).strip() in leave_subtype_map:   
                leave_subtype = leave_subtype_map[str(row["Leave sub-type"]).strip()]
                
            else:
                leave_subtype=None


            accrualtype_map = {
                    "Per pay": 1,
                    "Per time worked": 2,
                    "Per annum": 3,
                            }
            account=None
            if str(row["Expense"]) != "nan" or str(row["Expense"]) !=" ":
                for j3 in range(0,len(account_data)):
                    if str(row["Expense"]) == account_data[j3]['Name']:
                        account=account_data[j3]["Id"]
                
                
            accrualtypeId = None
            if str(row["DEFAULT RATES (OPTIONAL) Accrual period"]) in accrualtype_map:
                accrualtypeId = accrualtype_map[str(row["DEFAULT RATES (OPTIONAL) Accrual period"])]
            else:
                accrualtypeId = 0


        
            if leaveitemtype == 12:
                QuerySet['IncludeLeaveLoadingInSuperCalculation'] = str(row['Include leave loading amounts in super calculations'])
                
                if str(row['Leave loading (%)'])=='nan' or str(row['Leave loading (%)'])== ' ':
                    QuerySet['LeaveLoadingPercentage'] = 0
                else:
                    QuerySet['LeaveLoadingPercentage'] = str(row['Leave loading (%)'])
            

            if str(row['Maximum accumulation (hours)'])=='nan' or str(row['Maximum accumulation (hours)'])== ' ':
                QuerySet['Maximum'] = '0' 
            else:
                QuerySet['Maximum'] = str(row['Maximum accumulation (hours)'])    


            QuerySet['LeaveItemType'] = leaveitemtype
            QuerySet['Name'] = str(row['Leave item name']).strip()
            QuerySet['Description'] = str(row["Description (optional)"]).strip()        
            QuerySet['ExpenseAccountId'] = account
            QuerySet['AccrualPeriodId'] = accrualtypeId


            if not math.isnan(row['DEFAULT RATES (OPTIONAL) Annual entitlement (hours)']) and row['DEFAULT RATES (OPTIONAL) Annual entitlement (hours)'] != "":
                QuerySet['AnnualEntitlement'] = row['DEFAULT RATES (OPTIONAL) Annual entitlement (hours)']
            else:
                QuerySet['AnnualEntitlement'] = 0 
            
            QuerySet['IsResetEveryYear'] = str(row['Reset balance to nil each year']).strip()
            QuerySet['IsPayOnTermination'] = str(row['Pay on termination']).strip()
            QuerySet['IsInTimeWorkedAccrual'] = str(row['Include in time worked leave accruals']).strip()
            QuerySet['IsShownLeaveBalanceOnPaySlip'] = str(row['Show balance on pay slip']).strip()
            QuerySet['LeaveItemSubType'] = leave_subtype
            
                
            # print(QuerySet)
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
