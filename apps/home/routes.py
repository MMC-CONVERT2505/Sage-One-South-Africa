import json
import os
from pathlib import Path
from apps.util.qbo_util import post_data_in_myob, post_data_in_qbo, retry_payload_for_xero_to_myob, retry_payload_for_qbo_to_myob, retry_payload_for_excel_to_myob, retry_payload_for_xero_to_qbo, retry_payload_for_myob_to_qbo, retry_payload_for_excel_to_reckon,retry_payload_for_sageone_to_reckonone
import asyncio
import pdfkit
import zipfile
import io
import pandas as pd
from io import BytesIO
from bson import ObjectId

from apps.util.log_file import log_config_job_creation
from apps.home.data_util import get_job_details
import datetime
from datetime import datetime, timedelta
import ast
import random
import string
from sqlalchemy import desc
import time
import openpyxl
from flask import render_template, redirect, request, url_for, jsonify,flash,get_flashed_messages,make_response,Response,send_file
from flask.helpers import get_root_path
from flask_login import login_required
from jinja2 import TemplateNotFound
from sqlalchemy.orm import aliased
from werkzeug.utils import secure_filename
from flask import Flask
import requests
import webbrowser
import base64


from apps import db
from apps.authentication.routes import login
from apps.authentication.forms import CreateAccountForm
from apps.authentication.forms import CreateJobForm, CreateSettingForm, CreateSelectidForm, CreateIdNameForm, CreateEmailForm, CreateauthcodeForm, CreateFileInfoForm, CreateXeroToolSettingForm,SageOneLoginForm,CreateCustomerInfoForm,CreateToolFileInfoForm,CreateGetdataForm
from apps.authentication.models import Users
from apps.home import blueprint
from apps.home.models import EntityDataReadDetails
from apps.home.models import Jobs, JobExecutionStatus, Task, TaskExecutionStatus, TaskExecutionStep, ToolId, File_Info, XeroTokens, XeroToolSettings,SageUser,SageReckonTokens,ToolFile,UserAccount
from apps.home.models import MyobSettings, QboSettings, XeroSettings, Tool, ToolSettings, XeroToolSettings,CustomerInfo
from apps.myconstant import *
from apps.tasks.myob_to_qbo_task import read_sageone_write_reckon_task,retry_reckon_write_task
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import get_pagination_for_records,get_pagination_for_records_date
from apps.mmc_settings.all_settings import *
from redis import StrictRedis
redis = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@blueprint.route("/index")
@login_required
def index():
    # return render_template('home/index.html', segment='index')

    data = []

    all_files = [
        "all_bill",
        "all_invoices",
        "chart_of_account",
        "classified_COA",
        "combined_bill",
        "customer",
        "employee",
        "item",
        "item_bill",
        "item_invoice",
        "job",
        "journal",
        "misc_bill",
        "professional_bill",
        "received_money",
        "service_bill",
        "spend_money",
        "supplier",
        "taxcode",
        "trial_balance",
    ]

    for fname in all_files:
        edrd = EntityDataReadDetails()
        edrd.entity_name = fname
        edrd.last_read_count = 10
        data.append(edrd)

    return render_template("home/myob-entities.html", segment="myob", data=data)



@blueprint.route("/myob")
@login_required
def myob_entities():
    data = []

    all_files = [
        "all_bill",
        "all_invoices",
        "chart_of_account",
        "classified_COA",
        "combined_bill",
        "customer",
        "employee",
        "item",
        "item_bill",
        "item_invoice",
        "job",
        "journal",
        "misc_bill",
        "professional_bill",
        "received_money",
        "service_bill",
        "spend_money",
        "supplier",
        "taxcode",
        "trial_balance",
    ]

    for fname in all_files:
        edrd = EntityDataReadDetails()
        edrd.entity_name = fname
        edrd.last_read_count = 10
        data.append(edrd)

    return render_template("home/myob-entities.html", segment="myob", data=data)


@blueprint.route("/jobs")
@login_required
def jobs():
    page = request.args.get('page', 1, type=int)
    tool1 = aliased(Tool)
    tool2 = aliased(Tool)
    jobs = (
        db.session.query(
            Jobs,
            tool1.tool_name.label("input_tool"),
            tool2.tool_name.label("output_tool"),
        )
        .join(tool1, Jobs.input_account_id == tool1.id)
        .join(tool2, Jobs.output_account_id == tool2.id)
    )

    jobs_data = jobs.paginate(page=page, per_page=100)
    # jobs_data.items.reverse()

    return render_template("home/jobs.html", segment="jobs", jobs=jobs_data)


@blueprint.route("/tasks/<int:job_id>")
@login_required
def tasks_by_job11(job_id):
    tasks = Task.query.filter(
        Task.job_id == job_id
    ).all()

    job_and_task = db.session.query(Jobs, Task)\
        .join(Task, Jobs.id == Task.job_id)\
        .filter(Jobs.id == job_id)\
        .all()
    
    return render_template("home/tasks.html", segment="tasks", data=job_and_task, job_id=job_id)



@blueprint.route("/start_job/<int:job_id>")
@login_required
def start_job(job_id):
    # read_sageone_write_reckon_task.apply_async(args=[job_id])
    tasks = Task.query.filter(
        Task.job_id == job_id
    ).all()
    return render_template("home/tasks.html", segment="tasks", data=tasks)


@blueprint.route("/startJobByID/<int:job_id>", methods=["POST"])

def startJobByID(job_id):
    job_id = redis.get(f'MMCJOB_{job_id}')
    token_data = Jobs.query.filter(Jobs.id == job_id).first()
    token_data.is_successful = 1
    status_data=reckon_filestatus("InProgress",job_id)

    if status_data == True:
        asyncio.run(read_sageone_write_reckon_task(job_id))
        return render_template("home/conversion_underway.html")
    else:
        get_flashed_messages()
        flash('Please enable reckon file status', 'error')
        return redirect(
            url_for(
                ".start_conversion",job_id=job_id
            )
        )


@blueprint.route("/startJobByIDSelf/<int:job_id>", methods=["POST"])
@login_required
def startJobByIDSelf(job_id):
    asyncio.run(read_sageone_write_reckon_task(job_id))
    return json.dumps({'status': 'success'})

@blueprint.route("/startJobByIDUser", methods=["POST"])
@login_required
def startJobByIDUser():
    job_id = request.form['job_id']
    create_logfile(job_id)
    asyncio.run(read_sageone_write_reckon_task(job_id))
    return json.dumps({'status': 'success'})


@blueprint.route("/startJobByIDreport/<int:job_id>", methods=["POST"])
@login_required
def startJobByIDreport(job_id):
    print("inside start job id report ======")

    asyncio.run(read_sageone_write_reckon_task(job_id))
    return json.dumps({'status': 'success'})





@blueprint.route("/retryPayload", methods=["POST"])
@login_required
def retryPayload():
    print("inside retry")
    dbname = get_mongodb_database()
    task_id = request.form['task_id']
    _id = request.form['_id']
    payload1 = request.form['payload']
    payload_data = json.loads(payload1)

    tool1 = aliased(Tool)
    tool2 = aliased(Tool)
    task_details = db.session.query(Task).get(task_id)
    job_id = task_details.job_id
    jobs, input_tool, output_tool = db.session.query(Jobs, tool1.account_type.label('input_tool'),
                                                     tool2.account_type.label(
                                                         'output_tool')
                                                     ).join(tool1, Jobs.input_account_id == tool1.id
                                                            ).join(tool2, Jobs.output_account_id == tool2.id
                                                                   ).filter(Jobs.id == job_id).first()

    function_name = task_details.function_name

    if output_tool == RECKON:
        if input_tool == SAGEONE:
            payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
                job_id)
            status = retry_payload_for_sageone_to_reckonone(
                job_id, payload_data, _id, task_id, function_name)

            if status == 'success':
                return json.dumps({'status': 'success'})
            else:
                return json.dumps({'status': 'error'})

        if input_tool == EXCEL:
            payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
                job_id)
            # print("inside excel input retry" )
            status = retry_payload_for_excel_to_reckon(
                job_id, payload_data, _id, task_id, function_name)

            if status == 'success':
                return json.dumps({'status': 'success'})
            else:
                return json.dumps({'status': 'error'})


@blueprint.route("/task_execution_details/<int:task_id>")
@login_required
def task_execution_details(task_id):
    task_steps = TaskExecutionStep.query.filter(
        TaskExecutionStep.task_id == task_id
    ).all()
    return render_template("home/task_execution_details.html", segment="task_steps", data=task_steps)


@blueprint.route("/conversion_report/<int:job_id>")
# @login_required
def conversion_report(job_id):
    dbname = get_mongodb_database()

    function_name = ["Chart of Account", "Supplier", "Customer", "Item", "Spend Money",
                     "Receive Money", "Bank Transfer", "Journal", "Invoice", "Bill", "Invoice Payment", "Bill Payment"]
    table_name = [dbname['sage_coa'], dbname['sage_supplier'], dbname['sage_customer'], dbname['sage_item'], dbname['sage_spend_money'], dbname['sage_received_money'],
                  dbname['sage_bank_transfer'], dbname['sage_manual_journal'], dbname['sage_invoice'], dbname['sage_bill'], dbname['sage_invoice_payment'], dbname['sage_bill_payment']]

    condition1 = {"job_id": f"{job_id}"}
    condition2 = {"job_id": f"{job_id}", "is_pushed": 1}
    condition3 = {"job_id": f"{job_id}", "is_pushed": 0}

    all_data = []
    pushed_data = []
    unpushed_data = []
    for k in range(0, len(table_name)):
        print(k)

        all_data1 = table_name[k].count_documents(condition1)
        pushed_data1 = table_name[k].count_documents(condition2)
        unpushed_data1 = table_name[k].count_documents(condition3)
        all_data.append(all_data1)
        pushed_data.append(pushed_data1)
        unpushed_data.append(unpushed_data1)

    return render_template("home/conversion_report.html", function_name=function_name, data1=all_data, data2=pushed_data, data3=unpushed_data)


# @blueprint.route("/xero-connect", methods=["GET", "POST"])
# def xero_connect():

#     client_id = XERO_CI
#     client_secret = XERO_CS
#     redirect_uri = XERO_REDIRECT
#     scope = "email%20profile%20openid%20accounting.reports.read%20payroll.employees%20payroll.employees.read%20accounting.settings%20accounting.transactions%20accounting.transactions.read%20accounting.contacts%20offline_access"

#     CLIENT_ID = f"{client_id}"
#     CLIENT_SECRET = f"{client_secret}"
#     clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
#     encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
#     auth_code = "%s" % encoded_u

#     auth_url = ('''https://login.xero.com/identity/connect/authorize?''' +
#                 '''response_type=code''' +
#                 '''&client_id=''' + client_id +
#                 '''&client_secret=''' + client_secret +
#                 '''&redirect_uri=''' + redirect_uri +
#                 '''&scope=''' + scope +
#                 '''&state=123456''')
#     print(auth_url)

#     # webbrowser.open_new(auth_url)

#     return redirect(auth_url)


# @blueprint.route("/create_auth_code", methods=["GET", "POST"])
# def create_auth_code():
#     create_file_info_form = CreateFileInfoForm(request.form)
#     if request.method == "GET":

#         return render_template("home/create_store_file_info.html",
#                                form=create_file_info_form
#                                )

#     if request.method == "POST":
#         File_info = File_Info()

#         File_info.file_name = request.form["name"]
#         db.session.add(File_info)
#         db.session.commit()

#         key_to_clear = 'my_file_key'
#         redis.delete(key_to_clear)

#         redis.set('my_file_key', File_info.id)
#         print(redis.get('my_file_key'), "request data same function ")

#         client_id = XERO_CI
#         client_secret = XERO_CS
#         CLIENT_ID = f"{client_id}"
#         CLIENT_SECRET = f"{client_secret}"
#         clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
#         encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
#         auth_code = "%s" % encoded_u
#         redirect_uri = XERO_REDIRECT
#         auth_code1 = request.args.get("code")
#         print(auth_code1)

#         exchange_code_url = "https://identity.xero.com/connect/token"
#         response = requests.post(exchange_code_url,
#                                  headers={'Authorization': "Basic" "  " + f'{auth_code}',
#                                           'Content-Type': 'application/x-www-form-urlencoded'
#                                           },
#                                  data={
#                                      'grant_type': 'authorization_code',
#                                      'code': f"{auth_code1}",
#                                      'redirect_uri': f"{redirect_uri}"
#                                  })
#         json_response = response.json()
#         print(json_response)

#         token_data = XeroTokens()
#         token_data.xero_access_token = response.json().get("access_token")
#         token_data.xero_refresh_token = response.json().get("refresh_token")
#         db.session.add(token_data)
#         db.session.commit()

#         key_to_clear = 'my_xero_key'
#         redis.delete(key_to_clear)

#         redis.set('my_xero_key', token_data.id)
#         print(redis.get('my_xero_key'), "request data same function ")

#         return redirect(
#             url_for(
#                 ".create_auth_data"


#             )
#         )




