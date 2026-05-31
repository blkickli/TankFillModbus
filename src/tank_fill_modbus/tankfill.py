'''
TankFill - A simulation of filling a tank with a variable speed pump.

Brad L. Kicklighter, P.E.
4-15-2022
'''

__author__ = "Brad L. Kicklighter, P.E."
__version__ = "2026.05.31"

import math
import csv
import time
from userpaths import get_my_documents
from .repeatedtimer import RepeatedTimer
from .physical_constants import DENSITY_WATER


class TankFill(object):
  '''
  Class to represent a cylindrical tank with variable flow rate input 
  from a variable speed pump. Water flows out of tank at bottom by
  gravity.
  
  Set parameters of system when creating object.
  Calling begin() function starts periodic timer that calls 
  _calc_water_height(). Calling end() ends the simulation.
  Call set_plc_pump_speed() to set current pump speed from PLC
  and calculate input flow rate. Call get_plc_water_height() to get
  water height scaled for PLC. Call set_plc_set_point to set the set
  point from the PLC and call get_plc_set_point to get the set
  point from the PLC.
  '''
  
  ####################################################################
  #Public Interface
  ####################################################################
  def __init__(self, tank_diameter, tank_height, tau, max_inflow, delta_t, max_plc_pump_speed, max_plc_water_height):
    '''
    Initialization of TankFill object.
    
    :param tank_diameter: Diameter of tank (m)
    :param tank_height: Height of tank (m)
    :param tau: Time constant of tank outflow (s)
    :param max_inflow: Maximum flow rate of pump (kg/s)
    :param delta_t: Simulation time step (s)
    :param max_plc_pump_speed: Maximum pump speed from PLC
    :param max_plc_water_height: Maximum water height to PLC
    '''
    
    # System Properties
    self.tank_diameter = tank_diameter  # Tank diameter in meters (m)
    self.tank_height = tank_height  # Tank height in meters (m)
    self.tank_area = self._area_circle(self.tank_diameter)  # Tank base area in square meters (m^2)
    self.tank_volume = self._volume_cyl(self.tank_area, self.tank_height)  # Tank volume in cubic meters (m^3)
    self.tau = tau  # System time constant in seconds (s)
    self.max_inflow = max_inflow  # Maximum input flow rate in kilograms per second (kg/s)
    self.delta_t = delta_t  # Simulation time step in seconds (s)
    self.documents_path = get_my_documents()
    
    # PLC Properties
    self.max_plc_pump_speed = max_plc_pump_speed  # Maximum pump speed from PLC
    self.max_plc_water_height = max_plc_water_height  # Maximum water height to PLC
    
    # Current Values
    self.inflow = 0.0  # Current input flow rate in kilograms per second (kg/s) (0.0 to max_inflow)
    self.water_height = 0.0  # Current height of water in meters (m) (0.0 to tank_height)
    self.plc_water_height = 0  # Current height of water scaled for PLC (integer 0 to max_plc_water_height)
    self.plc_pump_speed = 0  # Current pump speed from PLC (integer 0 to max_plc_pump_speed)
    self.plc_set_point = 0  # Current set point (not used by model, just part of data collection)
    
    # Simulation data
    self.sim_data = []
    self._append_sim_data_header()
    self.start_time = time.perf_counter()  # Get start time of simulation
    self.last_data_file = ''  # Path and name of last data file saved
    
    # Timer Thread
    self.timer = RepeatedTimer(self.delta_t, self._calc_water_height)
    
  def begin(self):
    '''
    Start tank simulation.
    '''
    self.timer.start()  # RepeatedTimer self starts so this is not necessary

  def end(self):
    '''
    End tank simulation.
    '''
    self.timer.stop()
  
  def set_plc_pump_speed(self, plc_pump_speed):
    '''
    Clamps PLC pump speed, stores value, and calculates input flow rate.
    
    :param plc_pump_speed: pump speed from PLC (0 to max_plc_pump_speed)
    '''
    self.plc_pump_speed = max(min(plc_pump_speed, self.max_plc_pump_speed), 0)
    self._calc_inflow()
    
  def get_plc_pump_speed(self):
    '''
    Returns the current pump speed from the PLC.
    
    :returns: pump speed (0 to max_plc_pump_speed)
    '''
    return self.plc_pump_speed
    
  def get_plc_water_height(self):
    '''
    Returns the current water height scaled for PLC.
    
    :returns: water height (0 to max_plc_water_height)
    '''
    return self.plc_water_height
    
  def get_plc_set_point(self):
    '''
    Returns the current set point from the PLC.
    
    :returns: set point
    '''
    return self.plc_set_point

  def set_plc_set_point(self, set_point):
    '''
    Sets the current set point from the PLC.
    '''
    self.plc_set_point = set_point
    
  def clear_sim_data(self):
    '''
    Clears simulation data.
    '''
    self.sim_data.clear()
    self._append_sim_data_header()
    self.start_time = time.perf_counter()
    
  def save_sim_data(self):
    '''
    Save simulation data in documents folder with file name containing current date and time. Simulation data is cleared after save.
    '''
    self.last_data_file = self.documents_path + "\\" + "simulation_data_" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
    with open(self.last_data_file, 'w', newline='') as csvfile:
      csvwriter = csv.writer(csvfile)
      csvwriter.writerows(self.sim_data)
    self.clear_sim_data()

  def get_last_data_file(self):
    '''
    Gets path and name of last data file saved.
    
    :returns: path and name of last data file saved
    '''
    return self.last_data_file
  
  ####################################################################
  #Private Interface    
  ####################################################################
  def _clamp_height(self, val):
    '''
    Clamps a water height in meters (m) to 0.0 to tank_height.
    
    :param val: water height (m)
    :returns: clamped height (m)
    '''  
    return max(min(val, self.tank_height), 0.0)
  
  # TODO: move area and volume functions to their own file
  def _area_circle(self, diameter):
    '''
    Calculates the area of a circle.
    
    :param diameter: diameter of circle
    :returns: area of circle
    '''
    return math.pi * (diameter / 2) ** 2
  
  def _volume_cyl(self, area, height):
    '''
    Calculates the volume of a cylinder.
    
    :param area: area of cylinder base
    :param height: height of cylinder
    :returns: volume of cylinder
    '''
    return area * height
    
  def _calc_water_height(self):
    '''
    Calculates current water height in meters (m) and scaled for PLC. Height is clamped. Appends simulation data to list.
    '''
    self.water_height = self._clamp_height(self.water_height + self.delta_t * (self.inflow / (DENSITY_WATER * self.tank_area) - self.water_height / self.tau))
    self._calc_plc_water_height()
    self._append_sim_data()
    
  def _calc_plc_water_height(self):
    '''
    Calculates the water height as an integer scaled for the PLC.
    '''
    self.plc_water_height = int(round(self.max_plc_water_height * self.water_height / self.tank_height))
    
  def _calc_pump_mtr_frac(self):
    '''
    Calculates the pump motor fraction based on the pump speed from the PLC.
    
    :returns: pump motor drive fraction (0.0 to 1.0)
    '''
    return float(self.plc_pump_speed) / float(self.max_plc_pump_speed)
    
  def _calc_inflow(self):
    '''
    Calculates current input flow rate in kilograms per second (kg/s) based on pump motor percentage.
    
    :returns: input flow rate (kg/s)
    '''
    self.inflow = self._calc_pump_mtr_frac() * self.max_inflow
    return self.inflow
  
  def _calc_outflow(self):
    '''
    Calculates current output flow rate in kilograms per second (kg/s).
    
    :returns: output flow rate (kg/s)
    '''
    return DENSITY_WATER * self.water_height * self.tank_area / self.tau

  def _append_sim_data(self):
    '''
    Appends current time, PLC pump speed, PLC water height, and PLC set point to simulation data.
    '''
    self.sim_data.append([time.perf_counter() - self.start_time, 
                         self.get_plc_pump_speed(), 
                         self.get_plc_water_height(), 
                         self.get_plc_set_point()])
    
  def _append_sim_data_header(self):
    '''
    Appends header record to simulation data.
    '''
    self.sim_data.append(["Time (s)", "Pump Speed", "Water Height", 
                          "Set Point"])
    