#! /usr/bin/env python

import multiprocessing

def fact(n):
	rez = 1
	if n > 1:
		for i in range(2,n+1):
			rez = rez * i
	return rez
#TO THINK - why acts slower then perfected one when both make one split?
def fact_double(n):
	def part(st,fin,pipe):
		rez = 1
		for i in range(st,fin+1):
			rez = rez * i
		pipe.send(rez)
	mid = n/2
	pipe1 = multiprocessing.Pipe()
	p1 = multiprocessing.Process(target=part,args=(1,mid,pipe1[0],))
	pipe1 = pipe1[1]
	pipe2 = multiprocessing.Pipe()
	p2 = multiprocessing.Process(target=part,args=(mid+1,n,pipe2[0],))
	pipe2 = pipe2[1]
	p1.start()
	p2.start()
	return pipe1.recv()*pipe2.recv()

def part(queueIn,queueOut,lock,start,end):
	cont = True
	start.wait()
	while cont:
		lock.acquire()
		if queueIn.empty():
			lock.release()
			queueOut.close()
			cont = False
		else:
			st,fin = queueIn.get()
			lock.release()
			rez = 1
			for i in range(st,fin+1):
				rez = rez * i
			queueOut.put(rez)
	end.set()
	return 0
def fact_double_perf(n, max_blocks=15,min_size=500, spec_reduce=reduce):
		
	start = multiprocessing.Event()
	end1 = multiprocessing.Event()
	end2 = multiprocessing.Event()
	lock = multiprocessing.Lock()
	queueIn = multiprocessing.Queue()
	queueOut = multiprocessing.Queue()
	
	p1 = multiprocessing.Process(target=part,args=(queueIn, queueOut, lock, start, end1, ))
	p2 = multiprocessing.Process(target=part,args=(queueIn, queueOut, lock, start, end2, ))
	p1.start()
	p2.start()
	
	dist = n/max_blocks
	if dist < min_size:
		dist = min_size
	st = 1
	fin = st + dist-1
	count = 1
	while fin<n:
		queueIn.put((st,fin,))
		count = count + 1
		st = fin + 1
		fin = st + dist - 1
	queueIn.put((st,n,))
	queueIn.close()
	queueIn.join_thread()
	start.set()
	tmp = 1
	lst = []
	end1.wait()
	end2.wait()
	for i in range(0,count):
		lst.append(queueOut.get())
	tmp = spec_reduce(lambda x,y:x*y,lst,1) 
	return tmp;
def qr_slave(queueIn,queueOut,operate,finish,lock):
	cont = True
	while not(finish.is_set()):
		operate.wait()
		lock.acquire()
		if queueIn.empty():
			lock.release()
		else:
			x,y = queueIn.get()
			#print str(os.getpid())+" got something"
			lock.release()
			queueOut.put(x*y)
			#print str(os.getpid())+" sent something"
	queueOut.close()
	return 0
def quickreduce(func,lst,start=None):
	operate = multiprocessing.Event()
	finish = multiprocessing.Event()
	lock = multiprocessing.Lock()
	queueIn = multiprocessing.Queue()
	queueOut = multiprocessing.Queue()
	
	p1 = multiprocessing.Process(target=qr_slave,args=(queueIn, queueOut, operate, finish, lock, ))
	p2 = multiprocessing.Process(target=qr_slave,args=(queueIn, queueOut, operate, finish, lock, ))
	p1.start()
	p2.start()
	
	if not(start==None):
		old = [start,]
	else:
		old = []
	old.extend(lst)
	arr = [old,[],]
	p = 0
	ln = len(arr[p])
	while ln>1:
		prev = arr[p]
		p = 1 - p
		arr[p] = []
		next = arr[p]
		cnt = 0
		for i in range(0,ln/2):
			#print "Trying to send "+str((prev[2*i],prev[2*i+1],))
			queueIn.put((prev[2*i],prev[2*i+1],))
			cnt = cnt + 1
		#print str(cnt)+" requests sent"
		if ln%2==1:
			next.append(prev[-1])
		operate.set()
		for i in range(0,cnt):
			next.append(queueOut.get())
		operate.clear()
		ln = len(next)
	queueIn.close()
	finish.set()
	operate.set()
	return arr[p][0]
fact_double_perf_spec_reduce = lambda n,max_blocks=126,min_size=500: fact_double_perf(n=n,max_blocks=max_blocks,min_size=min_size,spec_reduce=quickreduce)
def factorial(n):
	if n<5000:
		return fact(n)
	elif n<10000:
		return fact_double_perf(n)
	elif n<14000:
		return fact_double(n)
	else:
		return fact_double_perf_spec_reduce(n)
