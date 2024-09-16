import pyudev
import subprocess
import time
from pathlib import Path
import os
from datetime import datetime
import shutil
import utilities


#Input top port and destination bottom port

class USBControlTool:
	def __init__(self):
		self.context = pyudev.Context()
		self.monitor = pyudev.Monitor.from_netlink(self.context)
		self.monitor.filter_by(subsystem="usb")
		self.blocked_devices = set()
		self.connected_devices = [None,None]
		#1 for sourc ; 0 for destination
		self.most_recent = 0
	def start_monitoring(self):
		observer = pyudev.MonitorObserver(self.monitor, callback=self.handle_usb_event, name="usb-monitor")
		observer.start()
		try:
			print("USB Device Control Tool is running. Press Control+C to exit")
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			pass
		finally:
			observer.stop()
			observer.join()
	def handle_usb_event(self,device):

		if device.action == "add":

			if self.is_device_blocked(device):
				print(f"Blocking USB Device: {device}")
				self.block_device(device)
			else:
				if device.sys_path[-1] != "0":

					self.connected_devices[int(device.sys_path[-1])-1] = device
					if device.sys_path[-1] == "1":
						utilities.logging("Device connected with port indicator 1")
						self.most_recent = 1
					elif device.sys_path[-1]== "2":
						utilities.logging("Device connected with port indicator 1")
						self.most_recent = 0
					#print(device.sys_path[-1])
					#print(self.most_recent)
					self.update_connected()

					if None not in self.connected_devices:
						try:
							utilities.logging("Initialized copying")
							initializeCopying(self.connected_devices,self.most_recent)
							utilities.logging("Copying done")
						except Exception as er:
							utilities.logging("Error during copying: "+str(er))
							pass
		elif device.action == "remove":
			utilities.logging("Device removed")
			if device in  self.blocked_devices:
				self.unblock_device()
			else:
				if  device.sys_path[-1] != "0":
					self.connected_devices[int(device.sys_path[-1])-1] = None
					self.update_connected()

	def is_device_blocked(self, device):
		return False

	def block_device(self,device):
		self.blocked_devices.add(device)
		subprocess.run(["sudo","echo","0",">",f"/sys{device.sys_path}/authorized"])

	def unblock_device(self,device):
		self.blocked_devices.remove(device)
		subprocess.run(["sudo","echo","1",">",f"/sys{device.sys_path}/authorized"])

	def update_connected(self):
		print("Updated connections")
		print(self.connected_devices)



def list_files(path):
	file_list = []
	for root, dirs, files in os.walk(path):
		for file in files:
			file_list.append(os.path.join(root,file))
	return file_list



def copyFile(file,tmpart):
	utilities.logging("Started copy of " + file )
	try:
		subprocess.run(["sudo", "cp", file, "/media/bkPrg/dest/" + tmpart + "-Unfinished"])
		utilities.logging("Finished copying " + file)
		return 0
	except Exception as e:
		utilities.logging("Error inside copyFile: " + str(e))
		return 1




def initializeCopying(devices,indicator):
	status = 0
	utilities.logging("Opening partitions file")
	try:
		partitionsFile = open("/proc/partitions")
		lines = partitionsFile.readlines()[2:]

		temp = []
		print(partitionsFile.readlines())
		for line in lines:
			words = [x.strip() for x in line.split()]
			deviceName = words[3]
			temp.append([deviceName])
		utilities.logging("Got partitions successfully: " + str(temp))
	except Exception as e:
		status += 1
		utilities.logging("Error in getting partitions: " + str(e))

	utilities.logging("Assigning Partitions")
	try:
		source = ""
		destination = ""
		temporary = [temp[len(temp) - 3], temp[len(temp) - 1]]
		print(temporary)
		if indicator == 0:
			source = temporary[0]
			destination = temporary[1]
		else:
			source = temporary[1]
			destination = temporary[0]
		utilities.logging("Succesfully assigned partitions: Source: " + source + " Destination: " + destination)
	except Exception as e:
		status += 1
		utilities.logging("Error assigning partitions: " + str(e))

	utilities.logging("Mounting source")
	try:
		subprocess.run(["sudo", "mount","-t", "exfat","/dev/"+ source[0], "/media/bkPrg/src"])
		utilities.logging("Source successfully Mounted")
	except Exception as e:
		status += 1
		utilities.logging("Error mounting Source: " + str(e))
	utilities.logging("Mounting destination")
	try:
		subprocess.run(["sudo","mount","-t","exfat", "/dev/"+ destination[0], "/media/bkPrg/dest"])
		utilities.logging("Destination successfully Mounted")
	except Exception as e:
		status += 1
		utilities.logging("Error mounting Destination: " + str(e))
	utilities.logging("Mounting completed with " +str(status)+ " errors")
	utilities.logging("Getting list of all files in source")
	try:
		srcList = list_files("/media/bkPrg/src")
		utilities.logging("Successfully received list of all files in source")
	except Exception as e:
		status += 1
		utilities.logging("Error getting all files in source: " + str(e))
	utilities.logging("Creating destination folder")
	try:
		crTm = datetime.now()
		tmpart = str(crTm.year)+"-"+str(crTm.month)+"-"+str(crTm.day)+"-"+str(crTm.hour)+"-"+str(crTm.minute)+"-"+str(crTm.second)
		subprocess.run(["sudo", "mkdir", "/media/bkPrg/dest/"+tmpart+"-Unfinished"])
		utilities.logging("Succesfully created destination folder: /media/bkPrg/dest/"+tmpart+"-Unfinished")
	except Exception as e:
		status += 1
		utilities.logging("Error creating destination folder: " + str(e))
	utilities.logging("Starting copy phase")
	filestatus = 0
	for file in srcList:
		filestatus += copyFile(file, tmpart)
	if filestatus == 0:
		utilities.logging("Copied every file without errors")
	else:
		utilities.logging(str(filestatus)+" errors occured while trying to copy every file")
	status += filestatus
	utilities.logging("Renaming folder")
	try:
		subprocess.run(["sudo", "mv" , "/media/bkPrg/dest/"+tmpart+"-Unfinished", "/media/bkPrg/dest/"+str(status)+"errs-"+tmpart])
		utilities.logging("Folder successfully renamed")
	except Exception as e:
		status += 1
		utilities.logging("Error renaming destination folder: " + str(e))
	if status == 0:
		utilities.logging("SUCCESSFULLY COPIED "+str(len(srcList))+" files")
	utilities.logging("Unmounting Source")
	try:
		subprocess.run(["sudo","umount","/dev/"+source[0]])
		utilities.logging("Source Unmounted")
	except Exception as e:
		status += 1
		utilities.logging("Error unmounting source: " + str(e))
	utilities.logging("Unmounting Destination")
	try:
		subprocess.run(["sudo","umount","/dev/"+destination[0]])
		utilities.logging("Destination Unmounted")
	except Exception as e:
		status += 1
		utilities.logging("Error unmounting desitnation: " + str(e))
	utilities.logging("All Unmounted")
	utilities.logging("Total amount of errors: " + str(status))
	print("DONE")
def main():
	usb_tool = USBControlTool()
	devices = usb_tool.start_monitoring()

if __name__ == "__main__":
	main()
