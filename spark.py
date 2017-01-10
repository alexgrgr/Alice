#!/usr/bin/python
# -*- coding: UTF-8 -*-
################################################################################
#                                 SPARKLIB                                     #
#               https://alice-apiai.herokuapp.com:443/apiai                    #
# It will wait until a POST with path=/webhook message is sent to that socket  #
# and perform a search of the parameter 'employee' on all sheets on Smartsheet #
################################################################################

import json
import requests
import os

# Spark's header with Token defined in environmental variables
spark_header = {
        'Authorization': 'Bearer ' + os.environ.get('SPARK_ACCESS_TOKEN', None),
        'Content-Type': 'application/json; charset: utf-8'
        }

#-----------------------------List of Team--------------------------------------
# For better visualization, list of possible teams will be published here
clinic_basico   = 'Y2lzY29zcGFyazovL3VzL1RFQU0vYmY3OTgyYTAtN2JmZS0xMWU2LWJiMTItNzE4OTcyNTk3OGYx'
clinic_medio    = 'Y2lzY29zcGFyazovL3VzL1RFQU0vYzU3YjIzNzAtN2JmZS0xMWU2LTk4M2YtMDVjOWNjYzZjNjJj'
clinic_avanzado = 'Y2lzY29zcGFyazovL3VzL1RFQU0vY2M4MDUxOTAtN2JmZS0xMWU2LWJiMTItNzE4OTcyNTk3OGYx'

def add_to_team (team, user):
    #This will add the user specified in user to the team name in team
    #For now, teams are:
    if team == ('basico'|'básico'):
        teamId = clinic_basico
    if team == ('medio'|'intermedio'):
        teamId = clinic_medio
    if team == ('avanzado'|'alto'):
        teamId = clinic_avanzado
    print ("Añadir al team con ID: "+teamId)
    r = requests.post('https://api.ciscospark.com/v1/team/memberships',
          headers=spark_header, data=json.dumps({"teamId" : teamId,
                                            "personEmail" : user['personEmail'],
                                            "isModerator" : "false"}))
    print("Code after add_team POST: "+str(r.status_code))
    if r.status_code !=200:
        print(str(json.loads(r.text)))
        if   r.status_code == 403:
            status= "Oops, no soy moderador de dicho team"
        elif r.status_code == 409:
            status= str(user['displayName'])+", ya es usted miembro"
        elif r.status_code == 404:
            status= "Disculpe. Ya no soy miembro ni moderador de dicho grupo"
        else:
            status='Unknown error 4xx'
    else:
        status = str(user['displayName'])+", ha sido correctamente añadido al \
                                                                 team: " + team
        print (status)
    return status

def get_displayName (personId):
    # To get the displayName of the user, Spark only needs to know the personId
    # or the personEmail
    message = requests.get(url='https://api.ciscospark.com/v1/people/'+personId,
                        headers=spark_header)
    JSON = message.json()
    return JSON.get("displayName")

def mention (displayName, personEmail):
    # Formats a mention in a spark markdown message
    mention = "<@personEmail:"+ personEmail + "|" + displayName +">"
    return mention

def bot_answer(message, files, user= None, roomId= None):
    # This will generate a response to spark

    # [Debug]
    print ('Send to spark: \t'+ str(message))
    # [Debug] print ('Send to user: \t' + str(user))
    # [Debug] print ('Send to room: \t' + str(roomId))
    if roomId != None:
        #Send in roomId received
        if files['name'] is "":
            r = requests.post('https://api.ciscospark.com/v1/messages',
                         headers=spark_header, data=json.dumps({"roomId":roomId,
                                                               "markdown":message
                                                                }))
        else:
            r = requests.post('https://api.ciscospark.com/v1/messages',
                         headers=spark_header, data=json.dumps({"roomId":roomId,
                                                               "markdown":message,
                                      "files": (str(files['name']),
                                                open(files['path'], 'rb'),
                                                 str(files['filetype']))
                                                                            }))
    elif user != None:
        if files['name'] is "":
            #Send to user
            r = requests.post('https://api.ciscospark.com/v1/messages',
                               headers=spark_header,
                               data=json.dumps({"personEmail":user['personEmail'],
                                                   "markdown":message
                                                }))
        else:
            r = requests.post('https://api.ciscospark.com/v1/messages',
                               headers=spark_header,
                               data=json.dumps({"personEmail":user['personEmail'],
                                                   "markdown":message,
                                                      "files":files
                                                }))
    else:
        print ("Send Message: No RoomId or UserId specified")

    print("Code after send_message POST: "+str(r.status_code))
    status= "Message sent to Spark"
    if r.status_code !=200:
        print(str(json.loads(r.text)))
        if   r.status_code == 403:
            status= "Oops, no soy moderador del team de dicha sala"
        elif r.status_code == 404:
            status= "Disculpe. Ya no soy miembro ni moderador de dicho grupo"
        elif r.status_code == 409:
            status= "Lo siento, no ha podido ser enviado (409)"
        elif r.status_code == 500:
            status= "Perdón, los servidores de Spark están sufriendo problemas.\
                               Compruébelo aquí: https://status.ciscospark.com/"
        elif r.status_code == 503:
            status= "Lo siento. Parece ser que los servidores de Spark no \
                                            pueden recibir mensajes ahora mismo"
        else:
            response = r.json()
            status= str('Error desconocido: \ '
                                         + response['errors'][0]['description'])
    return status
