import os
import time
import sys

# get current time
now = time.time()	

# get customer id from command line
cust_id = sys.argv[1]	

dir_list = [f'./report_files/{cust_id}',f'./database_files/{cust_id}',f'./source_files/{cust_id}']	

# loop through files
for dir in dir_list:
	# get list of files in dir
	#check if dir exists
	if os.path.exists(dir):
		file_list = os.listdir(dir)
		# loop through files\
		for file in file_list:
			# get file creation time
			file_ctime = os.path.getctime(dir+'/'+file)
			# if file is older than 6 months, delete it
			if now - file_ctime > 15552000:
				# check if file is a directory
				if os.path.isdir(dir+'/'+file):
					# delete directory
					os.rmdir(dir+'/'+file)
					print(f"{dir+'/'+file} deleted")
				else:
					# delete file
					os.remove(dir+'/'+file)
					print(f"{dir+'/'+file} deleted")