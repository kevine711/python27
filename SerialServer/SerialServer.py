# ##### Started from online
#http://www.binarytides.com/python-socket-server-code-example/
#By Kevin Ersoy 

##### Script description
#this script has two main parts
# 1. Open TCP server for incoming connection from other automation
# 2. Establish serial connection to TeraXion box and forward all messages from TCP to serial

# Socket server in python using select function
import socket, select
import time  #used for sleep
import string
import sys
import serial

def check_server(address, port):
    # Create a TCP socket
    s = socket.socket()
    #print "Attempting to connect to %s on port %s" % (address, port)
    try:
      readyForUse = s.connect_ex((address, port))
      #print readyForUse
      if (readyForUse == 0):
        #print "Connected to %s on port %s" % (address, port)
        return True
      else:
        #print "Connection to %s on port %s failed: %s" % (address, port, e)
        return False
    except:
      pass

if __name__ == "__main__":

  ########### TCP SERVER CONNECTION FROM LOCALHOST #############
  # start listen server
  CONNECTION_LIST = []  # list of socket clients
  RECV_BUFFER = 4096
  RECV_BUFFER_SSH = 4096
  chan_BUFFER = 4096
  chan=""
  comString=""
  serialConn=0
  ser = serial.Serial()
  
  #Detect optional arguments for ip, user, pass
  if len(sys.argv) == 2:
    print "Setting serial connection port to: " + sys.argv[1]
    comString = sys.argv[1]

  SERVER_PORT = 49594
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # this has no effect, why ?
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  
  # Try desired port, if unavailable increment until you find one
  while check_server('127.0.0.1',SERVER_PORT):
    print str(SERVER_PORT) + " in use, incrementing..."
    SERVER_PORT += 1

  server_socket.bind(("0.0.0.0", SERVER_PORT))
  server_socket.listen(10)

  # CONNECTION_LIST for the socket objects / address / port  
  # Add server socket to the list of readable connections
  CONNECTION_LIST.append([server_socket,"0.0.0.0",SERVER_PORT])

  print "Chat server started on port " + str(SERVER_PORT)
  if len(sys.argv) < 2:
    print "To establish serial connection enter the following details (example)"
    print "COM3"
  data = ''

  while 1:
    # Get the list sockets which are ready to be read through select
    socket_list = [item[0] for item in CONNECTION_LIST] #get first item of each item in CONNECTION_LIST
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    #passing the server socket as connection of potential readers
    
    
    for sock in read_sockets:
      #New connection
      if sock == server_socket:
        # Handle the case in which there is a new connection recieved through server_socket
        sockfd, addr = server_socket.accept()  #accept returns a new socket object, sockfd, and address of the other end of the socket
        CONNECTION_LIST.append([sockfd,addr[0],addr[1]])  #add the new socket to the list
        client_socket = sockfd                            #only relay to latest client, log here
        print "Client %s, %s connected" % (addr[0],addr[1])
        print len(CONNECTION_LIST)
      #Some incoming message from a client
      elif sock == client_socket:  # Data received from client, process it
        try:
          #In Windows, sometimes when a TCP program closes abruptly,
          # a "Connection reset by peer" exception will be thrown
          data = sock.recv(RECV_BUFFER)
          if data:    #Actually got data, send to SSH     
            #for some reason, data has some formatting characters
            #when printing, it loses the first letter. showing only printable characters fixes this
            data = "".join(ch for ch in data if (ord(ch)>31 and ord(ch)<126) or ord(ch) == 0 )            
            print data
            #if serial not connected yet, parse for serial details
            if serialConn == 0 and len(data)>3:
              print "Setting serial connection port to: " + data
              comString = data
              if comString != "":
                #establish serial connection here
                ser.port = comString
                ser.baudrate = 115200
                ser.bytesize = serial.EIGHTBITS #number of bits per bytes
                ser.parity = serial.PARITY_NONE #set parity check: no parity
                ser.stopbits = serial.STOPBITS_ONE #number of stop bits
                #ser.timeout = None          #block read
                ser.timeout = 1            #non-block read
                #ser.timeout = 2              #timeout block read
                ser.xonxoff = False     #disable software flow control
                ser.rtscts = False     #disable hardware (RTS/CTS) flow control
                ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
                ser.writeTimeout = 2     #timeout for write
                try: 
                    ser.open()
                except Exception, e:
                    print "error open serial port: " + str(e)
                if ser.isOpen():
                  serialConn=1
                  ser.flushInput() #flush input buffer, discarding all its contents
                  ser.flushOutput()#flush output buffer, aborting current output 
            elif len(data) > 3:
              print "Writing to serial device: " + data
              ser.write(data)
              
          elif (len(data) == 0): #disconnected
            print 'client disconnected'
            toremove = [element for element in CONNECTION_LIST if element[0] == sock]
            removeIndex = CONNECTION_LIST.index(toremove[0])
            del CONNECTION_LIST[removeIndex]
            sock.close()
            ser.close()
            serialConn=0
          # client disconnected, so remove from socket list
        except Exception as e:
          #print "I/O error {0} : {1}".format(e.errno, e.strerror)
          print "Error:", sys.exc_info()[0]
          print "Client (%s, %s) is offline" % addr
          sock.close()
          toremove = [element for element in CONNECTION_LIST if element[0] == sock]
          removeIndex = CONNECTION_LIST.index(toremove[0])
          del CONNECTION_LIST[removeIndex]
          continue
      else:
        client_socket = sock