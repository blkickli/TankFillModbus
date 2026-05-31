'''
RepeatedTimer - Library to schedule a periodic task.
From eraoul who modified it from MestreLion.
https://stackoverflow.com/questions/474528/how-to-repeatedly-execute-a-function-every-x-seconds
repeatedtimer.py

Brad L. Kicklighter, P.E.
1-2-2023

Usage Example:
from time import sleep

def hello(name):
    print "Hello %s!" % name

print "starting..."
rt = RepeatedTimer(1, hello, "World") # it auto-starts, no need of rt.start()
try:
    sleep(5) # your long-running job goes here...
finally:
    rt.stop() # better in a try/finally block to make sure the program ends!
'''

__author__ = "Brad L. Kicklighter, P.E."
__version__ = "2023.01.02"

import threading 
import time

class RepeatedTimer(object):
  """Repeatedly executes a function at a specified interval."""
  def __init__(self, interval, function, *args, **kwargs):
    """Initializes the RepeatedTimer with the specified interval and function."""
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.next_call = time.time()
    self.start()

  def _run(self):
    """Runs the scheduled function and schedules the next call."""
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    """Starts the timer to execute the function at the specified interval."""
    if not self.is_running:
      self.next_call += self.interval
      self._timer = threading.Timer(self.next_call - time.time(), self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    """Stops the timer and cancels any scheduled function calls."""
    self._timer.cancel()
    self.is_running = False
    