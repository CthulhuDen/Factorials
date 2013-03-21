Factorials
==========

Module with quick multiprocess implementations of factorial function

For example, on my core 2 duo standard math.factorial takes 15 secs and factorial function from this module less then 1 sec.

==========

Author(s): Denis <cthulhu> Yuzhanin (CthulhuDen@gmail.com)

Usage notes:
	Simply import factorials file from this project, than you can call factorials.factorial

	There is supplied time tester in repository
	test.py [num [out [hash]]]
		num - Number to calculate factorial of
		out - Either "number" to print outputs, "hash" to print hashes or "noans" to skip printing output
		hash - (Only available with 'hash' option) string specifying hash method (must be one of those supplied in hashlib)
