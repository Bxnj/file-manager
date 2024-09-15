import pyudev
import subprocess
import time
from pathlib import Path
import os
from datetime import datetime
import shutil

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
						self.most_recent = 1
					elif device.sys_path[-1]== "2":
						self.most_recent = 0
					print(device.sys_path[-1])
					print(self.most_recent)
					self.update_connected()

					if None not in self.connected_devices:
						try:
							copying(self.connected_devices,self.most_recent)
						except Exception as er:
							print(er)
							print("Copy unsuccessful")
							pass
		elif device.action == "remove":
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







def copying(devices,indicator):
	time.sleep(3)
	print(indicator)
	partitionsFile = open("/proc/partitions")
	lines = partitionsFile.readlines()[2:]
	print(lines)
	temp = []
	for line in lines:
		words = [x.strip() for x in line.split()]
		deviceName = words[3]
		temp.append([deviceName])
	source =""
	destination = ""
	temporary = [temp[len(temp)-3],temp[len(temp)-1]]
	print(temporary)
	if indicator == 0:
		source = temporary[0]
		destination = temporary[1]
	else:
		source = temporary[1]
		destination = temporary[0]
	print(source, destination)
	print("Mounting Source")
	subprocess.run(["sudo", "mount","-t", "exfat","/dev/"+source[0], "/media/bkPrg/src"])
	print("Source successfully Mounted")
	print("Mounting Destination")
	subprocess.run(["sudo","mount","-t","exfat", "/dev/"+destination[0], "/media/bkPrg/dest"])	
	print("Destination successfully Mounted")
	print("Mounting completed")
	srcList = list_files("/media/bkPrg/src")
	crTm = datetime.now()
	tmpart = str(crTm.year)+"-"+str(crTm.month)+"-"+str(crTm.day)+"-"+str(crTm.hour)+"-"+str(crTm.minute)+"-"+str(crTm.second)
	print("time done")
	subprocess.run(["sudo", "mkdir", "/media/bkPrg/dest/"+tmpart+"-Unfinished"])
	time.sleep(5)
	print(srcList)
	time.sleep(5)
	for file in srcList:
		#time.sleep(1)
		subprocess.run(["sudo","cp",file,"/media/bkPrg/dest/"+tmpart+"-Unfinished"])
		print("Copying file: "+ str(file))
	subprocess.run(["sudo", "mv" , "/media/bkPrg/dest/"+tmpart+"-Unfinished", "/media/bkPrg/dest/"+tmpart])
	print("SUCCESSFULLY COPIED "+str(len(srcList))+" files")
	print("Unmounting Source")
	subprocess.run(["sudo","umount","/dev/"+source[0]])
	print("Source Unmounted")
	print("Unmounting Destination")
	subprocess.run(["sudo","umount","/dev/"+destination[0]])
	print("Destination Unmounted")
	print("All Unmounted Successfully")
def main():
	usb_tool = USBControlTool()
	devices = usb_tool.start_monitoring()

if __name__ == "__main__":
	main()
