import zmq
import random
import time
import sys

context = zmq.Context()

# socket with workers
workers = context.socket(zmq.PUSH)
workers.bind("tcp://*:5557")

# socket with sink
sink = context.socket(zmq.PUSH)
sink.connect("tcp://localhost:5558")


print("Press enter when workers are ready...")
_ = input()
print("sending tasks to workers")

sink.send(b'0')

#random.seed()

totalTime = 0

# for task in range(100):
#     workload = random.randint(1,100)
#     totalTime += workload
#     workers.send_string(u'%i' % workload)

for task in range(int(sys.argv[2])):
    workers.send_string('hola mundo')


workers.close()
sink.close()
context.term()
