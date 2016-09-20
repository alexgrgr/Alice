#!/usr/bin/python
# -*- coding: UTF-8 -*-
################################################################################
#                                                                              #
#               https://smartsheet-apiai.herokuapp.com:443                     #
# It will wait until a POST with path=/webhook message is sent to that socket  #
# and perform a search of the parameter 'employee' on all sheets on Smartsheet #
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
#Buffer for capturing messages from Spark
mbuffer = {"message":"","personId":"","personEmail":""}
user = {"personId":"","personEmail":""}

@app.route('/webhook', methods=['POST','GET'])
def webhook():
    req = request.get_json(silent=True, force=True)
    try:
        print("[API.ai] There is an action: "+req["result"]["action"]) #This only
                                                    #exists if POSTed from apia.ia
    except:
        print ('[Spark]')
        res = spark_webhook(req)
        print ("That´s all for now")
        res = json.dumps(res, indent=4)
        #print(res)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        return r
    else:
        res = apiai_webhook(req)
        print ("Nothing else. POSTing api.ai")
        res = json.dumps(res, indent=4)
        #print(res)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        return r


def spark_webhook (req):
    #JSON is from Spark. This will contain the message, a personId and a personEmail
    print ("I´m going to buffer this shit")
    print ("Before buffering: "+str(req))
    if spark.buffer_it(req, mbuffer):
        return{"Buffer": "Buffer correct"}
    else: return{"Buffer": "Buffer error"}

def apiai_webhook(req):
    print ("Parameters: "+str(req.get("result").get("parameters")))
    # api.ai request to search for an employee
    if req.get("result").get("action") == 'search.employee':
        print ("Asked to search employee")
        query = req.get("result").get("parameters").get("employee")
        string_res = sdk.search_employee(smartsheet, query)

    # api.ai request to search PAM of a particular partner
    elif req.get("result").get("action") == 'search.pam':
        print ("Asked to search pam")
        sdk.get_user(req, mbuffer, user)
        string_res="No Yet Implemented (app2:line55)"
        #if sdk.is_partner(smartsheet, user): string_res = sdk.search_pam(req)

    # api.ai request to add a Partner to a specific Team
    elif req.get("result").get("action") == 'add.sparkclinic':
        print ("Asked to set spark clinic")
        if sdk.get_user(req, mbuffer, user):
            print("User is: "+str(user))
            team = req.get("result").get("parameters").get("sparkclinic")
            print ("team is: "+str(team))
            string_res  = spark.add_to_team(team, user)
        else:
            string_res="Fallo en la obtención del usuario desde Spark"
            print(string_res)
    else:
        string_res = "Ooops, se ha solicitado a Alice algo no implementado"
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
