#How to Provide Replies including some data residing on Smartsheet, using Api.ai Webhook

This example demonstrates how easily you can use `Api.ai webhook` to provide information allocated at [Smartsheet] (https://smartsheet.com). At the actual stage, it will only search for a phrase starting with **_Empleado_** and retrieve only the cell on the same row and contiguous cell.

Please, come back often, as it will be heavily updated next days. A changelog will be provided with instructions to make your deployment work.

**Note**:*Smartsheet Access Token will need to be created at Personal Settings-> API Access on Smartsheet Website. Then it must be uploaded to Heroku as an enviroment variable: `Variable: SMARTSHEET_ACCESS_TOKEN    Value= [YOUR_TOKEN]`*

# Deploy it to Heroku:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

#api.ai Configuration

  1. Under Fulfillment, set URL to `https://[yourappname].herokuapp.com/webhook`

  2. Enable webhook and set `action` to `smartsheet.apiai`under the *Intent* to be used
