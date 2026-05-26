'''
unitconv - A set of unit conversion functions.
unitconv.py

Brad L. Kicklighter, P.E.
4-15-2022
'''

__author__ = "Brad L. Kicklighter, P.E."
__version__ = "2022.04.16"


def m_to_mm(val):
  '''
  Converts distances in meters (m) to millimeters (mm).
  
  :param val: distance (m) to be converted
  :returns: converted distance (mm)
  '''
  return val * 1000.0

def mm_to_m(val):
  '''
  Converts distances in millimeters (mm) to meters (m).
  
  :param val: distance (mm) to be converted
  :returns: converted distance (m)
  '''
  return val / 1000.0

def sq_m_to_sq_mm(val):
  '''
  Converts areas in square meters (m^2) to square millimeters (mm^2).
  
  :param val: area (m^2) to be converted
  :returns: converted area (mm^2)
  '''
  return val * 1.0e6

def sq_mm_to_sq_m(val):
  '''
  Converts areas in square millimeters (mm^2) to square meters (m^2).
  
  :param val: area (mm^2) to be converted
  :returns: converted area (m^2)
  '''
  return val / 1.0e6

def cu_m_to_cu_mm(val):
  '''
  Converts volumes in cubic meters (m^3) to cubic millimeters (mm^3).
  
  :param val: volume (m^3) to be converted
  :returns: converted volume (mm^3)
  '''
  return val * 1.0e9

def cu_mm_to_cu_m(val):
  '''
  Converts volumes in cubic millimeters (mm^3) to cubic meters (m^3).
  
  :param val: volume (mm^3) to be converted
  :returns: converted volume (m^3)
  '''
  return val / 1.0e9

def cu_m_to_L(val):
  '''
  Converts volumes in cubic meters (m^3) to liters (L).
  
  :param val: volume (m^3) to be converted
  :returns: converted volume (L)
  '''
  return val * 1000.0
  
def L_to_cu_m(val):
  '''
  Converts volumes in liters (L) to cubic meters (m^3).
  
  :param val: volume (L) to be converted
  :returns: converted volume (m^3)
  '''
  return val / 1000.0

def L_to_cu_mm(val):
  '''
  Converts volumes in liters (L) to cubic millimeters (mm^3).
  
  :param val: volume (L) to be converted
  :returns: converted volume (mm^3)
  '''
  return cu_m_to_cu_mm(L_to_cu_m(val))

def cu_mm_to_L(val):
  '''
  Converts volumes in cubic millimeters (mm^3) to liters (L).
  
  :param val: volume (mm^3) to be converted
  :returns: converted volume (L)
  '''
  return cu_m_to_L(cu_mm_to_cu_m(val))

def min_to_s(val):
  '''
  Converts times in minutes (min) to seconds (s).
  
  :param val: time (min) to be converted
  :returns: converted time (s)
  '''
  return val * 60.0
  
def s_to_min(val):
  '''
  Converts times in seconds (s) to minutes (min).
  
  :param val: time (s) to be converted
  :returns: converted time (min)
  '''
  return val / 60.0
  
def s_to_ms(val):
  '''
  Converts times in seconds (s) to milliseconds (ms).
  
  :param val: time (s) to be converted
  :returns: converted time (ms)
  '''
  return val * 1000

def ms_to_s(val):
  '''
  Converts times in milliseconds (ms) to seconds (s).
  
  :param val: time (ms) to be converted
  :returns: converted time (s)
  '''
  return val / 1000

def inv_min_to_inv_s(val):
  '''
  Converts rates in inverse minutes (1/min) to inverse seconds (1/s).
  
  :param val: rate (1/min) to be converted
  :returns: converted rate (1/s)
  '''
  return val / 60.0

def inv_s_to_inv_min(val):
  '''
  Converts rates in inverse seconds (1/s) to inverse minutes (1/min).
  
  :param val: rate (1/s) to be converted
  :returns: converted rate (1/min)
  '''
  return val * 60.0
  
def mass_flow_to_vol_flow(val, density):
  '''
  Converts mass flow rates in kilograms per second (kg/s) to volume flow rates in cubic meters per second (m^3/s) using density in kilograms per cubic meter (kg/m^3).
  
  :param val: mass flow rate (kg/s) to be converted
  :param density: density (kg/m^3)
  :returns: converted volume flow rate (m^3/s)
  '''
  return val / density

def vol_flow_to_mass_flow(val, density):
  '''
  Converts volume flow in cubic meters per second (m^3/s) to mass flow rates in kilograms per second (kg/s) using density in kilograms per cubic meter (kg/m^3).
  
  :param val: volume flow rate (m^3/s) to be converted
  :param density: (kg/m^3)
  :returns: converted mass flow rate (kg/s)
  '''
  return val * density