@blueprint.route("/create_auth_data", methods=["GET", "POST"])
def create_auth_data():
    create_xero_tool_setting_form = CreateXeroToolSettingForm(request.form)

    if request.method == "GET":

        abc = get_xerocompany_data()
        if abc == False:
            return "you choose wrong file name file name does't match"

        else:

            xero_token_data = XeroTokens.query.filter(
                XeroTokens.id == redis.get('my_xero_key')).first()

            xero_access_token = xero_token_data.xero_access_token
            xero_refresh_token = xero_token_data.xero_refresh_token
            xero_client_id = xero_token_data.xero_company_id

            return render_template("home/create_xero_setting.html",
                                   XERO_KEY=XERO_KEY,
                                   xero_access_token=xero_access_token,
                                   xero_refresh_token=xero_refresh_token,
                                   xero_client_id=xero_client_id,
                                   form=create_xero_tool_setting_form
                                   )

    if request.method == "POST":

        xero_tool_setting = XeroToolSettings()
        xero_tool_setting.name = request.form["name"]
        xero_tool_setting.account_type = request.form["account_type"]
        xero_tool_setting.tool_type = request.form["tool_type"]
        xero_tool_setting.client_id = request.form["client_id"]
        xero_tool_setting.client_secret = request.form["client_secret"]
        xero_tool_setting.refresh_token = request.form["refresh_token"]
        xero_tool_setting.access_token = request.form["access_token"]
        xero_tool_setting.xero_tenant_id = request.form["xero_tenant_id"]
        xero_tool_setting.state = request.form["state"]
        xero_tool_setting.scopes = request.form["Scopes"]
        xero_tool_setting.redirect_uri = request.form["re_directURI"]
        db.session.add(xero_tool_setting)
        db.session.commit()


        return render_template("home/create_job.html")


