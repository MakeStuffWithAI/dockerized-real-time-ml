# We now need the json library so we can load and export json data
# import json
import os
import numpy as np
import pandas as pd
from joblib import load
from sklearn import preprocessing

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Set environnment variables
MODEL_DIR = os.environ["MODEL_DIR"]
MODEL_FILE_LR = os.environ["MODEL_FILE_LR"]
MODEL_PATH_LR = os.path.join(MODEL_DIR, MODEL_FILE_LR)
UPDATE_INTERVAL = int(os.environ["UPDATE_INTERVAL"])
RETRAIN_INTERVAL = int(os.environ["RETRAIN_INTERVAL"])


#Set up logging, force it to stdout
import sys
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# Loading lr model
app = Flask(__name__)
app.logger.debug("Loading model from: {}".format(MODEL_PATH_LR))
lr = load(MODEL_PATH_LR)

@app.route('/retrain', methods=['POST','GET'])
def retrain():
    app.logger.debug("Retraining...")
    import train
    score = train.train()
    lr = load(MODEL_PATH_LR)
    return f"{score:0.4f}"

@app.route('/update', methods=['POST','GET'])
def update():
    app.logger.debug("Updating...")
    ##This function just updates the training CSV
    ##  with the latest data
    json_ = fetch()
    data = json_['data'][0]
    time_string = data['from']
    forecast = data['intensity']['forecast']
    actual = data['intensity']['actual']
    index = data['intensity']['index']
    line = [time_string,actual,forecast,index]
    from csv import writer
    with open('carbon.csv', 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(line)
        app.logger.debug("added\n {}".format(line))
    f_object.close()
    return "added\n {}".format(line)

@app.route('/predict/<int:forecast>', methods=['POST','GET'])
def predict(forecast,actual=0):
    if actual == 0:
        actual = forecast

    if lr:
            try:
                d = {"forecast": [forecast]}
                frame = pd.DataFrame(d)
                prediction = lr.predict(frame)
                return "Prediction {} . Actual {}, PercentErr {}%".format(prediction, actual, (np.abs(actual - prediction )/ prediction))


                prediction = list(lr.predict(query))
                return prediction
                # return jsonify({'prediction': str(prediction)})
            except Exception as e:
                return "{}".format(e)
    else:
        return ('Missing Model')

@app.route('/predict/latest', methods=['POST','GET'])
def predict_latest():
    json_ = fetch()
    forecast = json_['data'][0]['intensity']['forecast']
    actual = json_['data'][0]['intensity']['actual']
    # d = {"forecast": [forecast],"actual":[actual]}
    d = {"forecast": [forecast]}

    if lr:
        try:
            json_ = fetch()
            forecast = json_['data'][0]['intensity']['forecast']
            actual = json_['data'][0]['intensity']['actual']
            # d = {"forecast": [forecast],"actual":[actual]}
            d = {"actual": [actual]}
            frame = pd.DataFrame(d)
            prediction = lr.predict(frame)
            return "Prediction {} . Actual {}, PercentErr {}%".format(prediction, actual, (np.abs(actual - prediction )/ prediction))


            prediction = list(lr.predict(query))
            return prediction
            # return jsonify({'prediction': str(prediction)})
        except Exception as e:
            return "{}".format(e)
    else:
        return ('Missing Model')

@app.route('/fetch',methods=['POST', 'GET'])
def fetch():
    import requests
    from csv import writer
    r = requests.get('https://api.carbonintensity.org.uk/intensity')
    data = r.json()
    return data

def scheduled_update():
    app.logger.debug("updating")
    update()
if __name__ == "__main__":
    #setup scheduler
    app.logger.debug("Updating every {} minute(s)".format(UPDATE_INTERVAL))
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(scheduled_update,'interval',minutes=UPDATE_INTERVAL)
    sched.start()
    app.logger.debug("Retraining every {} minute(s)".format(RETRAIN_INTERVAL))
    sched2 = BackgroundScheduler(daemon=True)
    sched2.add_job(retrain,'interval',minutes=RETRAIN_INTERVAL)
    sched2.start()
    app.run(debug=True, host='0.0.0.0')

