# import traceback

# import requests

# from apps import db
# from apps.home.models import Jobs
# from apps.home.models import Tool, ToolSettings
# # from apps.util.qbo_util import add_job_status
# from datetime import datetime
# from apps.util.log_file import log_config

# def post_reckon_settings(job_id):
#     logging = log_config(job_id)
#     try:
#         logging.info(f"{job_id} inside post_reckon_settings")
#         main_url = "https://identity.reckon.com/connect/token"
#         keys = (
#             db.session.query(Jobs, ToolSettings.keys, ToolSettings.values, ToolSettings.id)
#             .join(Tool, Jobs.output_account_id == Tool.id)
#             .join(ToolSettings, ToolSettings.tool_id == Tool.id)
#             .filter(Jobs.id == job_id)
#             .all()
#         )

#         data1 = (
#             db.session.query(ToolSettings.id, Tool.tool_name, Tool.account_type, Tool.id, ToolSettings.keys,
#                              ToolSettings.values,ToolSettings.created_at)
#             .join(Tool, ToolSettings.tool_id == Tool.id)
#             .filter(Tool.account_type == "Reckon")
#             .all())

#         data2 = data1[0]

        
#         for row in keys:
#             if row[1] == "client_id":
#                 client_id = row[2]
#             if row[1] == "client_secret":
#                 client_secret = row[2]
#             if row[1] == "id_secret_encoded":
#                 id_secret_encoded = row[2]
#             if row[1] == "redirect_url":
#                 redirect_url = row[2]
#             if row[1] == "Ocp-Apim-Subscription-Key":
#                Subscription_Key = row[2]

#             if row[1] == "token":
#                 token = row[2]
#                 token_id = row[3]
#             if row[1] == "refresh_token":
#                 refresh_token = row[2]
#                 refresh_token_id = row[3]
#             if row[1] == "url":
#                 url = row[2]
#             if row[1] == "book":
#                 book = row[2]

#         difference_of_time = (datetime.now() - data2[6]).seconds
#         headers = {
#             'Authorization': f"Basic {id_secret_encoded}",
#             'Content-Type': 'application/x-www-form-urlencoded',
#         }

#         if difference_of_time >= 120:

#             payload = f"grant_type=refresh_token&refresh_token={refresh_token}&redirect_uri={redirect_url}"

#             response = requests.request("POST", main_url, headers=headers, data=payload)
#             re = response.json()
#             new_access_token = re["access_token"]
#             new_refresh_token = re["refresh_token"]

#             for row in data1:
#                 if row[4] == "refresh_token":
#                     refresh_token_data_id1 = row[0]
#                     db.session.query(ToolSettings).filter_by(id=refresh_token_data_id1).update(
#                         {"values": new_refresh_token})


#                 if row[4] == "token":
#                     access_token_data_id1 = row[0]

#                     db.session.query(ToolSettings).filter_by(id=access_token_data_id1).update(
#                         {"values": new_access_token})

#                 if row[5] :
#                     updated_time = row[0]
#                     db.session.query(ToolSettings).filter_by(id=updated_time).update(
#                         {"created_at": datetime.now()})



#             db.session.commit()

#             base_url = f"{url}/{book}"
#             payload = {}

#             post_headers = {
#                 'Authorization': f'Bearer {new_access_token}',
#                 'Content-Type': 'application/json',
#                 'Ocp-Apim-Subscription-Key': f'{Subscription_Key}'
#             }

#             get_headers = {
#                 'Authorization': f'Bearer {new_access_token}',
#                 'Content-Type': 'application/json',
#                 'Ocp-Apim-Subscription-Key': f'{Subscription_Key}'
#             }

#             return payload, base_url, book, headers, post_headers, get_headers

#         else:
#             base_url = f"{url}/{book}"
#             payload = {}

#             post_headers = {
#                 'Authorization': f'Bearer {token}',
#                 'Content-Type': 'application/json',
#                 'Ocp-Apim-Subscription-Key': f'{Subscription_Key}'
#             }

#             get_headers = {
#                 'Authorization': f'Bearer {token}',
#                 'Content-Type': 'application/json',
#                 'Ocp-Apim-Subscription-Key': f'{Subscription_Key}'
#             }

#             return payload, base_url, book,headers, post_headers, get_headers

#     except Exception as ex:
#         traceback.print_exc()
#         logging.error(ex, exc_info=True)



import traceback

import requests

from flask import request
from apps import db
from apps.home.models import Jobs
from apps.home.models import Tool, ToolSettings
# from apps.util.qbo_util import add_job_status
from datetime import datetime
from apps.util.log_file import log_config

