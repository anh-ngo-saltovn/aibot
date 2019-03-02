import queue
import threading
import time
import os
from pydub import AudioSegment
from pydub.playback import play




class MyThread (threading.Thread):

    def __init__(self, threadID, name = None, delay = None):
        self.threadLock = threading.Lock()
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay
        self._please_stop = False
        self.status = 0
    def run(self):
        print ("Starting " + self.name)
        # Get lock to synchronize threads
        self.threadLock.acquire()
        if self.name == 'alarm':
            self.start_alarm(self.delay)
        # Free lock to release next thread
        self.threadLock.release()

    def start_alarm(self, delay):
        time.sleep(delay)
        self.status = 1
        alarm_file = "/home/pi/AI-Smart-Mirror/sample-audio-files/martian-gun.mp3"
        print ("%s: %s" % ('alarm', time.ctime(time.time())))
        while not self._please_stop:
            # os.system("mpg123 " + alarm_file)
            song = AudioSegment.from_mp3(alarm_file)
            play(song)
            time.sleep(2)


    def stop_alarm(self):
        print ("Stopping " + self.name)
        self._please_stop = True
        self.status = 0

# threadLock = threading.Lock()
# threads = []
#
# # Notify threads it's time to exit
# exitFlag = 1
# i = 0
# thread1 = myThread(1, "alarm", 20)
# while i < 5:
#     time.sleep(1)
#     print(i)
#     if i == 1:
#         # Create new threads
#         thread1.start()
#         threads.append(thread1)
#     i += 1
# time.sleep(30)
# print ("stop")
# thread1.stop_alarm()
#
#
# # Wait for all threads to complete
# for t in threads:
#    t.join()
# print ("Exiting Main Thread")