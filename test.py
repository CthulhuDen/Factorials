#! /usr/bin/env python

import time, math, hashlib, factorials

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
					print "\tOutput hash: "+ rez
				elif isinstance(hashway,str):
					try:
						rez = hashlib.new(hashway,rez).hexdigest()
						print "\tOutput hash: "+ rez

					except:
						print "\tSpecified hash type is not supported!"
				else:
					try:
						rez = hashway(rez)
						print "\tOutput hash: "+ rez
					except:
						print "\tHash function supported failed!"
			else:
				print "\tOutput: "+rez
funcs["timetest"] = timetest

def present(f_list, f_discrs):
		print "Functions available in module:"
		for func in f_list:
			print "\t"+func+" \t "+f_discrs[func]
		print "End of list"

alllist.append("math_fact")
funcdiscr["math_fact"] = "Factorial from \'math\' module"
funcs["math_fact"] = math.factorial
alllist.append("fact")
funcdiscr["fact"] = "Simple factorial implementation"
funcs["fact"] = factorials.fact
alllist.append("fact_double")
funcdiscr["fact_double"] = "Double-process factorial implementation"
funcs["fact_double"] = factorials.fact_double
alllist.append("fact_double_perf")
funcdiscr["fact_double_perf"] = "Perfected double-process factorial implementation"
funcs["fact_double_perf"] = factorials.fact_double_perf
alllist.append("fact_double_perf_tuned")
funcdiscr["fact_double_perf_tuned"] = "Perfected double-process factorial implementation TUNED"
funcs["fact_double_perf_tuned"] = lambda x: factorials.fact_double_perf(x,22,100)
alllist.append("fact_double_perf_spec_reduce")
funcdiscr["fact_double_perf_spec_reduce"] = "Two-process with enhanced reduce implementation"
funcs["fact_double_perf_spec_reduce"] = lambda n,max_blocks=126,min_size=500: factorials.fact_double_perf(n=n,max_blocks=max_blocks,min_size=min_size,spec_reduce=factorials.quickreduce)
alllist.append("fact_double_perf_spec_reduce_tuned")
funcdiscr["fact_double_perf_spec_reduce_tuned"] = "Duo-process with enchanced reduce implementation TUNED"
funcs["fact_double_perf_spec_reduce_tuned"] = lambda x: funcs["fact_double_perf_spec_reduce"] (x,128,100)
funclist = alllist+["timetest",]
run = True
if __name__=="__main__":
	if run:
		timetest(100000,["math_fact","fact_double","fact_double_perf","fact_double_perf_spec_reduce",],hash=True)
		#timetest(4000,["fact_double","fact_double_perf",],hash=True,hashway="lol")
		#timetest(1000,["fact_double_perf_spec_reduce","fact_double_perf_spec_reduce_tuned",],hash=True,hashway=lambda x:x.org())
	else:
		present(funclist, funcdiscr)
