import socket, select
import sys
import atexit

#Function to send message to all connected clients
def send_to_all_tata ():
	message = 'server_tata'
	print('_Servertata')
	#Message not forwarded to server and sender itself
	for socket in connected_list:
		if socket != server_socket :
			socket.send(message)

	for socket in connected_list:
		if socket != server_socket :
			connected_list.remove(socket)

atexit.register(send_to_all_tata)

def send_to_all_irrespective (message, origin_port, port):
	print 'Fuck '
	return

	#Message not forwarded to server and sender itself
	for socket in connected_list and origin_port != port:
		if socket != server_socket:
			socket.send(message)


#Function to send message to all connected clients
def send_to_all (sock, message):
	#Message not forwarded to server and sender itself
	for socket in connected_list:
		if socket != server_socket and socket != sock :
			try :
				socket.send(message)
			except :
				# if connection not available
				socket.close()
				connected_list.remove(socket)

def sense_change(port):
	with open('update.txt', 'r') as file:
		msg, origin_port = file.readline().split(',')
		send_to_all_irrespective(msg, origin_port, port)

def set_update(message, port):
	with open('update.txt','w') as file:
		file.write(str(message) + ',' + str(port))

if __name__ == "__main__":
	name=""
	#dictionary to store address corresponding to username
	record={}
	# List to keep track of socket descriptors
	connected_list = []
	buffer = 4096

	# port = 5001
	if len(sys.argv)<2:
		port = int(raw_input("Enter Port to listen: "))
	else:
		port = int(sys.argv[1])
		if len(sys.argv) == 3:
			hostname = sys.argv[2]
		else:
			hostname = 'localhost'

    # port = 5001

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_socket.bind((hostname, port))
	server_socket.listen(10) #listen atmost 10 connection at one time

	# Add server socket to the list of readable connections
	connected_list.append(server_socket)

	print "\33[32m \t\t\t\tSERVER WORKING \33[0m" 

	try:
		while 1:
	        # Get the list sockets which are ready to be read through select
			rList,wList,error_sockets = select.select(connected_list,[],[])

			for sock in rList:
				#New connection
				if sock == server_socket:
					# Handle the case in which there is a new connection recieved through server_socket
					sockfd, addr = server_socket.accept()
					name=sockfd.recv(buffer)
					connected_list.append(sockfd)
					record[addr]=""
					#print "record and conn list ",record,connected_list
	                
	                #if repeated username
					if name in record.values():
						sockfd.send("\r\33[31m\33[1m Username already taken!\n\33[0m")
						del record[addr]
						connected_list.remove(sockfd)
						sockfd.close()
						continue
					else:
	                    #add name and address
						record[addr]=name
						print "Client (%s, %s) connected" % addr," [",record[addr],"]"
						sockfd.send("\33[32m\r\33[1m Welcome to chat room. Enter 'tata' anytime to exit\n\33[0m")
						send_to_all(sockfd, "\33[32m\33[1m\r "+name+" joined the conversation \n\33[0m")

				#Some incoming message from a client
				else:
					# Data from client
					try:
						data1 = sock.recv(buffer)
						#print "sock is: ",sock
						data=data1[:data1.index("\n")]
						#print "\ndata received: ",data
	                    
	                    #get addr of client sending the message
						i,p=sock.getpeername()
						if data == "tata":
							msg="\r\33[1m"+"\33[31m "+record[(i,p)]+" left the conversation \33[0m\n"
							send_to_all(sock,msg)
							print "Client (%s, %s) is offline" % (i,p)," [",record[(i,p)],"]"
							del record[(i,p)]
							connected_list.remove(sock)
							sock.close()
							continue

						else:
							message = data
							msg="\r\33[1m"+"\33[35m "+record[(i,p)]+": "+"\33[0m"+data+"\n"
							send_to_all(sock,msg)
							set_update(message, port)
	            
	                #abrupt user exit
					except:
						(i,p)=sock.getpeername()
						send_to_all(sock, "\r\33[31m \33[1m"+record[(i,p)]+" left the conversation unexpectedly\33[0m\n")
						print "Client (%s, %s) is offline (error)" % (i,p)," [",record[(i,p)],"]\n"
						del record[(i,p)]
						connected_list.remove(sock)
						sock.close()
						continue

		server_socket.close()

	except KeyboardInterrupt:
		print 'KeyBoard Interupt'
	

