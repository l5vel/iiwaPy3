# -*- coding: utf-8 -*-
"""
About the script:
An exmple on controlling KUKA iiwa robot from
Python3 using the iiwaPy3 class

Created on Tue Oct  1 11:56:31 2019
Modified on 3rd-Jan-2021

@author: Mohammad Safeea

Test script of realtime impedance mode
plot joints torques feedback while controlling the robot

"""

import math
import time
import numpy.core.multiarray

import matplotlib.pyplot as plt

from iiwaPy3 import iiwaPy3

from MATLABToolBoxStart import MATLABToolBoxStart

# KUKA iiwa robot IP and port
#KUKA_IP = "192.168.0.50"  # Replace with actual robot IP KUKA 141
KUKA_IP = "192.168.0.49"  # Replace with actual robot IP KUKA 71
KUKA_PORT = 30300 # default port, any changes should reflect in WB
# start the matlab client
wakeup = MATLABToolBoxStart(KUKA_IP,KUKA_PORT)
try:
    wakeup.start_client()
    time.sleep(2)
except Exception as e:
    print(f"Starting client failed with error message: {e}")

# Connect to the robot
try:
    iiwa = iiwaPy3(KUKA_IP)
except Exception as e:
    print(f"Client running but connection failed with error message: {e}")

def updateArrays(x, y, n, x1, y1):
    temp = n - 1
    for i in range(temp):
        y[i] = y[i + 1]
        x[i] = x[i + 1]
    x[temp] = x1
    y[temp] = y1


def updatePlot(line, fig, x, y):
    line.set_xdata(x)
    line.set_ydata(y)
    plt.axis([x[0], x[-1], -1, 1])
    fig.canvas.draw()
    fig.canvas.flush_events()

n=50
x = np.zeros(n)
y = np.sin(x)

plt.ion()

fig = plt.figure()
graph = fig.add_subplot(111)
line1, = graph.plot(x, y, 'r-') # Returns a tuple of line objects, thus the comma

# read some data from the robot
try:
    # Move to an initial position    
    jPos = [0, 0, 0, -math.pi / 2, 0, math.pi / 2, 0];
    vRel = [0.1]
    iiwa.movePTPJointSpace(jPos, vRel)
    # Motion variables
    w = 0.6  # Angular velocity of the sinusoidal motion
    theta = 0  # Motion displacement from equilibrium
    interval = 2 * math.pi  # interval of motion
    a = math.pi / 6  # Amplitude of motion
    counter = 0  # To count the number of iterations
    index = 0  # Index of the joint
    jposVec = iiwa.getJointsPos()
    j0Pos = jposVec[index]
    # Define the load data
    weightOfTool = 1.0  # 1 kg
    cOMx = 0.0
    cOMy = 0.0
    cOMz = 0.0
    # Define stiffness data
    cStiness = 900
    rStifness = 80
    nStifness = 50
    iiwa.realTime_startImpedanceJoints(weightOfTool, cOMx, cOMy, cOMz, cStiness, rStifness, nStifness)
    # some timing variables
    t0 = time.time()
    t_0 = time.time()
    while theta < interval:
        deltat = time.time() - t0
        theta = w * deltat
        jposVec[index] = j0Pos - a * (1 - math.cos(theta))
        if (time.time() - t_0) > 0.002:
            taw = iiwa.sendJointsPositionsGetMTorque(jposVec)
            print(taw)
            # print(taw)
            # y1=taw[0]
            # x1=deltat
            # updateArrays(x,y,n,x1,y1)
            updatePlot(line1,fig,x,y)
            t_0 = time.time()
            counter = counter + 1

    deltat = time.time() - t0
    iiwa.realTime_stopDirectServoJoints()
except:
    print('an error happened')

iiwa.close()
print('update freq')
print(counter / deltat)
