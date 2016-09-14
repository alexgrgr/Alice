#How to Provide Replies about some data on Smartsheet using Api.ai Webhook

This example shows how you can use `Api.ai webhook` to provide information allocated at [Smartsheet] (https://smartsheet.com)
At the actual stage, it will only search for a phrase starting with **_Empleado_** and retrieve only the cell on the same row and contiguous cell.
**Note**:*Smartsheet Access Token will need to be created at Personal Settings-> API Access on Smartsheet Website*
# Deploy to:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
Deploy it now to heroku

In order to connect *api.ai* webhook, URL is `https://[yourappname].herokuapp.com/webhook`

An intent with **webhook enabled** is needed, and `action` to be `smartsheet.apiai`
