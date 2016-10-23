#!/usr/bin/python
# -*- coding: UTF-8 -*-
################################################################################
#                                 ALICEBOT                                     #
#               https://alice-apiai.herokuapp.com:443/apiai                    #
# It will wait until a POST with path=/webhook message is sent to that socket  #
# and perform the action specified:                                            #
#   ·Search query in smartsheet [OK]                                           #
#   ·Add user to a team [OK- Not for all teams ]                               #
#   ·Search Partner's PAM and send it privately to Partner [Waiting]           #
#   ·Create a demo personal room for trial and sent info to mail [Waiting]     #
#                                                                              #
# In a nutshell, we are receiving vital info from both streams, to be able to  #
# compute the required action:                                                 #
#         ______________                               ______________          #
#        |  From SPARK |                              | From API.AI |          #
#        |-------------|                              |-------------|          #
#        |   message   |                              |  message    |          #
#        |  personId   |                              |  actions    |          #
#        | personEmail |                              | parameters  |          #
#        | displayName |                              --------------           #
#        ---------------                                                       #
# personID or personEmail is needed to know who are we talking to              #
################################################################################

import smartsheet
import sdk
import spark
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

# Instantiation of Smartsheet object. It is a custom object. Be careful guessing
# the content in objects. Refer directly to the library code, not API Docs.
smartsheet = smartsheet.Smartsheet()

# Buffer for capturing messages from Spark
sbuffer = {k: {"timestamp":float(6),"message":"","personId":"","personEmail":"",
                                           "displayName":""} for k in range(20)}
# Buffer for capturing messages from api.ai
abuffer = {k: {"timestamp":float(6),"message":"","action":"",
                                             "parameters":""} for k in range(4)}
# Defining user's dict
user    = {"personId":"","personEmail":"","displayName":""}

@app.route('/apiai', methods=['POST','GET'])
def apiai():
    req = request.get_json(silent=True, force=True)
    print("[API.ai] There is an action: "+req["result"]["action"])    #This only
                                                  #exists if POSTed from apia.ia
    res = apiai_webhook(req)
    print ("DONE: POSTing to api.ai")
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

@app.route('/webhook', methods=['POST','GET'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print ('[Spark]')

    res = spark_webhook(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def spark_webhook (req):
    # JSON is from Spark. This will contain the message, a personId and a
    # personEmail that will be buffered for future use
    if sdk.buffer_it(req, sbuffer):
        return {"Buffer": "Buffer correct"}
    else: return {"Buffer": "Buffer error"}

def apiai_webhook(req):
    # JSON is from api.ai. This will contain the message, the action and the
    # parameters
    print ("Parameters: "+str(req.get("result").get("parameters")))
    # api.ai request to search for an employee
    action = req.get("result").get("action")
    if  action == 'search.query':
        print ("Asked to search something in smartsheet")
        query = req.get("result").get("parameters").get("query")
        string_res = sdk.search_employee(smartsheet, query)

    # api.ai request to search PAM of a particular partner
    elif action == 'search.pam':
        print ("Asked to search PAM")
        partner = req.get("result").get("parameters").get("partner")
        if sdk.get_user(req, sbuffer, user):
            pam = sdk.search_pam (smartsheet, user, partner)
            string_res= str(pam)
        else:
            string_res="Fallo en la obtención del usuario desde Spark. Pruebe \
                        de nuevo, por favor."
            print(string_res)

    #api.ai request to search PAM of the user that solicites it
    elif action == 'search.mypam':
        print ("Asked to search my PAM")
        sdk.get_user(req, sbuffer, user)
        if sdk.get_user(req, sbuffer, user):
            pam = sdk.search_pam (smartsheet, user)
            string_res= pam
        else:
            string_res="Fallo en la obtención del usuario desde Spark. Pruebe \
                        de nuevo, por favor."
            print(string_res)
        string_res="No Yet Implemented (alice:line105)"

    # api.ai request to add a Partner to a specific Team
    elif action == 'add.sparkclinic':
        print ("Asked to set Spark Clinic")
        if sdk.get_user(req, sbuffer, user):
            team = req.get("result").get("parameters").get("sparkclinic")
            print ("team is: "+str(team))
            string_res  = spark.add_to_team(team, user)
        else:
            string_res="Fallo en la obtención del usuario desde Spark. Pruebe \
                        de nuevo, por favor."
            print(string_res)
    else:
        string_res = "Ooops, se ha solicitado a Alice algo no implementado\n\t \
                    Action: " + str(action)
    #return{str(string_res)}
    #res = sdk.answer_json(str(string_res))
    return{
        "speech": str(string_res),
        "displayText": str(string_res),
        #"data": {},
        # "contextOut": [],
        "source": "smartsheet-apiai"
        }

# App is listening to webhooks. Next line is used to executed code only if it is
# running as a script, and not as a module of another script.
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print ("Starting app on port " +  str(port))
    app.run(debug=True, port=port, host='0.0.0.0', threaded=True)
