import snap7
import struct
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import concurrent.futures
from threading import Lock
from queue import Queue
import time

# --------------------------
# Configuration
# --------------------------
PLC_IP = '192.168.0.1'  # Default PLC IP (can be overridden via query param)
PLC_RACK = 0
PLC_SLOT = 1
PLC_PORT = 102
MAX_STRING_LENGTH = 254
MAX_WORKERS = 10  # Number of threads for concurrent operations
PLC_CONNECTION_POOL_SIZE = 3  # Number of PLC connections to maintain in pool
TAG_CONFIG = {
    'DB1_DBD0': {'db': 1, 'offset': 0, 'dtype': 'DINT'},
    'DB1_DBD4': {'db': 1, 'offset': 4, 'dtype': 'DINT'},
    'DB1_DBD5': {'db': 1, 'offset': 5, 'dtype': 'DINT'},
    'DB1_DBD6': {'db': 1, 'offset': 6, 'dtype': 'DINT'},
    'DB1_DBD7': {'db': 1, 'offset': 7, 'dtype': 'DINT'},
    'DB1_DBD8': {'db': 1, 'offset': 8, 'dtype': 'DINT'},
    'DB1_DBD9': {'db': 1, 'offset': 9, 'dtype': 'DINT'},
    'DB1_DBD10': {'db': 1, 'offset': 10, 'dtype': 'DINT'},
    'DB1_DBD12': {'db': 1, 'offset': 12, 'dtype': 'REAL'},
    'DB1_DBD16': {'db': 1, 'offset': 16, 'dtype': 'REAL'},
    'DB1_DBX24': {'db': 1, 'offset': 24, 'dtype': 'STRING', 'max_length': 254}, #Below Newly added tags from DB1_DBD65304 to DB1_DBD65432
    'DB1_DBD65304': {'db': 1, 'offset': 65304, 'dtype': 'DINT'},
    'DB1_DBD65308': {'db': 1, 'offset': 65308, 'dtype': 'DINT'},
    'DB1_DBD65312': {'db': 1, 'offset': 65312, 'dtype': 'DINT'},
    'DB1_DBD65316': {'db': 1, 'offset': 65316, 'dtype': 'DINT'},
    'DB1_DBD65320': {'db': 1, 'offset': 65320, 'dtype': 'DINT'},
    'DB1_DBD65324': {'db': 1, 'offset': 65324, 'dtype': 'DINT'},
    'DB1_DBD65328': {'db': 1, 'offset': 65328, 'dtype': 'DINT'},
    'DB1_DBD65332': {'db': 1, 'offset': 65332, 'dtype': 'DINT'},
    'DB1_DBD65336': {'db': 1, 'offset': 65336, 'dtype': 'DINT'},
    'DB1_DBD65340': {'db': 1, 'offset': 65340, 'dtype': 'DINT'},
    'DB1_DBD65344': {'db': 1, 'offset': 65344, 'dtype': 'DINT'},
    'DB1_DBD65348': {'db': 1, 'offset': 65348, 'dtype': 'DINT'},
    'DB1_DBD65352': {'db': 1, 'offset': 65352, 'dtype': 'DINT'},
    'DB1_DBD65356': {'db': 1, 'offset': 65356, 'dtype': 'DINT'},
    'DB1_DBD65360': {'db': 1, 'offset': 65360, 'dtype': 'DINT'},
    'DB1_DBD65364': {'db': 1, 'offset': 65364, 'dtype': 'DINT'},
    'DB1_DBD65368': {'db': 1, 'offset': 65368, 'dtype': 'DINT'},
    'DB1_DBD65372': {'db': 1, 'offset': 65372, 'dtype': 'DINT'},
    'DB1_DBD65376': {'db': 1, 'offset': 65376, 'dtype': 'DINT'},
    'DB1_DBD65380': {'db': 1, 'offset': 65380, 'dtype': 'DINT'},
    'DB1_DBD65384': {'db': 1, 'offset': 65384, 'dtype': 'DINT'},
    'DB1_DBD65388': {'db': 1, 'offset': 65388, 'dtype': 'DINT'},
    'DB1_DBD65392': {'db': 1, 'offset': 65392, 'dtype': 'DINT'},
    'DB1_DBD65396': {'db': 1, 'offset': 65396, 'dtype': 'DINT'},
    'DB1_DBD65400': {'db': 1, 'offset': 65400, 'dtype': 'DINT'},
    'DB1_DBD65404': {'db': 1, 'offset': 65404, 'dtype': 'DINT'},
    'DB1_DBD65408': {'db': 1, 'offset': 65408, 'dtype': 'DINT'},
    'DB1_DBD65412': {'db': 1, 'offset': 65412, 'dtype': 'DINT'},
    'DB1_DBD65416': {'db': 1, 'offset': 65416, 'dtype': 'DINT'},
    'DB1_DBD65420': {'db': 1, 'offset': 65420, 'dtype': 'DINT'},
    'DB1_DBD65424': {'db': 1, 'offset': 65424, 'dtype': 'DINT'},
    'DB1_DBD65428': {'db': 1, 'offset': 65428, 'dtype': 'DINT'},
    'DB1_DBD65432': {'db': 1, 'offset': 65432, 'dtype': 'DINT'},
  'DB2_DBD65304': {'db': 2, 'offset': 65304, 'dtype': 'DINT'},
  'DB2_DBD65308': {'db': 2, 'offset': 65308, 'dtype': 'DINT'},
  'DB2_DBD65312': {'db': 2, 'offset': 65312, 'dtype': 'DINT'},
  'DB2_DBD65316': {'db': 2, 'offset': 65316, 'dtype': 'DINT'},
  'DB2_DBD65320': {'db': 2, 'offset': 65320, 'dtype': 'DINT'},
  'DB2_DBD65324': {'db': 2, 'offset': 65324, 'dtype': 'DINT'},
  'DB2_DBD65328': {'db': 2, 'offset': 65328, 'dtype': 'DINT'},
  'DB2_DBD65332': {'db': 2, 'offset': 65332, 'dtype': 'DINT'},
  'DB2_DBD65336': {'db': 2, 'offset': 65336, 'dtype': 'DINT'},
  'DB2_DBD65340': {'db': 2, 'offset': 65340, 'dtype': 'DINT'},
  'DB2_DBD65344': {'db': 2, 'offset': 65344, 'dtype': 'DINT'},
  'DB2_DBD65348': {'db': 2, 'offset': 65348, 'dtype': 'DINT'},
  'DB2_DBD65352': {'db': 2, 'offset': 65352, 'dtype': 'DINT'},
  'DB2_DBD65356': {'db': 2, 'offset': 65356, 'dtype': 'DINT'},
  'DB2_DBD65360': {'db': 2, 'offset': 65360, 'dtype': 'DINT'},
  'DB2_DBD65364': {'db': 2, 'offset': 65364, 'dtype': 'DINT'},
  'DB2_DBD65368': {'db': 2, 'offset': 65368, 'dtype': 'DINT'},
  'DB2_DBD65372': {'db': 2, 'offset': 65372, 'dtype': 'DINT'},
  'DB2_DBD65376': {'db': 2, 'offset': 65376, 'dtype': 'DINT'},
  'DB2_DBD65380': {'db': 2, 'offset': 65380, 'dtype': 'DINT'},
  'DB2_DBD65384': {'db': 2, 'offset': 65384, 'dtype': 'DINT'},
  'DB2_DBD65388': {'db': 2, 'offset': 65388, 'dtype': 'DINT'},
  'DB2_DBD65392': {'db': 2, 'offset': 65392, 'dtype': 'DINT'},
  'DB2_DBD65396': {'db': 2, 'offset': 65396, 'dtype': 'DINT'},
'DB2_DBD65400': {'db': 2, 'offset': 65400, 'dtype': 'DINT'},
'DB2_DBD65404': {'db': 2, 'offset': 65404, 'dtype': 'DINT'},
'DB2_DBD65408': {'db': 2, 'offset': 65408, 'dtype': 'DINT'},
'DB2_DBD65412': {'db': 2, 'offset': 65412, 'dtype': 'DINT'},
'DB2_DBD65416': {'db': 2, 'offset': 65416, 'dtype': 'DINT'},
'DB2_DBD65420': {'db': 2, 'offset': 65420, 'dtype': 'DINT'},
'DB2_DBD65424': {'db': 2, 'offset': 65424, 'dtype': 'DINT'},
'DB2_DBD65428': {'db': 2, 'offset': 65428, 'dtype': 'DINT'},
'DB2_DBD65432': {'db': 2, 'offset': 65432, 'dtype': 'DINT'},#///////DINT end String Started
'DB1_DBX24': {'db': 1, 'offset': 24, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX280': {'db': 1, 'offset': 280, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX536': {'db': 1, 'offset': 536, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX792': {'db': 1, 'offset': 792, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX1048': {'db': 1, 'offset': 1048, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX1304': {'db': 1, 'offset': 1304, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX1560': {'db': 1, 'offset': 1560, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX1816': {'db': 1, 'offset': 1816, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX2072': {'db': 1, 'offset': 2072, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX2328': {'db': 1, 'offset': 2328, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX2584': {'db': 1, 'offset': 2584, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX2840': {'db': 1, 'offset': 2840, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX3096': {'db': 1, 'offset': 3096, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX3352': {'db': 1, 'offset': 3352, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX3608': {'db': 1, 'offset': 3608, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX3864': {'db': 1, 'offset': 3864, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX4120': {'db': 1, 'offset': 4120, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX4376': {'db': 1, 'offset': 4376, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX4632': {'db': 1, 'offset': 4632, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX4888': {'db': 1, 'offset': 4888, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX5144': {'db': 1, 'offset': 5144, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX5400': {'db': 1, 'offset': 5400, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX5656': {'db': 1, 'offset': 5656, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX5912': {'db': 1, 'offset': 5912, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX6168': {'db': 1, 'offset': 6168, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX6424': {'db': 1, 'offset': 6424, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX6680': {'db': 1, 'offset': 6680, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX6936': {'db': 1, 'offset': 6936, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX7192': {'db': 1, 'offset': 7192, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX7448': {'db': 1, 'offset': 7448, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX7704': {'db': 1, 'offset': 7704, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX7960': {'db': 1, 'offset': 7960, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX8216': {'db': 1, 'offset': 8216, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX8472': {'db': 1, 'offset': 8472, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX8728': {'db': 1, 'offset': 8728, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX8984': {'db': 1, 'offset': 8984, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX9240': {'db': 1, 'offset': 9240, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX9496': {'db': 1, 'offset': 9496, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX9752': {'db': 1, 'offset': 9752, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX10008': {'db': 1, 'offset': 10008, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX10264': {'db': 1, 'offset': 10264, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX10520': {'db': 1, 'offset': 10520, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX10776': {'db': 1, 'offset': 10776, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX11032': {'db': 1, 'offset': 11032, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX11288': {'db': 1, 'offset': 11288, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX11544': {'db': 1, 'offset': 11544, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX11800': {'db': 1, 'offset': 11800, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX12056': {'db': 1, 'offset': 12056, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX12312': {'db': 1, 'offset': 12312, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX12568': {'db': 1, 'offset': 12568, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX12824': {'db': 1, 'offset': 12824, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX13080': {'db': 1, 'offset': 13080, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX13336': {'db': 1, 'offset': 13336, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX13592': {'db': 1, 'offset': 13592, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX13848': {'db': 1, 'offset': 13848, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX14104': {'db': 1, 'offset': 14104, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX14360': {'db': 1, 'offset': 14360, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX14616': {'db': 1, 'offset': 14616, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX14872': {'db': 1, 'offset': 14872, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX15128': {'db': 1, 'offset': 15128, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX15384': {'db': 1, 'offset': 15384, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX15640': {'db': 1, 'offset': 15640, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX15896': {'db': 1, 'offset': 15896, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX16152': {'db': 1, 'offset': 16152, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX16408': {'db': 1, 'offset': 16408, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX16664': {'db': 1, 'offset': 16664, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX16920': {'db': 1, 'offset': 16920, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX17176': {'db': 1, 'offset': 17176, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX17432': {'db': 1, 'offset': 17432, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX17688': {'db': 1, 'offset': 17688, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX17944': {'db': 1, 'offset': 17944, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX18200': {'db': 1, 'offset': 18200, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX18456': {'db': 1, 'offset': 18456, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX18712': {'db': 1, 'offset': 18712, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX18968': {'db': 1, 'offset': 18968, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX19224': {'db': 1, 'offset': 19224, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX19480': {'db': 1, 'offset': 19480, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX19736': {'db': 1, 'offset': 19736, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX19992': {'db': 1, 'offset': 19992, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX20248': {'db': 1, 'offset': 20248, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX20504': {'db': 1, 'offset': 20504, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX20760': {'db': 1, 'offset': 20760, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX21016': {'db': 1, 'offset': 21016, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX21272': {'db': 1, 'offset': 21272, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX21528': {'db': 1, 'offset': 21528, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX21784': {'db': 1, 'offset': 21784, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX22040': {'db': 1, 'offset': 22040, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX22296': {'db': 1, 'offset': 22296, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX22552': {'db': 1, 'offset': 22552, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX22808': {'db': 1, 'offset': 22808, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX23064': {'db': 1, 'offset': 23064, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX23320': {'db': 1, 'offset': 23320, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX23576': {'db': 1, 'offset': 23576, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX23832': {'db': 1, 'offset': 23832, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX24088': {'db': 1, 'offset': 24088, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX24344': {'db': 1, 'offset': 24344, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX24600': {'db': 1, 'offset': 24600, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX24856': {'db': 1, 'offset': 24856, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX25112': {'db': 1, 'offset': 25112, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX25368': {'db': 1, 'offset': 25368, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX25624': {'db': 1, 'offset': 25624, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX25880': {'db': 1, 'offset': 25880, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX26136': {'db': 1, 'offset': 26136, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX26392': {'db': 1, 'offset': 26392, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX26648': {'db': 1, 'offset': 26648, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX26904': {'db': 1, 'offset': 26904, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX27160': {'db': 1, 'offset': 27160, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX27416': {'db': 1, 'offset': 27416, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX27672': {'db': 1, 'offset': 27672, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX27928': {'db': 1, 'offset': 27928, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX28184': {'db': 1, 'offset': 28184, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX28440': {'db': 1, 'offset': 28440, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX28696': {'db': 1, 'offset': 28696, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX28952': {'db': 1, 'offset': 28952, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX29208': {'db': 1, 'offset': 29208, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX29464': {'db': 1, 'offset': 29464, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX29720': {'db': 1, 'offset': 29720, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX29976': {'db': 1, 'offset': 29976, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX30232': {'db': 1, 'offset': 30232, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX30488': {'db': 1, 'offset': 30488, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX30744': {'db': 1, 'offset': 30744, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX31000': {'db': 1, 'offset': 31000, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX31256': {'db': 1, 'offset': 31256, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX31512': {'db': 1, 'offset': 31512, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX31768': {'db': 1, 'offset': 31768, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX32024': {'db': 1, 'offset': 32024, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX32280': {'db': 1, 'offset': 32280, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX32536': {'db': 1, 'offset': 32536, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX32792': {'db': 1, 'offset': 32792, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX33048': {'db': 1, 'offset': 33048, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX33304': {'db': 1, 'offset': 33304, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX33560': {'db': 1, 'offset': 33560, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX33816': {'db': 1, 'offset': 33816, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX34072': {'db': 1, 'offset': 34072, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX34328': {'db': 1, 'offset': 34328, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX34584': {'db': 1, 'offset': 34584, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX34840': {'db': 1, 'offset': 34840, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX35096': {'db': 1, 'offset': 35096, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX35352': {'db': 1, 'offset': 35352, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX35608': {'db': 1, 'offset': 35608, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX35864': {'db': 1, 'offset': 35864, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX36120': {'db': 1, 'offset': 36120, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX36376': {'db': 1, 'offset': 36376, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX36632': {'db': 1, 'offset': 36632, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX36888': {'db': 1, 'offset': 36888, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX37144': {'db': 1, 'offset': 37144, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX37400': {'db': 1, 'offset': 37400, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX37656': {'db': 1, 'offset': 37656, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX37912': {'db': 1, 'offset': 37912, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX38168': {'db': 1, 'offset': 38168, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX38424': {'db': 1, 'offset': 38424, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX38680': {'db': 1, 'offset': 38680, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX38936': {'db': 1, 'offset': 38936, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX39192': {'db': 1, 'offset': 39192, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX39448': {'db': 1, 'offset': 39448, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX39704': {'db': 1, 'offset': 39704, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX39960': {'db': 1, 'offset': 39960, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX40216': {'db': 1, 'offset': 40216, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX40472': {'db': 1, 'offset': 40472, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX40728': {'db': 1, 'offset': 40728, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX40984': {'db': 1, 'offset': 40984, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX41240': {'db': 1, 'offset': 41240, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX41496': {'db': 1, 'offset': 41496, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX41752': {'db': 1, 'offset': 41752, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX42008': {'db': 1, 'offset': 42008, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX42264': {'db': 1, 'offset': 42264, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX42520': {'db': 1, 'offset': 42520, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX42776': {'db': 1, 'offset': 42776, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX43032': {'db': 1, 'offset': 43032, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX43288': {'db': 1, 'offset': 43288, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX43544': {'db': 1, 'offset': 43544, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX43800': {'db': 1, 'offset': 43800, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX44056': {'db': 1, 'offset': 44056, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX44312': {'db': 1, 'offset': 44312, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX44568': {'db': 1, 'offset': 44568, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX44824': {'db': 1, 'offset': 44824, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX45080': {'db': 1, 'offset': 45080, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX45336': {'db': 1, 'offset': 45336, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX45592': {'db': 1, 'offset': 45592, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX45848': {'db': 1, 'offset': 45848, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX46104': {'db': 1, 'offset': 46104, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX46360': {'db': 1, 'offset': 46360, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX46616': {'db': 1, 'offset': 46616, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX46872': {'db': 1, 'offset': 46872, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX47128': {'db': 1, 'offset': 47128, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX47384': {'db': 1, 'offset': 47384, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX47640': {'db': 1, 'offset': 47640, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX47896': {'db': 1, 'offset': 47896, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX48152': {'db': 1, 'offset': 48152, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX48408': {'db': 1, 'offset': 48408, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX48664': {'db': 1, 'offset': 48664, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX48920': {'db': 1, 'offset': 48920, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX49176': {'db': 1, 'offset': 49176, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX49432': {'db': 1, 'offset': 49432, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX49688': {'db': 1, 'offset': 49688, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX49944': {'db': 1, 'offset': 49944, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX50200': {'db': 1, 'offset': 50200, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX50456': {'db': 1, 'offset': 50456, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX50712': {'db': 1, 'offset': 50712, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX50968': {'db': 1, 'offset': 50968, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX51224': {'db': 1, 'offset': 51224, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX51480': {'db': 1, 'offset': 51480, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX51736': {'db': 1, 'offset': 51736, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX51992': {'db': 1, 'offset': 51992, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX52248': {'db': 1, 'offset': 52248, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX52504': {'db': 1, 'offset': 52504, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX52760': {'db': 1, 'offset': 52760, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX53016': {'db': 1, 'offset': 53016, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX53272': {'db': 1, 'offset': 53272, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX53528': {'db': 1, 'offset': 53528, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX53784': {'db': 1, 'offset': 53784, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX54040': {'db': 1, 'offset': 54040, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX54296': {'db': 1, 'offset': 54296, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX54552': {'db': 1, 'offset': 54552, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX54808': {'db': 1, 'offset': 54808, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX55064': {'db': 1, 'offset': 55064, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX55320': {'db': 1, 'offset': 55320, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX55576': {'db': 1, 'offset': 55576, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX55832': {'db': 1, 'offset': 55832, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX56088': {'db': 1, 'offset': 56088, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX56344': {'db': 1, 'offset': 56344, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX56600': {'db': 1, 'offset': 56600, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX56856': {'db': 1, 'offset': 56856, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX57112': {'db': 1, 'offset': 57112, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX57368': {'db': 1, 'offset': 57368, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX57624': {'db': 1, 'offset': 57624, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX57880': {'db': 1, 'offset': 57880, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX58136': {'db': 1, 'offset': 58136, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX58392': {'db': 1, 'offset': 58392, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX58648': {'db': 1, 'offset': 58648, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX58904': {'db': 1, 'offset': 58904, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX59160': {'db': 1, 'offset': 59160, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX59416': {'db': 1, 'offset': 59416, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX59672': {'db': 1, 'offset': 59672, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX59928': {'db': 1, 'offset': 59928, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX60184': {'db': 1, 'offset': 60184, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX60440': {'db': 1, 'offset': 60440, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX60696': {'db': 1, 'offset': 60696, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX60952': {'db': 1, 'offset': 60952, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX61208': {'db': 1, 'offset': 61208, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX61464': {'db': 1, 'offset': 61464, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX61720': {'db': 1, 'offset': 61720, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX61976': {'db': 1, 'offset': 61976, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX62232': {'db': 1, 'offset': 62232, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX62488': {'db': 1, 'offset': 62488, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX62744': {'db': 1, 'offset': 62744, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX63000': {'db': 1, 'offset': 63000, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX63256': {'db': 1, 'offset': 63256, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX63512': {'db': 1, 'offset': 63512, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX63768': {'db': 1, 'offset': 63768, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX64024': {'db': 1, 'offset': 64024, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX64280': {'db': 1, 'offset': 64280, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX64536': {'db': 1, 'offset': 64536, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX64792': {'db': 1, 'offset': 64792, 'dtype': 'STRING', 'max_length': 254},
'DB1_DBX65048': {'db': 1, 'offset': 65048, 'dtype': 'STRING', 'max_length': 254},# DB2 started Below
'DB2_DBX24': {'db': 2, 'offset': 24, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX280': {'db': 2, 'offset': 280, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX536': {'db': 2, 'offset': 536, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX792': {'db': 2, 'offset': 792, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX1048': {'db': 2, 'offset': 1048, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX1304': {'db': 2, 'offset': 1304, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX1560': {'db': 2, 'offset': 1560, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX1816': {'db': 2, 'offset': 1816, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX2072': {'db': 2, 'offset': 2072, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX2328': {'db': 2, 'offset': 2328, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX2584': {'db': 2, 'offset': 2584, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX2840': {'db': 2, 'offset': 2840, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX3096': {'db': 2, 'offset': 3096, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX3352': {'db': 2, 'offset': 3352, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX3608': {'db': 2, 'offset': 3608, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX3864': {'db': 2, 'offset': 3864, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX4120': {'db': 2, 'offset': 4120, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX4376': {'db': 2, 'offset': 4376, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX4632': {'db': 2, 'offset': 4632, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX4888': {'db': 2, 'offset': 4888, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX5144': {'db': 2, 'offset': 5144, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX5400': {'db': 2, 'offset': 5400, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX5656': {'db': 2, 'offset': 5656, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX5912': {'db': 2, 'offset': 5912, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX6168': {'db': 2, 'offset': 6168, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX6424': {'db': 2, 'offset': 6424, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX6680': {'db': 2, 'offset': 6680, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX6936': {'db': 2, 'offset': 6936, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX7192': {'db': 2, 'offset': 7192, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX7448': {'db': 2, 'offset': 7448, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX7704': {'db': 2, 'offset': 7704, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX7960': {'db': 2, 'offset': 7960, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX8216': {'db': 2, 'offset': 8216, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX8472': {'db': 2, 'offset': 8472, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX8728': {'db': 2, 'offset': 8728, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX8984': {'db': 2, 'offset': 8984, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX9240': {'db': 2, 'offset': 9240, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX9496': {'db': 2, 'offset': 9496, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX9752': {'db': 2, 'offset': 9752, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX10008': {'db': 2, 'offset': 10008, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX10264': {'db': 2, 'offset': 10264, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX10520': {'db': 2, 'offset': 10520, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX10776': {'db': 2, 'offset': 10776, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX11032': {'db': 2, 'offset': 11032, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX11288': {'db': 2, 'offset': 11288, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX11544': {'db': 2, 'offset': 11544, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX11800': {'db': 2, 'offset': 11800, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX12056': {'db': 2, 'offset': 12056, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX12312': {'db': 2, 'offset': 12312, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX12568': {'db': 2, 'offset': 12568, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX12824': {'db': 2, 'offset': 12824, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX13080': {'db': 2, 'offset': 13080, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX13336': {'db': 2, 'offset': 13336, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX13592': {'db': 2, 'offset': 13592, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX13848': {'db': 2, 'offset': 13848, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX14104': {'db': 2, 'offset': 14104, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX14360': {'db': 2, 'offset': 14360, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX14616': {'db': 2, 'offset': 14616, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX14872': {'db': 2, 'offset': 14872, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX15128': {'db': 2, 'offset': 15128, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX15384': {'db': 2, 'offset': 15384, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX15640': {'db': 2, 'offset': 15640, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX15896': {'db': 2, 'offset': 15896, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX16152': {'db': 2, 'offset': 16152, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX16408': {'db': 2, 'offset': 16408, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX16664': {'db': 2, 'offset': 16664, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX16920': {'db': 2, 'offset': 16920, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX17176': {'db': 2, 'offset': 17176, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX17432': {'db': 2, 'offset': 17432, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX17688': {'db': 2, 'offset': 17688, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX17944': {'db': 2, 'offset': 17944, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX18200': {'db': 2, 'offset': 18200, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX18456': {'db': 2, 'offset': 18456, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX18712': {'db': 2, 'offset': 18712, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX18968': {'db': 2, 'offset': 18968, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX19224': {'db': 2, 'offset': 19224, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX19480': {'db': 2, 'offset': 19480, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX19736': {'db': 2, 'offset': 19736, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX19992': {'db': 2, 'offset': 19992, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX20248': {'db': 2, 'offset': 20248, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX20504': {'db': 2, 'offset': 20504, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX20760': {'db': 2, 'offset': 20760, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX21016': {'db': 2, 'offset': 21016, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX21272': {'db': 2, 'offset': 21272, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX21528': {'db': 2, 'offset': 21528, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX21784': {'db': 2, 'offset': 21784, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX22040': {'db': 2, 'offset': 22040, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX22296': {'db': 2, 'offset': 22296, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX22552': {'db': 2, 'offset': 22552, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX22808': {'db': 2, 'offset': 22808, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX23064': {'db': 2, 'offset': 23064, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX23320': {'db': 2, 'offset': 23320, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX23576': {'db': 2, 'offset': 23576, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX23832': {'db': 2, 'offset': 23832, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX24088': {'db': 2, 'offset': 24088, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX24344': {'db': 2, 'offset': 24344, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX24600': {'db': 2, 'offset': 24600, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX24856': {'db': 2, 'offset': 24856, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX25112': {'db': 2, 'offset': 25112, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX25368': {'db': 2, 'offset': 25368, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX25624': {'db': 2, 'offset': 25624, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX25880': {'db': 2, 'offset': 25880, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX26136': {'db': 2, 'offset': 26136, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX26392': {'db': 2, 'offset': 26392, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX26648': {'db': 2, 'offset': 26648, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX26904': {'db': 2, 'offset': 26904, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX27160': {'db': 2, 'offset': 27160, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX27416': {'db': 2, 'offset': 27416, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX27672': {'db': 2, 'offset': 27672, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX27928': {'db': 2, 'offset': 27928, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX28184': {'db': 2, 'offset': 28184, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX28440': {'db': 2, 'offset': 28440, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX28696': {'db': 2, 'offset': 28696, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX28952': {'db': 2, 'offset': 28952, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX29208': {'db': 2, 'offset': 29208, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX29464': {'db': 2, 'offset': 29464, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX29720': {'db': 2, 'offset': 29720, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX29976': {'db': 2, 'offset': 29976, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX30232': {'db': 2, 'offset': 30232, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX30488': {'db': 2, 'offset': 30488, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX30744': {'db': 2, 'offset': 30744, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX31000': {'db': 2, 'offset': 31000, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX31256': {'db': 2, 'offset': 31256, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX31512': {'db': 2, 'offset': 31512, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX31768': {'db': 2, 'offset': 31768, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX32024': {'db': 2, 'offset': 32024, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX32280': {'db': 2, 'offset': 32280, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX32536': {'db': 2, 'offset': 32536, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX32792': {'db': 2, 'offset': 32792, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX33048': {'db': 2, 'offset': 33048, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX33304': {'db': 2, 'offset': 33304, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX33560': {'db': 2, 'offset': 33560, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX33816': {'db': 2, 'offset': 33816, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX34072': {'db': 2, 'offset': 34072, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX34328': {'db': 2, 'offset': 34328, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX34584': {'db': 2, 'offset': 34584, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX34840': {'db': 2, 'offset': 34840, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX35096': {'db': 2, 'offset': 35096, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX35352': {'db': 2, 'offset': 35352, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX35608': {'db': 2, 'offset': 35608, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX35864': {'db': 2, 'offset': 35864, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX36120': {'db': 2, 'offset': 36120, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX36376': {'db': 2, 'offset': 36376, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX36632': {'db': 2, 'offset': 36632, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX36888': {'db': 2, 'offset': 36888, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX37144': {'db': 2, 'offset': 37144, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX37400': {'db': 2, 'offset': 37400, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX37656': {'db': 2, 'offset': 37656, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX37912': {'db': 2, 'offset': 37912, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX38168': {'db': 2, 'offset': 38168, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX38424': {'db': 2, 'offset': 38424, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX38680': {'db': 2, 'offset': 38680, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX38936': {'db': 2, 'offset': 38936, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX39192': {'db': 2, 'offset': 39192, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX39448': {'db': 2, 'offset': 39448, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX39704': {'db': 2, 'offset': 39704, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX39960': {'db': 2, 'offset': 39960, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX40216': {'db': 2, 'offset': 40216, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX40472': {'db': 2, 'offset': 40472, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX40728': {'db': 2, 'offset': 40728, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX40984': {'db': 2, 'offset': 40984, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX41240': {'db': 2, 'offset': 41240, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX41496': {'db': 2, 'offset': 41496, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX41752': {'db': 2, 'offset': 41752, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX42008': {'db': 2, 'offset': 42008, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX42264': {'db': 2, 'offset': 42264, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX42520': {'db': 2, 'offset': 42520, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX42776': {'db': 2, 'offset': 42776, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX43032': {'db': 2, 'offset': 43032, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX43288': {'db': 2, 'offset': 43288, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX43544': {'db': 2, 'offset': 43544, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX43800': {'db': 2, 'offset': 43800, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX44056': {'db': 2, 'offset': 44056, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX44312': {'db': 2, 'offset': 44312, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX44568': {'db': 2, 'offset': 44568, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX44824': {'db': 2, 'offset': 44824, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX45080': {'db': 2, 'offset': 45080, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX45336': {'db': 2, 'offset': 45336, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX45592': {'db': 2, 'offset': 45592, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX45848': {'db': 2, 'offset': 45848, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX46104': {'db': 2, 'offset': 46104, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX46360': {'db': 2, 'offset': 46360, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX46616': {'db': 2, 'offset': 46616, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX46872': {'db': 2, 'offset': 46872, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX47128': {'db': 2, 'offset': 47128, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX47384': {'db': 2, 'offset': 47384, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX47640': {'db': 2, 'offset': 47640, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX47896': {'db': 2, 'offset': 47896, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX48152': {'db': 2, 'offset': 48152, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX48408': {'db': 2, 'offset': 48408, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX48664': {'db': 2, 'offset': 48664, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX48920': {'db': 2, 'offset': 48920, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX49176': {'db': 2, 'offset': 49176, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX49432': {'db': 2, 'offset': 49432, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX49688': {'db': 2, 'offset': 49688, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX49944': {'db': 2, 'offset': 49944, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX50200': {'db': 2, 'offset': 50200, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX50456': {'db': 2, 'offset': 50456, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX50712': {'db': 2, 'offset': 50712, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX50968': {'db': 2, 'offset': 50968, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX51224': {'db': 2, 'offset': 51224, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX51480': {'db': 2, 'offset': 51480, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX51736': {'db': 2, 'offset': 51736, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX51992': {'db': 2, 'offset': 51992, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX52248': {'db': 2, 'offset': 52248, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX52504': {'db': 2, 'offset': 52504, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX52760': {'db': 2, 'offset': 52760, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX53016': {'db': 2, 'offset': 53016, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX53272': {'db': 2, 'offset': 53272, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX53528': {'db': 2, 'offset': 53528, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX53784': {'db': 2, 'offset': 53784, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX54040': {'db': 2, 'offset': 54040, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX54296': {'db': 2, 'offset': 54296, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX54552': {'db': 2, 'offset': 54552, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX54808': {'db': 2, 'offset': 54808, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX55064': {'db': 2, 'offset': 55064, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX55320': {'db': 2, 'offset': 55320, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX55576': {'db': 2, 'offset': 55576, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX55832': {'db': 2, 'offset': 55832, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX56088': {'db': 2, 'offset': 56088, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX56344': {'db': 2, 'offset': 56344, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX56600': {'db': 2, 'offset': 56600, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX56856': {'db': 2, 'offset': 56856, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX57112': {'db': 2, 'offset': 57112, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX57368': {'db': 2, 'offset': 57368, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX57624': {'db': 2, 'offset': 57624, 'dtype': 'STRING', 'max_length': 254},
    'DB2_DBX57880': {'db': 2, 'offset': 57880, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX58136': {'db': 2, 'offset': 58136, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX58392': {'db': 2, 'offset': 58392, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX58648': {'db': 2, 'offset': 58648, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX58904': {'db': 2, 'offset': 58904, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX59160': {'db': 2, 'offset': 59160, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX59416': {'db': 2, 'offset': 59416, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX59672': {'db': 2, 'offset': 59672, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX59928': {'db': 2, 'offset': 59928, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX60184': {'db': 2, 'offset': 60184, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX60440': {'db': 2, 'offset': 60440, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX60696': {'db': 2, 'offset': 60696, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX60952': {'db': 2, 'offset': 60952, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX61208': {'db': 2, 'offset': 61208, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX61464': {'db': 2, 'offset': 61464, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX61720': {'db': 2, 'offset': 61720, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX61976': {'db': 2, 'offset': 61976, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX62232': {'db': 2, 'offset': 62232, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX62488': {'db': 2, 'offset': 62488, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX62744': {'db': 2, 'offset': 62744, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX63000': {'db': 2, 'offset': 63000, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX63256': {'db': 2, 'offset': 63256, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX63512': {'db': 2, 'offset': 63512, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX63768': {'db': 2, 'offset': 63768, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX64024': {'db': 2, 'offset': 64024, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX64280': {'db': 2, 'offset': 64280, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX64536': {'db': 2, 'offset': 64536, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX64792': {'db': 2, 'offset': 64792, 'dtype': 'STRING', 'max_length': 254},
'DB2_DBX65048': {'db': 2, 'offset': 65048, 'dtype': 'STRING', 'max_length': 254},
}

# --------------------------
# Setup
# --------------------------
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("S7-1200")

# --------------------------
# PLC Connection Pool
# --------------------------
class PLCConnectionPool:
    def __init__(self):
        self.pool = Queue(maxsize=PLC_CONNECTION_POOL_SIZE)
        self.lock = Lock()
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize the connection pool with fresh connections"""
        for _ in range(PLC_CONNECTION_POOL_SIZE):
            conn = self._create_connection()
            if conn:
                self.pool.put(conn)

    def _create_connection(self, ip=PLC_IP):
        """Create a new PLC connection"""
        plc = snap7.client.Client()
        try:
            plc.connect(ip, PLC_RACK, PLC_SLOT, PLC_PORT)
            if plc.get_connected():
                return plc
        except Exception as e:
            logger.error(f"PLC connection failed: {str(e)}")
        return None

    def get_connection(self, ip=PLC_IP):
        """Get a connection from the pool"""
        with self.lock:
            if not self.pool.empty():
                conn = self.pool.get()
                if conn and conn.get_connected():
                    return conn
                # If connection is bad, create a new one
                return self._create_connection(ip)
            else:
                return self._create_connection(ip)

    def return_connection(self, conn):
        """Return a connection to the pool"""
        with self.lock:
            if conn and conn.get_connected():
                self.pool.put(conn)
            else:
                # If connection is bad, create a new one
                new_conn = self._create_connection()
                if new_conn:
                    self.pool.put(new_conn)

    def close_all(self):
        """Close all connections in the pool"""
        with self.lock:
            while not self.pool.empty():
                conn = self.pool.get()
                if conn:
                    try:
                        conn.disconnect()
                    except:
                        pass

# Global connection pool
plc_pool = PLCConnectionPool()

# --------------------------
# PLC Communication Functions with Threading
# --------------------------
def read_plc_value(plc, db, offset, dtype, max_length=None):
    """Read a value from PLC with error handling"""
    try:
        if dtype == 'REAL':
            data = plc.db_read(db, offset, 4)
            return round(struct.unpack('>f', bytes(data))[0], 2)
        elif dtype == 'DINT':
            data = plc.db_read(db, offset, 4)
            return int.from_bytes(data, byteorder='big', signed=True)
        elif dtype == 'STRING':
            data = plc.db_read(db, offset, max_length + 2)
            current_length = data[1]
            return data[2:2+current_length].decode('ascii').strip('\x00')
        return None
    except Exception as e:
        logger.error(f"Read error for DB{db}.{offset}: {str(e)}")
        return None

def write_plc_value(plc, db, offset, dtype, value, max_length=None):
    """Write a value to PLC with error handling"""
    try:
        if dtype == 'DINT':
            data = int(value).to_bytes(4, byteorder='big', signed=True)
            plc.db_write(db, offset, data)
        elif dtype == 'REAL':
            data = struct.pack('>f', float(value))
            plc.db_write(db, offset, data)
        elif dtype == 'STRING':
            if not isinstance(value, str):
                value = str(value)
            if len(value) > max_length:
                value = value[:max_length]
            data = bytearray(max_length + 2)
            data[0] = max_length
            data[1] = len(value)
            data[2:2+len(value)] = value.encode('ascii')
            plc.db_write(db, offset, data)
        else:
            return False
        return True
    except Exception as e:
        logger.error(f"Write error for DB{db}.{offset}: {str(e)}")
        return False

def batch_read_operation(tag_configs, plc_ip):
    """Perform batch read operations using thread pool"""
    results = {}
    plc = None
    
    try:
        plc = plc_pool.get_connection(plc_ip)
        if not plc:
            return {"error": "PLC connection failed"}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_tag = {
                executor.submit(
                    read_plc_value, 
                    plc, 
                    config['db'], 
                    config['offset'], 
                    config['dtype'], 
                    config.get('max_length')
                ): tag_name 
                for tag_name, config in tag_configs.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_tag):
                tag_name = future_to_tag[future]
                try:
                    results[tag_name] = future.result()
                except Exception as e:
                    logger.error(f"Error reading tag {tag_name}: {str(e)}")
                    results[tag_name] = None
                    
        return results
    finally:
        if plc:
            plc_pool.return_connection(plc)

def batch_write_operation(write_requests, plc_ip):
    """Perform batch write operations using thread pool"""
    results = {}
    plc = None
    
    try:
        plc = plc_pool.get_connection(plc_ip)
        if not plc:
            return {"error": "PLC connection failed"}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_request = {}
            
            for item in write_requests:
                tag = item.get('tag')
                config = TAG_CONFIG.get(tag)
                if not config:
                    results[tag] = {"status": "Failed", "error": "Tag not found"}
                    continue
                
                future = executor.submit(
                    write_plc_value,
                    plc,
                    config['db'],
                    config['offset'],
                    config['dtype'],
                    item.get('value'),
                    config.get('max_length')
                )
                future_to_request[future] = item
                
            for future in concurrent.futures.as_completed(future_to_request):
                item = future_to_request[future]
                tag = item.get('tag')
                try:
                    success = future.result()
                    results[tag] = {
                        "status": "Success" if success else "Failed",
                        "value_written": item.get('value'),
                        "data_type": TAG_CONFIG[tag]['dtype']
                    }
                except Exception as e:
                    logger.error(f"Error writing tag {tag}: {str(e)}")
                    results[tag] = {
                        "status": "Failed",
                        "error": str(e)
                    }
                    
        return results
    finally:
        if plc:
            plc_pool.return_connection(plc)

# --------------------------
# API Routes
# --------------------------
@app.route('/insertDataToPlc', methods=['POST'])
def insert_data_to_plc():
    """Batch write data to PLC"""
    try:
        plc_ip = request.args.get('ip') or PLC_IP
        data_list = request.json
        
        if not isinstance(data_list, list):
            return jsonify({"message": "Payload must be a list"}), 400
        
        start_time = time.time()
        results = batch_write_operation(data_list, plc_ip)
        elapsed = time.time() - start_time
        
        logger.info(f"Write operation completed in {elapsed:.3f} seconds")
        
        return jsonify({
            "message": "Write completed",
            "execution_time": elapsed,
            "data": results
        }), 200

    except Exception as e:
        logger.error(f"Exception in insertDataToPlc: {str(e)}")
        return jsonify({"message": "Exception occurred", "error": str(e)}), 500

@app.route('/readDataTagsFromPlc', methods=['GET'])
def read_tags():
    """Get list of available tags"""
    return jsonify({"tags": list(TAG_CONFIG.keys())}), 200

@app.route('/readDataFromPlcByTags', methods=['GET'])
def read_all_data():
    """Read all configured tags from PLC"""
    try:
        plc_ip = request.args.get('ip') or PLC_IP
        start_time = time.time()
        results = batch_read_operation(TAG_CONFIG, plc_ip)
        elapsed = time.time() - start_time
        
        logger.info(f"Read all operation completed in {elapsed:.3f} seconds")
        
        return jsonify({
            "message": "Read successful",
            "execution_time": elapsed,
            "data": results
        }), 200
    except Exception as e:
        logger.error(f"Exception in read_all_data: {str(e)}")
        return jsonify({"message": "Read failed", "error": str(e)}), 500

@app.route('/getTagValues', methods=['POST'])
def get_tag_values():
    """Read specific tags provided in request"""
    try:
        plc_ip = request.args.get('ip') or PLC_IP
        requested_tags = request.json.get('tags', [])
        
        if not isinstance(requested_tags, list) or not requested_tags:
            return jsonify({"message": "No tags specified", "error": "Empty or invalid request"}), 400
        
        # Filter only the requested tags that exist in our config
        tag_configs = {
            tag: TAG_CONFIG[tag] 
            for tag in requested_tags 
            if tag in TAG_CONFIG
        }
        
        start_time = time.time()
        results = batch_read_operation(tag_configs, plc_ip)
        elapsed = time.time() - start_time
        
        logger.info(f"Selective read operation completed in {elapsed:.3f} seconds")
        
        return jsonify({
            "data": results,
            "execution_time": elapsed
        }), 200

    except Exception as e:
        logger.error(f"Exception in get_tag_values: {str(e)}")
        return jsonify({"message": "Selective read failed", "error": str(e)}), 500

@app.teardown_appcontext
def shutdown_plc_pool(exception=None):
    """Cleanup PLC connections when app shuts down"""
    plc_pool.close_all()

# Run App
# --------------------------
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8083, threaded=True)
    finally:
        plc_pool.close_all()