import traceback
import os
import requests
import pandas as pd
import openpyxl
from datetime import datetime

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from flask.helpers import get_root_path
import math
from apps.util.qbo_util import instance_check


def get_excel_reckon_employee(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_employee"]

        file_prefix = str(job_id)
        files_directory = os.path.join(get_root_path('apps'), 'files/')
        filename = next((f for f in os.listdir(files_directory)
                        if f.startswith(file_prefix)), None)
        if filename is None:
            return
        path = os.path.join(files_directory, filename)
        workbook = openpyxl.load_workbook(path)
        employee_data = pd.read_excel(path, 'Employee')

        instance_name = None

        for index, row in employee_data.iterrows():

            status_data = None
            if row["Status"] == "Active":
                status_data = True
            else:
                status_data = False

            PayFrequency_data = None
            if row["Pay freauency"] == "Weekly":
                PayFrequency_data = 1
            elif row["Pay freauency"] == "Fortnightly":
                PayFrequency_data = 2
            elif row["Pay freauency"] == "Monthly":
                PayFrequency_data = 3

            State_data = None
           
            statedata={"Queensland":"3A6A5C73-2F06-4558-BDAF-F1743A64B032","Western Australia":"DEBB78C4-E176-4E8B-A1EE-C49F889144F0","Australian Capital Territory":"EBC47D57-9449-459D-BD33-B5F7A8C57341","New South Wales":"2DAAC33F-30CE-4A69-B2C4-AB5356901459","Victoria":"10C75022-553C-46C2-AB63-9BA4DA24E8E2","Tasmania":"3379A643-52F9-4C34-8DA3-4860DB796A17","South Australia":"1E1E6166-487C-4D74-AC6F-29478FA8E333","Northern Territory":"1E78CFFE-C679-4252-8E2A-0245A0E99E23"}
            if row["State"] in statedata.keys():
                State_data=statedata[row["State"]]

            taxscale_data=None
            taxscale = {"Scale 1: Tax free threshold not claimed": "EF1C0BFF-A2E3-40F8-8FA8-24E0B1C5583F", "Voluntary/Flat rate": "DCDA2486-77DD-402F-A5A7-26D18F1721FA", "Working holiday maker": "10D25900-1B78-4372-A495-7A6BD8781DC0", "Scale 5: Full medicare exemption": "448C37D2-78E3-4E45-85B5-AE4532351785", "Scale 4: No TFN & No TFN foreign res": "2CBB1CC1-AD02-4D1F-AAC2-B62146DE4474",
                        "Scale 2: Tax free threshold claimed": "90A4B1ED-457F-4235-B62A-B6CECDCB0024", "Scale 3: Foreign resident": "B241328A-70FB-400D-9621-CE7E8475ABFD", "Scale 6: Half medicare exemption": "6352D8A0-C812-4542-9777-E4E62AD3B80D", "Seasonal worker programme": "9660334D-2EA3-4891-9030-ED145A7B7DCF"}

            if row["Tax Scale"] in taxscale.keys():
                taxscale_data=taxscale[row["Tax Scale"]]

            Accuralperiod_id=None
            if row["Accural period"]=="Per Pay":
                Accuralperiod_id=1
            elif  row["Accural period"]=="Per time worked":
                Accuralperiod_id=2
            elif  row["Accural period"]=="Per annum":
                Accuralperiod_id=3

            date1=str(row['Hire date']).split(" ")[0]
            transactiondate = datetime.strptime(date1, "%Y-%m-%d")
            transactiondate1=transactiondate.strftime("%Y-%m-%d")

            date2=str(row['Termination date']).split(" ")[0]
            transactiondate11 = datetime.strptime(date2, "%Y-%m-%d")
            transactiondate2=transactiondate11.strftime("%Y-%m-%d")
            
            date3=str(row['leave start date']).split(" ")[0]
            transactiondate22 = datetime.strptime(date3, "%Y-%m-%d")
            transactiondate3=transactiondate22.strftime("%Y-%m-%d")

            MaritalStatusId_data=None
            if row['Marital status']=="Not disclosed":
                MaritalStatusId_data=1
            elif row['Marital status']=="Single":  
                MaritalStatusId_data=2

            elif row['Marital status']=="Married/De-facto":  
                MaritalStatusId_data=3

            elif row['Marital status']=="Divorced":  
                MaritalStatusId_data=4

            elif row['Marital status']=="Widowed":  
                MaritalStatusId_data=5
            
            GenderId_data=None

            if row['Gender']=="Male":
                GenderId_data=1
            elif row['Gender']=="Female":  
                GenderId_data=2
            elif row['Gender']=="Unspecified":  
                GenderId_data=3

            print(index)
            employee_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "error": None,
                "payload": None,
                "IsPerson": True,
                "FirstNameBranchName": instance_check(instance_name, row['First name']),
                "SurnameBusinessName": instance_check(instance_name, row['Last name']),
                "Description": instance_check(instance_name, row['Display name']),
                "Email": instance_check(instance_name, row['EMAIL']),
                "Website": instance_check(instance_name, row['WEB']),
                "Notes": instance_check(instance_name, row['NOTES']),
                "PhoneNumber": instance_check(instance_name, row['PHONE']),
                "FaxNumber": instance_check(instance_name, row['FAX']),
                "MobileNumber": instance_check(instance_name, row['MOBILE']),
                "IsEmployee": True,
                "IsActive": status_data,

                "Addresses": [

                    {
                        "Line1": instance_check(instance_name, row['POSTAL ADDRESS']),
                        "Suburb": instance_check(instance_name, row['Suburb']),
                        "State": instance_check(instance_name, row['State']),
                        "Postcode": None if instance_check(instance_name, row['Postcode']) == None else str(row['Postcode'])[0:4],
                        "Country": instance_check(instance_name, row['POSTAL ADDRESS Country']),
                        "AddressType": "Postal",
                        "IsInternational": False
                    },
                    {
                        "Line1": instance_check(instance_name, row['POSTAL ADDRESS']),
                        "Suburb": instance_check(instance_name, row['Suburb']),
                        "State": instance_check(instance_name, row['State']),
                        "Postcode": None if instance_check(instance_name, row['Postcode']) == None else str(row['Postcode'])[0:4],
                        "Country": instance_check(instance_name, row['POSTAL ADDRESS Country']),
                        "AddressType": "Postal",
                        "IsInternational": False
                    }
                ],

                "EmployeeData": {

                    "PersonalDetail":{
                        "DateOfBirth":"hhsa",
                        "MaritalStatusId":MaritalStatusId_data,
                        "GenderId":GenderId_data,
                        "PayrollEmail":instance_check(instance_name, row['PRIMARY EMERGENCY CONTACT Relationship']),
                        



                    },


                    "EmployeeNumber": instance_check(instance_name, row['Employee number']),
                    "EmploymentType": instance_check(instance_name, row['Employee number']),
                    "PayFrequencyId": instance_check(instance_name, row['PayFrequency_data']),
                    "WeeklyHours": instance_check(instance_name, row['Weekly hours']),
                    "JobTitle": instance_check(instance_name, row['job title']),
                    "ManagerId": instance_check(instance_name, row['manager']),
                    "JobDescription": instance_check(instance_name, row['Job description']),
                    "HireDate":  transactiondate1,
                    "TerminationDate":  transactiondate2,

                    "Tax": {
                        "Tfn": instance_check(instance_name, row['Tax File Number (TFN)']),
                        "Residency": 2 if row['Residency'] == "Foreign resident" else 1,
                        "StateId": State_data,
                        "TaxScaleId":taxscale_data,
                        "TaxOffset":instance_check(instance_name, row['Tax Offset']),
                        "ExtraTax":instance_check(instance_name, row['Extra tax (0% Or $)']),
                    },
                    "Leaves":{
                        "AnnualEntitlement":instance_check(instance_name, row['Annuel entitlement']),
                        "AccrualPeriodId":Accuralperiod_id,
                        "AccumulationRate":instance_check(instance_name, row['Rate per period']),
                        "LeaveStartDate":transactiondate3,
                        "Maximum":instance_check(instance_name, row['Max']),
                        "Loading":instance_check(instance_name, row['Leave loading']),
                        "IsPayOnTermination":True if row["Pay on termination"] != None else False,
                    }
                },
                "Payments": {
                    "TypeId": 2 if row['PAYMENTS Type'] == "Direct credit" else 1,
                    "AccountName": instance_check(instance_name, row['PAYMENTS Account Name']),
                    "BankName": instance_check(instance_name, row['PAYMENTS Bank Name']),
                    "Bsb": instance_check(instance_name, row['PAYMENTS BSB']),
                    "AccountNumber": instance_check(instance_name, row['PAYMENTS Account Number']),
                    "Reference": instance_check(instance_name, row['PAYMENTS Refrence']),
                    "Amount": instance_check(instance_name, row['PAYMENTS Amount'])
                }
            }
            collection.insert_one(employee_payload)

    except Exception as ex:
        traceback.print_exc()
