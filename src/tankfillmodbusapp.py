'''
TankFillModbus - Tank fill simulation that communicates with a PLC via Modbus RTU
tankfillmodbusapp.py

Brad L. Kicklighter, P.E.
1-3-2022
'''

__author__ = "Brad L. Kicklighter, P.E."
__version__ = "2024.11.18"

from tankfill import *
import pymodbus.client as ModbusClient
import time
import tkinter as tk
from tkinter import ttk

# Modbus TCP Constants
HOST = '192.168.1.44'         # PLC IP address
# Tank Fill Simulation Constants
WATER_HEIGHT_ADDR = 0x0000    # DS1
PUMP_SPEED_ADDR = 0x0001      # DS2
SET_POINT_ADDR = 0x0002       # DS3
TANK_DIAMETER = 0.25          # Diameter of tank (m)
TANK_HEIGHT = 0.3             # Height of tank (m)
TAU = 25                      # Time constant of out flow of tank (s)
MAX_IN_FLOW = 0.5             # Maximum input flow rate to tank (kg/s)
TIME_STEP = 0.05              # Simulation time step (s)
PLC_MAX_PUMP_SPEED = 10000    # Maximum pump speed (PLC)
PLC_MAX_WATER_HEIGHT = 10000  # Maximum water height (PLC)
# Tank Animation Constants
ANI_TANK_HEIGHT = 100         # pixels
ANI_TANK_WIDTH = int(ANI_TANK_HEIGHT * TANK_DIAMETER / TANK_HEIGHT)  # pixels
CANVAS_BORDER = 20            # pixels
CANVAS_HEIGHT = ANI_TANK_HEIGHT + 2 * CANVAS_BORDER  # pixels
CANVAS_WIDTH = ANI_TANK_WIDTH + 2 * CANVAS_BORDER  # pixels
TANK_X0 = (CANVAS_WIDTH - ANI_TANK_WIDTH ) // 2  # pixels
TANK_Y0 = (CANVAS_HEIGHT - ANI_TANK_HEIGHT) // 2  # pixels
TANK_X1 = TANK_X0 + ANI_TANK_WIDTH  # pixels
TANK_Y1 = TANK_Y0 + ANI_TANK_HEIGHT  # pixels

class App(tk.Tk):
  """tkinter app for the Tank Fill Modbus simulation."""
  def __init__(self):
    """Initializes the tkinter app."""
    tk.Tk.__init__(self)
    
    # Attributes
    self.client = None  # Modbus client
    self.t = None       # TankFill object
    
    # App Window
    self.title('Tank Fill Modbus')
    self.exiting = False
    self.log = tk.Text(self, state='disabled', width=60, height=20, wrap='char')
    self.log.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
    self.canvas = tk.Canvas(self, height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
    self.tankoutline = self.canvas.create_line(TANK_X0 - 1, TANK_Y0, TANK_X0 - 1, TANK_Y1, TANK_X1, TANK_Y1, TANK_X1, TANK_Y0, fill='black')
    self.water = self.canvas.create_rectangle(TANK_X0, TANK_Y1, TANK_X1, TANK_Y1, fill='blue', width=0)
    self.canvas.grid(row=0, column=3, padx=5, pady=5)
    self.clear_btn = tk.Button(self, text='Clear Data', command=self.on_clear_data)
    self.clear_btn.grid(row=1, column=0, padx=5, pady=5)
    self.save_btn = tk.Button(self, text='Save Data', command=self.on_save_data)
    self.save_btn.grid(row=1, column=1, padx=5, pady=5)
    self.save_exit_btn = tk.Button(self, text='Save Data & Exit', command=self.save_exit_app)
    self.save_exit_btn.grid(row=1, column=2, padx=5, pady=5)
    self.exit_btn = tk.Button(self, text='Exit', command=self.exit_app)
    self.exit_btn.grid(row=1, column=3, padx = 5, pady=5)
    self.write_to_log('tankfillmodbusapp ')
    self.write_to_log(__version__)
    self.write_to_log('\n')
    self.client = ModbusClient.ModbusTcpClient(host=HOST)
    self.client.connect()
    if self.client.is_socket_open():
      self.write_to_log('Connected to ' + HOST + '\n')
      self.t = TankFill(TANK_DIAMETER, TANK_HEIGHT, TAU, MAX_IN_FLOW, 
                        TIME_STEP, PLC_MAX_PUMP_SPEED, PLC_MAX_WATER_HEIGHT)
      self.do_modbus_comm()
    else:
      self.write_to_log('Not connected')
      self.clear_btn.configure(state='disabled')
      self.save_btn.configure(state='disabled')
      self.save_exit_btn.configure(state='disabled')
  
  def write_to_log(self, msg):
    """Writes a message to the log text box."""
    self.log['state'] = 'normal'
    self.log.insert('end', msg)
    self.log['state'] = 'disabled'
    
  def on_clear_data(self):
    """Clears the simulation data."""
    self.t.clear_sim_data()
    self.write_to_log('Data cleared\n')
    
  def on_save_data(self):
    """Saves the simulation data to a CSV file."""
    self.t.save_sim_data()
    self.write_to_log('Data saved: ')
    self.write_to_log(self.t.get_last_data_file())
    self.write_to_log('\n')
    
  def do_modbus_comm(self):
    """Performs Modbus communication with the PLC."""
    if not self.client.is_socket_open():
      self.write_to_log('Reconnecting\n')
      self.client.connect()
    if self.exiting == False:
      # Send current water height to the PLC
      wr = self.client.write_register(address=WATER_HEIGHT_ADDR, 
                                      value=self.t.get_plc_water_height())
      # Ignore write errors for now
    if self.exiting == False:
      # Get the current desired pump speed and the current set point from the PLC
      rr = self.client.read_holding_registers(address=PUMP_SPEED_ADDR, count=2)
      if not rr.isError():
        self.t.set_plc_pump_speed(rr.registers[0])
        self.t.set_plc_set_point(rr.registers[1])
    if self.exiting == False:
      # Update tank animation
      self.update_tank_animation()
    if self.exiting == False:
      self.after(1, self.do_modbus_comm)
    
  def save_exit_app(self):
    """Saves the simulation data and exits the app."""
    if self.t != None:
      self.on_save_data()
    self.exit_app()
  
  def exit_app(self):
    """Exits the app and closes the Modbus connection."""
    self.exiting = True
    if self.client != None and self.client.is_socket_open() == True:
      self.client.close()
    self.destroy()
    
  def update_tank_animation(self):
    """Updates the tank animation based on the current water height."""
    plc_water_height = self.t.get_plc_water_height()
    ani_water_height = plc_water_height * ANI_TANK_HEIGHT // PLC_MAX_WATER_HEIGHT
    self.canvas.coords(self.water, TANK_X0, TANK_Y0 + ANI_TANK_HEIGHT - ani_water_height, TANK_X1, TANK_Y1)

def main():
  """Creates the tkinter app and runs the main loop."""
  root = App()
  root.mainloop()
  
if __name__ == "__main__":
  main()
  