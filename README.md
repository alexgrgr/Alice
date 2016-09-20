
#How to Provide Replies about some data on Smartsheet using Api.ai Webhook

This example shows how you can use `Api.ai webhook` to provide information
allocated at [Smartsheet] (https://smartsheet.com)
At the actual stage, it will only search for a phrase starting with **_Empleado_**
 and retrieve only the cell on the same row and contiguous cell.
**Note**:*Smartsheet Access Token will need to be created at Personal Settings->
 API Access on Smartsheet Website*

#How to Provide Replies including some data residing on Smartsheet, using Api.ai Webhook

This example demonstrates how easily you can use `Api.ai webhook` to provide information allocated at [Smartsheet] (https://smartsheet.com). At the actual stage, it will only search for a phrase starting with **_Empleado_** and retrieve only the cell on the same row and contiguous cell.

Please, come back often, as it will be heavily updated next days. A changelog will be provided with instructions to make your deployment work.

**Note**:*Smartsheet Access Token will need to be created at Personal Settings-> API Access on Smartsheet Website. Then it must be uploaded to Heroku as an enviroment variable: `Variable: SMARTSHEET_ACCESS_TOKEN    Value= [YOUR_TOKEN]`*

# Deploy it to Heroku:

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
Deploy it now to heroku

In order to connect *api.ai* webhook, URL is
`https://[yourappname].herokuapp.com/webhook`

An intent with **webhook enabled** is needed, and `action` to be one of the
following:\n
\t`search.employee`: it will search for an employee. Just an example.
\t`search.pam`: it will verify the person asking is authorized to now that data.
Then, his/her PAM will be searched on Smartsheet. Finally, the bot will announce on the group asked that it is a sensitive data and that it will tell the partner in a 1-to-1 room.
\t`add.sparkclinic`: partner will be added to the room he asked to be in.
