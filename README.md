# dockercompose-http
Use-case:
Small demo instance (amazon t2.micro) hosting many infrequently and ad-hoc used projects leveraging docker-compose.
Instance is too small to run all the projects at the time. This script allows "lazy loading" of these projects and with an inactivity timeout, it makes sure they are torn down after they are not used.

## Available endpoints:

### GET / 
returns available docker-compose "projects" to spin up

### POST /start
start an available docker-compose project
```
{
    "project" : "name_of_the_project_to_spin_up",
    "timeout" : [optional]timeout in seconds (after this number of seconds inactivity the compose project is going to be stopped),
    "log_file" : [optional only with timeout]"name of the log file to output docker logs"
}
```

### POST /stop
start an available docker-compose project
```
{
    "project" : "name_of_the_project_to_stop"
}
```