#! /usr/bin/env python

import slaves

def fact(n):
	rez = 1
	if n > 1:
		for i in range(2,n+1):
			rez = rez * i
	return rez

#TO THINK - why acts slower then perfected one when both make one split?
def fact_part(st_fin):
	st,fin = st_fin
	rez = 1
	for i in range(st,fin+1):
		rez = rez * i
	return rez

def fact_double(n):
	mid = n/2
	s = slaves.slaves(2,fact_part)
	s.put((1,mid))
	s.put((mid+1,n))
	s.start()
	rez = s.get()*s.get()
	s.terminate()
	return rez

def prod(x):
	a,b = x
	return a*b

def fact_double_perf(n, max_blocks=15,min_size=500, spec_reduce=reduce):
	s = slaves.slaves(4,fact_part)
	dist = n/max_blocks
	if dist < min_size:
		dist = min_size
	st = 1
	fin = st + dist - 1
	count = 1
	while fin<n:
		s.put((st,fin,))
		count = count + 1
		st = fin + 1
		fin = st + dist -1
	s.start()
	s.put((st,n))
	lst = []
	for i in range(0,count):
		lst.append(s.get())
	s.terminate()
	return spec_reduce(lambda x,y:x*y,lst,1)

def quickreduce(func,lst,start=None,slavs=None):
	if slavs is None:
		s = slaves.slaves(4,prod)
		s.start()
		s.pause()
	else:
		s = slavs
	if start is None:
		old = []
	else:
		old = [start,]
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
			s.put((prev[2*i],prev[2*i+1],))
			cnt = cnt + 1
		if ln%2==1:
			next.append(prev[-1])
		s.resume()
		for i in range(0,cnt):
			next.append(s.get())
		s.pause()
		ln = len(next)
	s.terminate()
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
