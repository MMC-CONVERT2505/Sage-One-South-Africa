# import json
# import requests
# from apps.mmc_settings.all_settings import get_settings_reckon
# from apps.util.db_mongo import get_mongodb_database
# from apps.util.qbo_util import post_data_in_reckon
# import asyncio
# from apps.util.log_file import log_config


# def write_all_employee_functions(job_id,task_id):
#     print("inside write_all_employee_functions in  payroll ****1")
#     logging = log_config(job_id)
#     try:

#         logging.info(f"{job_id} inside write_all_employee_functions")
#         dbname=get_mongodb_database()
#         payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

#         url = f"{base_url}/payroll/contacts"
#         logging.info(f"{job_id} write_all_employee_functions--> url-->{url}")

#         excel_reckon_employee = dbname['excel_payroll_employee_details']
#         x = excel_reckon_employee.find({"job_id":job_id})
#         excel_reckon_employee1 = []
#         for k in x:
#             excel_reckon_employee1.append(k)
#         # print("excel_reckon_employee1 payload>>>>>>>>>>>>>>>>>>>>>>>>>>",excel_reckon_employee1)
        
#         employee_data=None

#         for i in range(0,len(excel_reckon_employee1)):
#             _id=excel_reckon_employee1[i]['_id']
#             task_id=excel_reckon_employee1[i]['task_id']
#             excel_reckon_employee1[i].pop("_id")
#             excel_reckon_employee1[i].pop("job_id")
#             excel_reckon_employee1[i].pop("task_id")
#             excel_reckon_employee1[i].pop("is_pushed")
#             excel_reckon_employee1[i].pop("error")
#             excel_reckon_employee1[i].pop("payload")
#             employee_payload = json.dumps(excel_reckon_employee1[i])

#             employee_data = json.loads(employee_payload)

#             print("payload>>>> 1 employee_payload function  ***",employee_payload)
        
#         leave_entitlement_data=None

#         leave_entitlement = dbname["excel_reckon_leave_entitlements"]
#         x = leave_entitlement.find({"job_id":job_id})
#         leave_entitlement1 = []
#         for k in x:
#             leave_entitlement1.append(k)
#         for i in range(0,len(leave_entitlement1)):
#             _id=leave_entitlement1[i]['_id']
#             task_id=leave_entitlement1[i]['task_id']
#             leave_entitlement1[i].pop("_id")
#             leave_entitlement1[i].pop("job_id")
#             leave_entitlement1[i].pop("task_id")
#             leave_entitlement1[i].pop("is_pushed")
#             leave_entitlement1[i].pop("error")
#             leave_entitlement1[i].pop("payload")
#             leave_entitlement_payload = json.dumps(leave_entitlement1[i])

#             print("payload>>>> 2 inside write leave_entitlement function  ***>>",leave_entitlement_payload)

         
   
            
#             leave_entitlement_data = json.loads(leave_entitlement_payload)

#             employee_data["EmployeeData"]["Leaves"] = leave_entitlement_data["Leaves"]

#             updated_employee_payload = json.dumps(employee_data)

#             print("Updated payload with leaves data:", updated_employee_payload)
            
#             asyncio.run(post_data_in_reckon(url, post_headers, updated_employee_payload,excel_reckon_employee,_id, job_id,task_id, excel_reckon_employee1[i]["FirstNameBranchName"]))
           

#     except Exception as ex:
#         import traceback
#         traceback.print_exc()
#         logging.error(ex, exc_info=True)





import json
import asyncio
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
from apps.util.log_file import log_config

async def process_employee_record(url, post_headers, employee_data, excel_reckon_employee, _id, job_id, task_id, branch_name):
    updated_employee_payload = json.dumps(employee_data)
    await post_data_in_reckon(url, post_headers, updated_employee_payload, excel_reckon_employee, _id, job_id, task_id, branch_name)

