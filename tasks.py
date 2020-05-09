#!/usr/bin/python

from __future__ import absolute_import

import logging
import os
import time
import random
from datetime import datetime
from os import listdir
from os.path import isfile, join
from celery.exceptions import Reject
from celery import Celery
from celery.signals import task_failure

import celeryconfig

# Celery Setup
app = Celery()
app.config_from_object(celeryconfig)

# Log Setup
logger = logging.getLogger(__name__)


###############
# STORY 1
################
# Defining the exceptions
class BlackList(Exception):
    pass


class TransmissionFail(Exception):
    pass


TRANSMISSION_LIST = ('padme-amidala',
                     'anakin-skywalker',
                     'luke-skywalker',
                     'chewbacca',
                     'r2',
                     'qui-gon',
                     'obi-wa',
                     'yoda')


@app.task(bind=True, name='story_1_transmit_message', retry_kwargs={'max_retries': 5}, acks_late=True)
def story_1_transmit_message(self, _from, to, subject, message):
    """
    Task used to transmit the message
    """
    logger.info("Transmitting message to %s" % to)
    try:
        # Delay for 2 seconds to simulate the transmission
        time.sleep(2)
        # Simulating success and fail
        success = random.randint(0, 1)
        black_list = random.randint(0, 1)
        # End Simulation

        # If the person is on black list raise an exception
        if black_list:
            raise BlackList("This person %s is banned" % to)
        # If the transmission failed, raise an exception
        if not success:
            raise TransmissionFail("Transmission fail")
    except BlackList as exc:
        # If that person is on blacklist then cancel the transmission for it
        logger.error(str(exc))
        raise Reject(exc, requeue=False)
    except TransmissionFail as exc:
        # If the transmission has failed for some reason then let's retry
        retry_time = 5 * (story_1_transmit_message.request.retries or 1)
        logger.info("Message transmission failed, trying to send again to %s in %s seconds" % (to, str(retry_time)))  # noqa
        self.retry(exc=exc, countdown=retry_time)
    else:
        logger.info("Message to %s has been transmitted" % to)


@app.task(bind=True, name='story_1_send_messages')
def story_1_send_messages(self):
    """
    Task used to trigger the transmission task (story_1_transmit_message)
    for each recipient
    """
    logger.info("Starting message transmission")
    for person in TRANSMISSION_LIST:
        body = "Hey, Naboo Royal Cruiser is calling you!!"
        subject = "Urgent message from Naboo Royal"
        _from = "princess-leia"
        story_1_transmit_message.delay(_from, person, subject, body)

###############
# END STORY 1
################

###############
# END STORY 2
################


BINARY_SEQUENCE = {0: 01010111,
                   1: 01100101,
                   2: 00100000,
                   3: 01100110,
                   4: 01101111,
                   5: 01110101,
                   6: 01101110,
                   7: 01100100,
                   8: 00100000,
                   9: 01100001,
                   10: 01101110,
                   11: 00100000,
                   12: 01100001,
                   13: 01101100,
                   14: 01101001,
                   15: 01100101,
                   16: 01101110,
                   17: 00101100,
                   18: 00100000,
                   19: 01110111,
                   20: 01100101,
                   21: 00100000,
                   22: 01101110,
                   23: 01100101,
                   24: 01100101,
                   25: 01100100,
                   26: 00100000,
                   27: 01110101,
                   28: 01110010,
                   29: 01100111,
                   30: 01100101,
                   31: 01101110,
                   32: 01110100,
                   33: 00100000,
                   34: 01101000,
                   35: 01100101,
                   36: 01101100,
                   37: 01110000,
                   38: 00100000,
                   39: 01110100,
                   40: 01101111,
                   41: 00100000,
                   42: 01100100,
                   43: 01100101,
                   44: 01100001,
                   45: 01101100,
                   46: 00100000,
                   47: 01110111,
                   48: 01101001,
                   49: 01110100,
                   50: 01101000,
                   51: 00100000,
                   52: 01101001,
                   53: 01110100,
                   54: 00101110
                   }

