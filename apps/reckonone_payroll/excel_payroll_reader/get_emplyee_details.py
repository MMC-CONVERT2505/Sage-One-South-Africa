
import traceback
import os
import openpyxl
import pandas as pd
from flask.helpers import get_root_path
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import instance_check
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.log_file import log_config
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta


def get_excel_payroll_employee_details(job_id, task_id):
    logging = log_config(job_id) 
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_payroll_employee_details"]

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        leave_data = pd.read_excel(path, 'Employee details')

        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/payroll/payschedules"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_payschedules_from_api--> url-->{url} response status-->{response.status_code}")
        JsonResponse1 = response.json()
       

        for index, row in leave_data.iterrows():
            
            IsActive = None

            if str(row['Status']).strip()== "Active":
                IsActive =True
            else:
                IsActive =False
            
            # IsBusinessAddressValue=None
            # if row['IsBusinessAddressDifferent']=="True":
            #    IsBusinessAddressValue=True
            # else:
            #     IsBusinessAddressValue=False
            pay_schedule_Id=None
            for i in range(0, len(JsonResponse1)):
                if JsonResponse1[i]["Name"]==str(row['Pay Shedule']):
                     pay_schedule_Id=JsonResponse1[i]["Id"]
                     break  
             
            
            mobile_number="-"
            if str(row['MOBILE']) =="nan" or str(row['MOBILE']) ==" ":
                mobile_number="-"
            else:
                mobile_number=str(row['MOBILE']).replace(" ","")

            phone_number="-"
            if str(row['PHONE']) =="nan" or str(row['PHONE']) ==" ":
                phone_number="-"
            else:
                phone_number=str(row['PHONE']).replace(" ","")

            fax_number="-"
            if str(row['FAX']) =="nan" or str(row['FAX']) ==" ":
                fax_number="-"
            else:
                fax_number=str(row['FAX'])

            email="-"
            if str(row['EMAIL']) =="nan" or str(row['EMAIL']) ==" ":
                email="-"
            else:
                email=str(row['EMAIL'])

            QuerySet = {
                'job_id': job_id,
                'task_id': task_id,
                'is_pushed': 0,
                'error': None,
                'payload': None,
                "employee_id":str(row['Employee Id']),
                'Description': str(row['Display name']).strip(),
                'FirstNameBranchName': str(row['First name']).strip(),
                'SurnameBusinessName': str(row['Last name']).strip(),
                'IsActive': IsActive,
                'Email': email,
                'PhoneNumber': phone_number,
                'FaxNumber': fax_number,
                'MobileCode': mobile_number,
                'MobileNumber': mobile_number,
                "IsBusinessAddressDifferent":row['IsBusinessAddressDifferent'],
            }
            
           
            if row['IsBusinessAddressDifferent']=="True":
                
                optional_street="-"
                if str(row['POSTAL Street address 2 (optional)']) =="nan" or str(row['POSTAL Street address 2 (optional)']) ==" ":
                    optional_street=" "
                else:
                    optional_street=str(row['POSTAL Street address 2 (optional)'])

                address_template_1 = {
                    "Line1": str(row['POSTAL Street address']),
                    "Line2": optional_street, 
                    "Suburb": str(row['POSTAL Suburb']),
                    "State": str(row['POSTAL State']),
                    "Postcode": str(row['POSTAL Postcode']),
                    "Country": str(row['POSTAL Country']),
                    "AddressType":"Postal",
                }
                address_template_2 = {
                    "Line1": str(row['POSTAL Street address']),
                    "Line2": optional_street, 
                    "Suburb": str(row['POSTAL Suburb']),
                    "State": str(row['POSTAL State']),
                    "Postcode": str(row['POSTAL Postcode']),
                    "Country": str(row['POSTAL Country']),
                    "AddressType":"Business",
                }
                QuerySet['Addresses'] = [address_template_1, address_template_2] 
            else:
                optional_street_postal="-"
                if str(row['POSTAL Street address 2 (optional)']) =="nan" or str(row['POSTAL Street address 2 (optional)']) ==" ":
                    optional_street_postal=" "
                else:
                    optional_street_postal=str(row['POSTAL Street address 2 (optional)'])

                address_template1 = {
                    "Line1": str(row['POSTAL Street address']),
                    "Line2": optional_street_postal, 
                    "Suburb": str(row['POSTAL Suburb']),
                    "State": str(row['POSTAL State']),
                    "Postcode": str(row['POSTAL Postcode']),
                    "Country": str(row['POSTAL Country']),
                    "AddressType":"Postal",
                }
                optional_street_physical="-"
                if str(row["PHYSICAL Street address 2 (optional)"]) =="nan" or str(row["PHYSICAL Street address 2 (optional)"]) ==" ":
                    optional_street_physical=" "
                else:
                    optional_street_physical=str(row["PHYSICAL Street address 2 (optional)"])

                address_template2 = {
                    "Line1": str(row["PHYSICAL Street address"]), 
                    "Line2": optional_street_physical,
                    "Suburb": str(row["PHYSICAL Suburb"]),
                    "State": str(row["PHYSICAL State"]),
                    "Postcode": str(row["PHYSICAL Postcode"]),
                    "Country": str(row["PHYSICAL Country"]),
                    "AddressType":"Business",
                }


                QuerySet['Addresses'] = [address_template1, address_template2]

            marital_Status={
                "Undisclosed":1,
                "Single":2,
                "Married/De facto":3,
                "Divorced":4,
                "Widowed":5
            }
            marital_Status_Id = None

            if row['Marital status'] in marital_Status:
                marital_Status_Id = marital_Status[row["Marital status"]]
            else:
                marital_Status_Id = None
            

            emergency_address1_name="-"
            if str(row['PRIMARY EMERGENCY CONTACT Name']) =="nan" or str(row['PRIMARY EMERGENCY CONTACT Name']) ==" ":
                 emergency_address1_name="-"
            else:
                 emergency_address1_name=str(row['PRIMARY EMERGENCY CONTACT Name'])
            
            emergency_address1_relationship="-"
            if str(row['PRIMARY EMERGENCY CONTACT Relationship']) =="nan" or str(row['PRIMARY EMERGENCY CONTACT Relationship']) ==" ":
                 emergency_address1_relationship="-"
            else:
                 emergency_address1_relationship=str(row['PRIMARY EMERGENCY CONTACT Relationship'])

            emergency_address1_phone="-"
            if str(row['PRIMARY EMERGENCY CONTACT Phone']) =="nan" or str(row['PRIMARY EMERGENCY CONTACT Phone']) ==" ":
                 emergency_address1_phone="-"
            else:
                 emergency_address1_phone=str(row['PRIMARY EMERGENCY CONTACT Phone'])
                 
            emergency_address1={
                "Name":emergency_address1_name,
                "Relationship": emergency_address1_relationship,
                "PhoneNumber": emergency_address1_phone,
                # "IsPrimary" : str(row["PRIMARY EMERGENCY CONTACT IsPrimary"])
                "IsPrimary" : True
            }

            emergency_address2_name="-"
            if str(row['SECONDARY EMERGENCY CONTACT Name']) =="nan" or str(row['SECONDARY EMERGENCY CONTACT Name']) ==" ":
                 emergency_address2_name="-"
            else:
                 emergency_address2_name=str(row['SECONDARY EMERGENCY CONTACT Name'])
            
            emergency_address2_relationship="-"
            if str(row['SECONDARY EMERGENCY CONTACT Relationship']) =="nan" or str(row['SECONDARY EMERGENCY CONTACT Relationship']) ==" ":
                 emergency_address2_relationship="-"
            else:
                 emergency_address2_relationship=str(row['SECONDARY EMERGENCY CONTACT Relationship'])

            emergency_address2_phone="-"
            if str(row['SECONDARY EMERGENCY CONTACT Phone']) =="nan" or str(row['SECONDARY EMERGENCY CONTACT Phone']) ==" ":
                 emergency_address2_phone="-"
            else:
                 emergency_address2_phone=str(row['SECONDARY EMERGENCY CONTACT Phone'])

            emergency_address2={
                "Name":emergency_address2_name,
                "Relationship": emergency_address2_relationship,
                "PhoneNumber": emergency_address2_phone,
                # "IsPrimary" : str(row["SECONDARY EMERGENCY CONTACT IsPrimary"])
                "IsPrimary" : False
            }

            GenderId=None
         
            if str(row["Gender Male"])=="True" or str(row["Gender Male"])=="TRUE" or str(row["Gender Male"])=="1.0":
                GenderId=1 
            if str(row["Gender Female"])=="True" or str(row["Gender Female"])=="TRUE" or str(row["Gender Female"])=="1.0":
                GenderId=2
            if str(row["Gender Non Binary"])=="True" or str(row["Gender Non Binary"])=="TRUE" or str(row["Gender Non Binary"])=="1.0":
                GenderId=3
            
            date1=str(row['Date of birth']).split(" ")[0]
            transactiondate = datetime.strptime(date1, "%Y-%m-%d")
            transactiondate1=transactiondate.strftime("%Y-%m-%d")
            

            personal_details={

                "DateOfBirth" : transactiondate1,
                "MaritalStatusId":marital_Status_Id,
                "GenderId":GenderId,
                "PayrollEmail":email,
                
            }
            
            print(personal_details['DateOfBirth'])
            
            
          
            personal_details["EmergencyContacts"]=[emergency_address1, emergency_address2]
            
            
            payfrequency_map = {
                "Weekly": 1,
                "Fortnightly": 2,
                "Monthly": 3
            }

            employment_type={
                "Full time":1,
                "Part time":2,
                "Casual":3,
                "Labour hire":4,
                "Voluntary agreement":5,
                "Death beneficiary":6
            }   
            
            payfrequency=None
            if row["Pay frequency"] in payfrequency_map:
                payfrequency = payfrequency_map[row["Pay frequency"]]
            else:
                payfrequency = None
            
            employment=None
            if row["Employment type"] in employment_type:
                employment = employment_type[row["Employment type"]]
            else:
                employment = None
                
            
            residency={
                "Resident":1,
                "Foreign resident":2
            }
            tax_scale={
                "Scale 1: Tax free threshold not claimed":"EF1C0BFF-A2E3-40F8-8FA8-24E0B1C5583F",
                "Voluntary/Flat rate":"DCDA2486-77DD-402F-A5A7-26D18F1721FA",
                "Working holiday maker":"10D25900-1B78-4372-A495-7A6BD8781DC0",
                "Scale 5: Full medicare exemption":"448C37D2-78E3-4E45-85B5-AE4532351785",
                "Scale 4: No TFN & No TFN foreign res":"2CBB1CC1-AD02-4D1F-AAC2-B62146DE4474",
                "Scale 2: Tax free threshold claimed":"90A4B1ED-457F-4235-B62A-B6CECDCB0024",
                "Scale 3: Foreign resident":"B241328A-70FB-400D-9621-CE7E8475ABFD",
                "Scale 6: Half medicare exemption":"6352D8A0-C812-4542-9777-E4E62AD3B80D",
                "Seasonal worker programme":"9660334D-2EA3-4891-9030-ED145A7B7DCF"
            }

            resident=None
            if row['Tax Residency'] in residency:
                resident = residency[row["Tax Residency"]]
            else:
                resident = None

            tax_scaleId=None
            if row["Tax Scale"] in tax_scale:
                tax_scaleId=tax_scale[row["Tax Scale"]]
            else:
                tax_scaleId = None


            state_names={
                "ACT":"EBC47D57-9449-459D-BD33-B5F7A8C57341",
                "NSW":"2DAAC33F-30CE-4A69-B2C4-AB5356901459",
                "VIC":"10C75022-553C-46C2-AB63-9BA4DA24E8E2",
                "QLD":"3A6A5C73-2F06-4558-BDAF-F1743A64B032",
                "WA":"DEBB78C4-E176-4E8B-A1EE-C49F889144F0",
                "SA":"1E1E6166-487C-4D74-AC6F-29478FA8E333",
                "TAS":"3379A643-52F9-4C34-8DA3-4860DB796A17",
                "NT":"1E78CFFE-C679-4252-8E2A-0245A0E99E23"
            }
            
            state_id=None
            if row["Tax State"] in state_names:
                state_id=state_names[row["Tax State"]]
            else:
                state_id = None

            tax_income_names={
            "Salary and Wages":"3253dc53-ca77-45a1-ba2a-d4632e971222",
            "Closely Held Payees":"df1a5f23-a9c9-49df-9633-c9ec3f54dd86"

            }
            tax_income=None
            if row["Tax Income Type"] in tax_income_names:
                tax_income=tax_income_names[row["Tax Income Type"]]
            else:
                tax_income = None

            IsMedicareAdjustment=None
            if row['Employee has a Medicare levy Surcharge amount'] ==1:
                IsMedicareAdjustment="e014ffad-1d99-4031-a0f7-fb327c906489"
            if row['Employee has a Medicare levy Surcharge amount'] ==1.25:
                IsMedicareAdjustment="e014ffad-1d99-4031-a0f7-fb327c906490"
            if row['Employee has a Medicare levy Surcharge amount'] ==1.50:
                IsMedicareAdjustment="e014ffad-1d99-4031-a0f7-fb327c906491"
            

            tax_offset=None
            if str(row['Employee Claimed Other Tax Offset']) =="nan" or str(row['Employee Claimed Other Tax Offset']) ==" ":
                tax_offset=None
            else:
                tax_offset=str(row['Employee Claimed Other Tax Offset'])

            extra_tax=None
            if str(row['Employee requested an upward variation amount']) =="nan" or str(row['Employee requested an upward variation amount']) ==" " : 
                extra_tax=None
            else:
                extra_tax=str(row['Employee requested an upward variation amount'])

            extra_tax_from_date=None
            if str(row['Employee requested an upward variation date']) =="nan" or str(row['Employee requested an upward variation date']) ==" " or str(row['Employee requested an upward variation date']) == "NaT":
                extra_tax_from_date=None
            else:
                extra_tax_from_date=str(row['Employee requested an upward variation date'])

            is_help_Or_Tsl=False
            if str(row['Employee has Student Debt']) =="nan" or str(row['Employee has Student Debt']) ==" " or str(row['Employee has Student Debt']) =="False" or  str(row['Employee has Student Debt']) =="0.0":
                is_help_Or_Tsl=False
            elif (str(row['Employee has Student Debt']) =="True" or str(row['Employee has Student Debt']) =="1.0" ):
                is_help_Or_Tsl=True
            else:
                is_help_Or_Tsl=str(row['Employee has Student Debt'])
           

            IsSfss=False
            if str(row["Exclude this employee's data from being reported to the ATO via STP"]) =="nan" or str(row["Exclude this employee's data from being reported to the ATO via STP"]) ==" " or str(row["Exclude this employee's data from being reported to the ATO via STP"]) =="False" or  str(row["Exclude this employee's data from being reported to the ATO via STP"]) =="0.0":
                IsSfss=False
            elif (str(row["Exclude this employee's data from being reported to the ATO via STP"]) =="True" or str(row["Exclude this employee's data from being reported to the ATO via STP"]) =="1.0" ):
                IsSfss=True
            else:
                IsSfss=str(row['Employee has Student Debt'])
             
            number_of_children=0
            if str(row['Employee has a Medicare levy Reduction Children Number']) =="nan" or str(row['Employee has a Medicare levy Reduction Children Number']) ==" " or str(row['Employee has a Medicare levy Reduction Children Number']) =="False" or str(row['Employee has a Medicare levy Reduction Children Number']) =="0.0":
                number_of_children=0
            else:
                number_of_children=int(row['Employee has a Medicare levy Reduction Children Number'])
 
            
           

            tax_details={
     
                "Tfn": str(row['Tax TFN']).replace(" ",""),
				"Residency": resident,
                "IsHelpOrTsl": is_help_Or_Tsl,
                "IsSfss": IsSfss,
                "MedicareIncreaseId":IsMedicareAdjustment,
                "StateId": state_id,
                "TaxOffset": tax_offset,
                "ExtraTax": extra_tax,
                "ExtraTaxFromDate":extra_tax_from_date,
                "NumberOfChildren":number_of_children,
                "IsStaturotyRate": False,
                "TaxScaleId":tax_scaleId,
                "IncomeStreamCodeId":tax_income

            }


            job_title="-"
            if str(row['job title']) =="nan" or str(row['job title']) ==" ":
                 job_title="-"
            else:
                 job_title=str(row['job title'])

            manager="-"
            if str(row['Manager (Optional)']) =="nan" or str(row['Manager (Optional)']) ==" ":
                 manager="-"
            else:
                 manager=str(row['Manager (Optional)'])

            pay_schedule="-"
            if str(row['Pay Shedule']) =="nan" or str(row['Pay Shedule']) ==" ":
                 pay_schedule="-"
            else:
                 pay_schedule=str(row['Pay Shedule'])


            # hire_date="-"
            # if str(row['Hire date']) =="nan" or str(row['Hire date']) ==" ":
            #      hire_date="-"
            # else:
            #      hire_date=str(row['Hire date']).split(" ")[0]

            date2=str(row['Hire date']).split(" ")[0]
            transactiondate_1 = datetime.strptime(date2, "%Y-%m-%d")
            transactiondate_2=transactiondate_1.strftime("%Y-%m-%d")

        
                

            employee_data={
                "EmployeeNumber":str(row['Employee number']),
                "PaySchedule":pay_schedule,
                "WeeklyHours":str(row['Standard hours worked per week']),
                "JobTitle":job_title,
                "Manager":manager,
                "HireDate":transactiondate_2,
                "EmploymentTypeId":employment,
                "PayScheduleId":pay_schedule_Id,
                "PayFrequencyId":payfrequency,
                "PersonalDetail":personal_details,
                "Tax":tax_details
            }
          
            QuerySet["EmployeeData"]=employee_data

            print(QuerySet)
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
