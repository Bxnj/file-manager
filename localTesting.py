import utilities
import time
import multiprocessing as mp
print("Number of processors: ", mp.cpu_count())
useablePool = mp.cpu_count()-4
#pool = mp.Pool(useablePool)

testcount = 1000
startTime = time.time()
for i in range(testcount):
    utilities.logging("This is a test nr: " + str(i) +"\n")
endTime = time.time()

print("Took about " + str(endTime-startTime) + " seconds for an average of:" + str((endTime-startTime)/testcount) + " seconds per write")