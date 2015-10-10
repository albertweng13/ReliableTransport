import random

from BasicTest import *

"""
This tests random packet drops. We randomly decide to drop about half of the
packets that go through the forwarder in either direction.

Note that to implement this we just needed to override the handle_packet()
method -- this gives you an example of how to extend the basic test case to
create your own.
"""
class DropFirstAckTest(BasicTest):
    def __init__(self, forwarder, input_file):
        BasicTest.__init__(self, forwarder, input_file)
        self.myname = "DropFirstAckTest"
        self.dropCount = 0

    def handle_packet(self):
        for p in self.forwarder.in_queue:
            msgtype, seqno = self.split_packet(p.full_packet)[:2]
            #print "seen %s, %s" % (msgtype,seqno)
            if self.dropCount <1 and msgtype == "ack":
                print "dropping %s %s" %(msgtype, seqno)
                self.dropCount+=1
            else:
                self.forwarder.out_queue.append(p)

        # empty out the in_queue
        self.forwarder.in_queue = []


    def split_packet(self, message):
        pieces = message.split('|')
        msg_type, seqno = pieces[0:2] # first two elements always treated as msg type and seqno
        checksum = pieces[-1] # last is always treated as checksum
        data = '|'.join(pieces[2:-1]) # everything in between is considered data
        return msg_type, seqno, data, checksum

class DropFirstStartPacketTest(BasicTest):
    def __init__(self, forwarder, input_file):
        BasicTest.__init__(self, forwarder, input_file)
        self.myname = "DropFirstStartPacketTest"
        self.dropCount = 0

    def handle_packet(self):
        for p in self.forwarder.in_queue:
            msgtype, seqno = self.split_packet(p.full_packet)[:2]
            if self.dropCount < 1 and msgtype == "start":
                print "dropping %s" % (msgtype)
                self.dropCount+=1
            else:
                self.forwarder.out_queue.append(p)

        # empty out the in_queue
        self.forwarder.in_queue = []

    def split_packet(self, message):
        pieces = message.split('|')
        msg_type, seqno = pieces[0:2] # first two elements always treated as msg type and seqno
        checksum = pieces[-1] # last is always treated as checksum
        data = '|'.join(pieces[2:-1]) # everything in between is considered data
        return msg_type, seqno, data, checksum