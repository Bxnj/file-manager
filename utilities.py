from datetime import datetime
import time
from pathlib import Path
#Only for local testing
#logFolderPath = "C:/Users\Bentox\Downloads/"

#Raspberry Pi
logFolderPath = "home/bnj/"

def logging(toLog):
    crTm = datetime.now()
    currentTimeString = str(crTm.year)+"-"+str(crTm.month)+"-"+str(crTm.day)+"-"+str(crTm.hour)+"-"+str(crTm.minute)+"-"+str(crTm.second)+"-"+str(crTm.microsecond)
    logfile = logFolderPath + "Log-"+str(crTm.year)+"-"+str(crTm.month)+"-"+str(crTm.day) +".txt"
    my_file = Path(logfile)
    if not my_file.exists() :
        with my_file.open('w') as file:
            file.write("Log file: \n")
        file.close()
    with open(logfile, "a") as myfile:
        myfile.write(currentTimeString+": " +toLog)
    myfile.close()

