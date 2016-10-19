import sys
import os
import time
import queue

DB = 1

class process:
    def __init__(self,name,at,cbt,nb,io):
        #name, arrival time, cpu burst time, number of bursts, io burst time
        self.name = name
        self.arrivalTime = at
        self.CPUBurst = cbt
        self.remainingBurstTime = cbt
        self.numBursts = nb
        self.IOBurst = io
        self.status = "None"
        self.Completed = False
        self.completedTime = -1
        self.nIE = 0        #next Interesting Event

    def __str__(self):
        outputStr = ''
        outputStr += "Process " + str(self.name) + ":"
        outputStr += "\n\tArrival Time: " + str(self.arrivalTime)
        outputStr += "\n\tCPU Burst Time: " + str(self.CPUBurst)
        outputStr += "\n\tNumber of Bursts: " + str(self.numBursts)
        outputStr += "\n\tIO Burst Time: " + str(self.IOBurst)
        return outputStr

    def complete(self,time):
        self.completed = True
        self.completedTime = time

    def preempt(self,timeLeft):
        self.remainingBurstTime = timeLeft
        self.status = "ready"

    def getName(self):
        return self.name

    def getArrivalTime(self):
        return self.arrivalTime

    def getCPUBurstTime(self):
        return self.CPUBurst

    def getRemainingBurstTime(self):
        return self.remainingBurstTime

    def getNumBursts(self):
        return self.numBursts

    def getIOBurstTime(self):
        return self.IOBurst

    def completed(self):
        return self.Completed

    def completionTime(self):
        return self.completedTime

    def getStatus(self):
        return self.status

    def block(self):
        self.status = "blocked"

    def run(self):
        self.status = "running"

    def ready(self):
        self.status = "ready"

    def __lt__(self,other):
        return self.arrivalTime < other.arrivalTime



def processFile(fn):
    #this function takes a filename and returns a list of processes parsed from the file, sorted by arrival time
    processes = []
    try:
        f = open(fn)
    except OSError:
        #file did not open correctly
        sys.stderr.write("ERROR: invalid input file format\n")
        sys.exit()
    i = 0 #line number
    for line in f:
        i += 1
        if line.startswith('#'):
            #ignore comments
            continue
        elif line.strip() == '':
            #ignore empty lines
            continue
        else:
            #split a valid line by the '|' delimiter and create a process from it
            line = line.split('|')
            if len(line) != 5:
                if DB == 1:
                    sys.exit("ERROR: invalid input file format: line " + str(i) + " does not have the correct number of arguments. Exiting...")
                else:
                    sys.stderr.write("ERROR: invalid input file format\n")
                    sys.exit()
            processes.append(process(line[0], line[1], line[2], line[3], line[4]))
            # line[0] - Process Name
            # line[1] - Initial arrival time
            # line[2] - CPU Burst Time
            # line[3] - Number of Bursts
            # line[4] - io Time
            #print(processes[len(processes)-1])
    
    return processes

def statsOutput(statList, of, appending=False):
    if appending:
        f = open(of, 'a')
    else:
        f = open(of, 'w')
    f.write("Algorithm " + statList[0] + "\n")
    f.write("-- average CPU burst time: " + str(statList[1]) + " ms\n")
    f.write("-- average wait time: " + str(statList[2]) + " ms\n")
    f.write("-- average turnaround time: " + str(statList[3]) + " ms\n")
    f.write("-- total number of context switches: " + str(statList[4]) + "\n")
    f.write("-- total number of preemptions: " + str(statList[5]) + "\n")

def pReadyQueue(queue):
    queueString = '[Q'
    # empty queue
    if len(queue) == 0:
        queueString += ' empty'
    # otherwise fill in process names
    else:
        for x in range(len(queue)):
            queueString += ' '
            queueString += queue[x][0].getName()

    return queueString + ']'

