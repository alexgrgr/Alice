#How to Provide Replies with some data on Smartsheet using Api.ai Webhook

This example demonstrates how easily you can use `Api.ai webhook` to provide information allocated at [Smartsheet] (https://smartsheet.com)
At the actual stage, it will only search for a phrase starting with **_Empleado_** and retrieve only the cell on the same row and contiguous cell.

**Note**:*Smartsheet Access Token will need to be created at Personal Settings-> API Access on Smartsheet Website*

# Deploy it to Heroku:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

#api.ai Configuration

  1. Under Fulfillment, set URL to `https://[yourappname].herokuapp.com/webhook`

  2. Enable webhook and set `action` to `smartsheet.apiai`under the *Intent* to be used
