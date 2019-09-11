

# encoding: utf-8
#
#   Task worker - design 2
#   Adds pub-sub flow to receive and respond to kill signal
#
#   Author: Jeremy Avnet (brainsik) <spork(dash)zmq(at)theory(dot)org>
#

import sys
import time
import zmq
import string
import random
import hashlib

def hashString(s):
    sha = hashlib.sha256()
    sha.update(s.encode('ascii'))
    return sha.hexdigest()

def generation(challenge, size = 25):
    answer = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                      for x in range(size))
    attempt = challenge + answer
    return attempt, answer

def proofOfWork(challenge):
    found = False
    attempts = 0
    while not found:
        attempt, answer = generation(challenge, 64)

        hash = hashString(attempt)
        if hash.startswith('0000'):
            found = True
            print(hash)
        attempts += 1
    print("numero de intentos =>",attempts)
    return answer

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://localhost:5557")

# Socket to send messages to
sender = context.socket(zmq.PUSH)
sender.connect("tcp://localhost:5558")

# Socket for control input
controller = context.socket(zmq.SUB)
controller.connect("tcp://localhost:5559")
controller.setsockopt(zmq.SUBSCRIBE, b"")

# Process messages from receiver and controller
poller = zmq.Poller()
poller.register(receiver, zmq.POLLIN)
poller.register(controller, zmq.POLLIN)
# Process messages from both sockets

found = False

while not found:
    socks = dict(poller.poll())
    time.sleep(1)

    # Any waiting controller command acts as 'KILL'
    if socks.get(controller) == zmq.POLLIN:
        message = controller.recv_string()
        print(message)
        found = True
        #break

    # Any waiting controller command acts as 'KILL'
    elif socks.get(receiver) == zmq.POLLIN:
        message = receiver.recv_string()

        # Process task
        challenge = message  # Workload

        # Do the work
        answer =proofOfWork(challenge)

        # Send results to sink
        sender.send_string(answer)
