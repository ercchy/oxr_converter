# USD converter

## Intro
This is a API for a simple currency converter. It will convert anything you ask it too, to USD. Nothing more :).

### Running

#### Docker & Docker Compose
The app is encapsulated within the docker containers. This means that you have to have Docker installed.
We are ochestrating the containers with the `docker-compose`, but that comes installed with most installations of Docker.

#### Envs
Before we build containers we need to set the `.env` file. For this reason, the project has an `.env.setme` file, which needs to be renamed to just plain `.env`. Check if there is any values that needs to be updated (there shouldn't) and update them.

#### Running 
Since we haven't taken care of waiting for initializing of the database, we will first have to raise the database container alone. Do this with:

```docker-compose up --build -d db```

We have set persistency of the database set to a file on a local drive. In this way we can check if database is innitialized. If you have folder `db/data/converter` on your file structure for this project.
 
After we have initialized database, we will build and run other containers. We can do that with a simple command:

```docker-compose up --buid -d```

note: `-d` is a flag that containers are runing in daemon mode. You can turn this off, by simply not adding the flag.

### Testing

You can test this app with `curl`. 

If you wish to make an operation and save the converted data you can use:

```curl -d '{"code":"BTC", "amount":"1.66"}' -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/grab_and_save```

Where your `code` and `amount` can be changed accordingly.

Example of a `curl` call for retrieving data:
```curl -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/last?currency=BTC&records=6```

### Notes:   

* We are using Decimal type for all finacial conversions, rounded up and to precision of 8 didgits
* In production it would be better to use [flask-restplus](https://flask-restplus.readthedocs.io/en/stable/). It also provides swagger documentation.
* Getting currency catalog, would ideally be cached trough a cron job or a lambda function.
* Currency values could be refreshed trough a cron or a lambda and saved to the Redis, from where the app would then retrieve the values.


### TODOS:
[*] Write docs 
[] Write tests    
[] Resolve TODOS withing the code   
[] Make flask wait for mysql on initializing
[] Make a simple frontend app


### References:

Some things I picked up around the webs and used it
* [Flask boilerplate](https://github.com/sugud0r/flask-restful-boilerplate/tree/master/flask_api)
* [Timeout for request to external API](https://www.peterbe.com/plog/best-practice-with-retries-with-requests)
* [Documentation on the Retry class](https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#module-urllib3.util.retry)