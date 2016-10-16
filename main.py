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
		self.numBursts = nb
		self.IOBurst = io
		self.status = "None"
		self.Completed = False
		self.completedTime = -1
		self.nIE = 0		#next Interesting Event

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

	def getName(self):
		return self.name

	def getArrivalTime(self):
		return self.arrivalTime

	def getCPUBurstTime(self):
		return self.CPUBurst

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


def RoundRobin(processList, t_slice=84):
	#given a process list, do the RR algorithm and return the 5 needed output stats
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

	# Initialize variables
	live = True		# For simulation status
	time = 0 		# Elapsed in milliseconds
	completed = 0	# Number of processes completely finished
	burstCount = 0	# Number of total bursts 
	enter = 0
	exit = 0

	
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
					processList[i].ready()
					cpuQueue.append(processList[i])
					cpuQueue = sorted(cpuQueue,key=lambda x: int(x.CPUBurst))
					print("time %sms: Process %s arrived [Q %s]" %(time, processList[i].name, print_queue(cpuQueue)))
					enter += 1
				elif (processList[i].status == "None"):
					processList[i].nIE = processList[i].arrivalTime
		# end processing into cpuQueue

		# check move io -> cpuQueue
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
		# end move io -> cpuQueue

				
		# Run CPUBurst
		if len(cpuQueue) > 0 and len(runningQueue) == 0:
			runningQueue.append(cpuQueue.pop(0))
			time += 4
			print ("time %sms: Process %s started using the CPU [Q %s]" %(time, runningQueue[0].name, print_queue(cpuQueue)))
			runningQueue[0].run()
			#time += int(runningQueue[0].CPUBurst)
			runningQueue[0].nIE = time + int(runningQueue[0].CPUBurst)

			# Decrement number of bursts
			runningQueue[0].numBursts = int(runningQueue[0].numBursts) - 1

		# Display Burst completion
		if len(runningQueue) == 1 and int(runningQueue[0].numBursts) > 0 and int(runningQueue[0].nIE) <= time:
			print ("time %sms: Process %s completed a CPU burst; %s to go [Q " %(time, runningQueue[0].name, runningQueue[0].numBursts), end='')
			runningQueue[0].nIE = time + int(runningQueue[0].IOBurst)
			
			# increment averages
			AvgCPUBurst += int(runningQueue[0].CPUBurst)

			print("%s]" %(print_queue(cpuQueue)))
			runningQueue[0].block()
			print("time %sms: Process %s blocked on I/O until time %sms [Q " % (time, runningQueue[0].name, runningQueue[0].nIE), end='')
			print("%s]" %(print_queue(cpuQueue)))
			time += 3
			# Send process to IO
			ioQueue.append(runningQueue.pop(0))
		# end Burst completion
		
		# check for remaining CPU bursts
		elif len(runningQueue) == 1 and int(runningQueue[0].numBursts) <= 0 and runningQueue[0].nIE == time:
			print ("time %sms: Process %s terminated [Q " %(time, runningQueue[0].name), end='')
			runningQueue[0].complete(time)
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
		# end CPU burst check

		time += 1
	# end Sim loop



	#----------------------------------------------------------------------



	# Get Average CPU Burst
	#AvgCPUBurst /= burstCount
	print ("BurstCount =", burstCount)
	print ("AvgCPUBurst =", AvgCPUBurst)
	print ("Shit Time =", time)

	# Get Average Wait


	numContextSwitches = 0;
	numPreemptions = 0;

	return ["SJF",AvgCPUBurst, AvgWait,AvgTurnaround,numContextSwitches,numPreemptions];


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
	SJF(processList)
	#FCFS(processList)

# -- average CPU burst time: ###.## ms
# -- average wait time: ###.## ms
# -- average turnaround time: ###.## ms
# -- total number of context switches: ##
# -- total number of preemptions: ##















