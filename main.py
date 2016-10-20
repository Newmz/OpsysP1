import sys
import os
import time
import queue

DB = 1

class process:
    def __init__(self,name,at,cbt,nb,io):
        #name, arrival time, cpu burst time, number of bursts, io burst time
        self.name = name
        self.arrivalTime = int(at)
        self.CPUBurst = int(cbt)
        self.remainingBurstTime = int(cbt)
        self.numBursts = int(nb)
        self.IOBurst = int(io)
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
    f.write("-- average CPU burst time: {:005.2f} ms\n".format(statList[1]))
    f.write("-- average wait time: {:005.2f} ms\n".format(statList[2]))
    f.write("-- average turnaround time: {:005.2f} ms\n".format(statList[3]))
    f.write("-- total number of context switches: {:d}\n".format(statList[4]))
    f.write("-- total number of preemptions: {:d}\n".format(statList[5]))
    f.close()

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
    processList = sorted(processList, key=lambda p:int(p.getArrivalTime()))

    numprocs = len(processList)
    plistidx = 0
    time = 0

    AvgCPUBurst = 0.0
    AvgWait = 0.0
    AvgTurnaround = 0.0
    numContextSwitches = 0
    numPreemptions = 0

    waitTime = [0] * numprocs
    arriveTime = []
    running = 1
    sliceend = sys.maxsize
    burstend = sys.maxsize
    cswitchend = sys.maxsize
    blockend = []

    # Populate initial arrival times
    for x in processList:
        arriveTime.append(int(x.getArrivalTime()))

    # Calculate average burst time
    numbursts = 0
    for x in processList:
        AvgCPUBurst += int(x.getCPUBurstTime()) * int(x.getNumBursts())
        numbursts += int(x.getNumBursts())
    AvgCPUBurst /= numbursts


    print('time {0:d}ms: Simulator started for RR {1}'.format(time, pReadyQueue(readyq)))
    # Loop for cpu simulation
    while running:
        # If arrival time for the next process, add it to the ready queue
        if plistidx < numprocs:
            nextproc = processList[plistidx]
            if int(nextproc.getArrivalTime()) == time:
                readyq.append((nextproc,time))
                plistidx += 1
                if len(runq) == 0:
                    cswitchend = time + t_cs // 2

                print('time {0:d}ms: Process {1} arrived {2}'.format(time, nextproc.getName(), pReadyQueue(readyq)))


        # If time for a context switch
        if time == cswitchend:
            numContextSwitches += 1

            nextp = readyq.pop(0)
            runq.append((nextp[0],time))
            sliceend = time + t_slice
            burstend = time + int(runq[0][0].getRemainingBurstTime())

            # Update wait time
            waitTime[processList.index(nextp[0])] += time - nextp[1] - t_cs

            print('time {0:d}ms: Process {1} started using the CPU {2}'.format(time, runq[len(runq)-1][0].getName(), pReadyQueue(readyq)))

            # Reset the variable
            cswitchend = sys.maxsize

        else:
            # If run queue empty add process from ready queue
            if len(runq) < m and len(readyq) > 0 and cswitchend == sys.maxsize:
                runq.append((readyq.pop(0)[0],time))
                sliceend = time + t_slice
                burstend = time + int(runq[0][0].getRemainingBurstTime())

                print('time {0:d}ms: Process {1} started using the CPU {2}'.format(time, runq[len(runq)-1][0].getName(), pReadyQueue(readyq)))

            # If time for burst to finish
            if time == burstend:
                # Remove from running queue
                done = runq.pop(0)[0]
                done.numBursts = str(int(done.getNumBursts()) - 1)
                done.remainingBurstTime = done.getCPUBurstTime()

                # Add to turnaround time
                AvgTurnaround += time - arriveTime[processList.index(done)]

                # If process done
                if int(done.getNumBursts()) == 0:
                    done.complete(time)

                    print('time {0:d}ms: Process {1} terminated {2}'.format(time, done.getName(), pReadyQueue(readyq)))
                else:
                    print('time {0:d}ms: Process {1} completed a CPU burst; {2:d} to go {3}'.format(time, done.getName(),
                        int(done.getNumBursts()), pReadyQueue(readyq)))

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
                    numPreemptions += 1
                    # Remove from running queue
                    done = runq.pop(0)
                    done[0].preempt(str(int(done[0].getRemainingBurstTime()) - time + done[1]))

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

                    # Reset running variables
                    sliceend = time + t_slice

            # If time to return from being blocked
            if len(blockend) > 0 and time == min(blockend, key=int):
                # Number of processes finished with io
                n = blockend.count(time)
                for x in range(n):
                    i = blockend.index(time)
                    blockend.pop(i)

                    done = blockq.pop(i)
                    readyq.append((done,time))

                    # Udate arrival time for new burst
                    arriveTime[processList.index(done)] = time

                    print('time {0:d}ms: Process {1} completed I/O {2}'.format(time, done.getName(), pReadyQueue(readyq)))

        # For when there's a process that needs to switch in
        if len(runq) == 0 and len(readyq) > 0 and cswitchend == sys.maxsize:
            cswitchend = time + t_cs // 2
            waitTime[processList.index(readyq[0][0])] += t_cs // 2


        # Determine the next significant time
        nextevent = sys.maxsize

        # Time of next process arrival
        if plistidx < numprocs:
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

        # Determine state for completing the simulation
        if len(readyq) == 0 and len(runq) == 0 and plistidx >= numprocs - 1 and len(blockq) == 0:
            time += t_cs // 2
            running = 0
        else:
            time = nextevent


    # Calculate average wait time
    for x in waitTime:
        AvgWait += x
    AvgWait /= numbursts
    # Calulate average turnaround time
    AvgTurnaround /= numbursts

    print('time {0:d}ms: Simulator ended for RR'.format(time))

    return ["RR",AvgCPUBurst, AvgWait,AvgTurnaround,numContextSwitches,numPreemptions];

