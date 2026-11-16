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
import requests


def get_excel_payroll_Leaveentitlements(job_id, task_id):
   
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_leave_entitlements"]

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        leave_data = pd.read_excel(path,'Leave entitlements')


        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/payroll/leaveitems"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        data=response.json()
      
        
        instance_name = None
        for index, row in leave_data.iterrows():
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            QuerySet['Leaves']=None
            QuerySet["employee_id"]=str(row['Employee Id'])
            
            leaves=[]
            QuerySet1={}

            personal_leave_Leave_type = {
                                 "Annual": 12,
                                 "Personal": 13,
                                 "LongService": 14,
                                 "OtherLeave": 15
                                }
            
            personal_Leave=None
            # if row['Personal leave Leave type'] in personal_leave_Leave_type:
            #     personal_Leave = personal_leave_Leave_type[row["Personal leave Leave type"]]
            #     QuerySet1['PayItemTypeId'] = personal_Leave
            # else:
            #     personal_Leave=None
            QuerySet1['LeaveName'] = str(row['Personal leave Leave type']).strip()
            for k in range(0,len(data)):
                if QuerySet1['LeaveName'] == data[k]['Name']:
                    QuerySet1['PayItemsLeavesId']=data[k]['LeaveItemId']
                    QuerySet1['PayItemTypeId'] = data[k]['LeaveItemType']
                    break
                
            if row['Personal leave Accrual period Per Time Worked'] in [True,"TRUE"]:
                QuerySet1['AccrualPeriodId'] = 2
            elif row['Personal leave Accrual period Per Pay'] in [True,"TRUE"]:
                QuerySet1['AccrualPeriodId'] = 1
            elif row['Personal leave Accrual period Per annum'] in [True,"TRUE"]:
                QuerySet1['AccrualPeriodId'] = 3    
            else:
                QuerySet1['AccrualPeriodId']=0

                    
            QuerySet1['AnnualEntitlement'] = (row['Personal leave Annual entitlement (Hours)'])
            QuerySet1['LeaveStartDate'] = str(row['Personal leave Leave start date']).split(" ")[0]
            QuerySet1['AccumulationRate'] = (row['Personal leave Accrual rate per time worked'])
            QuerySet1['IsPayOnTermination'] =bool(row['Personal leave Pay on termination'])

            if type(row['Personal leave Maximum accumulation (optional)']) != int:
                QuerySet1['Maximum'] =row['Personal leave Maximum accumulation (optional)']=0
            else:
                QuerySet1['Maximum'] = str(row['Personal leave Maximum accumulation (optional)'])
                    
            if  QuerySet1['LeaveName']!= "nan" and QuerySet1['LeaveStartDate'] != "NaT" :
                leaves.append(QuerySet1)

            QuerySet2={}
            Annual_leave_Leave_type = {
                                "Annual": 12,
                                "Personal": 13,
                                "LongService": 14,
                                "OtherLeave": 15
                                }
            
            Annual_Leave=None
            if row['Annual leave Leave type'] in Annual_leave_Leave_type:
                Annual_Leave = Annual_leave_Leave_type[row["Annual leave Leave type"]]
                QuerySet2['PayItemTypeId'] = Annual_Leave
            else:
                Annual_Leave=None
                    

            QuerySet2['LeaveName'] = str(row['Annual leave Leave type']).strip()
            for k in range(0,len(data)):
                if QuerySet2['LeaveName'] == data[k]['Name']:
                    QuerySet2['PayItemsLeavesId']=data[k]['LeaveItemId']
                    QuerySet2['PayItemTypeId'] = data[k]['LeaveItemType']
                    break                    
                    
            if row['Annual leave Accrual period Per Time Worked'] == True:
                QuerySet2['AccrualPeriodId']=2
            elif row['Annual leave Accrual period Per Pay'] ==True:
                QuerySet2['AccrualPeriodId']=1
            elif row['Annual leave Accrual period Per annum'] ==True:
                QuerySet2['AccrualPeriodId']=3
            else:
                QuerySet2['AccrualPeriodId']=0
                        
            QuerySet2['AnnualEntitlement'] = (row['Annual leave Annual entitlement (Hours)'])
            QuerySet2['LeaveStartDate'] = str(row['Annual leave Leave start date']).split(" ")[0]
            QuerySet2['AccumulationRate'] = (row['Annual leave Accrual rate per time worked'])
            QuerySet2['IsPayOnTermination'] = bool(row['Annual leave Pay on termination'])
                    
            if type(row['Annual leave Maximum accumulation (optional)']) != int:
                QuerySet2['Maximum'] = row['Annual leave Maximum accumulation (optional)']=0
            else:
                QuerySet2['Maximum'] = str(row['Annual leave Maximum accumulation (optional)'])                    

            if  QuerySet2['LeaveName']!= "nan" and QuerySet2['LeaveStartDate'] != "NaT" :
                leaves.append(QuerySet2)
        
                    
            QuerySet3={}
            Other_leave_Leave_type = {
                                    "compassionative leave":15,
                                    "RDO":15,
                                    "long Service leave":14
                                    }
            Other_Leave=None

            QuerySet3['LeaveName'] = str(row['Other Leave type']).strip()
            print(QuerySet3['LeaveName'])
            for k in range(0,len(data)):
                if  QuerySet3['LeaveName'] == data[k]['Name']:
                    QuerySet3['PayItemsLeavesId']=data[k]['LeaveItemId']
                    QuerySet3['PayItemTypeId'] = data[k]['LeaveItemType']
                    


            # if row['Other Leave type'] in Other_leave_Leave_type:
            #     Other_Leave = Other_leave_Leave_type[row["Other Leave type"]]
            #     QuerySet3['PayItemTypeId'] = Other_Leave
            # else:
            #     Other_Leave=None

                    if row['Other leave Accrual period Per Time Worked'] == True:
                        QuerySet3['AccrualPeriodId']=2
                    elif row['Other leave Accrual period Per Pay'] == True:
                        QuerySet3['AccrualPeriodId']=1
                    elif row['Other leave Accrual period Per annum']== True:
                        QuerySet3['AccrualPeriodId']=3
                    else:
                        QuerySet3['AccrualPeriodId']=0

                    QuerySet3['AnnualEntitlement'] = (row['Other leave Annual entitlement (Hours)'])
                    QuerySet3['LeaveStartDate'] = str(row['Other Leave start date']).split(" ")[0]
                    QuerySet3['AccumulationRate'] = (row['Other leave Accrual rate per time worked'])
                    QuerySet3['IsPayOnTermination'] =bool(row['Other leave Pay on termination'])
                            
                    if type(row['Other leave Maximum accumulation (optional)']) != int:
                        QuerySet3['Maximum'] =row['Other leave Maximum accumulation (optional)']=0
                    else:
                        QuerySet3['Maximum'] = str(row['Other leave Maximum accumulation (optional)'])
                    
                    if  QuerySet3['LeaveName']!= "nan" and QuerySet3['LeaveStartDate'] != "NaT" :
                        leaves.append(QuerySet3)
                        break


            QuerySet4={}
            Other_leave_Leave_type = {
                                    "compassionative leave":15,
                                    "RDO":15,
                                    "long Service leave":14
                                    }
            Other_Leave=None


            QuerySet4['LeaveName'] = str(row['Other Leave type 2']).strip()
            for k in range(0,len(data)):
                if  QuerySet4['LeaveName'] == data[k]['Name']:
                    QuerySet4['PayItemsLeavesId']=data[k]['LeaveItemId']
                    QuerySet4['PayItemTypeId'] = data[k]['LeaveItemType']
                    
            

            # if row['Other Leave type 2'] in Other_leave_Leave_type:
            #     Other_Leave = Other_leave_Leave_type[row["Other Leave type 2"]]
            #     QuerySet4['PayItemTypeId'] = Other_Leave
            # else:
            #     Other_Leave=None

                    if row['Other leave Accrual period Per Time Worked 2'] == True:
                        QuerySet4['AccrualPeriodId']= 2
                    elif row['Other leave Accrual period Per Pay 2'] == True:
                        QuerySet4['AccrualPeriodId']= 1
                    elif row['Other leave Accrual period Per annum 2']== True:
                        QuerySet4['AccrualPeriodId']= 3
                    else:
                        QuerySet4['AccrualPeriodId']=0

                    QuerySet4['AnnualEntitlement'] = (row['Other leave Annual entitlement (Hours) 2'])
                    QuerySet4['LeaveStartDate'] = str(row['Other Leave start date 2']).split(" ")[0]
                    QuerySet4['AccumulationRate'] = (row['Other leave Accrual rate per time worked 2'])
                    QuerySet4['IsPayOnTermination'] = bool(row['Other leave Pay on termination 2'])
                            
                    if type(row['Other leave Maximum accumulation (optional) 2']) != int:
                        QuerySet4['Maximum'] =row['Other leave Maximum accumulation (optional) 2']=0
                    else:
                        QuerySet4['Maximum'] = str(row['Other leave Maximum accumulation (optional) 2'])

                    if  QuerySet4['LeaveName']!= "nan" and QuerySet4['LeaveStartDate'] != "NaT":
                        leaves.append(QuerySet4)
                        break        


            QuerySet5={}
            Other_leave_Leave_type = {
                                    "compassionative leave":15,
                                    "RDO":15,
                                    "long Service leave":14
                                    }
            Other_Leave=None


            QuerySet5['LeaveName'] = str(row['Other Leave type 3']).strip()
            for k in range(0,len(data)):
                if  QuerySet5['LeaveName'] == data[k]['Name']:
                    QuerySet5['PayItemsLeavesId']=data[k]['LeaveItemId']
                    QuerySet5['PayItemTypeId'] = data[k]['LeaveItemType']
                    
            

            # if row['Other Leave type 2'] in Other_leave_Leave_type:
            #     Other_Leave = Other_leave_Leave_type[row["Other Leave type 2"]]
            #     QuerySet4['PayItemTypeId'] = Other_Leave
            # else:
            #     Other_Leave=None

                    if row['Other leave Accrual period Per Time Worked 3'] == True:
                        QuerySet5['AccrualPeriodId']= 2
                    elif row['Other leave Accrual period Per Pay 3'] == True:
                        QuerySet5['AccrualPeriodId']= 1
                    elif row['Other leave Accrual period Per annum 3']== True:
                        QuerySet5['AccrualPeriodId']= 3
                    else:
                        QuerySet5['AccrualPeriodId']=0

                    QuerySet5['AnnualEntitlement'] = (row['Other leave Annual entitlement (Hours) 3'])
                    QuerySet5['LeaveStartDate'] = str(row['Other Leave start date 3']).split(" ")[0]
                    QuerySet5['AccumulationRate'] = (row['Other leave Accrual rate per time worked 3'])
                    QuerySet5['IsPayOnTermination'] = bool(row['Other leave Pay on termination 3'])
                            
                    if type(row['Other leave Maximum accumulation (optional) 3']) != int:
                        QuerySet5['Maximum'] =row['Other leave Maximum accumulation (optional) 3']=0
                    else:
                        QuerySet5['Maximum'] = str(row['Other leave Maximum accumulation (optional) 3'])

                    if  QuerySet5['LeaveName']!= "nan" and QuerySet5['LeaveStartDate'] != "NaT":
                        leaves.append(QuerySet5)
                        break        
            QuerySet6={}
            Other_leave_Leave_type = {
                                    "compassionative leave":15,
                                    "RDO":15,
                                    "long Service leave":14
                                    }
            Other_Leave=None


            QuerySet6['LeaveName'] = str(row['Other Leave type 4']).strip()
            for k in range(0,len(data)):
                if  QuerySet6['LeaveName'] == data[k]['Name']:
                    QuerySet6['PayItemsLeavesId']=data[k]['LeaveItemId']
                    QuerySet6['PayItemTypeId'] = data[k]['LeaveItemType']
                    
            

            # if row['Other Leave type 2'] in Other_leave_Leave_type:
            #     Other_Leave = Other_leave_Leave_type[row["Other Leave type 2"]]
            #     QuerySet4['PayItemTypeId'] = Other_Leave
            # else:
            #     Other_Leave=None

                    if row['Other leave Accrual period Per Time Worked 4'] == True:
                        QuerySet6['AccrualPeriodId']= 2
                    elif row['Other leave Accrual period Per Pay 4'] == True:
                        QuerySet6['AccrualPeriodId']= 1
                    elif row['Other leave Accrual period Per annum 4']== True:
                        QuerySet6['AccrualPeriodId']= 3
                    else:
                        QuerySet6['AccrualPeriodId']=0

                    QuerySet6['AnnualEntitlement'] = (row['Other leave Annual entitlement (Hours) 4'])
                    QuerySet6['LeaveStartDate'] = str(row['Other Leave start date 4']).split(" ")[0]
                    QuerySet6['AccumulationRate'] = (row['Other leave Accrual rate per time worked 4'])
                    QuerySet6['IsPayOnTermination'] = bool(row['Other leave Pay on termination 4'])
                            
                    if type(row['Other leave Maximum accumulation (optional) 4']) != int:
                        QuerySet6['Maximum'] =row['Other leave Maximum accumulation (optional) 4']=0
                    else:
                        QuerySet6['Maximum'] = str(row['Other leave Maximum accumulation (optional) 4'])

                    if  QuerySet6['LeaveName']!= "nan" and QuerySet6['LeaveStartDate'] != "NaT":
                        leaves.append(QuerySet6)
                        break        

            QuerySet['Leaves']=leaves
            # print(QuerySet)
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
