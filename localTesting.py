import utilities
import time

testcount = 100000
startTime = time.time()
for i in range(testcount):
    utilities.logging("This is a test nr: " + str(i) +"\n")
endTime = time.time()

print("Took about " + str(endTime-startTime) + " seconds for an average of:" + str((endTime-startTime)/testcount) + " seconds per write")