import random

from BasicTest import *

"""
This tests random packet drops. We randomly decide to drop about half of the
packets that go through the forwarder in either direction.

Note that to implement this we just needed to override the handle_packet()
method -- this gives you an example of how to extend the basic test case to
create your own.
"""
class RandomDropTest(BasicTest):
    def handle_packet(self):
        for p in self.forwarder.in_queue:
            if random.choice([True, False]):
                self.forwarder.out_queue.append(p)

        # empty out the in_queue
        self.forwarder.in_queue = []

    def result(self, receiver_outfile):
        """
        This should return some meaningful result. You could do something
        like check to make sure both the input and output files are identical,
        or that some other aspect of your test passed. This is called
        automatically once the forwarder has finished executing the test.

        You can return whatever you like, or even just print a message saying
        the test passed. Alternatively, you could use the return value to
        automate testing (i.e., return "True" for every test that passes,
        "False" for every test that fails).
        """
        if not os.path.exists(receiver_outfile):
            raise ValueError("No such file %s" % str(receiver_outfile))
        if self.files_are_the_same(self.input_file, receiver_outfile):
            print "Test passes!"
            return True
        else:
            print "Test fails: original file doesn't match received. :("
            wait = input("PRESS ENTER TO CONTINUE.")
            return False