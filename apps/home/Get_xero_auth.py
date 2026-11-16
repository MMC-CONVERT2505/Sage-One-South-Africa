import json 
import requests
import webbrowser
import base64

client_id = "BDDDE967BCF943098B8A44E164AE1A74"
client_secret= "JVCy3rDSvqkMelGOxJenpLkdiAgRgiHcXLe6GJZ79IAKXv_l"
redirect_uri= "https://www.mmcconvert.com"
scope="offline_access accounting.transactions"

CLIENT_ID = f"{client_id}"
CLIENT_SECRET=f"{client_secret}"
clientIdSecret = CLIENT_ID + ':' + CLIENT_SECRET
encoded_u = base64.b64encode(clientIdSecret.encode()).decode()
auth_code = "%s" % encoded_u

def XeroFirstAuth():
    auth_url =('''https://login.xero.com/identity/connect/authorize?'''+
              '''response_type=code'''+
              '''&client_id=''' + client_id +
              '''&client_secret=''' +client_secret +
              '''&redirect_uri=''' + redirect_uri +
              '''&scope='''+ scope +
              '''&state=123456''')
    
    webbrowser.open_new(auth_url)

    return auth_url
    
  