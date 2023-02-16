# How to run this app

First, install poetry if necessary, then init poetry so all dependencies are installed:

```{bash}
poetry init
```
Next, do this:

```{bash}
../run.sh
```

The above will:
* train (if necessary)
* build the docker image
* start up image for the app, with port 8000 mapped
* wait for the app to report healthy
* test a few endpoints
* leave the app running with logs tailing

# How to run tests
```{bash}
poetry run pytest
```
