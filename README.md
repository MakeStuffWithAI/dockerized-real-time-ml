# dockerized Real-Time ML Model (using Linear Regression) 
This container will deploy a small Linear Regression model using the 
training data in 'carbon.csv' and then regularly update itself with new data from 
the https://api.carbonintensity.org.uk/intensity API,
and retrain the model.

New data is appended to the training data csv, duplicate data is automatically dropped
and the data is reduced to the last 500 data points (or whatever the ARRAY_SIZE variable is set to).

Updates are every 30 minutes by default, and retraining is every 31 minutes by default.
You can change the Environment Variables in the Dockerfile to adjust
the UPDATE_INTERVAL and RETRAIN_INTERVAL.


## REQUIREMENTS
unix or linux OS
docker

(I used Docker version 20.10.7, build f0df350)
(I used macOS Catalina version 10.15.7)

## TO-RUN
clone the project into a local directory
navigate to that directory
```docker build -t ml-project .```
```docker run -p 5000:5000 ml-project```

## TO-DO
With some tweaking this could easily be expanded to use S3 or a database instead
of local storage, and it would be good to add some version control for models as well
the ability to still serve data while the model is re-training.

Also, right now this uses the jupyter/scipy-notebook image which is quite large. I'd like to get back down to a basic Alpine Linux container with Python