import traceback
import requests
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database

def get_reckon_projects(job_id, task_id):
    
    print(f"{job_id} inside get_reckon_projects-------------")
    
    try:
        
        # MongoDB
        dbname = get_mongodb_database()
        collection = dbname["reckon_projects"]

        # Reckon API settings
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(job_id)

        # ⚡ Projects endpoint
        url = f"{base_url}/projects/1000"  # Adjust if your Reckon API version/path is different

        response = requests.get(url, headers=get_headers, data=payload)

        if response.status_code != 200:
            return

        json_response = response.json()

        
        projects = json_response.get("Items", [])

        if not isinstance(projects, list):
            print("Items is not a list:", projects)
            return

        print(len(projects), "projects fetched")
        
        arr = []
        for project in projects:
            project["job_id"] = job_id
            project["task_id"] = task_id
            project["table_name"] = "reckon_projects"
            project["error"] = None
            project["is_pushed"] = 0

            arr.append(project)

        if arr:

            print(f"{job_id} Inserting {len(arr)} projects into MongoDB")
            collection.insert_many(arr)

    except Exception as ex:
        traceback.print_exc()
        print(f"Error in get_reckon_projects: {ex}")