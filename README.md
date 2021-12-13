# CS 375 - Conference App Design Document

By Rodney Sampson II & Reginald Peoples

Operating Systems - CS 375

Dr. Ali

## Project Demo

Follow these steps exactly to test the project code.

Open three terminals in the same directory containing the client and server files.

Start the server in one terminal
- Run: python3 server.py
 
Start two clients in the other two terminals
- Run: python3 client.py in one terminal
- Run: python3 client.py in another terminal

Enter usernames in the two clients.

Enter either “localhost” or “127.0.0.1” for the server ip on both clients
- This field can also be left blank and it will default to localhost

Enter “8888” for the server port on both clients

Click “Connect to Server” on both client to connect them to the server.

Enter any text into the text bar and click “Chat” to send messages between the clients.

## Network Communication

The Network Communication will be sending these messages in between the client and server side. They are prioritized in order of top to bottom.

-	Connecting to a server
-   Video
-   Audio
-   Text

The graphical user interface (GUI) is done using Python's tkinter library.

## Device Manager

Text can be freely captured and sent to the server from the GUI, however the main video device and main audio device each client will use will each need to first be identified and registered as the primary input device with the client application, and then a connection must be established between the client and that input device, and then a connection between the client and the server must be established to send the input device data to the server and then across all clients.

## Resource Management

We’re going to have each message type on different threads. These threads will be managed with the priority-queue methodology, therefore with every context-switch between threads the priority level of the next process is taken into account. This will keep our application focusing on the messages that matter most. It could pose an issue in the future, as if it runs each process to completion, no matter the run time.

## Compatibility

The language chosen for this project will be Python because of its ease of portability across devices/computers and its simple syntax to create programs as well as its simple libraries for sockets, GUIs, and multithreading/concurrency.

Both the server and the individual clients will be written to run identically on MacOS and Windows machines.
