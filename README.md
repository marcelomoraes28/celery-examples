# Celery POC examples

This project is intended to demonstrate how to use celery and a some examples of how to prevent failover.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine also execute each steps.

### Prerequisites

* Python 2
* [Redis](https://redis.io/)
* [Virtualenv](https://virtualenv.pypa.io/en/latest/)


### Installing

Creating the venv and activating
``` shell
virtualenv venv -p python2
source venv/bin/activate
```
Installing the python dependencies
``` shell
pip install -r requirements.txt
```

If you are running redis in different server/port, update the celeryconfig.py module with your configurations.

### Run Flower

Running a flower in a port 5555
``` shell
flower -A tasks --port=5555
```

### First Story

In a Galaxy far far away the war has begun. Princess Leia must send an urgent message for everyone in your transmission list, but her system must follow a few rules:
* The system must try to transmit the message at least 5 times, this will be safer to prevent another malicious person from capturing the message
* If the transmission fails, then try again in every 5 seconds + the retry number, let's suppose it is the third time the system is trying to transmit the message then the delay of the new attempt will be 5 * 3 = 15 seconds
* Since the war, many of Leia's allies have become evil then these people must not receive the transmission

![alt text](starwars.jpg)
#### Run

Start celery with 4 workers for starwars queue
```
celery -A tasks worker -Q starwars --loglevel=info --concurrency=4
```

In another terminal, open the python console and run the task
```python
import tasks
# Calling the task to start the transmission
tasks.story_1_send_messages.delay()
```

### Second Story

Nostromo spaceship has discovered a kind of S.O.S signal coming from nearby moon LV-426, They have founded in there a kind of eggs alien that infect Kane with a parasite. Now Nostromo needs to transmit an urgent message to earth about this event. The message is a binary sequence and each sequence must be send separately following these rules:
* The system must try to transmit the message at least 5 times;
* If the transmission fails, then try again in every 5 seconds + the retry number, and if the transmission fails more than 5 times then save the message into a log file into the transmissions_fails folder to be retransmitted;
* The system must create one file log in transmission_fails for each payload;
* The system must provided a schedule task that runs every 3 minutes searching the logs into transmission_fails folder to try to transmit again;
* If the transmission was successful then save the payload into a transmission_success folder.
* For each run of story_2_send_messages the system must create only one success log file into transmission_success and append each payload separate by \n

![alt text](alien.jpg)

#### Run

Start celery with 4 workers for alien queue and beat
```
celery -A tasks worker -Q alien --loglevel=info --concurrency=4 --beat
```

In another terminal, open the python console and run the task
```python
import tasks
# Calling the task to start the transmission
tasks.story_2_send_messages.delay()
```
