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
		self.Completed = False
		self.completedTime = -1
		self.timeLock = 0

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
			print(processes[len(processes)-1])
	sorted(processes, key=lambda p:p.getArrivalTime())
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


def RoundRobin(processList):
	#given a process list, do the RR algorithm and return the 5 needed output stats
	return ["RR",AvgCPUBurst, AvgWait,AvgTurnaround,numContextSwitches,numPreemptions];

def FCFS(processList):
	#given a process list, do the FCFS algorithm and return the 5 needed output stats
	#create FIFO queue
	processQueue = queue.Queue()
	return ["FCFS",AvgCPUBurst, AvgWait,AvgTurnaround,numContextSwitches,numPreemptions];

def SJF(processList):
	#given a process list, do the SJF algorithm and return the 5 needed output stats
 
	#Sort by smallest CPU burst to largest
	#Service time = Time elapsed from beginning until current period
	#Wait time = Service time - Arrival time

	#0 Context Switches
	#0 Preemptions

	# "Time" elapsed in milliseconds
	live = True
	time = 0
	completed = 0
	burstCount = 0
	target = 0


	# Initialize variables
	AvgCPUBurst = 0
	AvgWait = 0
	AvgTurnaround = 0

	# Start simulation

	# Sort SJF list by CPU Burst length
	byBurst = sorted(processList,key=lambda x: int(x.CPUBurst))
	finished = []
	endLength = len(byBurst)

	# Sim Loop
	while live:
		#print ("There are %r processes in the queue" % len(byBurst))

		# # start process skip
		# if int(byBurst[target].timeLock) > 0 & int(byBurst[target].timeLock) < time:
		# 	byBurst[target].timeLock = 0
		# 	continue

		# look for lowest process not in IO
		if int(byBurst[target].timeLock) > time:
			print("time %sms: Process %s blocked on I/O until time %sms" % (time, byBurst[target].name, byBurst[target].timeLock))
			target += 1
			continue
			
		# end process skip

		# increment time by CPU burst amount
		print ("time %sms: Process %s started using the CPU [Q %s]" %(time, byBurst[target].name, byBurst[target].name))
		time += int(byBurst[target].CPUBurst)
		byBurst[target].timeLock = time + int(byBurst[target].IOBurst)
		
		# Decrement number of bursts
		byBurst[target].numBursts = int(byBurst[target].numBursts) - 1

		# Display Burst completion
		if int(byBurst[target].numBursts) > 0:
			print ("time %sms: Process %s completed a CPU burst; [Q %s]" %(time, byBurst[target].name, byBurst[target].name))
			

		


		# increment averages
		AvgCPUBurst += int(byBurst[target].CPUBurst)



		# check for remaining CPU bursts
		if byBurst[target].numBursts <= 0:
			print ("time %sms: Process %s terminated; [Q %s]" %(time, byBurst[target].name, byBurst[target].name))
			byBurst[target].complete(time)
			# increment # of completed process chains
			completed += 1

			finished.append(byBurst.pop(target))
			
			# Sort SJF list by CPU Burst length
			byBurst = sorted(byBurst,key=lambda x: int(x.CPUBurst))

			# stop Sim if all completed
			if completed >= endLength:
				live = False
				break

			# Start list from beginning
			target = 0
			continue

		target = 0
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
	print("\n\n\n")
	for i in processList:
		print(i)
	statsOutput(["Test",1,2,3,4,5], sys.argv[2])
	SJF(processList);

# -- average CPU burst time: ###.## ms
# -- average wait time: ###.## ms
# -- average turnaround time: ###.## ms
# -- total number of context switches: ##
# -- total number of preemptions: ##