def RoundRobin(processList, m, t_slice=84, t_cs=8):
    #given a process list, do the RR algorithm and return the 5 needed output stats
    
    # Initialize queues to use
    readyq = []     #ready queue
    runq = []       #running queue (processes running) tuple with (process, time execution started)
    blockq = []        #blocked queue (processes performing io)
    sorted(processList, key=lambda p:p.getArrivalTime())

    numprocs = len(processList)
    plistidx = 0
    time = 0

    AvgCPUBurst = 0
    AvgWait = 0
    AvgTurnaround = 0
    numContextSwitches = 0
    numPreemptions = 0

    running = 1
    sliceend = sys.maxsize
    burstend = sys.maxsize
    cswitchend = sys.maxsize
    blockend = []

    print('time {0:d}ms: Simulator started for RR {1}'.format(time, pReadyQueue(readyq)))
    # Loop for cpu simulation
    while running:
        # If arrival time for the next process, add it to the ready queue
        nextproc = processList[plistidx]
        if int(nextproc.getArrivalTime()) == time:
            readyq.append((nextproc,time))
            plistidx += 1

            print('time {0:d}ms: Process {1} arrived {2}'.format(time, nextproc.getName(), pReadyQueue(readyq)))

        # Determine state for completing the simulation
        if len(readyq) == 0 and len(runq) == 0 and plistidx >= numprocs - 1:
            running = 0
            break


        # If time for a context switch
        if time == cswitchend:
            runq.append((readyq.pop(0)[0],time))
            sliceend = time + t_slice
            burstend = time + int(runq[0][0].getRemainingBurstTime())

            print('time {0:d}ms: Process {1} started using the CPU {2}'.format(time, runq[len(runq)-1][0].getName(), pReadyQueue(readyq)))

            # Reset the variable
            cswitchend = sys.maxsize

        else:
            # If run queue empty add process from ready queue
            if len(runq) < m:
                runq.append((readyq.pop(0)[0],time))
                sliceend = time + t_slice
                burstend = time + int(runq[0][0].getRemainingBurstTime())

                print('time {0:d}ms: Process {1} started using the CPU {2}'.format(time, runq[len(runq)-1][0].getName(), pReadyQueue(readyq)))

            # If time for burst to finish
            if time == burstend:
                # Remove from running queue
                done = runq.pop(0)[0]
                done.numBursts = int(done.numBursts) - 1
                done.remainingBurstTime = done.getCPUBurstTime()

                print('time {0:d}ms: Process {1} completed CPU burst; {2:d} to go {3}'.format(time, done.getName(),
                    int(done.numBursts), pReadyQueue(readyq)))

                # Add to blocked queue
                blockq.append(done)
                blockend.append(time + int(done.getIOBurstTime()))

                print('time {0:d}ms: Process {1} blocked on I/O until time {2:d}ms {3}'.format(time, done.getName(),
                    time + int(done.getIOBurstTime()), pReadyQueue(readyq)))

                # Reset running variables
                sliceend = sys.maxsize
                burstend = sys.maxsize
                
                # Context switch time if waiting process
                if len(readyq) > 0:
                    cswitchend = time + t_cs

            # If time for a preemption
            elif time == sliceend:
                if len(readyq) > 0:
                    # Remove from running queue
                    done = runq.pop(0)
                    done[0].preempt(str(int(done[0].getRemainingBurstTime()) - time - done[1]))

                    # Add to ready queue
                    readyq.append((done[0],time))

                    print('time {0:d}ms: Time slice expired; process {1} preempted with {2:d}ms to go {3}'.format(time, 
                        done[0].getName(), int(done[0].getRemainingBurstTime()), pReadyQueue(readyq)))

                    # Reset running variables
                    sliceend = sys.maxsize
                    burstend = sys.maxsize
                    cswitchend = time + t_cs
                else:
                    print('time {0:d}ms: Time slice expired; no preemption because ready queue is empty {1}'.format(time, pReadyQueue(readyq)))

            # If time to return from being blocked
            if len(blockend) > 0 and time == min(blockend, key=int):
                # Number of processes finished with io
                n = blockend.count(time)
                for x in range(n):
                    i = blockend.index(time)
                    blockend.pop(i)

                    done = blockq.pop(i)
                    if int(done.numBursts) <= 0:
                        done.complete(time)

                        print('time {0:d}ms: Process {1} terminated {2}'.format(time, done.getName(), pReadyQueue(readyq)))
                    else:
                        readyq.append(done,time)

                        print('time {0:d}ms: Process {1} completed I/O {2}'.format(time, done.getName(), pReadyQueue(readyq)))


        # Determine the next significant time
        nextevent = sys.maxsize

        # Time of next process arrival
        if plistidx < numprocs - 1:
            nextevent = int(processList[plistidx].getArrivalTime())
        # Time for context switch
        if cswitchend < nextevent:
            nextevent = cswitchend
        # Time for end of slice
        if sliceend < nextevent:
            nextevent = sliceend
        # Time for end of burst
        if burstend < nextevent:
            nextevent = burstend
        # Time for return from block
        if len(blockq) > 0 and min(blockend, key=int) < nextevent:
            nextevent = min(blockend, key=int)

        time = nextevent

    print('time {0:d}ms: Simulator ended for RR'.format(time))

    return ["RR",AvgCPUBurst, AvgWait,AvgTurnaround,numContextSwitches,numPreemptions];

