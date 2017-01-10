# How to use a Spark Bot to answer a user´s *natural language* question with the ability to retreive data from external sources

This example shows how you can use a NLP (*Natural Language Procesor*), such as `Api.ai` and `Watson` in a near future, to provide
information allocated at external sources or stored at the NLP database, in an easy way. This information and sources are described later in [`actions`](#actions).


## Deploy now:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)


>In order to connect [*api.ai*](https://docs.api.ai/docs/webhook#section-step-4 "Create an api.ai webhook") webhook, URL is
`https://[yourappname].herokuapp.com/apiai`

>In order to connect [*Spark*](https://developer.ciscospark.com/endpoint-webhooks-post.html "Create an Spark Webhook") webhook, URL is
`https://[yourappname].herokuapp.com/webhook`

An intent with **webhook enabled** is needed, and the following values for `action`:<a id="actions"></a>

+ `search.smartsheet`: it will search for a query in *Smartsheet*. Just an example of *Smartsheet´s* potential.

+ `search.pam`: it will verify that the person asking is authorized to know that
data. Then, his/her PAM will be searched on Smartsheet. Finally, the bot will
announce on the group asked that it is a sensitive data and that it will tell
the employee in a 1-to-1 room.

+ `search.mypam`: same as `search.pam` but only to get owns PAM data. Partners will
be answered in a 1-to-1 room.

+ `search.am` : only for internal employees, it will search comercial's data for
a given customer.

+ `add.sparkclinic`: partner will be added to the room he asked to be in.

**Note**: code for smartsheet is currently adapted to use specific Sheet IDs and
rows. This will change in a future to work with any IDs.

###Environmental variables
You will also need to set this *environmental variables* in [*Heroku*](https://devcenter.heroku.com/articles/config-vars#setting-up-config-vars-for-a-deployed-application "Set Env variables"):

|                Variable | Value                                                            |
|------------------------:|:-----------------------------------------------------------------|
|      APIAI_ACCESS_TOKEN | Your *api.ai* client access Token                                |
|              APIAI_LANG | Processing language for api.ai. Default is *en*. Spanish is *es* |
|                APP_NAME | Your app´s name                                                  |
| SMARTSHEET_ACCESS_TOKEN | Your *Smartsheet*´s Token to access *API*                        |
|      SPARK_ACCESS_TOKEN | Your bot´s Token to access *Spark* *API*                         |
|               BOT_EMAIL | Your bot´s email to discard its own messages                     |

####How to get a *Token*

+ **Smartsheet**: follow steps in [Documentation](http://smartsheet-platform.github.io/api-docs/#generating-access-token "Generate Access Token")
+ **Spark**: follow steps in [Documentation->Creating a Spark Bot](https://developer.ciscospark.com/bots.html "Create Bot and Generate Access Token")

##Changelog

##### New features:
+ Distingue entre partners, empleados de Cisco y el resto del mundo
+ Uso de *Markdown* para enviar mensajes
+ Poder mandar archivos a las salas o a personas

##### Bugs fixed:
+ Eliminados problemas al responder
+ Fácil añadir funciones

##### Planned:
+ Pregunta en otra sala para proporcionar una respuesta y la aprende
+ Se pueden añadir preguntas o modificar respuestas hablando con él por Spark
+ Preguntas confidenciales responder por privado
+ Fácil futura integración con Watson
+ Posible integración con Spark Video SDK
+ Mandar emails
+ Programar el envío de recordatorios a salas o personas
+ Integración con PacoApp
+ Escuchar en salas e identificar preguntas. Pregunta en otra sala para proporcionar una respuesta y la aprende
+ Estadísticas de la sala o equipo a los moderadores (gente que no ha participado para incentivarla,...)
