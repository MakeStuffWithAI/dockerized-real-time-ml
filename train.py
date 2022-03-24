import sys; print("Python", sys.version)
import numpy as np; print("NumPy", np.__version__)
import pandas as pd ; print("Pandas", pd.__version__)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import os 
import logging

def load_training_data_from_csv(path):
    ## This could also be expanded to load from S3 or a network location
    logging.info("Loaded from {}".format(path))
    return pd.read_csv(path)
def save_model(model,path):
    ## This just saves the model locally
    ##   this function could be easily expanded to save
    ##   to S3 or a database. Could also add some version
    ##   control here

    from joblib import dump
    dump(model, path)
    logging.info("Saved model to {}".format(path))

def save_training_data_as_csv(data,path):
    from pathlib import Path  
    filepath = Path('folder/subfolder/out.csv')  
    filepath.parent.mkdir(parents=True, exist_ok=True)  
    data.to_csv(filepath)
    logging.info("Saved data to from {}".format(path))


def train():
    
    TDATA_FILE = os.environ["TDATA_FILE"]
    MODEL_DIR = os.environ["MODEL_DIR"]
    MODEL_FILE_LR = os.environ["MODEL_FILE_LR"]
    MODEL_PATH_LR = os.path.join(MODEL_DIR, MODEL_FILE_LR)
    ARRAY_SIZE = int(os.environ["ARRAY_SIZE"])

    dataset = load_training_data_from_csv(TDATA_FILE)
    x_column_name = 'forecast'
    y_column_name = 'actual'
    dataset= dataset[[x_column_name,y_column_name]]
    #Get rid of any duplicates, especially since the update() function
    #is naieve and does not care whether it fetches duplicate data
    dataset.drop_duplicates()
    #get the last 500 elements of the array (assuming ARRAY_SIZE is 500)
    dataset = dataset[-ARRAY_SIZE:]
    x_label=np.array(dataset[x_column_name]).reshape(ARRAY_SIZE,1)
    y_label=np.array(dataset[y_column_name]).reshape(ARRAY_SIZE,1)
    x_train, x_test, y_train, y_test = train_test_split(x_label, y_label, test_size = 0.2, random_state = 100)
    regression_model=LinearRegression()
    regression_model.fit(x_train,y_train)
    r_sq = regression_model.score(x_train, y_train)

    #saving model and training data
    save_model(regression_model,MODEL_PATH_LR)
    save_training_data_as_csv(dataset,TDATA_FILE)

    return r_sq
        
if __name__ == '__main__':
    train()
