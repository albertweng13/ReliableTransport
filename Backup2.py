import sys
import getopt
import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        self.window = []
        self.ackcounter = 0
        self.acktracker = 0
        self.seqno = 0
        self.msgtype = None
        self.msg = ""
        self.nxtmsg = ""
        super(Sender, self).__init__(dest, port, filename, debug)
        if sackMode:
            raise NotImplementedError #remove this line when you implement SACK
    # Main sending loop.
    def start(self):
        self.msg = self.infile.read(1)
        #creates window of 5 and sends 5
        while ((self.seqno < 5) & (self.msgtype != 'end')):
            self.shift_window()

        #sends rest of file and handles responses
        while ((len(self.window) != 0) & (self.msgtype != 'end')):
            response = self.receive(0.50)
            self.handle_response(response) #checks response and adjusts window if neccesary
        self.infile.close()
        self.window = []
        self.ackcounter = 0
        self.acktracker = 0
        self.seqno = 0
        self.msgtype = None
        self.msg = ""
        self.nxtmsg = ""

    def shift_window(self):
        if (len(self.window) < 5) & (self.msgtype != 'end'):
            self.nxtmsg = self.infile.read(1)
            #if next message is empty then its the end
            if self.nxtmsg == '':
                self.msgtype = 'end'
            #make the first one start
            elif self.seqno == 0:
                self.msgtype = 'start'
            #otherwise its a data
            else:
                self.msgtype = 'data'

            packet = self.make_packet(self.msgtype,self.seqno,self.msg)
            #print packet
            self.send(packet)
            self.window.append(packet)
            self.msg = self.nxtmsg
            self.seqno += 1
            #print ("shiftwindow")

    def handle_response(self,response):
        #if None then its a timeout
        msgtype, ack, data, checksum = self.split_packet(response)
        if (response==None):
            self.handle_timeout()
        # make sure checksum works
        elif Checksum.validate_checksum(response)==False:
            print "recv: %s <--- CHECKSUM FAILED" % response
        # if checksum works
        elif Checksum.validate_checksum(response):
            #if acktracker equal to ack that means repeat ack
            if self.acktracker == ack:
                self.handle_dup_ack(ack)
            #if acktracker is less than ack that means new ack
            if self.acktracker < ack:
                print self.acktracker
                self.handle_new_ack(ack)
                print self.acktracker
            

    def handle_timeout(self):
        windowsize = len(self.window)
        counter = 0
        while counter < windowsize:
            packet = self.window.pop(0)
            self.send(packet)
            self.window.append(packet)
            counter += 1

    def handle_new_ack(self, ack):
        #print ("hi")
        while (self.acktracker < int(ack)):
            self.window.pop(0)
            self.shift_window()
            #print ("hi in loop")
            self.acktracker += 1

    def handle_dup_ack(self, ack):
        msgtype, ack, data, checksum = self.split_packet(ack)
        pass

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