# def post_reckon_settings(job_id):
#     logging = log_config(job_id)
#     try:
#         logging.info(f"{job_id} inside post_reckon_settings")
#         main_url = "https://identity.reckon.com/connect/token"
#         keys = (
#             db.session.query(Jobs, ToolSettings.keys, ToolSettings.values, ToolSettings.id)
#             .join(Tool, Jobs.output_account_id == Tool.id)
#             .join(ToolSettings, ToolSettings.tool_id == Tool.id)
#             .filter(Jobs.id == job_id)
#             .all()
#         )

#         # data1 = (
#         #     db.session.query(ToolSettings.id, Tool.tool_name, Tool.account_type, Tool.id, ToolSettings.keys,
#         #                      ToolSettings.values,ToolSettings.created_at)
#         #     .join(Tool, ToolSettings.tool_id == Tool.id)
#         #     .filter(Tool.account_type == "Reckon")
#         #     .all())

#         # data2 = data1[0]

        
#         for row in keys:
#             if row[1] == "client_id":
#                 client_id = row[2]
#             if row[1] == "client_secret":
#                 client_secret = row[2]
#             if row[1] == "id_secret_encoded":
#                 id_secret_encoded = row[2]
#             if row[1] == "redirect_url":
#                 redirect_url = row[2]
#             if row[1] == "Ocp-Apim-Subscription-Key":
#                Subscription_Key = row[2]

#             if row[1] == "token":
#                 token = row[2]
#                 token_id = row[3]
#             if row[1] == "refresh_token":
#                 refresh_token = row[2]
#                 refresh_token_id = row[3]
#             if row[1] == "url":
#                 url = row[2]
#             if row[1] == "book":
#                 book = row[2]

#         # difference_of_time = (datetime.now() - data2[6]).seconds

#         token=request.cookies.get('token')
#         refresh_token= request.cookies.get('refresh_token')
#         book= request.cookies.get('book')
        

    
#         headers = {
#             'Authorization': f"Basic {id_secret_encoded}",
#             'Content-Type': 'application/x-www-form-urlencoded',
#         }

        
#         base_url = f"{url}/{book}"
#         payload = {}

#         post_headers = {
#             'Authorization': f'Bearer {token}',
#             'Content-Type': 'application/json',
#             'Ocp-Apim-Subscription-Key': f'{Subscription_Key}'
#         }

#         get_headers = {
#             'Authorization': f'Bearer {token}',
#             'Content-Type': 'application/json',
#             'Ocp-Apim-Subscription-Key': f'{Subscription_Key}'
#         }

#         return payload, base_url, book,headers, post_headers, get_headers

#     except Exception as ex:
#         traceback.print_exc()
#         logging.error(ex, exc_info=True)

def post_reckon_settings(job_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside get_reckon_settings")
        main_url = "https://identity.reckon.com/connect/token"
        keys = (
            db.session.query(Jobs, ToolSettings.keys, ToolSettings.values, ToolSettings.id)
            .join(Tool, Jobs.output_account_id == Tool.id)
            .join(ToolSettings, ToolSettings.tool_id == Tool.id)
            .filter(Jobs.id == job_id)
            .all()
        )

        data1 = (
            db.session.query(ToolSettings.id, Tool.tool_name, Tool.account_type, Tool.id, ToolSettings.keys,
                             ToolSettings.values,ToolSettings.created_at)
            .join(Tool, ToolSettings.tool_id == Tool.id)
            .filter(Tool.account_type == "Reckon")
            .all())

        data2 = data1[0]


        for row in keys:
            if row[1] == "client_id":
                client_id = row[2]
            if row[1] == "client_secret":
                client_secret = row[2]
            if row[1] == "id_secret_encoded":
                id_secret_encoded = row[2]
            if row[1] == "redirect_url":
                redirect_url = row[2]
            if row[1] == "username":
                username = row[2]
            if row[1] == "password":
                password = row[2]
            if row[1] == "token":
                token = row[2]
                token_id = row[3]
            if row[1] == "refresh_token":
                refresh_token = row[2]
                refresh_token_id = row[3]
            if row[1] == "url":
                url = row[2]
            if row[1] == "book":
                book = row[2]

        difference_of_time = (datetime.now() - data2[6]).seconds
        headers = {
            'Authorization': f"Basic {id_secret_encoded}",
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        if difference_of_time >= 120:

            payload = f"grant_type=refresh_token&refresh_token={refresh_token}&redirect_uri={redirect_url}"

            response = requests.request("POST", main_url, headers=headers, data=payload)
            logging.info(f"{job_id} response status-->{response.status_code}")
            re = response.json()
            new_access_token = re["access_token"]
            new_refresh_token = re["refresh_token"]

            for row in data1:
                if row[4] == "refresh_token":
                    refresh_token_data_id1 = row[0]
                    db.session.query(ToolSettings).filter_by(id=refresh_token_data_id1).update(
                        {"values": new_refresh_token})


                if row[4] == "token":
                    access_token_data_id1 = row[0]

                    db.session.query(ToolSettings).filter_by(id=access_token_data_id1).update(
                        {"values": new_access_token})

                if row[5] :
                    updated_time = row[0]
                    db.session.query(ToolSettings).filter_by(id=updated_time).update(
                        {"created_at": datetime.now()})



            db.session.commit()

            base_url = f"{url}/{book}"
            payload = {}

            post_headers = {
                'Authorization': f'Bearer {new_access_token}',
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': 'bdddd3c7a4034e538e2fea7f61e92aa5'
            }

            get_headers = {
                'Authorization': f'Bearer {new_access_token}',
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': 'bdddd3c7a4034e538e2fea7f61e92aa5'
            }

            return payload, base_url, book, headers, post_headers, get_headers

        else:
            base_url = f"{url}/{book}"
            payload = {}

            post_headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': 'bdddd3c7a4034e538e2fea7f61e92aa5'
            }

            get_headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': 'bdddd3c7a4034e538e2fea7f61e92aa5'
            }

            return payload, base_url, book,headers, post_headers, get_headers

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)