def FCFS(processList):
    #given a process list, do the FCFS algorithm and return the 5 needed output stats
    #create FIFO queue
    sorted(processList, key=lambda p:p.getArrivalTime())

    processQueue = queue.Queue()
    outputstr = ""
    for p in processList:
        processQueue.put(p)
        outputstr += p.getName() + " "
        print("["+outputstr[:-1]+"]")
    print("["+outputstr[:-1]+"]")



    return ["FCFS",AvgCPUBurst, AvgWait,AvgTurnaround,numContextSwitches,numPreemptions];

def print_queue(queue):
    
    # empty queue
    if len(queue) == 0:
        return "empty"
    
    # otherwise fill in process names
    x = 0;
    queueString = ''
    while x < len(queue):
        if x < len(queue) - 1:
            queueString += str(queue[x].name)+' '
        else:
            queueString += str(queue[x].name)
        x+=1

    return queueString

def SJF(processList):
    #given a process list, do the SJF algorithm and return the 5 needed output stats
 
	#Sort by smallest CPU burst to largest
	#Service time = Time elapsed from beginning until current period
	#Wait time = Service time - Arrival time

	# Petey Ko

	# Initialize variables
	live = True		# For simulation status
	time = 0 		# Elapsed in milliseconds
	completed = 0	# Number of processes completely finished
	burstCount = 0	# Number of total bursts 
	enter = 0

	AvgCPUBurst = 0
	AvgWait = 0
	AvgTurnaround = 0

	# Sort SJF list by CPU Burst length
	#cpuQueue = sorted(processList,key=lambda x: int(x.CPUBurst))
	cpuQueue = []
	runningQueue = []
	ioQueue = []
	endLength = len(processList)


	# Start simulation
	print("time %sms: Simulator started for SJF [Q %s]" % (time, print_queue(cpuQueue)))

	# Sim Loop
	while live:
		# start processing into cpuQueue based on arrival time
		if enter < len(processList):
			for i in range(len(processList)):
				# Check for uninitilaized process
				if (processList[i].status == "None") and (int(processList[i].arrivalTime) <= time):
					# Add process and resort queue for SJF
					processList[i].ready()
					cpuQueue.append(processList[i])
					cpuQueue = sorted(cpuQueue,key=lambda x: int(x.CPUBurst))
					print("time %sms: Process %s arrived [Q %s]" %(time, processList[i].name, print_queue(cpuQueue)))
					enter += 1
				elif (processList[i].status == "None"):
					processList[i].nIE = processList[i].arrivalTime
		# end processing into cpuQueue

		# start io -> cpuQueue
		for i in range(len(ioQueue)):
			# move valid IO into CPU
			if int(ioQueue[i].nIE) < time:
				ioQueue[i].ready()
				cpuQueue.append(ioQueue.pop(i))
				time -= 1
				print("time %sms: Process %s completed I/O [Q " % (time, cpuQueue[len(cpuQueue)-1].name), end='')
				cpuQueue = sorted(cpuQueue,key=lambda x: int(x.CPUBurst))
				print("%s]" %(print_queue(cpuQueue)))				
				break
		# end io -> cpuQueue

				
		# start CPUBurst
		if len(cpuQueue) > 0 and len(runningQueue) == 0:
			runningQueue.append(cpuQueue.pop(0))
			time += 4
			print ("time %sms: Process %s started using the CPU [Q %s]" %(time, runningQueue[0].name, print_queue(cpuQueue)))
			runningQueue[0].run()
			#time += int(runningQueue[0].CPUBurst)
			runningQueue[0].nIE = time + int(runningQueue[0].CPUBurst)

			# Decrement number of bursts
			runningQueue[0].numBursts = int(runningQueue[0].numBursts) - 1
		# end CPUBurst

		# start Burst completion
		if len(runningQueue) == 1 and int(runningQueue[0].numBursts) > 0 and int(runningQueue[0].nIE) <= time:
			print ("time %sms: Process %s completed a CPU burst; %s to go [Q " %(time, runningQueue[0].name, runningQueue[0].numBursts), end='')
			runningQueue[0].nIE = time + int(runningQueue[0].IOBurst)
			
			# increment averages
			burstCount += 1
			AvgCPUBurst += int(runningQueue[0].CPUBurst)

			print("%s]" %(print_queue(cpuQueue)))
			
			# Block process and send to IO Queue
			runningQueue[0].block()
			print("time %sms: Process %s blocked on I/O until time %sms [Q " % (time, runningQueue[0].name, runningQueue[0].nIE), end='')
			AvgWait += runningQueue[0].nIE - time
			print("%s]" %(print_queue(cpuQueue)))
			time += 3
			# Send process to IO
			ioQueue.append(runningQueue.pop(0))
		
		# check for remaining CPU bursts
		elif len(runningQueue) == 1 and int(runningQueue[0].numBursts) <= 0 and runningQueue[0].nIE == time:
			print ("time %sms: Process %s terminated [Q " %(time, runningQueue[0].name), end='')
			runningQueue[0].complete(time)
			AvgTurnaround += int(runningQueue[0].completedTime) - int(runningQueue[0].arrivalTime)

			# increment # of completed process chains
			completed += 1
			runningQueue.pop(0)

			print ("%s]" %(print_queue(cpuQueue)))

			# stop Sim if all completed
			if completed >= endLength:
				live = False
				time += 4
				print("time %sms: Simulator ended for SJF" % (time))
				break

			time += 3
		# end Burst completion

		time += 1
	# end Sim loop



	#----------------------------------------------------------------------
	# Calculate Averages & Statistics
	AvgCPUBurst /= burstCount
	AvgWait /= endLength
	AvgTurnaround /= endLength
	numContextSwitches = 0;
	numPreemptions = 0;

	return ["SJF",AvgCPUBurst, AvgWait,AvgTurnaround,numContextSwitches,numPreemptions];

# end SJF

if __name__ == '__main__':
	if len(sys.argv) != 3:
		sys.exit("ERROR: Invalid arguments\nUSAGE: python main.py <input-file> <stats-output-file>")
	processList = processFile(sys.argv[1]) 
	m = 1 #for future use; number of processors in use
	t_cs = 8 #time required to perform a context switch
	n = len(processList) #number of processes
	t_slice = 84
	#for i in processList:
		#print(i)
	statsOutput(["Test",1,2,3,4,5], sys.argv[2])
	statsOutput(SJF(processList), sys.argv[2])
	#FCFS(processList)
    RoundRobin(processList, m, t_slice, t_cs)

# -- average CPU burst time: ###.## ms
# -- average wait time: ###.## ms
# -- average turnaround time: ###.## ms
# -- total number of context switches: ##
# -- total number of preemptions: ##















