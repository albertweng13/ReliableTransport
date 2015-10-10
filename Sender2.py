import sys
import getopt
import Checksum
from collections import deque
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        #for testing
        self.packetsize = 2
        self.printstatements = True

        #held variables
        self.window= []
        self.acktracker = 0
        self.windowgap = 0
        self.dupack = None 
        self.dupacktracker = 0
        super(Sender, self).__init__(dest, port, filename, debug)
        if sackMode: 
            # print ("sackmode time")
            self.sacklist = []
            #raise NotImplementedError #remove this line when you implement SACK
    # Main sending loop.
    def start(self):
        seqno = 0
        msg_type = None
        msg = self.infile.read(self.packetsize)
        while not msg_type =='end':
            #creates initial window
            while (seqno <5 and msg_type != 'end'):
                nxtmsg = self.infile.read(self.packetsize)
                #if next message is empty then its the end
                if nxtmsg == '':
                    msg_type = 'end'
                #make the first one start
                elif seqno == 0:
                    msg_type = 'start'
                #otherwise its a data
                else:
                    msg_type = 'data'

                packet = self.make_packet(msg_type,seqno,msg)
                #print packet
                self.send(packet)
                
                if self.printstatements:
                    print packet
                self.window.append(packet)
                msg = nxtmsg
                seqno += 1

            #for handle_new_ack, fills window back to 5 and sends packets.
            while (self.windowgap > 0 and msg_type != 'end' and len(self.window) <= 5):
                nxtmsg = self.infile.read(self.packetsize)
                #if next message is empty then its the end
                if nxtmsg == '':
                    msg_type = 'end'
                #make the first one start
                elif seqno == 0:
                    msg_type = 'start'
                #otherwise its a data
                else:
                    msg_type = 'data'

                packet = self.make_packet(msg_type,seqno,msg)
                
                if self.printstatements:
                    print packet
                self.send(packet)
                self.window.append(packet)
                msg = nxtmsg
                seqno += 1
                self.windowgap -= 1

            response = self.receive(0.50)
            
            if self.printstatements:
                print response
            self.handle_response(response)

        while(len(self.window) != 0):
            response=self.receive(0.50)
            
            if self.printstatements:
                print response
            self.handle_response(response)

        self.infile.close()

    def handle_response(self,response):
        if response == None:
            self.handle_timeout()
        # elif Checksum.validate_checksum(response) == False:
            
        #     # print "recv: %s <--- CHECKSUM FAILED" % response
        elif Checksum.validate_checksum(response):
            msgtype, ack, data, checksum = self.split_packet(response)
            if sackMode:
                split = ack.split(';')
                ack = int(split[0])
            else:
                ack = int(ack)

            if ack < self.acktracker:   
                # print ("rcv: buggy ack")
                response = self.receive(0.50)
                
                if printstatements:
                    print response
                self.handle_response(response)
            elif ack == self.acktracker:
                self.handle_dup_ack(ack)
            elif ack > self.acktracker:
                self.handle_new_ack(ack)
            

    def handle_timeout(self):
        windowsize = len(self.window)
        counter = 0
        while counter < windowsize:
            packet = self.window[counter]
            if sackMode:
                msgtype, seqno1, yolo, checksum = self.split_packet(packet)
                if int(seqno1) not in self.sacklist:
                    if self.printstatements:
                        print packet
                    
                    self.send(packet)
            else:
                if self.printstatements:
                    print packet
               
                self.send(packet)
            counter += 1

        self.dupacktracker = 0
        response = self.receive(0.50)
       
        if self.printstatements:
            print response
        self.handle_response(response)

    def handle_new_ack(self, ack):
        if sackMode:
            split = ack.split(';')
            ack1 = int(split[0])
            sack = split[1].split(',')
            for x in sack:
                if x != '' and int(x) not in self.sacklist:
                    self.sacklist.append(int(x))
        else:
            ack1 = int(ack)

        self.windowgap = ack1 - self.acktracker
        for x in range(0,self.windowgap):
            self.acktracker +=1
            self.window.pop(0)

    def handle_dup_ack(self, ack):
        if sackMode:
            split = ack.split(';')
            ack1 = int(split[0])
            sack = split[1].split(',')
            for x in sack:
                if x != ''and int(x) not in self.sacklist:
                    self.sacklist.append(int(x))
        else:
            ack1 = int(ack)

        if self.dupack == ack1:
            self.dupacktracker += 1
        else: 
            self.dupack = ack1
            self.dupacktracker = 1
        #resend first packet in window if 3 dup acks (not sackmode)
        #
        if self.dupacktracker >= 3:
            if sackMode:
                for x in self.window:
                    if not x in self.sacklist:
                        
                        if self.printstatements:
                            print ("dup_ack here")
                            print packet
                        
                        self.send(packet)
            else:
                packet = self.window[0]
                
                if self.printstatements:
                    print ("dup_ack here")
                    print packet
                
                self.send(packet)
            self.dupacktracker = 0

        response = self.receive(0.50)
        
        if self.printstatements:
            print response
        self.handle_response(response)

    def log(self, msg):
        if self.debug:
            print msg


'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"
        print "-k | --sack Enable selective acknowledgement mode"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest, port, filename, debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
