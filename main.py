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
	return ["SJF",AvgCPUBurst, AvgWait,AvgTurnaround,numContextSwitches,numPreemptions];


if __name__ == '__main__':
	if len(sys.argv) != 3:
		sys.exit("ERROR: Invalid arguments\nUSAGE: python main.py <input-file> <stats-output-file>")
	processList = processFile(sys.argv[1]) 
	print("\n\n\n")
	for i in processList:
		print(i)
	statsOutput(["Test",1,2,3,4,5], sys.argv[2])

# -- average CPU burst time: ###.## ms
# -- average wait time: ###.## ms
# -- average turnaround time: ###.## ms
# -- total number of context switches: ##
# -- total number of preemptions: ##