def post_reckon_settings_v2(job_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside get_reckon_settings")
        main_url = "https://identity.reckon.com/connect/token"
        keys = (
            db.session.query(Jobs, ToolSettings.keys, ToolSettings.values, ToolSettings.id)
            .join(Tool, Jobs.output_account_id == Tool.id)
            .join(ToolSettings, ToolSettings.tool_id == Tool.id)
            .filter(Jobs.id == job_id)
            .all()
        )

        data1 = (
            db.session.query(ToolSettings.id, Tool.tool_name, Tool.account_type, Tool.id, ToolSettings.keys,
                             ToolSettings.values,ToolSettings.created_at)
            .join(Tool, ToolSettings.tool_id == Tool.id)
            .filter(Tool.account_type == "Reckon")
            .all())

        data2 = data1[0]


        for row in keys:
            if row[1] == "client_id":
                client_id = row[2]
            if row[1] == "client_secret":
                client_secret = row[2]
            if row[1] == "id_secret_encoded":
                id_secret_encoded = row[2]
            if row[1] == "redirect_url":
                redirect_url = row[2]
            if row[1] == "username":
                username = row[2]
            if row[1] == "password":
                password = row[2]
            if row[1] == "token":
                token = row[2]
                token_id = row[3]
            if row[1] == "refresh_token":
                refresh_token = row[2]
                refresh_token_id = row[3]
            if row[1] == "url":
                url = row[2]
            if row[1] == "book":
                book = row[2]

        difference_of_time = (datetime.now() - data2[6]).seconds
        headers = {
            'Authorization': f"Basic {id_secret_encoded}",
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        if difference_of_time >= 120:

            payload = f"grant_type=refresh_token&refresh_token={refresh_token}&redirect_uri={redirect_url}"

            response = requests.request("POST", main_url, headers=headers, data=payload)
            logging.info(f"{job_id} response status-->{response.status_code}")
            re = response.json()
            new_access_token = re["access_token"]
            new_refresh_token = re["refresh_token"]

            for row in data1:
                if row[4] == "refresh_token":
                    refresh_token_data_id1 = row[0]
                    db.session.query(ToolSettings).filter_by(id=refresh_token_data_id1).update(
                        {"values": new_refresh_token})


                if row[4] == "token":
                    access_token_data_id1 = row[0]

                    db.session.query(ToolSettings).filter_by(id=access_token_data_id1).update(
                        {"values": new_access_token})

                if row[5] :
                    updated_time = row[0]
                    db.session.query(ToolSettings).filter_by(id=updated_time).update(
                        {"created_at": datetime.now()})



            db.session.commit()

            base_url = f"https://api.reckon.com/r1/v2/{book}"
            payload = {}

            post_headers = {
                'Authorization': f'Bearer {new_access_token}',
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': '690395d6e257490eb8382f13f331d0db'
            }

            get_headers = {
                'Authorization': f'Bearer {new_access_token}',
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': '690395d6e257490eb8382f13f331d0db'
            }

            return payload, base_url, book, headers, post_headers, get_headers

        else:
            base_url = f"https://api.reckon.com/r1/v2/{book}"
            payload = {}

            post_headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': '690395d6e257490eb8382f13f331d0db'
            }

            get_headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': '690395d6e257490eb8382f13f331d0db'
            }

            return payload, base_url, book,headers, post_headers, get_headers

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
