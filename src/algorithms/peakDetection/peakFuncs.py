import math

from infra.queue import Queue
from infra.simpleDataStructure import Sds
from infra.workerThread import WorkerThread


class PeakScorer(WorkerThread):

    def passThrough(self):
        while self.active:
            if not self.inputQueue.isEmpty():

                # Get next data point
                dp = self.inputQueue.dequeue()

                if dp == 'end':
                    self.completed = True
                    self.active = False
                    self.outputQueue.enqueue('end')
                    return

                self.data.append(dp)
                self.outputQueue.enqueue(dp)

    def maxDiff(self):
        while self.active:
            if not self.inputQueue.isEmpty():

                # Get next data point
                dp = self.inputQueue.dequeue()

                # Special case handling for end data point.
                if dp == 'end':
                    self.completed = True
                    self.active = False
                    self.outputQueue.enqueue('end')
                    return

                # Add data point to list and queue
                self.data.append(dp)
                self.window.enqueue(dp)

                # Once we reach the window size, do some processing!
                if len(self.window) == self.windowSize:

                    # Calculate peak score
                    midPoint = int(self.windowSize / 2)
                    maxDiffLeft = -100
                    maxDiffRight = -100

                    # Find max difference on left
                    for i in range(0, midPoint):
                        value = self.window[midPoint].mag - self.window[i].mag
                        if value > maxDiffLeft:
                            maxDiffLeft = value

                    # Find max difference on right
                    for i in range(midPoint + 1, len(self.window)):
                        value = self.window[midPoint].mag - self.window[i].mag
                        if value > maxDiffRight:
                            maxDiffRight = value

                    # Calculate peak score and create a new point
                    avg = (maxDiffRight + maxDiffLeft) / 2
                    new_dp = Sds(self.window[midPoint].time, avg, self.window[midPoint].mag)
                    self.outputQueue.enqueue(new_dp)
                    self.window.dequeue()

    def meanDiff(self):
        while self.active:
            if not self.inputQueue.isEmpty():

                # Get next data point
                dp = self.inputQueue.dequeue()

                # Special case handling for end data point.
                if dp == 'end':
                    self.completed = True
                    self.active = False
                    self.outputQueue.enqueue('end')
                    return

                # Add data point to list and queue
                self.data.append(dp)
                self.window.enqueue(dp)

                # Once we reach the window size, do some processing!
                if len(self.window) == self.windowSize:

                    # Calculate peak score
                    midPoint = int(self.windowSize / 2)
                    diffLeft = 0
                    diffRight = 0

                    # Find total difference on left
                    for i in range(0, midPoint):
                        value = self.window[midPoint].mag - self.window[i].mag
                        diffLeft += value

                    # Find total difference on right
                    for i in range(midPoint + 1, len(self.window)):
                        value = self.window[midPoint].mag - self.window[i].mag
                        diffRight += value

                    # Calculate peak score and create a new point
                    avg = (diffLeft + diffRight) / (self.windowSize - 1)
                    new_dp = Sds(self.window[midPoint].time, avg, self.window[midPoint].mag)
                    self.outputQueue.enqueue(new_dp)
                    self.window.dequeue()


    def panTompkins(self):
        while self.active:
            if not self.inputQueue.isEmpty():

                # Get next data point
                dp = self.inputQueue.dequeue()

                # Special case handling for end data point.
                if dp == 'end':
                    self.completed = True
                    self.active = False
                    self.outputQueue.enqueue('end')
                    return

                # Add data point to list and queue
                self.data.append(dp)
                self.window.enqueue(dp)

                # Once we reach the window size, do some processing!
                if len(self.window) == self.windowSize:

                    midPoint = int(self.windowSize / 2)

                    # Calculate mean of window
                    ssum = 0
                    for i in range(0,self.windowSize):
                        ssum += self.window[i].mag
                    mean = ssum / self.windowSize

                    new_mag = 0 if self.window[midPoint].mag - mean < 0 else self.window[midPoint].mag - mean
                    # Square it.
                    new_mag *= new_mag

                    # Calculate peak score and create a new point
                    new_dp = Sds(self.window[midPoint].time, new_mag, self.window[midPoint].mag)
                    self.outputQueue.enqueue(new_dp)
                    self.window.dequeue()

    # Constructor for the object
    # @args:
    #   1. params - dictionary containing relevant parameters
    #       a. 'window_size' - size of the window for maxDiff
    #       b. 'type' - the type of scorer to use
    #   2. smoothData - queue containing smoothed data
    #   3. smoothDataList - list containing smoothed data
    #   4. peakScores - queue containing peak scores data
    def __init__(self, params, smoothData, smoothDataList, peakScores):

        super(PeakScorer, self).__init__()

        # Internal references for smooth data
        self.inputQueue = smoothData
        self.data = smoothDataList
        self.outputQueue = peakScores

        # Internal window
        self.window = Queue()

        # Parameter unpacking
        self.windowSize = params['window_size']
        self.typ = params['type']

        # Assign target
        if self.typ == 'max_diff':
            self.target = self.maxDiff
        elif self.typ == 'mean_diff':
            self.target = self.meanDiff
        elif self.typ == 'pan_tompkins':
            self.target = self.panTompkins
        elif self.typ == 'pass_through':
            self.target = self.passThrough
        else:
            raise Exception('Unknown peak scorer type: ' + self.typ)


