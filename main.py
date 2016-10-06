import sys
import os
import time

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



def processFile(fn):
	processes = []
	try:
		f = open(fn)
	except OSError:
		#print("ERROR: file did not open correctly. perhaps the filename was incorrect?")
		sys.exit("ERROR: file did not open correctly. Exiting...")
	i = 0
	for line in f:
		i += 1
		if line.startswith('#'):
			continue
		elif line.strip() == '':
			continue
		else:
			line = line.split('|')
			if len(line) != 5:
				sys.exit("ERROR: invalid file format: line " + str(i) + " does not have the correct number of arguments. Exiting...")
			processes.append(process(line[0], line[1], line[2], line[3], line[4]))
			print(processes[len(processes)-1])
	return processes



def RoundRobin():
	return 0;

def FCFS():
	return 0;

def SJF():
	return 0;


if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.exit("ERROR: missing command-line arguments.\n\tformat:\tpython main.py <filename>")
	processList = processFile(sys.argv[1])














