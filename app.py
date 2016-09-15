################################################################################
# Smartsheet example code. This code will listen at:                           #
#               https://smartsheet-apiai.herokuapp.com:443                     #
# It will wait until a POST /webhook message is sent to that port and perform  #
# a search of the parameter employee on all sheets on Smartsheet               #
################################################################################
import os
import json
import urllib
import requests

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

#Smartsheet Access Token. This code will be updated very soon and Token deprecated
SMARTSHEET_ACCESS_TOKEN='3evtahorlb9df7bd6imx1rzdyj'
SmartToken= 'Bearer '+SMARTSHEET_ACCESS_TOKEN

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") != "smartsheet.apiai":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    employee = parameters.get("employee")
    #---------------Interface with Smartsheet's API----------------------------------------
    # Execute search_stuff and put result in 'search_res'
    search_res= search_stuff(SMARTSHEET_ACCESS_TOKEN, 'Empleado '+employee)

    # This is going to take into account only the first matched search.
    # The parameters needed to get the value of the cell on the right are sheetId and rowId
    # columnId is also needed, but only known in JSON received with get_row
    sheetId= search_res['results'][0]['parentObjectId']
    rowId  = search_res['results'][0]['objectId']
    #[Debug] Data for get_row
    #print('SheetId: '+str(sheetId) + '       RowId: '+str(rowId))
    #With the parameters needed to get the entire row, we request it
    row_res= get_row(SMARTSHEET_ACCESS_TOKEN,sheetId,rowId)
    #This is a botched job, as I ran out of time to do something neat
    #JSON is formatted in shuch a way that the cell where I know is the data I want is in here:
    whois = row_res['cells'][1]['value']
    # [Debug] Show the employee name
    #print(str(whois))
    #-----------End of Interface with Smartsheet's API-------------------------------------

    #This will create the speech response
    speech = "El empleado " + employee + " es " + str(whois) + "."
    # [Debug]
    print("Response:")
    print(speech)
    #This will format the JSON response message
    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "smartsheet-apiai"
    }

#----------This will search for the word (stuff) in all Smartsheet sheets-------------------------
def search_stuff(SMARTSHEET_ACCESS_TOKEN,stuff):
    #Create header for GET method
    header = {'Authorization':SmartToken}
    result = requests.get(url='https://api.smartsheet.com/2.0/search?query='+ stuff, headers=header)
    # Encode received message as JSON, as it's always going to be a JSON message
    JSONresponse = result.json()
    # [Debug] Create an Array for all matched results:
    #res_array = []
    #res_json= JSONresponse ['results'][0]['parentObjectId']
    #print(res_json)
    # [Debug] For each item in the JSON data
    #for EachResult in JSONresponse['results']:
        # [Debug] add the 'text' + 'Sheet ID' + 'Row ID' to the res_array
    #    res_array.append('Text: ' + EachResult.get('text') +
    #                    '   ParentObjectId: ' + str(EachResult.get('parentObjectId')) + '  ObjectId: ' + str(EachResult.get('objectId')))
    #    print(res_array)
    # Return the list of members
    return JSONresponse
#--------------------------------------------------------------------------------------------------

#-----------This will give an array with all the cells in a Smartsheet sheet row-------------------
def get_row(SMARTSHEET_ACCESS_TOKEN,sheetId, rowId):
    #Create header for GET method
    header = {'Authorization':SmartToken}
    result = requests.get(url='https://api.smartsheet.com/2.0/sheets/'+str(sheetId)+'/rows/'+str(rowId)+'?include=discussions,attachments,columns,columnType', headers=header)
    # Encode received message as JSON, as it's always going to be a JSON message
    JSONresponse = result.json()
    # [Debug] Create an Array for all matched results:
    #res_array = []
    # [Debug] For each item in the JSON data
    #for EachResult in JSONresponse['cells']:
        # [Debug] add the 'text' + 'Sheet ID' + 'Row ID' to the res_array
    #    res_array.append('columId: ' + str(EachResult.get('columnId')) +
    #                    '   Value: ' + str(EachResult.get('value')))
    #    print(res_array)
    # Return the list of members
    return JSONresponse
#--------------------------------------------------------------------------------------------------

#App is listening to webhooks
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port " +  str(port))

    app.run(debug=True, port=port, host='0.0.0.0')
