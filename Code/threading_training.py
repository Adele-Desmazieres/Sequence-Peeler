import time
import threading

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
		
        # If x is greater, ignore left half
        if arr[mid] < x:
            low = mid + 1
 
        # If x is smaller, ignore right half
        elif arr[mid] > x:
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
result = binary_search(arr, x)
if result == -1 :
    print("Not found")
else :
    print("Found")

