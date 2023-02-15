#!/bin/bash

IMAGE_NAME=lab2
APP_NAME=lab2
MODEL_FILENAME="model_pipeline.pkl"

# run the trainer if necessary
FILE=${IMAGE_NAME}/${MODEL_FILENAME}
if [ -f "$FILE" ]; then
    echo "$FILE exists, skipping training"
else 
    (cd ${IMAGE_NAME} && poetry run python ../trainer/train.py)
fi

# stop and remove image in case this script was run before
docker stop ${APP_NAME}
docker rm ${APP_NAME}

# rebuild and run the new image
docker build -t ${IMAGE_NAME} ./${APP_NAME}/
docker run -d --name ${APP_NAME} -p 8000:8000 ${IMAGE_NAME}

# wait for the /health endpoint to return a 200 and then move on
finished=false
while ! $finished; do
    health_status=$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/health")
    if [ $health_status == "200" ]; then
        finished=true
        echo "API is ready"
    else
        echo "API not responding yet"
        sleep 5
    fi
done

# check a few endpoints and their http response
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/hello?name=Winegar"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/hello?nam=Winegar"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/docs"

curl -o /dev/null -X POST "http://localhost:8000/predict/" \
   -H 'Content-Type: application/json' \
   -d '{"MedInc": 8.3252, "HouseAge": 41, "AveRooms": 6.98412698, "AveBedrms": 1.02380952, "Population": 322.0, "AveOccup": 2.55555556, "Latitude": 37.88, "Longitude": -122.23}'

# output and tail the logs for the container
docker logs -f ${APP_NAME}
