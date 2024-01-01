# python-slack-fr

## Introduction

This is a python service that uses the face-recognition library and the slack client library to read from specified slack channels new messages.

If a message contains an image, the service will apply the face-recognition library to check for faces in the images.
For any discovered face, the service will check a mongodb collection with saved facial embeddings for a match of the detected faces.
Faces that are matched will be reported via slack message to a different specified channel along with the name of the matched embedding drawn onto
the image and the face marked with a rectangle.

Faces that are not matched to existing embeddings will be saved into the mongodb collection and a message will be sent to the same slack channel
mentioned in the previous sentence. As in the previous case, an image will be sent with the unknown faces marked with a rectangle. 

The service admin should change the default name - "uknown" - to a designation for that embedding (ex. the name or alias of the detected face).
This can only be done by direct connection to the mongodb instance as a seperate admin interface does not exsist.

It was originally intended to be used with another application I wrote that monitors ONVIF cameras and posts motion events
with snapshots to Slack. For details, please see that project [here](https://github.com/Path-Variable/onvif-cam-poll).

## How to run

The service has a single dependency - a MongoDB database. It uses only a single collection for all operations.
If running on a Raspberry Pi 4, be aware that there are no official MongoDB images that will work. Please look for
alternate repositories or make your own MongoDB image. I am linking my own example [here](https://github.com/isaric/mongodb-raspberrypi-docker).

Using the Flask library, the service exposes a single endpoint that will accept Slack Event payloads.
It is up to the operator to make sure Slack Events are configured and routed to that service. For documentation on 
Slack Events and how to activate them, please check the relevant documentation [here](https://api.slack.com/apis/connections/events-api).
The service should be reachable from a public url over SSL.

### Environment variables

There are five environment variables that need to be specifed in order for the service to boot and work properly.

- SLACK_API_TOKEN - the bot token needed to access channels, read and post messages and media
- MONGO_CONNECTION_STRING - for connecting to the MongoDB database
- READ_SLACK_CHANNEL_ID - a comma seperated list of slack channel ids from which images should be read
- WRITE_SLACK_CHANNEL_ID - a single slack channel id to which messages from the service will be posted
- SLACK_VERIFICATION_TOKEN - the verification token that will be present on every incoming Slack Event guaranteeing its authenticity

### Docker and docker-compose

You can use the Docker image provided using the Github Container Registry in this repository. There is a seperate tag for ARM64 and AMD64
architectures. You can also use the provided dockerfiles to make your own image. The base images used are also my own compilation based on
others work.

The docker-compose file provided in the repository gives an example of how to run the service with dependencies and all of the environment
variables that need to be specified.

## Considerations

It is up to the operator to ensure compliance with local laws governing the use of facial recognition technology and personal data.

If you encounter any bugs or have changes you think would fit into this project, please file them in the Issues tab. They are welcome.
