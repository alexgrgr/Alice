#How use a Spark Bot to answer a user *natural language* question with external data

This example shows how you can use `Api.ai` and some Spark workarounds to provide
information allocated at external sources in an easy way. This information and sources are described later in [`actions`](#actions).


## Deploy now:           [![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)


>In order to connect [*api.ai*](https://docs.api.ai/docs/webhook#section-step-4 "Create an api.ai webhook") webhook, URL is
`https://[yourappname].herokuapp.com/apiai`

>In order to connect [*Spark*](https://developer.ciscospark.com/endpoint-webhooks-post.html "Create an Spark Webhook") webhook, URL is
`https://[yourappname].herokuapp.com/webhook`

An intent with **webhook enabled** is needed, and the following values for `action`:<a id="actions"></a>

+ `search.smartsheet`: it will search for a query in *Smartsheet*. Just an example of *Smartsheet´s* potential.

+ `search.pam`: it will verify the person asking is authorized to know that data.
Then, his/her PAM will be searched on Smartsheet. Finally, the bot will announce
on the group asked that it is a sensitive data and that it will tell the partner
in a 1-to-1 room. ***Not yet implemented***

+ `add.sparkclinic`: partner will be added to the room he asked to be in.

###Environmental variables
You will also need to set this *environmental variables* in [*Heroku*](https://devcenter.heroku.com/articles/config-vars#setting-up-config-vars-for-a-deployed-application "Set Env variables"):

| Variable | Value |
| --------:| :----- |
| SMARTSHEET_ACCESS_TOKEN | Your *Smartsheet*´s Token to access *API* |
| SPARK_ACCESS_TOKEN | Your bot´s Token to access *Spark* *API* |
| BOT_EMAIL | Your bot´s email to discard its own messages |

####How to get a *Token*

+ **Smartsheet**: follow steps in [Documentation](http://smartsheet-platform.github.io/api-docs/#generating-access-token "Generate Access Token")
+ **Spark**: follow steps in [Documentation->Creating a Spark Bot](https://developer.ciscospark.com/bots.html "Create Bot and Generate Access Token")