def write_all_employee_functions(job_id, task_id):
    print("inside write_all_employee_functions in payroll ****1")
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside write_all_employee_functions")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/payroll/contacts"
        logging.info(f"{job_id} write_all_employee_functions--> url-->{url}")

        excel_reckon_employee = dbname['excel_payroll_employee_details']
        leave_entitlement = dbname["excel_reckon_leave_entitlements"]
        pay_setup = dbname["excel_reckon_payroll_paysetup"]
        other_details = dbname["excel_reckon_other_details"]

          
        pay_setup_data_map = {}
        for pay_setup1 in pay_setup.find({"job_id": job_id}):
            _id = pay_setup1.pop('_id')
            task_id = pay_setup1.pop('task_id')
            is_pushed = pay_setup1.pop('is_pushed')
            error = pay_setup1.pop('error')
            payload = pay_setup1.pop('payload')
            employee_id = pay_setup1["employee_id"]  # Assuming you have some identifier for each employee
            pay_setup_data_map[employee_id] = json.loads(json.dumps(pay_setup1))
    
        leave_entitlement_data_map = {}
        for leave_entitlement1 in leave_entitlement.find({"job_id": job_id}):
            _id = leave_entitlement1.pop('_id')
            task_id = leave_entitlement1.pop('task_id')
            is_pushed = leave_entitlement1.pop('is_pushed')
            error = leave_entitlement1.pop('error')
            payload = leave_entitlement1.pop('payload')
            employee_id = leave_entitlement1["employee_id"]  # Assuming you have some identifier for each employee
            leave_entitlement_data_map[employee_id] = json.loads(json.dumps(leave_entitlement1))

        other_details_data_map = {}
        for other_details1 in other_details.find({"job_id": job_id}):
            _id = other_details1.pop('_id')
            task_id = other_details1.pop('task_id')
            is_pushed = other_details1.pop('is_pushed')
            error = other_details1.pop('error')
            payload = other_details1.pop('payload')
            employee_id = other_details1["employee_id"]  # Assuming you have some identifier for each employee
            other_details_data_map[employee_id] = json.loads(json.dumps(other_details1))

        for employee_record in excel_reckon_employee.find({"job_id": job_id}):
            _id = employee_record.pop('_id')
            task_id = employee_record.pop('task_id')
            job_id = employee_record.pop('job_id')
            is_pushed = employee_record.pop('is_pushed')
            error = employee_record.pop('error')
            payload = employee_record.pop('payload')
            employee_data = json.loads(json.dumps(employee_record))


            # Match leave entitlement data with the corresponding employee
            if 'employee_id' in employee_record:
                employee_id = employee_record['employee_id']  # Assuming you have some identifier for each employee
                if employee_id in leave_entitlement_data_map:
                    employee_data["EmployeeData"]["Leaves"] = leave_entitlement_data_map[employee_id]["Leaves"]
                else:
                    employee_data["EmployeeData"]["Leaves"] = []  # If no leave entitlement data found, you may handle this case accordingly

                if employee_id in other_details_data_map:
                    
                    employee_data["EmployeeData"]["Payments"] = other_details_data_map[employee_id]["Payments"]
                else:
                    employee_data["EmployeeData"]["Payments"] = []


                if employee_id in pay_setup_data_map:
                    
                    employee_data["EmployeeData"]["PaySetup"] =pay_setup_data_map[employee_id]["PaySetup"]
                    employee_data["EmployeeData"]["BaseRateAmount"] = round(pay_setup_data_map[employee_id].get("BaseRateAmount", None),2)
                    employee_data["EmployeeData"]["BaseRateAmountType"] = pay_setup_data_map[employee_id].get("BaseRateAmountType", None)
                    
                    # employee_data["EmployeeData"]["BaseRateAmount"]=pay_setup_data_map[employee_id]["BaseRateAmount"]
                    # employee_data["EmployeeData"]=pay_setup_data_map[employee_id]["BaseRateAmountType"]
                else:
                    employee_data["EmployeeData"]["PaySetup"] ={}

        
            # result.append(employee_data)
            asyncio.run(process_employee_record(url, post_headers, employee_data, excel_reckon_employee, _id, job_id, task_id, employee_record["FirstNameBranchName"]))

    except Exception as ex:
        import traceback
        traceback.print_exc()
        logging.error(ex, exc_info=True)





