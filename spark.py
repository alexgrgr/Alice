#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import requests

header = {
        'Authorization': 'Bearer NWMxOTI1MWEtODA1NC00NzM4LWJjMGEtNWM1YWYzNzdkMTFkOWI1ZGZiYzQtOTU3',
        'Content-Type': 'application/json'
        }

'''
Created on 19 sept. 2016

@author: algaitan
'''

def add_to_team (team, user):
    #For now, teams are:
    if team == 'basico':
        teamId = 'Y2lzY29zcGFyazovL3VzL1RFQU0vYmY3OTgyYTAtN2JmZS0xMWU2LWJiMTItNzE4OTcyNTk3OGYx'
    if team == 'medio':
        teamId = 'Y2lzY29zcGFyazovL3VzL1RFQU0vYzU3YjIzNzAtN2JmZS0xMWU2LTk4M2YtMDVjOWNjYzZjNjJj'
    if team == 'avanzado':
        teamId = 'Y2lzY29zcGFyazovL3VzL1RFQU0vY2M4MDUxOTAtN2JmZS0xMWU2LWJiMTItNzE4OTcyNTk3OGYx'
    print ("Añadir al team con ID: "+teamId)
    r = requests.post('https://api.ciscospark.com/v1/team/memberships',
    headers=header, data=json.dumps({"teamId" : teamId,
                                "personEmail" : user['personEmail'],
                                "isModerator" : "false"}))
    print("Code after add_team POST: "+str(r.status_code))
    if (r.status_code !=200):
        print(str(json.loads(r.text)))
        if r.status_code == 409:
            status= str(user['personEmail'])+", ya es usted miembro"
        elif r.status_code == 403:
            status= "Oops, no soy moderador de dicho team"
        else:
            status='Unknown error'
    else:
        status = str(user['personEmail'])+" ha sido correctamente añadido al team "+team
        #else: message = "Oops, no he podido procesar la solicitud"
        place = 'sameRoom'
    #bot_answer(place, "accion de miembro")
    print(status)
    return status

def bot_answer(place, message):
    if place == 'sameRoom':
        r = requests.post('https://api.ciscospark.com/v1/team/memberships', headers=header, data=json.dumps({"teamId" : teamId,"personEmail" : user['personEmail'], "isModerator" : "false"}))#"personId" : user['personId'],
        print("Code after add_team POST: "+str(r.status_code))
        if (r.status_code !=200):  #requests.codes_ok):
            print(str(json.loads(r.text)))
            if r.status_code == 409:
                result= "Ya es usted miembro"
                print(str(result))
    #elif place == '1to1':

    #else:

    return{result}

def buffer_it(JSON, mbuffer):
    # Webhook is triggered if a message is sent to the bot. We would  save the
    # JSON and the message unciphered
    JSONresponse = JSON
    messageId= JSONresponse['data']['id']
    print("Message ID: "+messageId)
    message = requests.get(url='https://api.ciscospark.com/v1/messages/'+messageId, headers=header)
    JSONresponse = message.json()
    # Then, message is retrieved, to compare with the one received from api.ai.
    # This is needed as it will demonstrate both messages are the same, and then
    # PersonId and PersonEmail would be extracted from it.
    # Dictionary Containing info would be lke this:
    # -------------------
    # |message decrypted|  Used to compare with the message from api.ai
    # |    personId     |  Speaker unique ID
    # |   personEmail   |  Speaker unique email
    # -------------------
    messagedecrypt  = JSONresponse.get("text")
    personId = JSONresponse.get("personId")
    personEmail = JSONresponse.get("personEmail")
    print ("Message Decrypted: \t"+messagedecrypt+ "\npersonId: \t"+personId+"\npersonEmail: \t"+personEmail)

    # Save all in buffer and then wait for new webhook
    mbuffer['message']    = messagedecrypt
    mbuffer['personId']   = personId
    mbuffer['personEmail']= personEmail
    return True