def FCFS(processList):
    #given a process list, do the FCFS algorithm and return the 5 needed output stats
    #create FIFO queue
    sorted(processList, key=lambda p:p.getArrivalTime())

    running = True
    time = 0
    finished = 0
    burstTotal = 0

    CPUQ = []
    IOQ = []        
    RunningQ = []  
    QAT = [] #QUEUE ARRIVAL TIME
    AvgWait = 0
    AvgCPUBurst = 0
    totalBursts = 0
    for p in processList:
        print(p.numBursts)
        for i in range(0, int(p.numBursts)):
            AvgCPUBurst += p.CPUBurst
            totalBursts += 1
    AvgCPUBurst /= totalBursts
    AvgTurnaround = 0

    numContextSwitches = 0
    numPreemptions = 0

    # Start simulation
    print("time %sms: Simulator started for FCFS [Q %s]" % (time, print_queue(CPUQ)))

    while running:
        #if any newly arrived processes need to be added, do so
        for p in processList:
            if p.getStatus() == "None" and p.getArrivalTime() <= time:
                p.ready()
                CPUQ.append(p)
                QAT.append(time)
                print("time %sms: Process %s arrived [Q %s]" %(time, p.name, print_queue(CPUQ)))
            elif p.getStatus() == "None":
                p.nIE = p.getArrivalTime()

        #if a process has finished IO and has more CPU Bursts, re-add it to the queue
        for p in IOQ:
            if p.nIE < time:
                p.ready()
                CPUQ.append(p)
                QAT.append(time)
                IOQ.remove(p)
                p.nIE = time
                time -= 1
                print("time %sms: Process %s completed I/O [Q " % (time, CPUQ[len(CPUQ)-1].name), end='')
                print("{}]".format(print_queue(CPUQ)))
                break

        #if the CPU is idle and there are processes in the ready queue, start the first
        if len(CPUQ) > 0 and len(RunningQ) == 0:
            RunningQ.append(CPUQ.pop(0))
            time += 4
            numContextSwitches += 1
            print ("time %sms: Process %s started using the CPU [Q %s]" %(time, RunningQ[0].name, print_queue(CPUQ)))
            RunningQ[0].run()
            RunningQ[0].nIE = time + RunningQ[0].CPUBurst
            RunningQ[0].numBursts -= 1


        #if a process has finished its CPU Burst, send it to do IO
        if len(RunningQ) == 1:
            if RunningQ[0].numBursts > 0 and RunningQ[0].nIE <= time:
               # if (RunningQ[0].IOBurst == 0):
                    #process is done-zo

                RunningQ[0].block()
                #RunningQ[0].numBursts -= 1
                print ("time %sms: Process %s completed a CPU burst; %s to go [Q " %(time, RunningQ[0].name, RunningQ[0].numBursts), end='')
                print("%s]" %(print_queue(CPUQ)))
                temp = RunningQ.pop(0)
                t = QAT.pop(0)
                AvgTurnaround += (time - t)
                AvgWait += (time - t) - 8 - temp.CPUBurst
                IOQ.append(temp)
                temp.nIE = time + temp.IOBurst
                print ("time %sms: Process %s blocked on I/O until time %sms [Q %s]" %(time, temp.name, temp.nIE, print_queue(CPUQ)))
                time += 3

            elif RunningQ[0].numBursts <= 0 and RunningQ[0].nIE <= time:
                print ("time %sms: Process %s terminated [Q " %(time, RunningQ[0].name), end='')
                RunningQ[0].complete(time)
                #AvgTurnaround += int(RunningQ[0].completedTime) - int(RunningQ[0].arrivalTime)
                #AvgTurnaround += (time - RunningQ[0].arrivalTime)
                t = QAT.pop(0)
                AvgTurnaround += (time - t)
                AvgWait += (time - t) - 8 - RunningQ[0].CPUBurst

                # increment # of completed process chains
                finished += 1
                RunningQ.pop(0)

                print ("%s]" %(print_queue(CPUQ)))

                # stop Sim if all completed
                if finished >= len(processList):
                    live = False
                    time += 4
                    print("time %sms: Simulator ended for FCFS" % (time))
                    break

                time += 3

        time += 1
        #if done, exit loop
    AvgWait/=numContextSwitches
    AvgTurnaround /= numContextSwitches


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
    live = True     # For simulation status
    time = 0        # Elapsed in milliseconds
    completed = 0   # Number of processes completely finished
    burstCount = 0  # Number of total bursts 
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
    #statsOutput(["Test",1,2,3,4,5], sys.argv[2])
    statsOutput(FCFS(processList), sys.argv[2])
    processList = processFile(sys.argv[1]) 
    statsOutput(SJF(processList), sys.argv[2], True)
    processList = processFile(sys.argv[1]) 
    statsOutput(RoundRobin(processList, m, t_slice, t_cs), sys.argv[2], True)
    

# -- average CPU burst time: ###.## ms
# -- average wait time: ###.## ms
# -- average turnaround time: ###.## ms
# -- total number of context switches: ##
# -- total number of preemptions: ##















