FROM python:3.8


RUN apt-get update -y --fix-missing                                                         \
    && apt-get install fluidsynth -y                                                        \
    && apt-get install sox -y        

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000

CMD ["python", "application.py"]