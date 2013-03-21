#! /usr/bin/env python

import multiprocessing

class slaves:
	def func(self, function,operating,queueIn,queueOut,terminator,lock):		#move out of class definition if possible
		cont = True
		while not(terminator.is_set()):
			operating.wait()
			lock.acquire()
			if queueIn.empty():
				lock.release()
			else:
				inp = queueIn.get()
				lock.release()
				rez = function(inp)
				queueOut.put(rez)
		queueOut.close()
		return 0
	
	def put(self,info):
		self.queueIn.put(info)

	def get(self):
		return self.queueOut.get()

	def terminate(self):
		self.operating.set()
		self.terminator.set()
		self.queueIn.close()
		
	def pause(self):
		self.operating.clear()

	def resume(self):
		self.operating.set()

	def __init__(self,number,function):
		self.queueIn = multiprocessing.Queue()
		self.queueOut = multiprocessing.Queue()
		self.terminator = multiprocessing.Event()
		self.operating = multiprocessing.Event()
		self.lock = multiprocessing.Lock()
		self.processes = []
		for i in range(0,number):
			self.processes.append(multiprocessing.Process(target=self.func,args=(function,self.operating,self.queueIn,self.queueOut,self.terminator,self.lock,)))

	def start(self):
		self.operating.set()
		for p in self.processes:
			p.start()

	
