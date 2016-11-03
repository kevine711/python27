# ##### Started from online
#http://www.binarytides.com/python-socket-server-code-example/
#By Kevin Ersoy 

##### Script description
#this script has two main parts
# 1. A TCP server is opened for client connection (labwindows automation in this case).
# 2. During some init from the TCP connection, an SSH connection is established at a provided IP, user, pass.  
#    Further communication between the TCP connection and the SSH connection is passed through this channel. 
# Command Line Arguments (Optional):
# 1- IP of SSH server
# 2- Username
# 3- Password
# If not using command line arguments, first client must supply "ip:x.x.x.x" "user:xxxx" "pass:xxxx" before SSH connection
# will be established.

# Socket server in python using select function
import socket, select
import time  #used for sleep
import string
import sys
import paramiko

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
  SSH_user=""           # SSH Username
  SSH_pass="null"       # SSH Password
  SSH_serverIP=""       # SSH Server IP
  SSH_conn=0            # SSH Connection Status
  CONNECTION_LIST = []  # list of socket clients
  RECV_BUFFER = 4096
  RECV_BUFFER_SSH = 4096
  chan_BUFFER = 4096
  chan=""
  
  #Detect optional arguments for ip, user, pass
  if len(sys.argv) == 4:
    SSH_serverIP = sys.argv[1]
    SSH_user = sys.argv[2]
    SSH_pass = sys.argv[3]

  ssh = paramiko.SSHClient()
  #paramiko.util.log_to_file("filename.log")
  SERVER_PORT = 49589
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
  if len(sys.argv) < 4:
    print "To establish SSH connection enter the following details"
    print "ip:x.x.x.x"
    print "user:xxxx"
    print "pass:xxxx"
  data = ''

  while 1:
    # Get the list sockets which are ready to be read through select
    socket_list = [item[0] for item in CONNECTION_LIST] #get first item of each item in CONNECTION_LIST
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    #passing the server socket as connection of potential readers
    #Check for data from SSH connection if open
    if SSH_conn == 1:
      try:
        chan_BUFFER = chan.recv(4096)
      except:
        pass
      if chan_BUFFER != []:
        print chan_BUFFER
        try:
          client_socket.send(chan_BUFFER)
          chan_BUFFER = []
        except:
          pass
    else:
      print 'SSH not connected'
    
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
            #if SSH not connected yet, parse for SSH details
            if SSH_conn == 0:
              temp = data.split(':')
              if temp[0] == "ip":
                SSH_serverIP = temp[1].strip()
              elif temp[0] == "user":
                SSH_user = temp[1].strip()
              elif temp[0] == "pass":
                if len(temp)==2:
                  SSH_pass = temp[1].strip()
              if SSH_serverIP != "":
                if SSH_pass != "null":
                  if SSH_user != "":
                    SSH_conn = 1
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())   #Auto add to host keys
                    try:
                      ssh.connect(SSH_serverIP,22,username=SSH_user,password=SSH_pass)  #Open SSH connection
                      print "Success!! -- Server: ", SSH_serverIP, "   Us: ", SSH_user
                      chan = ssh.invoke_shell(term='vt100', width=80, height=24, width_pixels=0, height_pixels=0)                      #Open shell with server
                      chan.settimeout(1)
                    except paramiko.AuthenticationException:
                      print "Authentication problem   -- Server: ", SSH_serverIP, "   User: ", SSH_user
                      continue
                    
                    stdin, stdout, stderr = ssh.exec_command("uptime") 
                    type(stdin)        
                    print stdout.readlines()
            else:
              temp = data.split('kevinSSH:')
              if len(temp) == 2:
                print "Sending to SSH Server:" + temp[1]
                stdin, stdout, stderr = ssh.exec_command(temp[1] + '\n') 
                time.sleep(1)
                type(stdin)        
                print stdout.readlines()
              else:                                             #Not SSH command, command intended for server shell
                print "Sending to SSH Shell:" + data 
                chan.send(data + '\n')
          elif (len(data) == 0): #disconnected
            print 'client disconnected'
            toremove = [element for element in CONNECTION_LIST if element[0] == sock]
            removeIndex = CONNECTION_LIST.index(toremove[0])
            del CONNECTION_LIST[removeIndex]
            sock.close()
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