def get_xerocompany_data():

    xero_company_name = File_Info.query.filter(
        File_Info.id == redis.get('my_file_key')).first()
    xero_access_token = XeroTokens.query.filter(
        XeroTokens.id == redis.get('my_xero_key')).first()
    print(xero_company_name.file_name, "print data company name ")

    url = "https://api.xero.com/connections"
    payload = {}
    headers = {
        'Authorization': f'Bearer {xero_access_token.xero_access_token}'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    json_response = response.json()

    if response.status_code == 200:
        json_response = response.json()
        for entry in json_response:
            if entry["tenantName"].lower() == xero_company_name.file_name.lower():
                print("inside true condition")
                token_data = XeroTokens.query.filter_by(
                    id=redis.get('my_xero_key')).first()
                token_data.xero_company_id = entry["tenantId"]
                db.session.commit()
                return True
        return False
    else:
        return False
    

@blueprint.route("/qbo_auth", methods=["GET", "POST"])
def qbo_auth():

    # CLIENT_ID = 'ABAngR99FX2swGqJy3xeHfeRfVtSJjHqlowjadjeGIg4W0mIdz'
    # CLIENT_SECRET = 'EC2abKy1uhHQcEpIDZy7EerH8i8hKl9gJ1ARGILE'

    # CLIENT_ID = 'ABpWOUWtcEG1gCun5dQbQNfc7dvyalw5qVF97AkJQcn5Lh09o6'
    # CLIENT_SECRET = 'LepyjXTADW592Dq5RYUP8UbGLcH5xtqDQhrf2xJN'

    # qtfy id client id and client secret

    auth_url="https://developer.intuit.com/app/developer/playground?code=AB11653902549GVs1sYca2hm547HNU66Gvz73WkYylRQBYUdcX&state=PlaygroundAuth&realmId=4620816365226489730"
   
    # auth_url = f'{AUTHORIZATION_ENDPOINT}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=com.intuit.quickbooks.accounting&state=12345'
    # auth_url = f'{AUTHORIZATION_ENDPOINT}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=com.intuit.quickbooks.accounting&state={random_key}'

    print(auth_url, "print auth url ")
    # webbrowser.open_new(auth_url)

    # return redirect(url_for("home_blueprint.jobs"))
    return webbrowser.open_new_tab(auth_url)


@blueprint.route("/records/<int:task_id>/<function_name>/<string:start_date>/<string:end_date>")
@login_required
def records(task_id, function_name,start_date,end_date):
    print(start_date,end_date,"start_date,end_date============")
    dbname = get_mongodb_database()
    page = request.args.get('page', 1, type=int)

    tool1 = aliased(Tool)
    tool2 = aliased(Tool)
    task_details = db.session.query(Task).get(task_id)
    job_id = task_details.job_id
    jobs, input_tool, output_tool = db.session.query(Jobs, tool1.account_type.label('input_tool'),
                                                     tool2.account_type.label(
                                                         'output_tool')
                                                     ).join(tool1, Jobs.input_account_id == tool1.id
                                                            ).join(tool2, Jobs.output_account_id == tool2.id
                                                                   ).filter(Jobs.id == job_id).first()

    print(input_tool, '===================')

    if input_tool == SAGEONE:

        if function_name == 'Chart of account':
            if output_tool == RECKON:
                page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                    task_id, dbname["sage_coa"])
                # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                # task_id, dbname["sage_coa"],start_date,end_date)
            
                data1 = []
                for i in data:
                    data1.append(i)
                return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)
        
        if function_name == 'Customer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["sage_customer"])
            
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
            #     task_id, dbname["sage_customer"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Supplier':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["sage_supplier"])
            
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
            #     task_id, dbname["sage_supplier"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'Trial Balance':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["sage_trial_balance"])
        
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'Item':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["sage_item"])
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
            #     task_id, dbname["sage_item"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        
        if function_name == 'Spend Money':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_spend_money"])
            
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_spend_money"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Receive Money':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_receive_money"])
            

            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_receive_money"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Invoice':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_invoice"])

            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_invoice"],start_date,end_date)

            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Invoice CreditNote':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_credit_note"])

            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_credit_note"],start_date,end_date)

            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Bill':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_bill"])
            
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_bill"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Bill VendorCredit':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_vendorcredit"])

            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_vendorcredit"],start_date,end_date)

            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

    
        if function_name == 'Journal':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_manual_journal"])
            
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_manual_journal"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Invoice Payment':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_invoice_payment"])
            
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_invoice_payment"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Bill Payment':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_bill_payment"])
            
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_bill_payment"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

          
        if function_name == 'Customer Adjustments':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_customer_adjustment"])

            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_customer_adjustment"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Supplier Adjustments':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_supplier_adjustment"])
            
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_supplier_adjustment"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)
        

        if function_name == 'Customer Write Off':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_customer_write_off"])
            
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_customer_write_off"],start_date,end_date)
           
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)
        
        if function_name == 'Bank Transfer':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_bank_transfer"])

            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_bank_transfer"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'Tax Payment':
            # page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
            #     task_id, dbname["sage_bank_transfer"])

            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records_date(
                task_id, dbname["sage_bank_transfer"],start_date,end_date)
            
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

    if input_tool == EXCEL and output_tool == RECKON:
        if function_name == 'Account':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_chart_of_account"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Customer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_contact"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Supplier':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_contact"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Employee':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_employee"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Item':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_item"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Invoice':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_invoice"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Bills':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_bill"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Customer payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_invoice_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Supplier Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_bill_payment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Journals':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_journal"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Bank Transfer':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_bank_transfer"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Spend Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_spend_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Receive Money':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_receive_money"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Invoice Over Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_invoice_overpayment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Bill Over Payment':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_bill_overpayment"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Credit Memo':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_creditnote"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'Pay Item Earning':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_payrollearning"])
            print("inside payi tems earnings data===========================>",data)
            data1 = []
            print("data----->>",data1)
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)
       
        if function_name == 'Payitem Allowance':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_payrollallowance"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)
       
        if function_name == 'Payroll Deduction':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_payrolldeduction"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)
       
        if function_name == 'Pay Item Reimbursement':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_reimbursement"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Pay Item Superannuation':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_payrollsuperannuation"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Pay Item Leave':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_payroll_leave"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Pay Item Company contribution':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_payroll_company_contribution"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'Pay Schedules':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_payrollSchedules"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'Superannuation funds':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_payroll_superannuation_funds"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'Employee details':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_payroll_employee_details"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'Leave entitlements':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_leave_entitlements"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'Other details':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_other_details"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'Pay Setup':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_payroll_paysetup"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)
        
        if function_name == 'YTDS Allowance':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["get_excel_ytds_allowance"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'YTDS Fringe benefits':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["get_excel_ytds_Fringe_benefits"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'YTDS Earning':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["get_excel_ytds_earning_leave"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'YTDS Leave':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["get_excel_ytds_leave"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'YTDS Reimbursement':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["get_excel_ytds_reimbursement"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'YTDS Superannuation':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["get_excel_ytds_superannuation"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'YTDS Tax':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["get_excel_ytds_tax"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'YTDS Company contributions':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["get_excel_ytds_company_contributions"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

        if function_name == 'YTDS Company contributions':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["get_excel_ytds_company_contributions"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'YTDS Deduction':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["get_excel_ytds_deduction"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)


        if function_name == 'Leave Balance':
            page, per_page, total_records, successful_count, error_count, data = get_pagination_for_records(
                task_id, dbname["excel_reckon_leave_balance"])
            data1 = []
            for i in data:
                data1.append(i)
            return render_template("home/records.html", data1=data1, page=page, per_page=per_page, total_records=total_records, successful_count=successful_count, error_count=error_count)

    records_data = jobs.paginate(page=page, per_page=50)
    return render_template("home/records.html", segment="records", records=records_data)



@blueprint.route("/job_execution_status/<int:job_id>")
@login_required
def Job_Execution_Status(job_id):
    job_execution_status = JobExecutionStatus.query.filter(
        JobExecutionStatus.job_id == job_id
    )
    return render_template(
        "home/job_status.html",
        segment="job_execution_status",
        data=job_execution_status,
    )


@blueprint.route("/task_execution_status/<int:job_id>")
@login_required
def Task_Execution_Status(task_id):
    task_execution_status = TaskExecutionStatus.query.filter(
        TaskExecutionStatus.task_id == task_id
    )
    return render_template(
        "home/job_status.html",
        segment="task_execution_status",
        data=task_execution_status,
    )

def get_company_info_sageone(username,password):
    print("get_company_info_sageone")
   
    url = "https://accounting.sageone.co.za/api/2.0.0/Company/Get?apikey={FA4FF7F8-216A-406A-A72C-D710DBE4F787}"

    CLIENT_ID = username
    CLIENT_SECRET = password
    clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
    encoded_u = base64.b64encode(clientIdSecret.encode()).decode()

    payload = {}
    headers = {
    'Authorization': f'Basic {encoded_u}',
    'Cookie': '__cf_bm=EE1lPFl7VsdLJxiY2_tHb.dUu0PEjm..GpoQqS7s36M-1707119230-1-Aef2QacB0s1Fl3SrjgDZjYpXUyaWlbN2B/mVB+rPcYKifKIGqDnkLcJkH9KN1uV/PY6kd2p6F4EPShy3vQN0ql4='
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response,"responseresponseresponse")


    return response.status_code


def get_company_data_sageone(username, password):
    company_data = []
    url_template = "https://accounting.sageone.co.za/api/2.0.0/Company/Get?$top=500&$skip={}&apikey={{FA4FF7F8-216A-406A-A72C-D710DBE4F787}}"
    offset = 0

    while True:
        url = url_template.format(offset)
        headers = {
            'Authorization': f'Basic {base64.b64encode((username + ":" + password).encode()).decode()}',
            'Cookie': '__cf_bm=EE1lPFl7VsdLJxiY2_tHb.dUu0PEjm..GpoQqS7s36M-1707119230-1-Aef2QacB0s1Fl3SrjgDZjYpXUyaWlbN2B/mVB+rPcYKifKIGqDnkLcJkH9KN1uV/PY6kd2p6F4EPShy3vQN0ql4='
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            JsonResponse = response.json()
            company_data.extend(JsonResponse["Results"])
            total_results = JsonResponse["TotalResults"]
            offset += len(JsonResponse["Results"])
            if offset >= total_results:
                break
        else:
            print("Failed to fetch data. Status code:", response.status_code)
            break

    print("Outside the function")
    print(company_data, "company_data======")
    return company_data

@blueprint.route("/SageOne_Login/<int:job_id>", methods=["GET", "POST"])

def SageOne_Login(job_id):

    create_sage_login_form = SageOneLoginForm(request.form)
    if request.method == "GET":
        return render_template("home/sageone_login.html",
                               form=create_sage_login_form                        
                               )
    if request.method == "POST":
        sage_info = SageUser()
        sage_info.job_id = job_id
        sage_info.email= request.form["sageusername"]
        sage_info.password = request.form["sagepassword"]
        db.session.add(sage_info)
        db.session.commit()

        username=request.form["sageusername"]
        password= request.form["sagepassword"]

        callback1=get_company_info_sageone(username,password)

        if callback1 in [200,201]:

            successful_data=get_company_data_sageone(username,password)
            sageone_company_name = CustomerInfo.query.filter(
                    CustomerInfo.job_id == job_id).first()
            sageone_user_data = SageUser.query.filter(
                    SageUser.job_id == job_id).first()
        
            token_data = SageReckonTokens()
            token_data.job_id = job_id
            token_data.sage_username = sageone_user_data.email
            token_data.sage_password = sageone_user_data.password
            db.session.add(token_data)
            db.session.commit()
            for entry in successful_data["Results"]:
                if sageone_company_name.Company.lower() == entry["DisplayName"].lower():
                    token_data1 = SageReckonTokens.query.filter(
                        SageReckonTokens.job_id == job_id).first()
                    token_data1.sage_company_id = entry["ID"]
                    db.session.add(token_data1)
                    db.session.commit()
                    return redirect(
                        url_for(
                            ".connect_output_tool",job_id=job_id

                        )
                    )
                
                else:
                    flash("Please enter a valid company name ")

                    return redirect(
                        url_for(
                            ".SageOne_Login",job_id=job_id
                        )
                    )

        else:

            flash("Please enter a valid email or password.")

            return redirect(
                url_for(
                    ".SageOne_Login",job_id=job_id

                )
            )
           
  


@blueprint.route("/delete_job_page", methods=["GET", "POST"])
@login_required
def delete_job_page():
    create_job_form = CreateJobForm(request.form)
    if request.method == "GET":
        input_settings = Tool.query.filter(
            Tool.tool_type == "Input", Tool.account_type == "Delete")
        # qbo_settings = QboSeCreateJobFormttings.query.all()
        output_settings = Tool.query.filter(Tool.tool_type == "Output")
        return render_template(
            "home/delete_job_page.html",
            segment="jobs",
            input_settings=input_settings,
            output_settings=output_settings,
            form=create_job_form,
        )

    if request.method == "POST":
        input_type = 'delete'

        # if account_type != EXCEL:
        if (
                request.form["output_account_id"] == "None"
        ):
            return redirect(
                url_for(
                    ".delete_job_page",
                    msg="Input account and output account are the mandatory fields!!!!.",
                    success=True,
                )
            )

        if len(request.form.getlist("mycheckbox")) == 0:
            return redirect(
                url_for(
                    ".delete_job_page",
                    msg="Please select atleast one function!!!!.",
                    success=True,



                )
            )

        # elif (request.form['myob_account'] is not None and request.form['xero_account'] == 'None') or (request.form['myob_account'] == 'None' and request.form['xero_account'] is not None):
        job = Jobs()
        fn = request.form.getlist('mycheckbox')
        job.functions = ",".join(fn)
        job.name = request.form["name"]
        job.description = request.form["description"]
        job.input_account_id = request.form["input_account_id"]
        job.output_account_id = request.form["output_account_id"]
        job.start_date = request.form["start_date"]
        job.end_date = request.form["end_date"]
        # TODO: Create job and tasks in same transaction, rollback if anything fails
        db.session.add(job)
        db.session.commit()
        # read_sageone_write_reckon_task.apply_async(args=[job.id])
        for fun in range(0, len(fn)):
            task = Task()
            task.function_name = fn[fun]
            task.job_id = job.id
            db.session.add(task)
            db.session.commit()
        return redirect(
            url_for(
                ".tasks_by_job",
                job_id=job.id,
                msg="Job created successfully!!!!.",
                success=True,
            )
        )


@blueprint.route("/create_id_name_page", methods=["GET", "POST"])
@login_required
def create_id_name_page():
    create_id_name_form = CreateIdNameForm(request.form)
    if request.method == "GET":
        return render_template(
            "home/create_id_name.html",
            segment="jobs",
            form=create_id_name_form,
        )

    if request.method == "POST":
        toolId = ToolId()
        toolId.Email = request.form["name"]
        toolId.client_id = request.form["client_id"]
        toolId.client_secret = request.form["client_secret"]
        db.session.add(toolId)
        db.session.commit()
        return redirect(
            url_for(
                ".create_auth_token",
                tool_id=toolId.id,
                msg="Email created successfully!!!!.",
                success=True,
            )
        )


@blueprint.route("/Reckon_job_page", methods=["GET", "POST"])
@login_required
def Reckon_job_page():
    create_job_form = CreateJobForm(request.form)
    if request.method == "GET":
        input_settings = Tool.query.filter(
            Tool.tool_type == "Input", Tool.account_type == "Excel")
        # qbo_settings = QboSeCreateJobFormttings.query.all()
        output_settings = Tool.query.filter(
            Tool.tool_type == "Output", Tool.account_type == "Reckon")
        return render_template(
            "home/create_job.html",
            segment="jobs",
            input_settings=input_settings,
            output_settings=output_settings,
            form=create_job_form,
        )

    if request.method == "POST":
        input_type = 'Excel'

        job_id = upload_file(request)
        return redirect(
            url_for(
                ".tasks_by_job",
                job_id=job_id,
                msg="Job created successfully!!!!.",
                success=True,
            )
        )


@blueprint.route("/onclickauth", methods=["GET", "POST"])
@login_required
def onclickauth():
    client_id = "BDDDE967BCF943098B8A44E164AE1A74"
    client_secret = "JVCy3rDSvqkMelGOxJenpLkdiAgRgiHcXLe6GJZ79IAKXv_l"
    redirect_uri = "https://www.mmcconvert.com"
    scope = "offline_access accounting.transactions"

    CLIENT_ID = f"{client_id}"
    CLIENT_SECRET = f"{client_secret}"
    clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
    encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
    auth_code = "%s" % encoded_u

    auth_url = ('''https://login.xero.com/identity/connect/authorize?''' +
                '''response_type=code''' +
                '''&client_id=''' + client_id +
                '''&client_secret=''' + client_secret +
                '''&redirect_uri=''' + redirect_uri +
                '''&scope=''' + scope +
                '''&state=123456''')

    webbrowser.open_new(auth_url)
    return redirect(
        url_for(
            ".create_auth_code"
        )
    )


@blueprint.route("/choice_email_page", methods=["GET", "POST"])
@login_required
def choice_email_page():
    choice_email_page_form = CreateEmailForm(request.form)
    if request.method == "GET":

        email_settings = ToolId.query.all()

        return render_template(
            "home/choice_email_name.html",
            segment="jobs",
            email_settings=email_settings,
            form=choice_email_page_form,
        )

    if request.method == "POST":
        toolId = ToolId()
        return redirect(
            url_for(
                ".create_auth_code",
                client_id=toolId.client_id,
                client_secret=toolId.client_secret,


            )
        )


# @blueprint.route("/id_select_page", methods=["GET", "POST"])
# @login_required
# def id_select_page():
#     create_idselect_form = CreateSelectidForm(request.form)
#     if request.method == "GET":

#         return render_template(
#             "home/delete_job_page.html",
#             segment="jobs",
#             form=create_idselect_form,
#         )

#     if request.method == "POST":


# @blueprint.route("/jobs/create", methods=["GET", "POST"])
# @login_required
# def create_job():
#     create_job_form = CreateJobForm(request.form)
#     if request.method == "GET":
#         input_settings = Tool.query.filter(
#             Tool.tool_type == "Input", Tool.account_type != "Delete")
#         # and XeroToolSettings.query.filter(XeroToolSettings.tool_type == "Input")
#         print(input_settings, "print input setting data")
#         # qbo_settings = QboSeCreateJobFormttings.query.all()
#         output_settings = Tool.query.filter(Tool.tool_type == "Output")
#         # and XeroToolSettings.query.filter(XeroToolSettings.tool_type == "Output")
#         print(output_settings)

#         return render_template(
#             "home/create_job.html",
#             segment="jobs",
#             input_settings=input_settings,
#             output_settings=output_settings,
#             form=create_job_form,
#         )

#     if request.method == "POST":
#         input_type = Tool.query.filter(
#             Tool.id == request.form["input_account_id"]
#         ).first()
#         account_type = input_type.account_type

#         if account_type != EXCEL:
#             if (request.form["input_account_id"] == "None") and (
#                     request.form["output_account_id"] == "None"
#             ):
#                 return redirect(
#                     url_for(
#                         ".create_job",
#                         msg="Input account and output account are the mandatory fields!!!!.",
#                         success=True,
#                     )
#                 )

#             if len(request.form.getlist("mycheckbox")) == 0:
#                 return redirect(
#                     url_for(
#                         ".create_job",
#                         msg="Please select atleast one function!!!!.",
#                         success=True,
#                     )
#                 )

#             # elif (request.form['myob_account'] is not None and request.form['xero_account'] == 'None') or (request.form['myob_account'] == 'None' and request.form['xero_account'] is not None):
#             job = Jobs()
#             fn = request.form.getlist('mycheckbox')
#             job.functions = ",".join(fn)
#             job.name = request.form["name"]
#             job.description = request.form["description"]
#             job.input_account_id = request.form["input_account_id"]
#             job.output_account_id = request.form["output_account_id"]
#             job.start_date = request.form["start_date"]
#             job.end_date = request.form["end_date"]
#             job_name = Jobs.query.filter(Jobs.name == job.name).first()
#             if job_name is None:
#                 db.session.add(job)
#                 db.session.commit()
#             else:
#                 flash("This job name is already exist,please create new one!")

#                 return redirect(
#                     url_for(
#                         ".create_job",

#                     )
#                 )
#             # TODO: Create job and tasks in same transaction, rollback if anything fails

#             # read_sageone_write_reckon_task.apply_async(args=[job.id])
#             for fun in range(0, len(fn)):
#                 task = Task()
#                 task.function_name = fn[fun]
#                 task.job_id = job.id
#                 db.session.add(task)
#                 db.session.commit()
#             return redirect(
#                 url_for(
#                     ".tasks_by_job",
#                     job_id=job.id,
#                     msg="Job created successfully!!!!.",
#                     success=True,
#                 )
#             )
#         else:
#             job_id = upload_file(request)
#             return redirect(
#                 url_for(
#                     ".tasks_by_job",
#                     job_id=job_id,
#                     msg="Job created successfully!!!!.",
#                     success=True,
#                 )
#             )


@blueprint.route("/myob_settings")
@login_required
def myob_settings():
    myob_settings = MyobSettings.query.all()
    return render_template(
        "home/myob_settings.html", segment="myob_settings", data=myob_settings
    )


@blueprint.route("/qbo_settings")
@login_required
def qbo_settings():
    settings = QboSettings.query.all()
    return render_template(
        "home/qbo_settings.html", segment="qbo_settings", data=settings
    )


@blueprint.route("/xero_settings")
@login_required
def xero_settings():
    xero_settings = XeroSettings.query.all()
    return render_template(
        "home/xero_settings.html", segment="xero_settings", data=xero_settings
    )


@blueprint.route("/tool")
@login_required
def tool():
    tool = Tool.query.all()
    return render_template("home/tool.html", segment="tool", data=tool)


@blueprint.route("/tool/create", methods=["GET", "POST"])
@login_required
def create_tool():
    create_setting_form = CreateSettingForm(request.form)
    if request.method == "GET":
        data = []
        return render_template(
            "home/create_tool.html",
            segment="settings",
            data=data,
            form=create_setting_form,
            MYOB_KEY=MYOB_KEY,
            QBO_KEY=QBO_KEY,
            XERO_KEY=XERO_KEY,
            MYOBLEDGER_KEY=MYOBLEDGER_KEY,
            EXCEL_KEY=EXCEL_KEY,
            DELETE_KEY=DELETE_KEY,
            RECKON_KEY=RECKON_KEY,
            SAGEONE_KEY=SAGEONE_KEY,
           
        )
    if request.method == "POST":
        setting = Tool(**request.form)
        db.session.add(setting)
        db.session.commit()
        return redirect(
            url_for(".tool", msg="Tool created successfully!!!!.", success=True)
        )


@blueprint.route("/tool/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_tool(id):
    if request.method == "GET":
        tool = Tool.query.filter(Tool.id == id).first()
        if tool:
            return render_template("home/edit_tool.html", tool=tool)

    if request.method == "POST":
        tool = Tool.query.filter(Tool.id == request.form["id"]).first()
        tool.tool_name = request.form["tool_name"]
        tool.keys = request.form["keys"]
        tool.account_type = request.form["account_type"]
        # tool.tool_type = request.form["tool_type"]
        db.session.commit()
        return redirect(
            url_for(".tool", msg="Tool updated successfully!!!!.", success=True)
        )


@blueprint.route("/tool_settings")
@login_required
def tool_settings():
    tool_settings = ToolSettings.query.all()
    return render_template(
        "home/tool_settings.html", segment="tool_settings", data=tool_settings
    )


@blueprint.route("/tool_settings/create/<int:id>", methods=["GET", "POST"])
@login_required
def create_tool_settings(id):
    create_setting_form = CreateSettingForm(request.form)
    if request.method == "GET":
        tool = Tool.query.filter(Tool.id == id).first()
        tool_xero_type = Tool.query.filter(Tool.account_type == "Xero").first()
        tool_settings = ToolSettings.query.filter(
            ToolSettings.tool_id == id).all()
        key_list = tool.keys.split(",")
        return render_template(
            "home/create_tool_settings.html",
            zip=zip,
            len=len,
            segment="settings",
            tool=tool,
            toolsettings=tool_settings,
            data=key_list,
            tool_xero_type=tool_xero_type,
            form=create_setting_form,
            
        )
    if request.method == "POST":
        tool = Tool.query.filter(Tool.id == id).first()
        key_list = tool.keys.split(",")
        for i in range(0, len(key_list)):
            tool_settings = ToolSettings.query.filter(
                ToolSettings.tool_id == id, ToolSettings.keys == key_list[i].strip(
                )
            ).first()

            if tool_settings is not None:
                tool_settings.keys = key_list[i].strip()
                tool_settings.values = request.form[key_list[i]].strip()
                db.session.commit()

            else:
                setting = ToolSettings()
                setting.tool_id = id
                setting.keys = key_list[i].strip()
                setting.values = request.form[key_list[i]].strip()
                db.session.add(setting)
                db.session.commit()
        return redirect(
            url_for(
                ".tool", msg="Tool setting created successfully!!!!.", success=True)
        )


@blueprint.route("/myob_settings/create", methods=["GET", "POST"])
@login_required
def create_setting():
    create_setting_form = CreateSettingForm(request.form)
    if request.method == "GET":
        data = []
        return render_template(
            "home/create_myob_setting.html",
            segment="settings",
            data=data,
            form=create_setting_form,
        )
    if request.method == "POST":
        setting = MyobSettings(**request.form)
        db.session.add(setting)
        db.session.commit()
        return render_template(
            "home/myob_settings.html", msg="Setting created successfully.", success=True
        )


@blueprint.route("/myob_settings/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_myob_setting(id):
    if request.method == "GET":
        myob = MyobSettings.query.filter(MyobSettings.id == id).first()
        if myob:
            return render_template("home/edit_myob_setting.html", myob=myob)

    if request.method == "POST":
        myob = MyobSettings.query.filter(
            MyobSettings.id == request.form["id"]).first()
        myob.name = request.form["name"]
        myob.client_id = request.form["client_id"]
        myob.company_file_id = request.form["company_file_id"]
        myob.username = request.form["username"]
        myob.client_secret = request.form["client_secret"]
        myob.access_token = request.form["access_token"]
        myob.password = request.form["password"]
        myob.company_file_uri = request.form["company_file_uri"]
        myob.refresh_token = request.form["refresh_token"]
        db.session.commit()
        return redirect(
            url_for(
                ".myob_settings", msg="Setting updated successfully!!!!.", success=True
            )
        )


@blueprint.route("/qbo_settings/create", methods=["GET", "POST"])
@login_required
def create_qbo_setting():
    create_setting_form = CreateSettingForm(request.form)
    if request.method == "GET":
        data = []
        return render_template(
            "home/create_qbo_setting.html",
            segment="qbo_settings",
            data=data,
            form=create_setting_form,
        )

    if request.method == "POST":
        setting = QboSettings(**request.form)
        db.session.add(setting)
        db.session.commit()

        return redirect(
            url_for(
                ".qbo_settings", msg="Setting Created Successfully!!!!.", success=True
            )
        )


@blueprint.route("/qbo_settings/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_qbo_setting(id):
    if request.method == "GET":
        qbo = QboSettings.query.filter(QboSettings.id == id).first()
        if qbo:
            return render_template("home/edit_qbo_setting.html", qbo=qbo)

    if request.method == "POST":
        qbo = QboSettings.query.filter(
            QboSettings.id == request.form["id"]).first()
        qbo.name = request.form["name"]
        qbo.client_id = request.form["client_id"]
        qbo.client_secret = request.form["client_secret"]
        qbo.minor_version = request.form["minor_version"]
        qbo.username = request.form["username"]
        qbo.company_id = request.form["company_id"]
        qbo.user_agent = request.form["user_agent"]
        qbo.access_token = request.form["access_token"]
        qbo.password = request.form["password"]
        qbo.base_url = request.form["base_url"]
        qbo.refresh_token = request.form["refresh_token"]
        db.session.commit()
        return redirect(
            url_for(
                ".qbo_settings", msg="Setting updated successfully!!!!.", success=True
            )
        )


@blueprint.route("/xero_settings/create", methods=["GET", "POST"])
@login_required
def create_xero_setting():
    create_setting_form = CreateSettingForm(request.form)
    if request.method == "GET":
        data = []
        return render_template(
            "home/create_xero_setting.html",
            segment="xero_settings",
            data=data,
            form=create_setting_form,
        )

    if request.method == "POST":
        setting = XeroSettings(**request.form)
        db.session.add(setting)
        db.session.commit()

        return redirect(
            url_for(
                ".xero_settings", msg="Setting created successfully!!!!.", success=True
            )
        )


@blueprint.route("/xero_settings/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_xero_setting(id):
    if request.method == "GET":
        xero = XeroSettings.query.filter(XeroSettings.id == id).first()
        if xero:
            return render_template("home/edit_xero_setting.html", xero=xero)

    if request.method == "POST":
        xero = XeroSettings.query.filter(
            XeroSettings.id == request.form["id"]).first()
        xero.name = request.form["name"]
        xero.client_id = request.form["client_id"]
        xero.xero_tenant_id = request.form["xero_tenant_id"]
        xero.username = request.form["username"]
        xero.password = request.form["password"]
        xero.client_secret = request.form["client_secret"]
        xero.re_directURI = request.form["re_directURI"]
        xero.access_token = request.form["access_token"]
        xero.scopes = request.form["scopes"]
        xero.state = request.form["state"]
        xero.refresh_token = request.form["refresh_token"]
        db.session.commit()
        return redirect(
            url_for(
                ".xero_settings", msg="Setting updated successfully!!!!.", success=True
            )
        )


@blueprint.route("/myob/entity/<entity_name>")
@login_required
def myob_entity_details(entity_name):
    data_from_db = None
    columns = None
    parent_path = Path(__file__).parent
    filepath = "{}/{}.json".format(parent_path, entity_name)

    with open(filepath, "r") as f:
        data_from_db = json.load(f)

    if data_from_db is not None:
        columns = list(data_from_db[0].keys())

    return render_template(
        "home/myob-entities-data.html",
        segment="myob",
        data=data_from_db,
        columns=columns,
        entity_name=entity_name,
    )


@blueprint.route("/<template>")
@login_required
def route_template(template):
    try:
        if not template.endswith(".html"):
            template += ".html"

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template("home/page-404.html"), 404

    except:
        return render_template("home/page-500.html"), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split("/")[-1]

        if segment == "":
            segment = "index"

        return segment

    except:
        return None


@blueprint.route("/users")
@login_required
def list_users():
    users = Users.query.all()
    return render_template("home/users.html", segment="users", data=users)


@blueprint.route("/register", methods=["GET", "POST"])
@login_required
def register():
    create_account_form = CreateAccountForm(request.form)
    if create_account_form and request.method == "POST":
        email = request.form["email"]
        # Check usename exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template(
                "home/register.html",
                msg="Email is already registered",
                success=False,
                form=create_account_form,
            )

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return redirect(
            url_for(
                ".list_users", msg="User added successfully!!!!.", success=True
            )
        )
    else:
        return render_template("home/register.html", form=create_account_form, user=None)


@blueprint.route("/users/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if request.method == "GET":
        user = Users.query.filter(Users.id == user_id).first()
        create_account_form = CreateAccountForm()
        if user:
            # create_account_form.data["first_name"] = user.first_name
            # create_account_form.data["last_name"] = user.last_name
            # create_account_form.data["email"] = user.email
            return render_template("home/register.html", form=create_account_form, user=user)

    create_account_form = CreateAccountForm(request.form)
    if create_account_form and request.method == "POST":
        # Check usename exists
        user_from_db = Users.query.filter_by(
            email=request.form["email"]).first()
        user_id = user_from_db.id
        # else we can create the user
        user = Users(**request.form)
        if user_id is None:
            db.session.add(user)
            return redirect(
                url_for(
                    ".list_users", msg="User added successfully!!!!.", success=True
                )
            )
        else:
            user_from_db.first_name = user.first_name if user_from_db.first_name != user.first_name else user_from_db.first_name
            user_from_db.last_name = user.last_name if user_from_db.last_name != user.last_name else user_from_db.last_name
            user_from_db.email = user.email if user_from_db.email != user.email else user_from_db.email
            user_from_db.password = user.password if user_from_db.password != user.password else user_from_db.password
            db.session.flush()
            db.session.commit()
        return redirect(
            url_for(
                ".list_users", msg="User updated successfully!!!!.", success=True
            )
        )
    else:
        return render_template("home/register.html", form=create_account_form)


@blueprint.route("/getInputAccountType", methods=["POST"])
@login_required
def getInputAccountType():
    input_type = request.form['input_type']
    print(input_type, "input type print")
    input_type = Tool.query.filter(
        Tool.id == input_type
    ).first()
    #  or XeroToolSettings.query.filter(
    #     XeroToolSettings.id == input_type
    # ).first()

    print(input_type, "print input_type")
    return json.dumps({'account_type': input_type.account_type})
    # return jsonify(input_type)


@blueprint.route("/getToolType", methods=["POST"])
@login_required
def getToolType():
    xero_tool = Tool.query.filter(
        Tool.account_type == "Xero"
    ).all()
    return render_template("home/create_tool_settings.html", xero_tool=xero_tool)
    # return json.dumps({'account_type': xero_tool})


@blueprint.route("/upload")
@login_required
def upload_file(request):
    basedir = os.path.abspath(os.path.dirname(__file__))
    uploaded_file = request.files['excelfile']
    job = Jobs()
    job.name = request.form["name"]
    response=request.url
    split_url = response.split('/')
    last_number = split_url[-1]
    print(last_number)
    job.file_id = last_number
    job.description = request.form["description"]
    job.input_account_id = request.form["input_account_id"]
    job.output_account_id = request.form["output_account_id"]
    job.filename = uploaded_file.filename
    job.start_date = None
    job.end_date = None

    # TODO: Create job and tasks in same transaction, rollback if anything fails
    db.session.add(job)
    db.session.commit()
    filename = f'{job.id}' + '_' + secure_filename(uploaded_file.filename)
    print(get_root_path('apps'))
    if filename != "":
        # uploaded_file.save('app/files/',filename)

        uploaded_file.save(os.path.join(
            get_root_path('apps'), 'files/', filename))
    path = os.path.join(get_root_path('apps'), 'files/', filename)
    print(path)
    data1 = openpyxl.load_workbook(path)
    sheets = data1.sheetnames
    print(sheets)

    # fn = request.form.getlist('mycheckbox')
    # job.functions = ",".join(fn)

    for fun in range(0, len(sheets)):
        task = Task()
        task.function_name = sheets[fun]
        task_response=request.url
        split_url = task_response.split('/')
        last_number = split_url[-1]
        task.file_id = last_number
        task.job_id = job.id
        db.session.add(task)
        db.session.commit()
    return job.id

    # save_path = "/uploads"apps/home/files
    # file_name = "abc.xlsx"
    # completeName = os.path.join(save_path, file_name)
    # file1 = open(completeName, "w")
    # file1.write("file information")
    # file1.close()
    # print("file created")
    # return send_from_directory(app.config['UPLOAD_PATH'],filename)



@blueprint.route("/connect_input_tool11", methods=["GET", "POST"])
def connect_input_tool11():
    create_customer_info_form = CreateCustomerInfoForm(request.form)
    if request.method == "GET":

        return render_template("home/connect_input_tool.html",
                               form=create_customer_info_form
                               )
    if request.method == "POST":
        job = Jobs()

        # job_functions = ['Existing Chart of account', 'Chart of account','Archieved Chart of account','Item','Archieved Customer','Archieved Supplier', 'Customer', 'Supplier', 'Job', 'Journal', 'Spend Money',
        #                  'Receive Money', 'Bank Transfer', 'Bill','Bill VendorCredit', 'Invoice','Invoice CreditNote', 'Payrun', 'Depreciation', 'Open Data', 'AR-AP', 'Trial Balance', 'Report']
        # job.functions = "Existing Chart of account,Chart of account,Archieved Chart of account,Item,Archieved Customer,Archieved Supplier,Customer,Supplier,Job,Journal,Spend Money,Receive Money,Bank Transfer,Bill,Bill VendorCredit,Invoice,Invoice CreditNote,Payrun,Depreciation,Open Data,AR-AP,Trial Balance,Report"

        length = 10
        job.name = ''.join(random.choice(
            string.ascii_letters + string.digits) for _ in range(length))
        print(job.name)
        job.description = ""
        job.input_account_id = 1
        job.output_account_id = 2
        job.start_date = ""
        job.end_date = ""
        db.session.add(job)
        db.session.commit()

        redis.set(f'MMCJOB_{job.id}', job.id)
      
        # for fun in range(0, len(job_functions)):
        #     print('inside for loop', job.id)
        #     task = Task()
        #     task.function_name = job_functions[fun]
        #     task.job_id = job.id
        #     db.session.add(task)
        #     db.session.commit()


        customer_info = CustomerInfo()
        customer_info.job_id = job.id
        customer_info.Company = request.form["inputCompany"]
        customer_info.Email = request.form["inputEmail"]
        customer_info.First_Name = request.form["inputFirstName"]
        customer_info.Last_Name = request.form["inputLastName"]
        customer_info.start_date = request.form["start_date"]
        customer_info.end_date = request.form["end_date"]
        customer_info.cust_status = "basic_data"
        db.session.add(customer_info)
        db.session.commit()

        return redirect(
            url_for(
                ".SageOne_Login",job_id=redis.get(f'MMCJOB_{job.id}')


            )
        )
    
@blueprint.route("/mmc/<string:book_id>",methods=["GET", "POST"])
def mmc(book_id):
    if request.method == "GET":

        api_key = request.headers.get('x-api-key')
        random_key="2a9c1-8d3e2-4f7b9-6a0c5"

        if api_key == random_key:

            job_data = Jobs.query.filter(Jobs.reckon_bookid == book_id).order_by(Jobs.id.desc()).first()

            if job_data is not None:

                #data1=job_data["is_successful"]
                print(job_data)
                return jsonify({"ConversionStatus":"InProgress","status_code":200})
            else:
                return jsonify({"Message":"Reckon book id is not found"}),404
        else:
            return jsonify({"Message": "Unauthorized"}),401
        


@blueprint.route("/reckon_connect/<int:job_id>", methods=["GET", "POST"])
def reckon_connect(job_id):

    client_id = "3d95f9e7-38dc-469c-a197-209cf6e4d5d6"
    redirect_uri = RECKON_REDIRECT_URI
    # scope = "email%20profile%20openid%20accounting.reports.read%20payroll.employees%20payroll.employees.read%20accounting.settings%20accounting.transactions%20accounting.transactions.read%20accounting.contacts%20offline_access"
    scope = "openid+read+write+offline_access"
    CLIENT_ID = f"{client_id}"


    auth_url = ('''https://identity.reckon.com/connect/authorize?''' +
                '''response_type=code''' +
                '''&client_id=''' + client_id +
                '''&redirect_uri=''' + redirect_uri +
                '''&scope=''' + scope +
                f'''&state={job_id}'''
                '''&nonce=random_nonce''')

    return redirect(auth_url)


# @blueprint.route("/reckon_login/<int:job_id>", methods=["GET", "POST"])
# def reckon_login(job_id):
#         return redirect(
#             url_for(
#                 ".reckon_connect",job_id=job_id
#             )
#         ) 

def get_reckoncompany_data11(job_id):
    reckon_company_name = CustomerInfo.query.filter(
        CustomerInfo.job_id == job_id).first()
    reckon_access_token = SageReckonTokens.query.filter(
        SageReckonTokens.job_id == job_id).first()

    url = "https://api.reckon.com/r1//cashbooks"

    payload = {}
    headers = {
    'Authorization': f'Bearer {reckon_access_token.reckon_access_token}',
    'Ocp-Apim-Subscription-Key': 'bdddd3c7a4034e538e2fea7f61e92aa5'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        json_response = response.json()
        
        for entry in json_response:            
            if reckon_company_name.Company.lower() == entry["BookName"].lower():
                reckontoken_data = SageReckonTokens.query.filter(
                SageReckonTokens.job_id == job_id).first()
                reckontoken_data.reckon_company_id = entry["BookId"]
                db.session.commit()
                return True
        return False
    else:
        return False


@blueprint.route("/selfcallback",methods=["GET", "POST"])
def selfcallback():
    auth_code1 = request.args.get("code")
    job_state = request.args.get("state")
    
    client_id = '3d95f9e7-38dc-469c-a197-209cf6e4d5d6'
    client_secret = 'f9e34f69-a6aa-4f68-8637-d87e59cfa961'
    redirect_url =RECKON_REDIRECT_URI

    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    url = 'https://identity.reckon.com/connect/token'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encoded_credentials}'
    }

    body = {
        'grant_type': 'authorization_code',
        'code': f"{auth_code1}",
        'redirect_uri': f"{redirect_url}"
    }

    response = requests.post(url, headers=headers, data=body)

    json_response = response.json()
   
    reckontoken_data = SageReckonTokens.query.filter(
        SageReckonTokens.job_id == job_state).first()
    reckontoken_data.reckon_access_token = response.json().get("access_token")
    reckontoken_data.reckon_refresh_token = response.json().get("refresh_token")
    db.session.add(reckontoken_data)
    db.session.commit()

    File_data=get_reckoncompany_data11(job_state)

    if File_data == True:
        print("file is present in same organization")

        return redirect(
            
            url_for(
                ".start_conversion",job_id=job_state
            )
        )
    else:


        flash("Please select Valid file or valid user credentials")

        return redirect(
            
            url_for(
                ".connect_output_tool",job_id=job_state
            )
        )


@blueprint.route("/connect_output_tool/<int:job_id>")
def connect_output_tool(job_id):

    return render_template(
        "home/connect_output_tool.html",job_id=job_id
    )

@blueprint.route("/start_conversion/<int:job_id>")
def connect_reckon_tool(job_id):

    return render_template(
        "home/start_conversion.html",job_id=job_id
    )


@blueprint.route("/conversion_underway")
def conversion_underway():
    job_id = redis.get('my_key')
    return render_template(
        "home/conversion_underway.html",
        job_id=job_id

    )


def create_logfile(job_id):
    try:


        file_name = f"SageOne_To_ReckonOne_{job_id}.log"
        logfile_path = os.path.join('apps', 'static', 'logfile', file_name)
        print(logfile_path)


        with open(logfile_path, 'w') as file:
            pass

        print(f"Log file {logfile_path} created successfully.")

        return True
       
    except Exception as e:
        print(f"Error execution time: {e}")


@blueprint.route("/User_info", methods=["GET", "POST"])
@login_required
def User_info():

    if request.method == "GET":
        # all_customer_info = CustomerInfo.query.order_by(
        #     desc(CustomerInfo.id)).all()
        
        all_customer_basicinfo = CustomerInfo.query.filter_by(cust_status='basic_data').order_by(desc(CustomerInfo.id)).all()

        all_customer_authinfo = CustomerInfo.query.filter_by(cust_status='cust_authdata').order_by(desc(CustomerInfo.id)).all()


        return render_template(
            "home/end_user_info.html",
            all_customer_basicinfo=all_customer_basicinfo,
            all_customer_authinfo=all_customer_authinfo
        )
    
@blueprint.route("/reckon_filestatus", methods=["GET", "POST"])
def reckon_filestatus(status,job_id):
    
    api_key = 'mPU6UKeWcisk8sEaSyUh6Zlg3WGy7iT4v4FaxJe3'

    reckontoken_data = SageReckonTokens.query.filter(
        SageReckonTokens.job_id == job_id).first()
    
    book_id = reckontoken_data.reckon_company_id

    url = f'https://portal-backend.reckonapi.com/integrations/{book_id}/mmcconversion'

    headers = {
        'x-api-key': api_key
    }

    body = {
        'ConversionStatus': f'{status}'
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        return True
    else:
        return False


@blueprint.route("/reckon_connect1/<int:id>", methods=["GET", "POST"])
def reckon_connect1(id):
    # key_to_clear = 'reckon_key'
    # redis.delete(key_to_clear)
    # redis.set(f'reckon_key', id)
    # id=redis.get('reckon_key')

    print(id,"print reckon id data")

    # client_id = "53f51b0c-6f42-4b04-bde7-9a74340a801e"
    # redirect_uri = "https://mmc.vishleshak.io/reckon_callback"
    
    client_id = '3d95f9e7-38dc-469c-a197-209cf6e4d5d6'
    client_secret = 'f9e34f69-a6aa-4f68-8637-d87e59cfa961'
    redirect_uri =RECKON_REDIRECT_URI

    # client_id = '40864ca7-c3da-42f7-bb71-cecf72ad7fbe'
    # client_secret = '0d112ab1-e5d1-4f30-a30d-f2345605c94f'
    # redirect_uri ="http://127.0.0.1:5000/login"

    scope = "openid+read+write+offline_access"
    CLIENT_ID = f"{client_id}"

    auth_url = ('''https://identity.reckon.com/connect/authorize?''' +
                '''response_type=code''' +
                '''&client_id=''' + client_id +
                '''&redirect_uri=''' + redirect_uri +
                '''&scope=''' + scope +
                f'''&state={id}'''
                '''&nonce=random_nonce''')

    return redirect(auth_url)


@blueprint.route("/callback",methods=["GET", "POST"])
def callback():

    create_setting_form = CreateSettingForm(request.form)
    if request.method == "GET":
        id=request.args.get("state")
        print(id,"print reckon token id ======")
        tool = Tool.query.filter(Tool.id == id).first()
        tool_xero_type = Tool.query.filter(Tool.account_type == "Reckon").first()
        tool_settings = ToolSettings.query.filter(
            ToolSettings.tool_id == id).all()
        key_list = tool.keys.split(",")
        auth_code1 = request.args.get("code")
        # auth_code1 = "e0786b68d7dabd7ba99f771dc743e5bc"
        job_state = request.args.get("state")
        # client_id = '53f51b0c-6f42-4b04-bde7-9a74340a801e'
        # client_secret = '98ccec11-044d-4a4a-b358-c9bb00eaac69'
        # redirect_url ="https://mmc.vishleshak.io/reckon_callback"

        client_id = '3d95f9e7-38dc-469c-a197-209cf6e4d5d6'
        client_secret = 'f9e34f69-a6aa-4f68-8637-d87e59cfa961'
        redirect_url =RECKON_REDIRECT_URI


        # client_id = '40864ca7-c3da-42f7-bb71-cecf72ad7fbe'
        # client_secret = '0d112ab1-e5d1-4f30-a30d-f2345605c94f'
        # redirect_url ="http://127.0.0.1:5000/login"

        clientIdSecret = client_id + ':' + client_secret
        encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
        auth_code = "%s" % encoded_u

        id_secret_encoded= f'{auth_code}'
        Subscription_Key="bdddd3c7a4034e538e2fea7f61e92aa5"
        Reckon_URL="https://api.reckon.com/r1/"

        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        url = 'https://identity.reckon.com/connect/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {encoded_credentials}'
        }
        body = {
            'grant_type': 'authorization_code',
            'code': f"{auth_code1}",
            'redirect_uri': f"{redirect_url}"
        }        
        response = requests.post(url, headers=headers, data=body)
        json_response = response.json()
        print(json_response,"json response data ======")
        access_token=json_response["access_token"]
        refersh_token=json_response["refresh_token"]    
        reckon_dict={"client_id":client_id,"client_secret":client_secret,"id_secret_encoded": id_secret_encoded,"redirect_url":redirect_url,"Ocp-Apim-Subscription-Key":Subscription_Key,"token":access_token,"refresh_token":refersh_token,"url":Reckon_URL,"book":""}
        reckon_file_data=get_reckoncompany_data(access_token)
        user_account_data = UserAccount.query.filter().all()
        print(user_account_data,"user_account_data=========")

        return render_template(
                "home/create_tool_settings.html",
                zip=zip,
                len=len,
                segment="settings",
                tool=tool,
                data=key_list,
                tool_xero_type=tool_xero_type,
                form=create_setting_form,
                reckon_dict=reckon_dict,
                reckon_file_data=reckon_file_data,
                user_account_data=user_account_data,
                enable_search=True 


            )

    if request.method == "POST":

        id=request.args.get("state")
        print(id,"print reckon token state ======")

        response = make_response(
            redirect(url_for(".tool", msg="Tool setting created successfully!!!", success=True)))
        tool = Tool.query.filter(Tool.id == id).first()

        key_list = tool.keys.split(",")
        for i in range(0, len(key_list)):
            tool_settings = ToolSettings.query.filter(
                ToolSettings.tool_id == id, ToolSettings.keys == key_list[i].strip(
                )
            ).first()


            if tool_settings is not None:
                tool_settings.keys = key_list[i].strip()
                tool_settings.values = request.form[key_list[i]].strip()

                if tool_settings.keys == "token":

                    response.set_cookie('token', tool_settings.values, max_age=10800)

                if tool_settings.keys == "refresh_token":
                    response.set_cookie('refresh_token', tool_settings.values, max_age=10800)
               
                if tool_settings.keys == "book":
                    response.set_cookie('book', tool_settings.values, max_age=10800)
               

                db.session.commit()   
            else:


                setting = ToolSettings()
                setting.tool_id = id
                setting.keys = key_list[i].strip()
                setting.values = request.form[key_list[i]].strip()
                
                if setting.keys == "token":

                    response.set_cookie('token', setting.values, max_age=10800)

                if setting.keys == "refresh_token":
                    response.set_cookie('refresh_token', setting.values, max_age=10800)
               
                if setting.keys == "book":
                    response.set_cookie('book', setting.values, max_age=10800)
               


                # if setting.keys == "user_account":
                #     results = db.session.query(ToolSettings).filter(ToolSettings.keys == 'user_account',
                #                                                    ToolSettings.values == setting.values).all()
                #     token_data=[]
                #     for result in results:
                #         reckon_result = db.session.query(ToolSettings).filter(ToolSettings.tool_id ==result.tool_id,ToolSettings.keys.in_(['token', 'refresh_token'])).all()
                #         token_data.append(reckon_result)

                # if setting.keys == "token":
                #     token_data
                #     for token1 in token_data:
                #         for t1 in token1:
                #             if t1.keys =="token":

                #                 db.session.query(ToolSettings).filter(ToolSettings.tool_id == t1.tool_id,ToolSettings.keys == "token").update(
                #                     {"values": setting.values})

                #                 db.session.commit()


                # if setting.keys == "refresh_token":
                #     token_data
                #     for token1 in token_data:
                #         for t1 in token1:
                #             if t1.keys =="refresh_token":

                #                 db.session.query(ToolSettings).filter(ToolSettings.tool_id == t1.tool_id,ToolSettings.keys == "refresh_token").update(
                #                     {"values": setting.values})

                #                 db.session.commit()


                db.session.add(setting)
                db.session.commit()


        return response
    


def get_reckoncompany_data(access_token):
    
    url = "https://api.reckon.com/r1/v2/books"

    payload = {}
    headers = {
    'Authorization': f'Bearer {access_token}',
    'Ocp-Apim-Subscription-Key': '690395d6e257490eb8382f13f331d0db'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        json_response = response.json()
        # Extract the list of books from the response
        books = json_response.get("list", [])
        
        # Extract the id and name for each book and return as a list of dictionaries
        reckon_file_data = [{"id": book["id"], "name": book["name"]} for book in books]

        print(reckon_file_data,"reckon_file_data----------")

        return reckon_file_data
    else:
        print(f"Error: {response.status_code}")
        return []
    


@blueprint.route("/SageOne_Login_page/<int:id>", methods=["GET", "POST"])

def SageOne_Login_page(id):
    # key_to_clear_sageone = 'sageone_key'
    # redis.delete(key_to_clear_sageone)
    # redis.set('sageone_key', id)
    # id=redis.get('sageone_key')
    print(id,"id data ----")
    create_sage_login_form = SageOneLoginForm(request.form)
    print("SageOne_Login_page")
    
    if request.method == "GET":
        print("get block ")
        return render_template("home/sageone_login.html",
                               form=create_sage_login_form                        
                               )
    if request.method == "POST":
        sage_info = SageUser()
        sage_info.job_id = id
        sage_info.email= request.form["sageusername"]
        sage_info.password = request.form["sagepassword"]

        print(sage_info,"sage_info")
        db.session.add(sage_info)
        db.session.commit()

        username=request.form["sageusername"]
        password= request.form["sagepassword"]

        status_code_data=get_company_info_sageone(username,password)

        print(status_code_data,"status_code_data")

        if status_code_data == 200:

            return redirect(
                        url_for(
                            ".sageone_callback",id=id
                        )
                    ) 
        else:
            flash("Please enter a valid company name ")

            return redirect(
                url_for(
                    ".SageOne_Login_page",job_id=id
                )
            )



@blueprint.route("/sageone_callback/<int:id>",methods=["GET", "POST"])
def sageone_callback(id):
    # id=redis.get('sageone_key')

    print(id,"print sageone token id ======")
    create_setting_form = CreateSettingForm(request.form)
    if request.method == "GET":

        tool = Tool.query.filter(Tool.id == id).first()
        tool_xero_type = Tool.query.filter(Tool.account_type == "Sageone").first()
        tool_settings = ToolSettings.query.filter(
            ToolSettings.tool_id == id).all()
        key_list = tool.keys.split(",")

        sageone_user_data = SageUser.query.filter(
                    SageUser.job_id == id).first()

        username= sageone_user_data.email
        password= sageone_user_data.password

        print(username,password,"=====username,password====")
        api_key_data="FA4FF7F8-216A-406A-A72C-D710DBE4F787"
        sageone_file_data=get_company_data_sageone(username,password)
        print(sageone_file_data,"print file data =============")
        sageone_dict={"api_key":api_key_data,"username":username,"password":password,"company_id":""}

        return render_template(
                "home/create_tool_settings.html",
                zip=zip,
                len=len,
                segment="settings",
                tool=tool,
                data=key_list,
                tool_xero_type=tool_xero_type,
                form=create_setting_form,
                sageone_file_data=sageone_file_data,
                sageone_dict=sageone_dict,
                enable_search=True
            )

    if request.method == "POST":

        
        tool = Tool.query.filter(Tool.id == id).first()
        
        key_list = tool.keys.split(",")

        
        for i in range(0, len(key_list)):
            tool_settings = ToolSettings.query.filter(
                ToolSettings.tool_id == id, ToolSettings.keys == key_list[i].strip(
                )
            ).first()
            if tool_settings is not None:
                tool_settings.keys = key_list[i].strip()
                tool_settings.values = request.form[key_list[i]].strip()

                db.session.commit()   
            else:
                setting = ToolSettings()
                setting.tool_id = id
                setting.keys = key_list[i].strip()

               
                print(setting.keys,"keys==========")
                setting.values = request.form[key_list[i]].strip()
                print(setting.values,"values======")
                db.session.add(setting)
                db.session.commit()
        return redirect(
            url_for(
                ".tool", msg="Tool setting created successfully!!!!.", success=True)
        )

@blueprint.route("/tool/delete/<int:id>", methods=["GET","DELETE"])
@login_required
def delete_tool(id):
    try:
        toolsettings = ToolSettings.query.filter(
                ToolSettings.tool_id == id).all()
        print(toolsettings,"toolsetting data=======")
        
        if toolsettings:
            for setting in toolsettings:
                db.session.delete(setting)
            db.session.commit()
            
           
        tool = Tool.query.filter(Tool.id == id).first()

        
        if tool:
            db.session.delete(tool)
            db.session.commit()

            get_flashed_messages()
            flash('Tool setting deleted successfully!!!!', 'success')
        

            return redirect(
            url_for(
                ".tool", msg="Tool setting deleted successfully!!!!.", success=True))

        else:
            get_flashed_messages()
            flash('Tool setting not found !!!!', 'error')
        
            return redirect(
            url_for(
                ".tool", msg="Tool setting deleted successfully!!!!.", success=True))



    except Exception as e:
        return jsonify({'error': str(e)}), 500


@blueprint.route("/tool_file", methods=["GET", "POST"])
def tool_file():
    create_tool_file_info_form = CreateToolFileInfoForm(request.form)

    if request.method == "GET":
        output_settings = Tool.query.filter(Tool.tool_type == "Output")
       

        return render_template("home/create_tool_file.html",
                               output_settings=output_settings,
                               form=create_tool_file_info_form

                               )
    
    if request.method == "POST":
        tool_file = ToolFile()
        print(request.form["name"],"prount===",request.form["email"],"print==9595")
        tool_file.file_name = request.form["name"]
        tool_file.Email = request.form["email"]
        db.session.add(tool_file)
        db.session.commit()
        return redirect(
            url_for(
                ".connect_input_tool",
                
            )
        )


@blueprint.route("/connect_input_tool")
@login_required
def connect_input_tool():

    tool_files = ToolFile.query.filter(ToolFile.is_deleted != True).all()
    
    print(tool_files,"tool_files-======")
   
    return render_template("home/tool_files.html",tool_files=tool_files)

@blueprint.route("/filejobs/<int:id>")
@login_required
def filejobs(id):


    tool_file_name = ToolFile.query.filter(ToolFile.id == id).first()


    print(id,"filejobs id ==========")
    page = request.args.get('page', 1, type=int)
    tool1 = aliased(Tool)
    tool2 = aliased(Tool)
    jobs = (
        db.session.query(
            Jobs,
            tool1.tool_name.label("input_tool"),
            tool2.tool_name.label("output_tool"),
        )
        .join(tool1, Jobs.input_account_id == tool1.id)
        .join(tool2, Jobs.output_account_id == tool2.id)
        .filter(Jobs.file_id == id) 
    )

    jobs_data = jobs.paginate(page=page, per_page=100)
    # jobs_data.items.reverse()

    return render_template("home/jobs.html", segment="jobs", jobs=jobs_data,id=id,tool_file_name=tool_file_name)

@blueprint.route("/toolfile/delete/<int:id>", methods=["GET","DELETE"])
@login_required
def delete_toolfile(id):
    print("delete tool file ")
    try:
        
        jobs = Jobs.query.filter(Jobs.file_id == id).all()
        for job in jobs:
            job.is_deleted = True
        db.session.commit()
        file_data = ToolFile.query.filter(ToolFile.id == id).first()
        if file_data:
            file_data.is_deleted = True
            db.session.commit()
            get_flashed_messages()
            flash('Tool file deleted successfully!!!!', 'success')
    
            return redirect(
            url_for(
                ".connect_input_tool"))

        else:
            get_flashed_messages()
            flash('Tool file not found !!!!', 'error')
        
            return redirect(
            url_for(
                ".connect_input_tool"))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@blueprint.route("filejobs/tasks/<int:job_id>")
@login_required
def tasks_by_job(job_id):
    tasks = Task.query.filter(
        Task.job_id == job_id
    ).all()

    job_and_task = db.session.query(Jobs, Task)\
        .join(Task, Jobs.id == Task.job_id)\
        .filter(Jobs.id == job_id)\
        .all()
    
    return render_template("home/tasks.html", segment="tasks", data=job_and_task, job_id=job_id)


@blueprint.route("/allocation_progress/<int:job_id>")
@login_required
def allocation_progress_by_job(job_id):
    from apps.sage_one.sageone_reader.allocation_fetcher import allocation_progress
    job = Jobs.query.get(job_id)
    functions = (job.functions or "").split(",") if job else []
    return jsonify(allocation_progress(str(job_id), functions))

# @blueprint.route("filejobs/jobs/create/<int:id>", methods=["GET", "POST"])
# @login_required
# def create_job(id):
#     logging=log_config_job_creation(id)

#     create_job_form = CreateJobForm(request.form)
#     if request.method == "GET":
#         input_settings = Tool.query.filter(
#             Tool.tool_type == "Input", Tool.account_type != "Delete")
#         print(input_settings, "print input setting data")
#         output_settings = Tool.query.filter(Tool.tool_type == "Output")
#         print(output_settings)

#         return render_template(
#             "home/create_job.html",
#             segment="jobs",
#             input_settings=input_settings,
#             output_settings=output_settings,
#             form=create_job_form,
#         )

#     if request.method == "POST":
#         input_type = Tool.query.filter(
#             Tool.id == request.form["input_account_id"]
#         ).first()
#         account_type = input_type.account_type

#         if account_type != EXCEL:
#             if (request.form["input_account_id"] == "None") and (
#                     request.form["output_account_id"] == "None"
#             ):
#                 return redirect(
#                     url_for(
#                         ".create_job",
#                         msg="Input account and output account are the mandatory fields!!!!.",
#                         success=True,
#                     )
#                 )

#             if len(request.form.getlist("mycheckbox")) == 0:
#                 return redirect(
#                     url_for(
#                         ".create_job",
#                         msg="Please select atleast one function!!!!.",
#                         success=True,
#                     )
#                 )

#             job = Jobs()
#             fn = request.form.getlist('mycheckbox')
#             response=request.url
#             split_url = response.split('/')
#             last_number = split_url[-1]
#             print(last_number)
#             job.file_id = last_number
#             job.functions = ",".join(fn)
#             job.name = request.form["name"]
#             job.description = request.form["description"]
#             job.input_account_id = request.form["input_account_id"]
#             job.output_account_id = request.form["output_account_id"]
#             job.start_date = request.form["start_date"]
#             job.end_date = request.form["end_date"]

#             job_name = Jobs.query.filter(Jobs.name == job.name).first()
#             if job_name is None:
#                 db.session.add(job)
#                 db.session.commit()
#             else:
#                 flash("This job name is already exist,please create new one!")

#                 return redirect(
#                     url_for(
#                         ".create_job",id=last_number,

#                     )
#                 )
#             db.session.add(job)
#             db.session.commit()
#             for fun in range(0, len(fn)):
#                 task = Task()
#                 task_response=request.url
#                 split_url = task_response.split('/')
#                 last_number = split_url[-1]
#                 task.file_id = last_number
#                 task.function_name = fn[fun]
#                 task.job_id = job.id
#                 db.session.add(task)
#                 db.session.commit()
#             return redirect(
#                 url_for(
#                     ".tasks_by_job",
#                     job_id=job.id,
#                     msg="Job created successfully!!!!.",
#                     success=True,
#                 )
#             )
#         else:
#             job_id = upload_file(request)
#             return redirect(
#                 url_for(
#                     ".tasks_by_job",
#                     job_id=job_id,
#                     msg="Job created successfully!!!!.",
#                     success=True,
#                 )
#             )

@blueprint.route("filejobs/jobs/create/<int:id>", methods=["GET", "POST"])
@login_required
def create_job(id):
    logging = log_config_job_creation(id)

    create_job_form = CreateJobForm(request.form)
    try:
        if request.method == "GET":
            input_settings = Tool.query.filter(
                Tool.tool_type == "Input", Tool.account_type != "Delete"
            ).all()
            logging.debug(f"Input settings: {input_settings}")
            output_settings = Tool.query.filter(Tool.tool_type == "Output").all()
            logging.debug(f"Output settings: {output_settings}")

            return render_template(
                "home/create_job.html",
                segment="jobs",
                input_settings=input_settings,
                output_settings=output_settings,
                form=create_job_form,
            )

        if request.method == "POST":
            input_type = Tool.query.filter(Tool.id == request.form["input_account_id"]).first()
            if not input_type:
                logging.error("Input type not found.")
                return redirect(url_for(".create_job", id=id, msg="Invalid input account ID.", success=False))

            account_type = input_type.account_type

            if account_type != EXCEL:
                if (request.form["input_account_id"] == "None") or (request.form["output_account_id"] == "None"):
                    logging.warning("Input and output accounts are mandatory.")
                    return redirect(url_for(".create_job", id=id, msg="Input account and output account are the mandatory fields!!!!.", success=False))

                if len(request.form.getlist("mycheckbox")) == 0:
                    logging.warning("No functions selected.")
                    return redirect(url_for(".create_job", id=id, msg="Please select at least one function!!!!.", success=False))

                job = Jobs()
                fn = request.form.getlist('mycheckbox')
                job.file_id = id
                job.functions = ",".join(fn)
                job.name = request.form["name"]
                job.description = request.form["description"]
                job.input_account_id = request.form["input_account_id"]
                job.output_account_id = request.form["output_account_id"]
                job.start_date = request.form["start_date"]
                job.end_date = request.form["end_date"]

                job_name = Jobs.query.filter(Jobs.name == job.name).first()
                if job_name is None:
                    db.session.add(job)
                    db.session.commit()
                else:
                    flash("This job name already exists, please create a new one!")
                    logging.info("Job name already exists.")
                    return redirect(url_for(".create_job", id=id))

                for fun in fn:
                    task = Task()
                    task.file_id = id
                    task.function_name = fun
                    task.job_id = job.id
                    db.session.add(task)
                    db.session.commit()

                return redirect(url_for(".tasks_by_job", job_id=job.id, msg="Job created successfully!!!!.", success=True))

            else:
                job_id = upload_file(request)
                return redirect(url_for(".tasks_by_job", job_id=job_id, msg="Job created successfully!!!!.", success=True))
    except Exception as e:
        logging.exception("An error occurred while creating the job.")
        return redirect(url_for(".create_job", id=id, msg="An error occurred. Please try again.", success=False))


@blueprint.route("filejobs/sagejobs/create/<int:id>", methods=["GET", "POST"])
@login_required
def create_sagejob(id):
    logging = log_config_job_creation(id)

    create_job_form = CreateJobForm(request.form)
    try:
        if request.method == "GET":
            input_settings = Tool.query.filter(
                Tool.tool_type == "Input", Tool.account_type != "Delete"
            ).all()
            logging.debug(f"Input settings: {input_settings}")
            output_settings = Tool.query.filter(Tool.tool_type == "Output").all()
            logging.debug(f"Output settings: {output_settings}")

            return render_template(
                "home/create_sage_excel_job.html",
                segment="jobs",
                input_settings=input_settings,
                output_settings=output_settings,
                form=create_job_form,
            )

        if request.method == "POST":
            input_type = Tool.query.filter(Tool.id == request.form["input_account_id"]).first()
            if not input_type:
                logging.error("Input type not found.")
                return redirect(url_for(".create_job", id=id, msg="Invalid input account ID.", success=False))

            account_type = input_type.account_type

            if account_type != EXCEL:
                if (request.form["input_account_id"] == "None") or (request.form["output_account_id"] == "None"):
                    logging.warning("Input and output accounts are mandatory.")
                    return redirect(url_for(".create_job", id=id, msg="Input account and output account are the mandatory fields!!!!.", success=False))

                if len(request.form.getlist("mycheckbox")) == 0:
                    logging.warning("No functions selected.")
                    return redirect(url_for(".create_job", id=id, msg="Please select at least one function!!!!.", success=False))

                job = Jobs()
                fn = request.form.getlist('mycheckbox')
                job.file_id = id
                job.functions = ",".join(fn)
                job.name = request.form["name"]
                job.description = request.form["description"]
                job.input_account_id = request.form["input_account_id"]
                job.output_account_id = request.form["output_account_id"]
                job.start_date = request.form["start_date"]
                job.end_date = request.form["end_date"]

                job_name = Jobs.query.filter(Jobs.name == job.name).first()
                if job_name is None:
                    db.session.add(job)
                    db.session.commit()
                else:
                    flash("This job name already exists, please create a new one!")
                    logging.info("Job name already exists.")
                    return redirect(url_for(".create_job", id=id))

                for fun in fn:
                    task = Task()
                    task.file_id = id
                    task.function_name = fun
                    task.job_id = job.id
                    db.session.add(task)
                    db.session.commit()

                return redirect(url_for(".tasks_by_job", job_id=job.id, msg="Job created successfully!!!!.", success=True))

            else:
                job_id = upload_file(request)
                return redirect(url_for(".tasks_by_job", job_id=job_id, msg="Job created successfully!!!!.", success=True))
    except Exception as e:
        logging.exception("An error occurred while creating the job.")
        return redirect(url_for(".create_job", id=id, msg="An error occurred. Please try again.", success=False))




@blueprint.route("filejobs/reckonjobs/create/<int:id>", methods=["GET", "POST"])
@login_required
def create_reckonjobs(id):
    logging = log_config_job_creation(id)

    create_job_form = CreateJobForm(request.form)
    try:
        if request.method == "GET":
            input_settings = Tool.query.filter(
                Tool.tool_type == "Input", Tool.account_type != "Delete"
            ).all()
            logging.debug(f"Input settings: {input_settings}")
            output_settings = Tool.query.filter(Tool.tool_type == "Output").all()
            logging.debug(f"Output settings: {output_settings}")

            return render_template(
                "home/create_reckon_excel_job.html",
                segment="jobs",
                input_settings=input_settings,
                output_settings=output_settings,
                form=create_job_form,
            )

        if request.method == "POST":
            input_type = Tool.query.filter(Tool.id == request.form["input_account_id"]).first()
            if not input_type:
                logging.error("Input type not found.")
                return redirect(url_for(".create_job", id=id, msg="Invalid input account ID.", success=False))

            account_type = input_type.account_type

            if account_type != EXCEL:
                if (request.form["input_account_id"] == "None") or (request.form["output_account_id"] == "None"):
                    logging.warning("Input and output accounts are mandatory.")
                    return redirect(url_for(".create_job", id=id, msg="Input account and output account are the mandatory fields!!!!.", success=False))

                if len(request.form.getlist("mycheckbox")) == 0:
                    logging.warning("No functions selected.")
                    return redirect(url_for(".create_job", id=id, msg="Please select at least one function!!!!.", success=False))

                job = Jobs()
                fn = request.form.getlist('mycheckbox')
                job.file_id = id
                job.functions = ",".join(fn)
                job.name = request.form["name"]
                job.description = request.form["description"]
                job.input_account_id = request.form["input_account_id"]
                job.output_account_id = request.form["output_account_id"]
                job.start_date = request.form["start_date"]
                job.end_date = request.form["end_date"]

                job_name = Jobs.query.filter(Jobs.name == job.name).first()
                if job_name is None:
                    db.session.add(job)
                    db.session.commit()
                else:
                    flash("This job name already exists, please create a new one!")
                    logging.info("Job name already exists.")
                    return redirect(url_for(".create_job", id=id))

                for fun in fn:
                    task = Task()
                    task.file_id = id
                    task.function_name = fun
                    task.job_id = job.id
                    db.session.add(task)
                    db.session.commit()

                return redirect(url_for(".tasks_by_job", job_id=job.id, msg="Job created successfully!!!!.", success=True))

            else:
                job_id = upload_file(request)
                return redirect(url_for(".tasks_by_job", job_id=job_id, msg="Job created successfully!!!!.", success=True))
    except Exception as e:
        logging.exception("An error occurred while creating the job.")
        return redirect(url_for(".create_job", id=id, msg="An error occurred. Please try again.", success=False))


@blueprint.route("/reporttasks/<int:job_id>")
@login_required
def tasks_by_job_report(job_id):
    tasks = Task.query.filter(
        Task.job_id == job_id
    ).all()

    job_and_task = db.session.query(Jobs, Task)\
        .join(Task, Jobs.id == Task.job_id)\
        .filter(Jobs.id == job_id)\
        .all()
    
    return render_template("home/report_tasks.html", segment="tasks", data=job_and_task, job_id=job_id)


@blueprint.route("filejobs/report/create/<int:id>", methods=["GET", "POST"])
@login_required
def create_report(id):
    create_job_form = CreateJobForm(request.form)
    if request.method == "GET":
        input_settings = Tool.query.filter(
            Tool.tool_type == "Input", Tool.account_type != "Delete")
        output_settings = Tool.query.filter(Tool.tool_type == "Output")
        return render_template(
            "home/Report.html",
            segment="jobs",
            input_settings=input_settings,
            output_settings=output_settings,
            form=create_job_form,
        )

    if request.method == "POST":
        input_type = Tool.query.filter(
            Tool.id == request.form["input_account_id"]
        ).first()
        account_type = input_type.account_type

        job = Jobs()
        fn = ["Report"]
        response=request.url
        split_url = response.split('/')
        last_number = split_url[-1]
        print(last_number)
        job.file_id = last_number
        job.functions = ",".join(fn)
        job.name = request.form["name"]
        job.description = request.form["description"]
        job.input_account_id = request.form["input_account_id"]
        job.output_account_id = request.form["output_account_id"]
        job.start_date = request.form["start_date"]
        job.end_date = request.form["end_date"]

        job_name = Jobs.query.filter(Jobs.name == job.name).first()
        if job_name is None:
            db.session.add(job)
            db.session.commit()
        else:
            flash("This job name is already exist,please create new one!")

            return redirect(
                url_for(
                    ".create_report",id=last_number,

                )
            )
        db.session.add(job)
        db.session.commit()
        for fun in range(0, len(fn)):
            task = Task()
            task_response=request.url
            split_url = task_response.split('/')
            last_number = split_url[-1]
            task.file_id = last_number
            task.function_name = fn[fun]
            task.job_id = job.id
            db.session.add(task)
            db.session.commit()

        return redirect(
                url_for(
                    ".tasks_by_job_report",
                    job_id=job.id,
                    msg="Job created successfully!!!!.",
                    success=True,
                )
            )


@blueprint.route("/report_generation/<int:job_id>", methods=["GET", "POST"])
def report_generation(job_id):
    report_generation_previous_year(job_id)
    report_generation_current_year(job_id)

    return redirect(
        url_for(
            ".report_by_job",
            job_id=job_id
        )
    )

    
@blueprint.route("filejobs/report/<int:job_id>")
@login_required
def report_by_job(job_id):

    return render_template("home/report_preview.html", job_id=job_id)


@blueprint.route("/Create_final_previous_year_report", methods=["GET", "POST"])
def Create_final_previous_year_report(job_id):
    print(job_id,"job_id data ===== 1st years ")
    dbname = get_mongodb_database()

    job_data = Jobs.query.filter(
        Jobs.id == job_id
    ).first()

    job_file_data=job_data.output_account_id

    tool_data = Tool.query.filter(
        Tool.id == job_file_data
    ).first()

    print(tool_data.tool_name,"tool_data=====")

    file_name=tool_data.tool_name

    start_date,end_date=get_job_details(job_id)
        

    date_now = datetime.strptime(start_date, '%Y-%m-%d')
    start_date1 = date_now.date()
    start_date2 = start_date1.strftime('%d-%m-%Y')
   
    date_2 = date_now.replace(year=date_now.year + 1)
    new_start_date_only = date_2 - timedelta(days=1)
    new_start_date_only1 = new_start_date_only.date()
    new_start_date = new_start_date_only1.strftime('%d-%m-%Y')
    
    cust_job=f"{job_id}"
    cust_data = list(dbname["matched_customer_previous_year_balance"].find({"job_id": cust_job}))
    
    supp_job=f"{job_id}"
    supp_data = list(dbname["matched_supplier_previous_year_balance"].find({"job_id": supp_job}))

    coa_job=f"{job_id}"
    print(coa_job,"coa_job=============")
    coa_data = list(dbname["matched_trial_previous_year_balance"].find({"job_id": coa_job}))

    img_name = "Quickbooks-Emblem.png"
    qbo_img = os.path.join('apps', 'static', 'assets', 'img', img_name)

    print(len(cust_data), "print len of cust_data")
    print(len(supp_data), "print len of supp_data")
    print(len(coa_data), "print len of coa_data")

    return render_template("home/final_previous_years_report.html", cust_data=cust_data, supp_data=supp_data, coa_data=coa_data, qbo_img=qbo_img,start_date=start_date2,new_start_date=new_start_date,file_name=file_name)

@blueprint.route("/Create_final_current_year_report", methods=["GET", "POST"])
def Create_final_current_year_report(job_id):
    print(job_id,"job_id data =====")
    dbname = get_mongodb_database()

    job_data = Jobs.query.filter(
        Jobs.id == job_id
    ).first()

    job_file_data=job_data.output_account_id

    tool_data = Tool.query.filter(
        Tool.id == job_file_data
    ).first()

    print(tool_data.tool_name,"tool_data=====")

    file_name=tool_data.tool_name

    start_date,end_date=get_job_details(job_id)
    end_date_now11 = datetime.strptime(end_date, '%Y-%m-%d')

    formatted_date11= end_date_now11.date()
    end_date22= formatted_date11.strftime('%d-%m-%Y')

    

    date_now = datetime.strptime(start_date, '%Y-%m-%d')
    date_3 = date_now.replace(year=date_now.year + 1)
    formatted_date= date_3.date()
    date_2 = formatted_date.strftime('%d-%m-%Y')
    
    
    cust_job=f"{job_id}"
    cust_data = list(dbname["matched_customer_current_year_balance"].find({"job_id": cust_job}))
    supp_job=f"{job_id}"
    supp_data = list(dbname["matched_supplier_current_year_balance"].find({"job_id": supp_job}))

    coa_job=f"{job_id}"
    coa_data = list(dbname["matched_trial_current_year_balance"].find({"job_id": coa_job}))

    img_name = "Quickbooks-Emblem.png"
    qbo_img = os.path.join('apps', 'static', 'assets', 'img', img_name)

    print(len(cust_data), "print len of cust_data")
    print(len(supp_data), "print len of supp_data")
    print(len(coa_data), "print len of coa_data")

    
    return render_template("home/final_current_years_report.html", cust_data=cust_data, supp_data=supp_data, coa_data=coa_data, qbo_img=qbo_img,start_date=date_2,end_date=end_date22,file_name=file_name)

@blueprint.route("/report_previous_year_generation/<int:job_id>", methods=["GET", "POST"])
def report_generation_previous_year(job_id):
    print("inside report generation previous years data")

    create_final_report_response = Create_final_previous_year_report(job_id)
    job_id = job_id
    print(job_id,"print job id ======")
    if isinstance(create_final_report_response, Response):

        create_final_report_content = create_final_report_response.data.decode(
            'utf-8')
    else:
        create_final_report_content = str(create_final_report_response)

    options = {
        'page-size': 'A4',
        'margin-top': '10mm',
        'margin-right': '10mm',
        'margin-bottom': '10mm',
        'margin-left': '10mm',
        "enable-local-file-access": ""
    }
    try:
        file_name = f"Report_previous_year_{job_id}.pdf"
        pdf_path = os.path.join('apps', 'static', 'reports', file_name)
        print(pdf_path)
        pdfkit.from_string(create_final_report_content,
                           pdf_path, options=options,)
    except Exception as e:
        print(f"Error generating PDF: {e}")

    return redirect(
        url_for(
            ".report_by_job",
            job_id=job_id
        )
    )

    
@blueprint.route("/report_current_year_generation/<int:job_id>", methods=["GET", "POST"])
def report_generation_current_year(job_id):

    create_final_report_response = Create_final_current_year_report(job_id)
    job_id = job_id
    
    print(job_id)
    if isinstance(create_final_report_response, Response):

        create_final_report_content = create_final_report_response.data.decode(
            'utf-8')
    else:
        create_final_report_content = str(create_final_report_response)

    options = {
        'page-size': 'A4',
        'margin-top': '10mm',
        'margin-right': '10mm',
        'margin-bottom': '10mm',
        'margin-left': '10mm',
        "enable-local-file-access": ""
    }
    try:
        file_name = f"Report_current_year_{job_id}.pdf"
        pdf_path = os.path.join('apps', 'static', 'reports', file_name)
        print(pdf_path)
        pdfkit.from_string(create_final_report_content,
                           pdf_path, options=options,)
    except Exception as e:
        print(f"Error generating PDF: {e}")

    return redirect(
        url_for(
            ".report_by_job",
            job_id=job_id
        )
    )


@blueprint.route("/retrystartJobByID", methods=["POST"])
@login_required
def retrystartJobByID():
    job_id = request.form['job_id']
    print(job_id,"job_id data =========")
    asyncio.run(retry_reckon_write_task(job_id))
    return json.dumps({'status': 'success'})


@blueprint.route("/payment_data_report", methods=["GET", "POST"])
def payment_data_report():
       
    return render_template("home/get_payment_data.html")


def clean_payment_data(payment_data):
    fields_to_remove = ['job_id', 'task_id','_id']
    for record in payment_data:
        for field in fields_to_remove:
            if field in record:
                del record[field]
    return payment_data

def fetch_payment_data(collection_name, job_id):
    """Fetch payment data from the specified collection based on job_id."""
    dbname = get_mongodb_database()
    payment_collection = dbname[collection_name]
    return list(payment_collection.find({'job_id': f"{job_id}"}))

def generate_excel_file(payment_data, sheet_name):
    """Generate an Excel file from payment data."""
    df = pd.DataFrame(payment_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output


@blueprint.route("/payment_data", methods=["GET", "POST"])
def payment_data():
    create_get_info_form = CreateGetdataForm(request.form)

    dbname = get_mongodb_database()

    payment_data_types = [
        "invoice_payment", "bill_payment", "invoice","receive money","spend money","bill","coa", "customer", "supplier", "journal", "item", 
        "bank", "invoice creditnote", "bill vendorcredit", "open ar", "open ap", 
        "open trial balance","close trial balance", "bank transfer", "customer adjustment", 
        "supplier adjustment", "customer write off","tax",
        "invoice allocation", "bill allocation",
        "qbo invoice allocation", "qbo bill allocation"
    ]

    payment_data_mapping = {
        "invoice_payment": "sage_all_invoice_payment_data",
        "bill_payment": "sage_all_bill_payment_data",
        "invoice": "sage_all_invoice_data",
        "coa": "sage_all_coa_data",
        "bill": "sage_all_bill_data",
        "spend money": "sage_all_spend_money_data",
        "receive money": "sage_all_received_money_data",
        "customer": "sage_all_customer_data",
        "supplier": "sage_all_supplier_data",
        "journal": "sage_all_journal_data",
        "item": "sage_all_item_data",
        "bank": "sage_all_bank_data",
        "invoice creditnote": "sage_all_invoice_creditnote_data",
        "bill vendorcredit": "sage_all_bill_vendorcredit_data",
        "open ar": "sage_all_open_ar_data",
        "open ap": "sage_all_open_ap_data",
        "open trial balance": "sage_all_open_trial_balance_data",
        "bank transfer": "sage_all_bank_transfer_data",
        "customer adjustment": "sage_all_customer_adjustment_data",
        "supplier adjustment": "sage_all_supplier_adjustment_data",
        "customer write off": "sage_all_customer_write_off_data",
        "close trial balance":"sage_all_close_trial_balance_data",
        "tax":"sage_all_tax_data",
        "invoice allocation": "sage_all_invoice_allocation_data",
        "bill allocation": "sage_all_bill_allocation_data",
        "qbo invoice allocation": "sage_all_qbo_invoice_allocation_data",
        "qbo bill allocation": "sage_all_qbo_bill_allocation_data"
    }
    if request.method == "GET":

        return render_template("home/get_payment_data.html",
                                form=create_get_info_form
                            )

    if request.method == "POST":
        job_id = request.form.get('job_id')
        files = []


        job_name = Jobs.query.filter(Jobs.id == job_id).first()
        print(job_name.name,"job_name")
        job_name_data=job_name.name

        for data_type in payment_data_types:
            collection_name = payment_data_mapping.get(data_type)
            if not collection_name:
                continue

            payment_data = fetch_payment_data(collection_name, job_id)
            payment_data = clean_payment_data(payment_data)

            if not payment_data:
                flash(f"No data found for the given job ID for {data_type}.")
                continue

            output = generate_excel_file(payment_data, sheet_name=data_type.capitalize())
            output.seek(0)
            files.append((output, f'{data_type}_{job_id}.xlsx'))

        if not files:
            flash("No data found for the given job ID.")
            return render_template("home/get_payment_data.html", payment_data=None)

        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for file, filename in files:
                zip_file.writestr(filename, file.read())

        zip_buffer.seek(0)
        return send_file(zip_buffer, attachment_filename=f'{job_name_data}_{job_id}.zip', as_attachment=True)

     


# @blueprint.route("/Reckon_payment_data", methods=["GET", "POST"])
# def Reckon_payment_data():
#     create_get_info_form = CreateGetdataForm(request.form)

#     dbname = get_mongodb_database()
#     payment_data_types = [
#         "invoice_payment", "bill_payment", "invoice","receive money","spend money","bill","coa", "customer", "supplier", "journal", "item", 
#         "bank", "invoice creditnote", "bill vendorcredit", "open ar", "open ap", 
#         "open trial balance","close trial balance", "bank transfer", "customer adjustment", 
#         "supplier adjustment", "customer write off","tax_group"
#     ]

#     payment_data_mapping = {

#         "coa": "reckon_coa",
#         "invoice": "reckon_invoice_excel",
#         "bill": "reckon_bill_excel",
#         "item": "reckon_item",
#         "invoice creditnote": "reckon_invoice_creditnote_excel",
#         "bill vendorcredit": "reckon_bill_vendorcredit_excel",
#         "tax_group":"taxcode_reckon_excel",
#         "invoice_payment": "reckon_invoice_payment_excel",
#         "bill_payment": "reckon_bill_payment_excel",
        
#     }


   
#     if request.method == "GET":
    

#         return render_template("home/get_payment_data.html",
#                                 form=create_get_info_form
#                             )

#     if request.method == "POST":
#         job_id = request.form.get('job_id')
#         files = []


#         job_name = Jobs.query.filter(Jobs.id == job_id).first()
#         print(job_name.name,"job_name")
#         job_name_data=job_name.name

#         for data_type in payment_data_types:
#             collection_name = payment_data_mapping.get(data_type)
#             if not collection_name:
#                 continue

#             payment_data = fetch_payment_data(collection_name, job_id)
#             payment_data = clean_payment_data(payment_data)

#             if not payment_data:
#                 flash(f"No data found for the given job ID for {data_type}.")
#                 continue

#             output = generate_excel_file(payment_data, sheet_name=data_type.capitalize())
#             output.seek(0)
#             files.append((output, f'{data_type}_{job_id}.xlsx'))

#         if not files:
#             flash("No data found for the given job ID.")
#             return render_template("home/get_payment_data.html", payment_data=None)

#         # Create a zip file in memory
#         zip_buffer = io.BytesIO()
#         with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
#             for file, filename in files:
#                 zip_file.writestr(filename, file.read())

#         zip_buffer.seek(0)
#         return send_file(zip_buffer, attachment_filename=f'{job_name_data}_{job_id}.zip', as_attachment=True)

import io
import re
import zipfile
import pandas as pd
from flask import render_template, request, flash, send_file
from apps.home import blueprint

from apps.home.models import Jobs


# Regex to remove illegal XML characters (Excel restriction)
ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')

def clean_excel_value(value):
    """Remove illegal Excel characters and normalize strings."""
    if isinstance(value, str):
        value = ILLEGAL_CHARACTERS_RE.sub("", value)   # remove control chars
        value = value.replace("\r", " ").replace("\n", " ")  # normalize newlines
    return value


def generate_excel_file(data, sheet_name="Sheet1"):
    """Generate an Excel file in memory from given data."""
    df = pd.DataFrame(data)

    # Clean every cell for Excel safety
    for col in df.columns:
        df[col] = df[col].map(clean_excel_value)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output


@blueprint.route("/Reckon_payment_data", methods=["GET", "POST"])
def Reckon_payment_data():
    create_get_info_form = CreateGetdataForm(request.form)
    dbname = get_mongodb_database()

    payment_data_types = [
        "invoice_payment", "bill_payment", "invoice", "receive money", "spend money",
        "bill", "coa", "customer", "supplier", "journal", "item", "bank",
        "invoice creditnote", "bill vendorcredit", "open ar", "open ap",
        "open trial balance", "close trial balance", "bank transfer",
        "project",
        "customer adjustment", "supplier adjustment", "customer write off", "tax_group","item_history"
    ]

    payment_data_mapping = {
        "coa": "reckon_coa",
        "customer": "reckon_customer_data",
        "supplier": "reckon_supplier",
        "invoice": "reckon_invoice_excel",
        "bill": "reckon_bill_excel",
        "item": "reckon_item",
        "project": "reckon_projects",
        "item_history":"reckon_item_history",
        "invoice creditnote": "reckon_invoice_creditnote_excel",
        "bill vendorcredit": "reckon_bill_vendorcredit_excel",
        "tax_group": "taxcode_reckon_excel",
        "invoice_payment": "reckon_invoice_payment_excel",
        "bill_payment": "reckon_bill_payment_excel",
    }

    if request.method == "GET":
        return render_template("home/get_payment_data.html", form=create_get_info_form)

    if request.method == "POST":
        job_id = request.form.get("job_id")
        files = []

        job_name = Jobs.query.filter(Jobs.id == job_id).first()
        if not job_name:
            flash("Invalid job ID.")
            return render_template("home/get_payment_data.html", form=create_get_info_form)

        job_name_data = job_name.name

        for data_type in payment_data_types:
            collection_name = payment_data_mapping.get(data_type)
            if not collection_name:
                continue

            payment_data = fetch_payment_data(collection_name, job_id)
            payment_data = clean_payment_data(payment_data)

            if not payment_data:
                flash(f"No data found for the given job ID for {data_type}.")
                continue

            try:
                output = generate_excel_file(payment_data, sheet_name=data_type.capitalize())
                output.seek(0)
                files.append((output, f"{data_type}_{job_id}.xlsx"))
            except Exception as e:
                flash(f"Error while processing {data_type}: {e}")
                continue

        if not files:
            flash("No data found for the given job ID.")
            return render_template("home/get_payment_data.html", payment_data=None)

        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for file, filename in files:
                zip_file.writestr(filename, file.read())

        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            download_name=f"{job_name_data}_{job_id}.zip",
            as_attachment=True
        )



@blueprint.route("filejobs/selfservicejob/create/<int:id>", methods=["GET", "POST"])
@login_required
def create_selfservice_job(id):
    create_job_form = CreateJobForm(request.form)
    if request.method == "GET":
        input_settings = Tool.query.filter(
            Tool.tool_type == "Input", Tool.account_type != "Delete")
        output_settings = Tool.query.filter(Tool.tool_type == "Output")
        return render_template(
            "home/selfjob.html",
            segment="jobs",
            input_settings=input_settings,
            output_settings=output_settings,
            form=create_job_form,
        )

    if request.method == "POST":
        input_type = Tool.query.filter(
            Tool.id == request.form["input_account_id"]
        ).first()
        account_type = input_type.account_type

        job = Jobs()
        fn = ["Chart of account","Spend Money"]
        response=request.url
        split_url = response.split('/')
        last_number = split_url[-1]
        print(last_number)
        job.file_id = last_number
        job.functions = ",".join(fn)
        job.name = request.form["name"]
        job.description = request.form["description"]
        job.input_account_id = request.form["input_account_id"]
        job.output_account_id = request.form["output_account_id"]
        job.start_date = request.form["start_date"]
        job.end_date = request.form["end_date"]

        job_name = Jobs.query.filter(Jobs.name == job.name).first()
        if job_name is None:
            db.session.add(job)
            db.session.commit()
        else:
            flash("This job name is already exist,please create new one!")

            return redirect(
                url_for(
                    ".create_selfservice_job",id=last_number,

                )
            )
        db.session.add(job)
        db.session.commit()
        for fun in range(0, len(fn)):
            task = Task()
            task_response=request.url
            split_url = task_response.split('/')
            last_number = split_url[-1]
            task.file_id = last_number
            task.function_name = fn[fun]
            task.job_id = job.id
            db.session.add(task)
            db.session.commit()

        return redirect(
                url_for(
                    ".start_job_by_id",
                    job_id=job.id,
                    msg="Job created successfully!!!!.",
                    success=True,
                )
            )


@blueprint.route("/startjobbyid/<int:job_id>")
@login_required
def start_job_by_id(job_id):
    
    return render_template("home/startjob.html", job_id=job_id)


@blueprint.route("/selfservicetasks/<int:job_id>")
@login_required
def tasks_by_job_selfservice(job_id):
    tasks = Task.query.filter(
        Task.job_id == job_id
    ).all()

    job_and_task = db.session.query(Jobs, Task)\
        .join(Task, Jobs.id == Task.job_id)\
        .filter(Jobs.id == job_id)\
        .all()
    
    return render_template("home/self_service_task.html", segment="tasks", data=job_and_task, job_id=job_id)

