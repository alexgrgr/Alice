#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 19 sept. 2016

@author: algaitan
'''
def search_employee (smartsheet, query, parameter):
    #---------------Interface with Smartsheet's API-----------------------------
    # Uses SDK to search an specified text everywhere in your account sheets.
    search_res = smartsheet.Search.search(query)
    print ("Se ha pedido buscar: " +query)

    # Result is a smartsheet.models.SearchResult object.
    # This is going to take into account only the first matched search.
    # The parameters needed to get the value of the cell on the right are sheetId
    # and rowId. columnId is also needed, but only known in JSON received with
    # get_row
    sheetId= search_res.results[0].parent_object_id
    rowId= search_res.results[0].object_id

    #[Debug] Data for get_row (parameters to be able to ask for the correct cell)
    print('SheetId: '+str(sheetId) + ' and RowId: '+str(rowId))

    #With the parameters needed to get the entire row, we request it
    row = smartsheet.Sheets.get_row(sheetId, rowId, include='discussions,attachments,columns,columnType')

    # This is a botched job, as I ran out of time to do something neat
    # JSON is formatted in such a way that the cell where I know is the data I
    # want is in here:
    whois= row.cells[1].value
    #-----------End of Interface with Smartsheet's API--------------------------

    # This will create the speech response
    speech = "El empleado " + query + " es " + str(whois) + "."
    return {speech}

def answer_json(speech):
    # This will format the JSON response message
    return{
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "alice-apiai"
    }
def get_user(req, mbuffer, user):
    # This will search in buffer for the message to retrieve personID
    #message = req.get("result").get("resolvedQuery") #Message in api.ai JSON
    print("Mensaje de Spark: "+str(mbuffer['message']))
    print("Mensaje de API.ai: "+str(req.get("result").get("resolvedQuery")))
    if req.get("result").get("resolvedQuery") in mbuffer['message']:
        user['personId']   = mbuffer['personId']
        user['personEmail']= mbuffer['personEmail']
    else:
        print("Los mensajes no coinciden en los dos flujos")
        return False
    print("El mensaje fue enviado por: "+str(user))
    return{True}

def is_partner (smartsheet, user):
    # If user appears on Smartsheet, then is must be a Cisco Partner
    search_res = smartsheet.Search.search(user.personEmail)
    if search_res.results[0].text == user['PersonEmail']: return  {True}
    else: return{False}

def search_pam (req):
    return{"Not Yet Implemented"}
