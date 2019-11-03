#!/usr/bin/python

import psycopg2 as pgmanager
import psycopg2.extensions as ext
import datetime as time 
import time as timer
import json


# Connect to the Postgres DB
connection = pgmanager.connect(
	database="test_db", # name of the target database
	user="test_user",  # name of the user
	password="password123", # user's password 
	host="127.0.0.1", # IP address, where you db is running
	port="5432") # port number
#requirement of psycopg2 library
connection.set_isolation_level(ext.ISOLATION_LEVEL_AUTOCOMMIT)


print("Database was connected successfully!")

cursor = connection.cursor() # will execute Postgres DB commands
cursor.execute("LISTEN accounts_changed;") # Subscribing on listening of the particular channel

try:
	while True:
	
		# checking, if there are new messages
		connection.poll()
		
		#if there are some changes, read the whole database out and log it
		while connection.notifies:
			notify = connection.notifies.pop(0)
			print("There is a notification:",
				notify.pid,
				notify.channel,
				notify.payload)
	
			# Extracting date and time in user friendly format
			current_time = time.datetime.now()
			ttime = current_time.strftime("%d/%m/%Y-%H:%M:%S")
			
			# specify fields you want to return by from the certain table replacing "*"
			cursor.execute("SELECT * from test_table")
			data = cursor.fetchall() # Fetch the data
			print("Data retrieved successfully")
		
			# print out obtained data
			for info in data:
				print("ID = ", info[0])
				print("Status = ", info[1])
				print("Band = ", info[2])
				print("Song = ", info[3])
				print("Logged At = ", info[4])
			
			print("Data were printed")
		
		timer.sleep(1)

finally:
	# Gracefully disconnect from the DB
	connection.close()
	print("Connection was gracefully closed")
