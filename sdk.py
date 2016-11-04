#!/usr/bin/python
# -*- coding: UTF-8 -*-
################################################################################
#                                  SDKLIB                                      #
#               https://alice-apiai.herokuapp.com:443/apiai                    #
# This file contains functions for interfacing other API's and internal tasks  #
################################################################################

import requests
import spark
import uuid
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
    # This will retrieve personID, personEmail and displayName
    #print("API.ai ID: \t" + str(req.get("sessionId")))
    #print(" Spark ID: \t" + str(sbuffer['sessionId']))
    #if str(req.get("id"))[15:] in str(sbuffer['sessionId']):
    user['personId']   = sbuffer['personId']
    user['personEmail']= sbuffer['personEmail']
    user['displayName']= sbuffer['displayName']
    found= True
    print("Message sent by:    \n   personId: \t" + user['personId']
                          +"\n   personEmail: \t" + user['personEmail']
                          +"\n   displayName: \t" + user['displayName'])
    #else:
        # [Debug]
        #print("Los mensajes no coinciden. Siguiente mensaje.")
    #    found=False
    if not found: print ("Error, different sessionId")
    return found

def is_cisco (user):
    # If users email contains @cisco.com, then is must be a Cisco Employee
    print ("User email [is_cisco]" +  user['personEmail'])
    if "@cisco.com" in user['personEmail']: return True
    else: return False

def is_partner (smartsheet, user):
    # If user appears on Smartsheet, then is must be a Cisco Spain Partner
    # this information is on sheetid= 6064162607523716
    sheetId = 6064162607523716
    search_res = smartsheet.Search.search_sheet(sheetId, user['personEmail'])
    if search_res.results[0].text in user['PersonEmail']: return True
    else: return False

def search_pam (smartsheet, user, partner=None):
    # The PAM of the specified user is searched or user's PAM. The sheet with
    # this information has sheetid= 6064162607523716
    sheetId = 6064162607523716
    # if there is a partner string, then you are asking for a PAM different to
    # user's one. This info can only be disclosed internally, so Alice should
    # check first if this user is a Cisco employee. If asking for own PAM, Alice
    # will check to what partner user belongs to.
    if partner is None:
        print ("no partner specified")
        # In this case, check if user is partner. If true, retreive its pam
        if is_cisco (user):
            print ("Yeah. User is Cisco Employee")
            # Maybe is a Cisco employee and asks for its pam, something not possible
            string_res = "Pero " + spark.mention(user['displayName'],
                                                 user['personEmail']) + ", usted \
                                            es empleado de Cisco. No tiene PAM."
        #-----------------------------Problem here-----------------------------#
        elif is_partner (smartsheet, user):
            print("Yeah, user is partner")
            search_res = smartsheet.Search.search_sheet(sheetId, user['personEmail'])
            rowId  = search_res.results[0].object_id
            # With the parameters needed to get the entire row, we request it
            row = smartsheet.Sheets.get_row(sheetId, rowId,
                           include='discussions,attachments,columns,columnType')
            # --The following is a botched job--
            # JSON is formatted in such a way that the cell where I know where
            # the data I want is in here:
            pam = row.cells[1].value
            string_res = spark.mention(user['displayName'],
                                     user['personEmail']) + ", su PAM es:\
                                      _"+ pam + "_"
        #----------------------------------------------------------------------#
        else:
            # In this case, user is not a partner, nor a Cisco Employee. cannot
            # see internals
            string_res = user['displayName'] + ", usted no tiene permisos para \
                                            visualizar datos internos."
    else:
        print("Partner specified")
        # PAM for the user that is asked, if he/she is a Cisco Employee
        if is_cisco (smartsheet, user):
            print ("Yeah. User is Cisco Employee")
            search_res = smartsheet.Search.search_sheet(sheetId, partner)
            # As in search_employee, Result is a smartsheet.models.SearchResult
            # object.
            rowId  = search_res.results[0].object_id
            # With the parameters needed to get the entire row, we request it
            row = smartsheet.Sheets.get_row(sheetId, rowId,
                           include='discussions,attachments,columns,columnType')
            # --The following is a botched job--
            # JSON is formatted in such a way that the cell where I know where
            # the data I want is in here:
            partner = row.cells[1].value
            pam = row.cells[0].value
            string_res = "El PAM para el partner **" + partner + "** \
                                             es: _" + str(pam) + "_"
        else:
            # In this case, user is not a partner, nor a Cisco Employee. cannot
            # see internals
            string_res = user['displayName'] + ", usted no tiene permisos para \
                                            visualizar datos internos."
    print (string_res)
    return string_res

def buffer_it(JSON, sbuffer):
    # Webhook is triggered if a message is sent to the bot. The JSON and the
    # message unciphered are then saved
    # First step is to discard bot's own messages
    if JSON['data']['personEmail'] != os.environ.get('BOT_EMAIL',
                                                                '@sparkbot.io'):
        roomId    = JSON['data']["roomId"]
        messageId = JSON['data']['id']
        print("Message ID: "+messageId)
        # Message is ciphered. Unciphered message must be GET from Spark
        message = requests.get(url='https://api.ciscospark.com/v1/messages/'
                                            +messageId,
                                                    headers=spark_header)
        JSON = message.json()
        # Message is used, to compare it with the one received from api.ai.
        # This is needed as it will demonstrate both messages are the same, and
        # then PersonId and PersonEmail would be extracted from it.
        # Dictionary Containing info would be lke this:
        # -------------------
        # |    sessionId    |  Identifies message at API.ai
        # !      roomId     |  Saving just in case
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
        # Finally, a timestamp to let apiai identify messages.
        # [WARNING] UUIDV1 specifies string + time ID. Maybe there is need to use
        # roomId as identification, but not very well specified in Docs
        #sessionId = uuid.uuid1()
        # Session ID is based on roomId
        sessionId = uuid.uuid5(uuid.NAMESPACE_DNS, str(roomId))
        #sessionId = roomId
        print ("Message Decrypted: "  + messagedecrypt
                      + "\nroomId: \t"+ roomId
                    + "\npersonId: \t"+ personId
                  +"\npersonEmail: \t"+ personEmail
                  +"\ndisplayName: \t"+ displayName
                         +"\nuuid: \t"+ str(sessionId))
        # Save all in buffer and then wait for new webhook
        sbuffer['sessionId']  = str(sessionId)
        sbuffer['roomId']     = roomId
        sbuffer['message']    = messagedecrypt
        sbuffer['personId']   = personId
        sbuffer['personEmail']= personEmail
        sbuffer['displayName']= displayName
        print ("Buffer ACK. UUID= " + str(sessionId))
        return True
    else:
        print ("message from bot: ignoring")
        return False
