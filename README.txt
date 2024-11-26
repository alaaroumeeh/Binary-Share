Project: Binary Share
Objective: Simple and efficient file share between two nodes on a network.
Connection: Symmetric.
Structure:
	TCP stream sockets. Client connects to host, creating two streams in two threads,
	one for sending data, other for receiving data, respectively.
	Sender() procedure operates sending of files on stream#1 in thread#1.
	Receiver() procedure operates receival of files on stream#2 in thread#2.
	Log files client.log and host.log are created to record events and debug errors.	

Usage:
	Launch host.py file on a node. Server socket is bound to all interfaces
	-including localhost- with port 2024. Then launch client.py file on another
	node, input the IP address of the server to connect. Connecting successfully,
	a file dialog window will appear on both nodes, prompting you to choose what files to send.
	Closing the file dialog on a node will end sending files on it, but it can still receive files
	from the other node. Closing the two nodes' dialogs will end the program gently on both sides.
	
	Good luck.		
	Alaa Roumeih. Nov 27, 2024.
