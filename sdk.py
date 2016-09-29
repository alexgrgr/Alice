#!/usr/bin/python
# -*- coding: UTF-8 -*-
################################################################################
#                                  SDKLIB                                      #
#                  https://alice-apiai.herokuapp.com:443                       #
# This file contains functions for interfacing other API's and internal tasks  #
################################################################################

import requests
import time
import os

# Spark's header with Token defined in environmental variables
spark_header = {
        'Authorization': 'Bearer ' + os.environ.get('SPARK_ACCESS_TOKEN', None),
        'Content-Type': 'application/json'
        }

#------------------Interface with Smartsheet's API------------------------------

# Searchs an specified text everywhere in your account sheets.
def search_employee (smartsheet, query, parameter=0):
    search_res = smartsheet.Search.search(query)
    print ("Se ha pedido buscar: " +query)
    # Result is a smartsheet.models.SearchResult object. This particular
    # implementation is going to take into account only the first matched search.
    # The parameters needed to get the values of the cell on the right are
    # sheetId and rowId. columnId is also needed, but only known in JSON
    # received with get_row
    sheetId= search_res.results[0].parent_object_id
    rowId  = search_res.results[0].object_id

    #[Debug] Data for get_row (parameters to be able to ask for the correct cell)
    #print('SheetId: '+str(sheetId) + ' and RowId: '+str(rowId))

    # With the parameters needed to get the entire row, we request it
    row = smartsheet.Sheets.get_row(sheetId, rowId,
                           include='discussions,attachments,columns,columnType')

    # --The following is a botched job--
    # JSON is formatted in such a way that the cell where I know where the data
    # I want is in here:
    whois= row.cells[1].value
    speech = "La respuesta a \"" + query + "\" es: " + str(whois) + "."
    return speech

#---------------End of Interface with Smartsheet's API--------------------------

# This is not used for now
def answer_json(speech):
    # This will format the JSON response message
    return{
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "alice-apiai"
    }


def get_user(req, sbuffer, user):
    # This will search in buffer for the message, to retrieve personID
    for x in range(1, 20):
        print("Mensaje de Spark: \t"+str(sbuffer[x]['message']))
        print("Mensaje de API.ai: \t"+str(req.get("result").get("resolvedQuery")))
        if req.get("result").get("resolvedQuery") in sbuffer[x]['message']:
            user['personId']   = sbuffer[x]['personId']
            user['personEmail']= sbuffer[x]['personEmail']
            user['displayName']= sbuffer[x]['displayName']
            found= True
            print("Message sent by:    \n   personId: \t"+ user['personId']
                                  +"\n   personEmail: \t"+user['personEmail']
                                  +"\n   displayName: \t"+user['displayName'])
            break
        else:
            # [Debug]
            #print("Los mensajes no coinciden. Siguiente mensaje.")
            found=False
    if not found: print ("No coincidence among array")
    return found

def is_partner (smartsheet, user):
    # If user appears on Smartsheet, then is must be a Cisco Spain Partner
    search_res = smartsheet.Search.search(user.personEmail)
    if search_res.results[0].text == user['PersonEmail']: return True
    else: return False

def search_pam (user):
    # The user's PAM is searched
    return {"Not Yet Implemented"}

def buffer_it(JSON, sbuffer):
    # Webhook is triggered if a message is sent to the bot. The JSON and the
    # message unciphered are then saved
    # First step is to discard bot's own messages
    if JSON['data']['personEmail'] != os.environ.get('BOT_EMAIL',
                                                                '@sparkbot.io'):
        messageId= JSON['data']['id']
        print("Message ID: "+messageId)
        # Message is ciphered. Unciphered message must be GET from Spark
        message = requests.get(url='https://api.ciscospark.com/v1/messages/'
                                            +messageId,
                                                    headers=header)
        JSON = message.json()
        # Message is used, to compare it with the one received from api.ai.
        # This is needed as it will demonstrate both messages are the same, and
        # then PersonId and PersonEmail would be extracted from it.
        # Dictionary Containing info would be lke this:
        # -------------------
        # |    timestamp    |  If content is too old, it could be overwritten
        # |message decrypted|  Used to compare with the message from api.ai
        # |    personId     |  Speaker unique ID
        # |   personEmail   |  Speaker unique email
        # |   displayName   |  Speaker´s displayed name
        # -------------------
        # Note: as webhooks are received in a ramdom way and this Heroku app
        # cannot be threaded, they should be buffered.
        messagedecrypt  = JSON.get("text")
        personId        = JSON.get("personId")
        personEmail     = JSON.get("personEmail")
        # The Display Name of the person must be GET from Spark too
        displayName     = spark.get_displayName(personId)
        # Finally, a timestamp to be able to erase old messages
        timenow =time.time()
        print ("Message Decrypted: "  + messagedecrypt
                    + "\npersonId: \t"+ personId
                  +"\npersonEmail: \t"+ personEmail
                  +"\ndisplayName: \t"+ displayName
                    +"\ntimestamp: \t"+ str(timenow))
        # Save all in buffer and then wait for new webhook
        for x in range(1, 20):
            if ((timenow - sbuffer[x]['timestamp']) > float(5)):
                sbuffer[x]['timestamp']  = time.time()
                sbuffer[x]['message']    = messagedecrypt
                sbuffer[x]['personId']   = personId
                sbuffer[x]['personEmail']= personEmail
                sbuffer[x]['displayName']= displayName
                break
        print ("Buffer ACK. Timestamp= "+str(sbuffer[x]['timestamp']))
        #print ("Buffer ACK. personId= "+mbuffer['personId'])
        return True
    else:
        return False