FAILS_PATH_DIR = './transmission_fails/'
SUCCESS_PATH_DIR = './transmission_success/'


def generate_file_name():
    """
    Generate a filename based on the timestamp
    :return: filename following the pattern transmission_TIMESTAMP.log
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    return 'transmission_%s.log' % timestamp


def save_log(path, file_name, op, delimiter, *args):
    """
    Save a log file when each args will be converted and written into a file
    based on the delimiter
    Eg:
        INPUT: args = ('alien', 'isolation', '1')
               delimiter = '-'
        OUTPUT: alien-isolation-1

    :param path: Path dir
    :param file_name: Filename
    :param op: Operator to be used to open the file Eg 'w+', 'a'
    :param delimiter: Delimiter to join the args
    :param args: Arguments to be persisted into a file
    """
    with open("%s%s" % (path, file_name), op) as file:
        file.write(("-".join([str(arg) for arg in args])) + delimiter)


def get_files_name(path_dir):
    """
    Get all files names for a defined dir
    :param path_dir: Directory path
    :return: List of all files names
    """
    return [f for f in listdir(path_dir) if isfile(join(path_dir, f)) and 'transmission_' in f]  # noqa


def read_logs(path_dir, file_name):
    """
    Read a log file for a defined file
    The file content must follow the pattern:
        file_name-to-idx-message
    Eg:
        transmission_20200101101010.txt-earth-2-SOS
    :param path_dir: file dir
    :param file_name: filename
    :return: quadruple
    """
    with open(path_dir + file_name, 'r') as file:
        read = file.read()
        file_name, to, idx, message = read.split('-')
    return file_name, to, idx, message


# Celery signal to be dispatched when a task fails
@task_failure.connect
def task_failure_handler(sender=None, exception=None, **kwargs):
    if isinstance(exception, TransmissionFail):
        file_name = generate_file_name()
        save_log(FAILS_PATH_DIR, file_name, 'w+', '', *kwargs.get('args'))


@app.task(bind=True, name='story_2_transmit_message',
          retry_kwargs={'max_retries': 5}, acks_late=True)
def story_2_transmit_message(self, transmission_name, to, idx, message):
    """
    Task used to transmit the message
    """
    logger.info("Transmitting message to %s" % to)
    try:
        # Delay for 2 seconds to simulate the transmission
        time.sleep(2)
        # Simulating success and fail
        success = random.randint(0, 1)
        # End simulating

        # If the transmission failed, raise an exception
        if not success:
            raise TransmissionFail("Transmission fail")
    except TransmissionFail as exc:
        # If the transmission has failed for some reason then let's retry
        retry_time = 5 * (story_2_transmit_message.request.retries or 1)
        logger.info("Message transmission failed, trying to send again to %s in %s seconds" % (to, str(retry_time)))  # noqa
        self.retry(exc=exc, countdown=retry_time, throw=False)
    else:
        # If success then save the transmission into a log file
        save_log(SUCCESS_PATH_DIR, transmission_name, 'a', '\n', to, idx, message)
        logger.info("Message to %s has been transmitted" % to)


@app.task(bind=True, name='story_2_send_messages')
def story_2_send_messages(self):
    """
    Task used to trigger the transmission task (story_2_transmit_message)
    for earth receipt
    """
    logger.info("Starting message transmission")
    to = 'earth'
    transmission_name = generate_file_name()
    for idx, message in BINARY_SEQUENCE.items():
        story_2_transmit_message.delay(transmission_name, to, idx, message)


@app.task(bind=True, name='relay_messages')
def relay_messages(self):
    """
    Task to be scheduled to run from time to time
    """
    logger.info("Starting relay messages")
    files = get_files_name(FAILS_PATH_DIR)
    for file in files:
        transmission_name, to, idx, message = read_logs(FAILS_PATH_DIR, file)
        story_2_transmit_message.delay(transmission_name, to, idx, message)
        # When the transmit_message tasks was triggered then remove the file
        # from transmission_fails dir
        os.remove(FAILS_PATH_DIR + file)
