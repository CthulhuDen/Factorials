#! /usr/bin/env python

import os, time, multiprocessing, math, hashlib

alllist = []
funcs = dict()
funcdiscr = dict()

funcdiscr["timetest"] = "arg, f_list, info, rezs, hash - test functions"
def timetest(num, f_list="ALL", info=True, rezs = True, hash = False, hashway = None):
	if (type(f_list)==type("string")) and (f_list.upper()=="ALL"):
		f_list = alllist
	for func in f_list:
		string = "Testing function "+func+" with "+str(num)
		if info:
			string = string+" ("+funcdiscr[func]+")"
		print string + ":"
		tm = time.time()
		rez = funcs[func](num)
		tm = time.time() - tm
		print "\tSpent "+str(round(1000*tm)*.001)+" secs"
		print "\tAnswer's length is "+str(rez.bit_length())+" bits"
		if rezs:
			rez = str(rez)
			if hash:
				import hashlib
				if hashway is None:
					rez = hashlib.md5(rez).hexdigest()
				elif isinstance(hashway,str):
					rez = hashlib.new(hashway,rez)
				else:
					rez = hashway(rez)
				print "\tOutput hash: "+ rez
			else:
				print "\tOutput: "+rez
funcs["timetest"] = timetest

def present(f_list, f_discrs):
		print "Functions available in module:"
		for func in f_list:
			print "\t"+func+" \t "+f_discrs[func]
		print "End of list"

def is_prime(n):
	if n<=2:
		return True
	if n%2 == 0:
		return False
	for i in range(1, (int(n**0.51)+1)/2):
		if n%(2*i+1) == 0:
			return False
	return True

alllist.append("prime")
funcdiscr["prime"] = "Simple prime generator, utilizing simple prime contester"
def prime(n):
	if n==1:
		return 2
	if n==2:
		return 3
	k = 3
	for i in range(3,n+1):
		k = k + 2
		while not(is_prime(k)):
			k = k + 2
	return k
funcs["prime"] = prime

alllist.append("prime_dual")
funcdiscr["prime_dual"] = "Dual-process prime generator with simple prime contestor"
def prime_dual(n):
	def printlock(lock):
		lastprinted = ""
		toprint = ""
		while 1:
			toprint = str(lock)
			if not(toprint==lastprinted):
				#print "Lock is now "+toprint
				lastprinted = toprint
	
	def func_slave(pipe,event,lock):
		while 1:
			job = pipe.recv()
			#print lock
			#print str(os.getpid())+": Going to send results on "+str(job)
			lock.acquire()
			#print str(os.getpid())+": Sending results on "+str(job)
			pipe.send([job,is_prime(job)])
			event.set()
			lock.release()
	
	if n==1:
		return 2
	if n==2:
		return 3
	
	ev = multiprocessing.Event()
	lock = multiprocessing.Lock()
	
	pipe1 = multiprocessing.Pipe()
	p1 = multiprocessing.Process(target=func_slave,args=(pipe1[1],ev,lock,))
	pipe1 = pipe1[0]
	
	pipe2 = multiprocessing.Pipe()
	p2 = multiprocessing.Process(target=func_slave,args=(pipe2[1],ev,lock,))
	pipe2 = pipe2[0]
	
	p1.start()
	p2.start()
	
	pipe1.send(5)
	pipe2.send(7)
	
	k=7
	found = 2
	maxfound = 3
	prevmaxfound = 2
	
	p = multiprocessing.Process(target=printlock,args=(lock,))
	#p.start()
	
	while found < n:
		ev.wait()
		#print "Main got something!"
		lock.acquire()
		if pipe1.poll():
			rez = pipe1.recv()
			num,rez = rez[0],rez[1]
			#print num,rez
			if rez:
				found = found + 1
				if num>maxfound:
					prevmaxfound = maxfound
					maxfound =num
				elif num>prevmaxfound:
					prevmaxfound =num
				if found == n:
					ev.clear()
					lock.release()
					#print "Trying to recv2"
					rez = pipe2.recv()
					#print "Recv'd 2"
					num,rez = rez[0],rez[1]
					#print num,rez
					if rez:
						found = found+1
						if num>maxfound:
							prevmaxfound = maxfound
							maxfound = num
						elif num>prevmaxfound:
							prevmaxfound = num
					p1.terminate()
					p2.terminate()
					#p.terminate()
					if found==n:
						return maxfound
					else:
						return prevmaxfound
			k = k + 2
			pipe1.send(k)
		if pipe2.poll():
			rez = pipe2.recv()
			num,rez = rez[0],rez[1]
			#print num,rez
			if rez:
				found = found + 1
				if num>maxfound:
					prevmaxfound = maxfound
					maxfound =num
				elif num>prevmaxfound:
					prevmaxfound =num
				if found == n:
					ev.clear()
					lock.release()
					#print "Trying to recv2"
					rez = pipe1.recv()
					#print "Recv'd 2"
					num,rez = rez[0],rez[1]
					#print num,rez
					if rez:
						found = found+1
						if num>maxfound:
							prevmaxfound = maxfound
							maxfound = num
						elif num>prevmaxfound:
							prevmaxfound = num
					p1.terminate()
					p2.terminate()
					#p.terminate()
					if found==n:
						return maxfound
					else:
						return prevmaxfound
			k = k + 2
			pipe2.send(k)
		ev.clear()
		lock.release()
funcs["prime_dual"]=prime_dual

alllist.append("math_fact")
funcdiscr["math_fact"] = "Factorial implementation from math module"
funcs["math_fact"] = math.factorial

alllist.append("fact")
funcdiscr["fact"] = "Simple factorial implementation"
def fact(n):
	rez = 1
	if n > 1:
		for i in range(2,n+1):
			rez = rez * i
	return rez
funcs["fact"] = math.factorial

alllist.append("fact_double")
funcdiscr["fact_double"] = "Double-process factorial implementation"
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
funcs["fact_double"] = fact_double

alllist.append("fact_double_perf")
funcdiscr["fact_double_perf"] = "Perfected double-process factorial implementation"
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
funcs["fact_double_perf"] = fact_double_perf

alllist.append("fact_double_perf_tuned")
funcdiscr["fact_double_perf_tuned"] = "Perfected double-process factorial implementation TUNED"
funcs["fact_double_perf_tuned"] = lambda x: fact_double_perf(x,22,100)

alllist.append("fact_double_perf_spec_reduce")
funcdiscr["fact_double_perf_spec_reduce"] = "Two-process with enhanced reduce implementation"
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
funcs["fact_double_perf_spec_reduce"] = lambda n,max_blocks=126,min_size=500: fact_double_perf(n=n,max_blocks=max_blocks,min_size=min_size,spec_reduce=quickreduce)

alllist.append("fact_double_perf_spec_reduce_tuned")
funcdiscr["fact_double_perf_spec_reduce_tuned"] = "Duo-process with enchanced reduce implementation TUNED"
funcs["fact_double_perf_spec_reduce_tuned"] = lambda x: funcs["fact_double_perf_spec_reduce"] (x,128,100)

funclist = alllist+["timetest",]
run = True
if run:
	timetest(100000,["math_fact","fact_double","fact_double_perf","fact_double_perf_spec_reduce",],hash=True)
	#timetest(40000,["fact_double","fact_double_perf",],rezs=False,hash=True)
	#timetest(100000,["fact_double_perf_spec_reduce","fact_double_perf_spec_reduce_tuned",],rezs=False,hash=True)
else:
	present(funclist, funcdiscr)
