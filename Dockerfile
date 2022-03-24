FROM jupyter/scipy-notebook
USER root
RUN mkdir /home/jovyan/my-model
RUN useradd -ms /bin/bash joyvan
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt 

COPY train.py ./train.py
COPY carbon.csv ./carbon.csv

USER root
RUN chown -R joyvan:joyvan /home/jovyan
RUN chmod -R 777 /home/jovyan/

USER joyvan
ENV MODEL_DIR=/home/jovyan/my-model
ENV MODEL_FILE_LR=clf_lr.joblib
ENV TDATA_FILE=carbon.csv
ENV ARRAY_SIZE=500
ENV UPDATE_INTERVAL=1
ENV RETRAIN_INTERVAL=2

RUN python3 train.py
COPY api.py ./api.py

EXPOSE 5000
USER joyvan

CMD ["/home/jovyan/api.py"]
ENTRYPOINT ["python"]