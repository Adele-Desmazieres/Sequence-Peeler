import time
from threading import Thread

class CustomThread(Thread) :
	# constructor
	def __init__(self, arr, mid, x, greater):
		# execute the base constructor
		Thread.__init__(self)
		self.returnvalue = None
		self.arr = arr
		self.mid = mid
		self.x = x
		self.greater = greater

	def run(self) :
		self.returnvalue = compare_x(self.arr, self.mid, self.x, self.greater)


def compare_x(arr, mid, x, greater=True) :
	return x > arr[mid] if greater else x < arr[mid]


### code from https://www.geeksforgeeks.org/python-program-for-binary-search/
# Iterative Binary Search Function
# It returns index of x in given array arr if present,
# else returns -1
def binary_search(arr, x):
	low = 0
	high = len(arr) - 1
	mid = 0
 
	while low <= high:
 
		mid = (high + low) // 2

		#x1 = CustomThread(arr, mid, x, True)
		#x1.start()
		#x2 = CustomThread(arr, mid, x, False)
		#x2.start()
		#
		#a = x1.returnvalue
		#b = x2.returnvalue

		a = compare_x(arr, mid, x, True)
		b = compare_x(arr, mid, x, False)

		# If x is greater, ignore left half
		if a:
			low = mid + 1
 
		# If x is smaller, ignore right half
		elif b:
			high = mid - 1
 
		# means x is present at mid
		else:
			return mid
 
	# If we reach here, then the element was not present
	return -1
 
 
# Test array
arr = [ 0 ] * 100_000_000 + [ 1 ]
x = 1
 
# Function call
for i in range(1000) :
	result = binary_search(arr, x)
	if result == -1 :
		print("NOT found")
		exit(1)

print("All found")

