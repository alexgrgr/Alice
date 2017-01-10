#!/usr/bin/python
# -*- coding: UTF-8 -*-
################################################################################
#                                 ALICEBOT                                     #
#               https://alice-apiai.herokuapp.com:443/apiai                    #
#               https://alice-apiai.herokuapp.com:443/webhook                  #
# Flow:                                                                        #
# Spark--------------                                                          #
#                   |                                                          #
#                   --------->Alice------                                      #
#                                       |                                      #
#                                       ----------------------> NLP            #
#                                                                 |            #
#                                       --------------------------             #
#                                       |                                      #
#                        Alice<---------                                       #
# Spark<-------------if no actions                                             #
#                      if actions--------> External Sources:                   #
#                                                           smartsheet,        #
#                                                           PacoApp,           #
#                                                           Spark,...          #
#                                                             |                #
#                                       -----------------------                #
#                                       |                                      #
#                        Alice<---------                                       #
#                          |                                                   #
#                          -------------------------------------> NLP          #
#                                                                 |            #
#                                       --------------------------             #
#                                       |                                      #
# Spark<-----------------Alice<---------                                       #
# Actions specified:                                                           #
#   ·Search query in smartsheet [OK]                                           #
#   ·Add user to a team [OK- Not for all teams ]                               #
#   ·Search Partner's PAM and send it privately to Partner [Waiting]           #
#   ·Create a demo personal room for trial and sent info to mail [Waiting]     #
#                                                                              #
# personID or personEmail is needed to know who are we talking to              #
################################################################################

import smartsheet
import sdk
import time
import spark
import json
import os
import apiai
import nlpApiai
from datetime import timedelta

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

# Instantiation of APIai object.
ai = apiai.ApiAI(os.environ.get('APIAI_ACCESS_TOKEN', None))

# Instantiation of Smartsheet object. It is a custom object. Be careful guessing
# the content in objects. Refer directly to the library code, not API Docs.
smartsheet = smartsheet.Smartsheet()

# Buffer for capturing messages from Spark
sbuffer = {"timestamp":float(6),"sessionId":"","roomId":"","message":"",
           "personId":"","personEmail":"","displayName":"",
           "file":{"name":"","path":"","filetype":""}}
# Buffer for capturing messages from api.ai
#abuffer = {k: {"timestamp":float(6),"message":"","action":"",
#                                             "parameters":""} for k in range(4)}
abuffer = {"sessionId":"","confident":"", "message":"","action":"",
                                "parameters":""}

# Defining user's dict
user    = {"personId":"","personEmail":"","displayName":""}

@app.route('/webhook', methods=['POST','GET'])
def webhook():
    # Speed meassuring variable
    start = time.time()
    # Every message from Spark is received here. I will be analyzed and sent to
    # api.ai response will then sent back to Spark
    req = request.get_json(silent=True, force=True)
    #print ('[Spark]')
    res = spark_webhook(req, start)
    print (res)
    return None

@app.route('/apiai', methods=['POST','GET'])
def apiai():
    # If there is external data to retrieve, APIai will send a WebHook here
    req = request.get_json(silent=True, force=True)
    print("[API.ai] There is an action: "+req["result"]["action"])
    res = apiai_webhook(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def spark_webhook (req, start):
    # JSON is from Spark. This will contain the message, a personId, displayName,
    # and a personEmail that will be buffered for future use
    if sdk.buffer_it(req, sbuffer):
        # Once this is done, we need to prepare and send the message for APIai
        status = nlpApiai.apiai_send (ai, sbuffer, abuffer)
        #sdk.confident()
        # Answer from api.ai may include an action to post attachments
        if "att." in str(abuffer['action']):
            status = sdk.prepare_attachment(sbuffer, abuffer)
            print("Status attachement: "+ str(status))
        #print("Convert to spark")
        nlpApiai.apiai2spark(abuffer, sbuffer)
        status = spark.bot_answer(
                            sbuffer['message'] + " \n\n \n\n Time elapsed: " +
                                    str(timedelta(seconds=time.time() - start)),
                            sbuffer['file'],
                            None,
                            sbuffer['roomId'])
    else: status = "Error buffering"
    return status


def apiai_webhook(req):
    # JSON is from api.ai. This will contain the message, the action and the
    # parameters
    print ("Parameters: "+str(req.get("result").get("parameters")))
    # api.ai request to search for an employee
    action = req.get("result").get("action")
    if  action == 'search.query':
        if sdk.get_user(req, sbuffer, user):
            print ("Asked to search something in smartsheet")
            query = req.get("result").get("parameters").get("query")
            string_res = sdk.search_employee(smartsheet, query)
        else:
            string_res="Fallo en la obtención del usuario desde Spark. Pruebe \
                        de nuevo, por favor."

    # api.ai request to search PAM of a particular partner
    elif action == 'search.am':
        print ("Asked to search AM")
        client = req.get("result").get("parameters").get("client")
        if sdk.get_user(req, sbuffer, user):
            am = sdk.search_am (smartsheet, user, client)
            string_res= str(am)
        else:
            string_res="Fallo en la obtención del usuario desde Spark. Pruebe \
                        de nuevo, por favor."
        print (string_res)

        #api.ai request to search PAM of the user that ask for it
    elif action == 'search.myam':
        print ("Asked to search my AM")
        if sdk.get_user(req, sbuffer, user):
            am = sdk.search_am (smartsheet, user)
            string_res= str(am)
        print(string_res)
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
        print (string_res)

    #api.ai request to search PAM of the user that ask for it
    elif action == 'search.mypam':
        print ("Asked to search my PAM")
        if sdk.get_user(req, sbuffer, user):
            pam = sdk.search_pam (smartsheet, user)
            string_res= str(pam)
        print(string_res)

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
