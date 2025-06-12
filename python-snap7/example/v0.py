import snap7
import struct
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time
from collections import defaultdict
from threading import Lock
from functools import lru_cache

# -------------------------------
# Configuration
# -------------------------------
PLC_IP = '192.168.0.1'
PLC_RACK = 0
PLC_SLOT = 1
PLC_PORT = 102
MAX_DB_SIZE = 65536
MAX_STRING_LENGTH = 254
MIN_WRITE_INTERVAL = 0.005  # Aggressively reduced to 5ms
READ_CACHE_TTL = 0.02  # Aggressively reduced to 20ms
CONNECTION_TIMEOUT = 1  # Timeout for connection attempts in seconds

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
 'DB1_DBX24': {'db': 1, 'offset': 24, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX280': {'db': 1, 'offset': 280, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX536': {'db': 1, 'offset': 536, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX792': {'db': 1, 'offset': 792, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX1048': {'db': 1, 'offset': 1048, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX1304': {'db': 1, 'offset': 1304, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX1560': {'db': 1, 'offset': 1560, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX1816': {'db': 1, 'offset': 1816, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX2072': {'db': 1, 'offset': 2072, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX2328': {'db': 1, 'offset': 2328, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX2584': {'db': 1, 'offset': 2584, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX2840': {'db': 1, 'offset': 2840, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX3096': {'db': 1, 'offset': 3096, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX3352': {'db': 1, 'offset': 3352, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX3608': {'db': 1, 'offset': 3608, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX3864': {'db': 1, 'offset': 3864, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX4120': {'db': 1, 'offset': 4120, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX4376': {'db': 1, 'offset': 4376, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX4632': {'db': 1, 'offset': 4632, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX4888': {'db': 1, 'offset': 4888, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX5144': {'db': 1, 'offset': 5144, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX5400': {'db': 1, 'offset': 5400, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX5656': {'db': 1, 'offset': 5656, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX5912': {'db': 1, 'offset': 5912, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX6168': {'db': 1, 'offset': 6168, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX6424': {'db': 1, 'offset': 6424, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX6680': {'db': 1, 'offset': 6680, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX6936': {'db': 1, 'offset': 6936, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX7192': {'db': 1, 'offset': 7192, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX7448': {'db': 1, 'offset': 7448, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX7704': {'db': 1, 'offset': 7704, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX7960': {'db': 1, 'offset': 7960, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX8216': {'db': 1, 'offset': 8216, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX8472': {'db': 1, 'offset': 8472, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX8728': {'db': 1, 'offset': 8728, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX8984': {'db': 1, 'offset': 8984, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX9240': {'db': 1, 'offset': 9240, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX9496': {'db': 1, 'offset': 9496, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX9752': {'db': 1, 'offset': 9752, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX10008': {'db': 1, 'offset': 10008, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX10264': {'db': 1, 'offset': 10264, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX10520': {'db': 1, 'offset': 10520, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX10776': {'db': 1, 'offset': 10776, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX11032': {'db': 1, 'offset': 11032, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX11288': {'db': 1, 'offset': 11288, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX11544': {'db': 1, 'offset': 11544, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX11800': {'db': 1, 'offset': 11800, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX12056': {'db': 1, 'offset': 12056, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX12312': {'db': 1, 'offset': 12312, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX12568': {'db': 1, 'offset': 12568, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX12824': {'db': 1, 'offset': 12824, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX13080': {'db': 1, 'offset': 13080, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX13336': {'db': 1, 'offset': 13336, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX13592': {'db': 1, 'offset': 13592, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX13848': {'db': 1, 'offset': 13848, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX14104': {'db': 1, 'offset': 14104, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX14360': {'db': 1, 'offset': 14360, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX14616': {'db': 1, 'offset': 14616, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX14872': {'db': 1, 'offset': 14872, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX15128': {'db': 1, 'offset': 15128, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX15384': {'db': 1, 'offset': 15384, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX15640': {'db': 1, 'offset': 15640, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX15896': {'db': 1, 'offset': 15896, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX16152': {'db': 1, 'offset': 16152, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX16408': {'db': 1, 'offset': 16408, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX16664': {'db': 1, 'offset': 16664, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX16920': {'db': 1, 'offset': 16920, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX17176': {'db': 1, 'offset': 17176, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX17432': {'db': 1, 'offset': 17432, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX17688': {'db': 1, 'offset': 17688, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX17944': {'db': 1, 'offset': 17944, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX18200': {'db': 1, 'offset': 18200, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX18456': {'db': 1, 'offset': 18456, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX18712': {'db': 1, 'offset': 18712, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX18968': {'db': 1, 'offset': 18968, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX19224': {'db': 1, 'offset': 19224, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX19480': {'db': 1, 'offset': 19480, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX19736': {'db': 1, 'offset': 19736, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX19992': {'db': 1, 'offset': 19992, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX20248': {'db': 1, 'offset': 20248, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX20504': {'db': 1, 'offset': 20504, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX20760': {'db': 1, 'offset': 20760, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX21016': {'db': 1, 'offset': 21016, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX21272': {'db': 1, 'offset': 21272, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX21528': {'db': 1, 'offset': 21528, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX21784': {'db': 1, 'offset': 21784, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX22040': {'db': 1, 'offset': 22040, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX22296': {'db': 1, 'offset': 22296, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX22552': {'db': 1, 'offset': 22552, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX22808': {'db': 1, 'offset': 22808, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX23064': {'db': 1, 'offset': 23064, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX23320': {'db': 1, 'offset': 23320, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX23576': {'db': 1, 'offset': 23576, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX23832': {'db': 1, 'offset': 23832, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX24088': {'db': 1, 'offset': 24088, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX24344': {'db': 1, 'offset': 24344, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX24600': {'db': 1, 'offset': 24600, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX24856': {'db': 1, 'offset': 24856, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX25112': {'db': 1, 'offset': 25112, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX25368': {'db': 1, 'offset': 25368, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX25624': {'db': 1, 'offset': 25624, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX25880': {'db': 1, 'offset': 25880, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX26136': {'db': 1, 'offset': 26136, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX26392': {'db': 1, 'offset': 26392, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX26648': {'db': 1, 'offset': 26648, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX26904': {'db': 1, 'offset': 26904, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX27160': {'db': 1, 'offset': 27160, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX27416': {'db': 1, 'offset': 27416, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX27672': {'db': 1, 'offset': 27672, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX27928': {'db': 1, 'offset': 27928, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX28184': {'db': 1, 'offset': 28184, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX28440': {'db': 1, 'offset': 28440, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX28696': {'db': 1, 'offset': 28696, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX28952': {'db': 1, 'offset': 28952, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX29208': {'db': 1, 'offset': 29208, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX29464': {'db': 1, 'offset': 29464, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX29720': {'db': 1, 'offset': 29720, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX29976': {'db': 1, 'offset': 29976, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX30232': {'db': 1, 'offset': 30232, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX30488': {'db': 1, 'offset': 30488, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX30744': {'db': 1, 'offset': 30744, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX31000': {'db': 1, 'offset': 31000, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX31256': {'db': 1, 'offset': 31256, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX31512': {'db': 1, 'offset': 31512, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX31768': {'db': 1, 'offset': 31768, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX32024': {'db': 1, 'offset': 32024, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX32280': {'db': 1, 'offset': 32280, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX32536': {'db': 1, 'offset': 32536, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX32792': {'db': 1, 'offset': 32792, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX33048': {'db': 1, 'offset': 33048, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX33304': {'db': 1, 'offset': 33304, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX33560': {'db': 1, 'offset': 33560, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX33816': {'db': 1, 'offset': 33816, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX34072': {'db': 1, 'offset': 34072, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX34328': {'db': 1, 'offset': 34328, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX34584': {'db': 1, 'offset': 34584, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX34840': {'db': 1, 'offset': 34840, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX35096': {'db': 1, 'offset': 35096, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX35352': {'db': 1, 'offset': 35352, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX35608': {'db': 1, 'offset': 35608, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX35864': {'db': 1, 'offset': 35864, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX36120': {'db': 1, 'offset': 36120, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX36376': {'db': 1, 'offset': 36376, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX36632': {'db': 1, 'offset': 36632, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX36888': {'db': 1, 'offset': 36888, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX37144': {'db': 1, 'offset': 37144, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX37400': {'db': 1, 'offset': 37400, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX37656': {'db': 1, 'offset': 37656, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX37912': {'db': 1, 'offset': 37912, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX38168': {'db': 1, 'offset': 38168, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX38424': {'db': 1, 'offset': 38424, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX38680': {'db': 1, 'offset': 38680, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX38936': {'db': 1, 'offset': 38936, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX39192': {'db': 1, 'offset': 39192, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX39448': {'db': 1, 'offset': 39448, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX39704': {'db': 1, 'offset': 39704, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX39960': {'db': 1, 'offset': 39960, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX40216': {'db': 1, 'offset': 40216, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX40472': {'db': 1, 'offset': 40472, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX40728': {'db': 1, 'offset': 40728, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX40984': {'db': 1, 'offset': 40984, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX41240': {'db': 1, 'offset': 41240, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX41496': {'db': 1, 'offset': 41496, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX41752': {'db': 1, 'offset': 41752, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX42008': {'db': 1, 'offset': 42008, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX42264': {'db': 1, 'offset': 42264, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX42520': {'db': 1, 'offset': 42520, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX42776': {'db': 1, 'offset': 42776, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX43032': {'db': 1, 'offset': 43032, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX43288': {'db': 1, 'offset': 43288, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX43544': {'db': 1, 'offset': 43544, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX43800': {'db': 1, 'offset': 43800, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX44056': {'db': 1, 'offset': 44056, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX44312': {'db': 1, 'offset': 44312, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX44568': {'db': 1, 'offset': 44568, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX44824': {'db': 1, 'offset': 44824, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX45080': {'db': 1, 'offset': 45080, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX45336': {'db': 1, 'offset': 45336, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX45592': {'db': 1, 'offset': 45592, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX45848': {'db': 1, 'offset': 45848, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX46104': {'db': 1, 'offset': 46104, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX46360': {'db': 1, 'offset': 46360, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX46616': {'db': 1, 'offset': 46616, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX46872': {'db': 1, 'offset': 46872, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX47128': {'db': 1, 'offset': 47128, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX47384': {'db': 1, 'offset': 47384, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX47640': {'db': 1, 'offset': 47640, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX47896': {'db': 1, 'offset': 47896, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX48152': {'db': 1, 'offset': 48152, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX48408': {'db': 1, 'offset': 48408, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX48664': {'db': 1, 'offset': 48664, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX48920': {'db': 1, 'offset': 48920, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX49176': {'db': 1, 'offset': 49176, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX49432': {'db': 1, 'offset': 49432, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX49688': {'db': 1, 'offset': 49688, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX49944': {'db': 1, 'offset': 49944, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX50200': {'db': 1, 'offset': 50200, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX50456': {'db': 1, 'offset': 50456, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX50712': {'db': 1, 'offset': 50712, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX50968': {'db': 1, 'offset': 50968, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX51224': {'db': 1, 'offset': 51224, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX51480': {'db': 1, 'offset': 51480, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX51736': {'db': 1, 'offset': 51736, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX51992': {'db': 1, 'offset': 51992, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX52248': {'db': 1, 'offset': 52248, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX52504': {'db': 1, 'offset': 52504, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX52760': {'db': 1, 'offset': 52760, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX53016': {'db': 1, 'offset': 53016, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX53272': {'db': 1, 'offset': 53272, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX53528': {'db': 1, 'offset': 53528, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX53784': {'db': 1, 'offset': 53784, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX54040': {'db': 1, 'offset': 54040, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX54296': {'db': 1, 'offset': 54296, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX54552': {'db': 1, 'offset': 54552, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX54808': {'db': 1, 'offset': 54808, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX55064': {'db': 1, 'offset': 55064, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX55320': {'db': 1, 'offset': 55320, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX55576': {'db': 1, 'offset': 55576, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX55832': {'db': 1, 'offset': 55832, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX56088': {'db': 1, 'offset': 56088, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX56344': {'db': 1, 'offset': 56344, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX56600': {'db': 1, 'offset': 56600, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX56856': {'db': 1, 'offset': 56856, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX57112': {'db': 1, 'offset': 57112, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX57368': {'db': 1, 'offset': 57368, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX57624': {'db': 1, 'offset': 57624, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX57880': {'db': 1, 'offset': 57880, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX58136': {'db': 1, 'offset': 58136, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX58392': {'db': 1, 'offset': 58392, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX58648': {'db': 1, 'offset': 58648, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX58904': {'db': 1, 'offset': 58904, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX59160': {'db': 1, 'offset': 59160, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX59416': {'db': 1, 'offset': 59416, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX59672': {'db': 1, 'offset': 59672, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX59928': {'db': 1, 'offset': 59928, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX60184': {'db': 1, 'offset': 60184, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX60440': {'db': 1, 'offset': 60440, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX60696': {'db': 1, 'offset': 60696, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX60952': {'db': 1, 'offset': 60952, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX61208': {'db': 1, 'offset': 61208, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX61464': {'db': 1, 'offset': 61464, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX61720': {'db': 1, 'offset': 61720, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX61976': {'db': 1, 'offset': 61976, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX62232': {'db': 1, 'offset': 62232, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX62488': {'db': 1, 'offset': 62488, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX62744': {'db': 1, 'offset': 62744, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX63000': {'db': 1, 'offset': 63000, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX63256': {'db': 1, 'offset': 63256, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX63512': {'db': 1, 'offset': 63512, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX63768': {'db': 1, 'offset': 63768, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX64024': {'db': 1, 'offset': 64024, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX64280': {'db': 1, 'offset': 64280, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX64536': {'db': 1, 'offset': 64536, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX64792': {'db': 1, 'offset': 64792, 'dtype': 'STRING', 'max_length': 16},
'DB1_DBX65048': {'db': 1, 'offset': 65048, 'dtype': 'STRING', 'max_length': 16},# DB2 started Below
'DB2_DBX24': {'db': 2, 'offset': 24, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX280': {'db': 2, 'offset': 280, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX536': {'db': 2, 'offset': 536, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX792': {'db': 2, 'offset': 792, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX1048': {'db': 2, 'offset': 1048, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX1304': {'db': 2, 'offset': 1304, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX1560': {'db': 2, 'offset': 1560, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX1816': {'db': 2, 'offset': 1816, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX2072': {'db': 2, 'offset': 2072, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX2328': {'db': 2, 'offset': 2328, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX2584': {'db': 2, 'offset': 2584, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX2840': {'db': 2, 'offset': 2840, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX3096': {'db': 2, 'offset': 3096, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX3352': {'db': 2, 'offset': 3352, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX3608': {'db': 2, 'offset': 3608, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX3864': {'db': 2, 'offset': 3864, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX4120': {'db': 2, 'offset': 4120, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX4376': {'db': 2, 'offset': 4376, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX4632': {'db': 2, 'offset': 4632, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX4888': {'db': 2, 'offset': 4888, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX5144': {'db': 2, 'offset': 5144, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX5400': {'db': 2, 'offset': 5400, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX5656': {'db': 2, 'offset': 5656, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX5912': {'db': 2, 'offset': 5912, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX6168': {'db': 2, 'offset': 6168, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX6424': {'db': 2, 'offset': 6424, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX6680': {'db': 2, 'offset': 6680, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX6936': {'db': 2, 'offset': 6936, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX7192': {'db': 2, 'offset': 7192, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX7448': {'db': 2, 'offset': 7448, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX7704': {'db': 2, 'offset': 7704, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX7960': {'db': 2, 'offset': 7960, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX8216': {'db': 2, 'offset': 8216, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX8472': {'db': 2, 'offset': 8472, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX8728': {'db': 2, 'offset': 8728, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX8984': {'db': 2, 'offset': 8984, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX9240': {'db': 2, 'offset': 9240, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX9496': {'db': 2, 'offset': 9496, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX9752': {'db': 2, 'offset': 9752, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX10008': {'db': 2, 'offset': 10008, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX10264': {'db': 2, 'offset': 10264, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX10520': {'db': 2, 'offset': 10520, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX10776': {'db': 2, 'offset': 10776, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX11032': {'db': 2, 'offset': 11032, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX11288': {'db': 2, 'offset': 11288, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX11544': {'db': 2, 'offset': 11544, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX11800': {'db': 2, 'offset': 11800, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX12056': {'db': 2, 'offset': 12056, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX12312': {'db': 2, 'offset': 12312, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX12568': {'db': 2, 'offset': 12568, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX12824': {'db': 2, 'offset': 12824, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX13080': {'db': 2, 'offset': 13080, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX13336': {'db': 2, 'offset': 13336, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX13592': {'db': 2, 'offset': 13592, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX13848': {'db': 2, 'offset': 13848, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX14104': {'db': 2, 'offset': 14104, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX14360': {'db': 2, 'offset': 14360, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX14616': {'db': 2, 'offset': 14616, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX14872': {'db': 2, 'offset': 14872, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX15128': {'db': 2, 'offset': 15128, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX15384': {'db': 2, 'offset': 15384, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX15640': {'db': 2, 'offset': 15640, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX15896': {'db': 2, 'offset': 15896, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX16152': {'db': 2, 'offset': 16152, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX16408': {'db': 2, 'offset': 16408, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX16664': {'db': 2, 'offset': 16664, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX16920': {'db': 2, 'offset': 16920, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX17176': {'db': 2, 'offset': 17176, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX17432': {'db': 2, 'offset': 17432, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX17688': {'db': 2, 'offset': 17688, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX17944': {'db': 2, 'offset': 17944, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX18200': {'db': 2, 'offset': 18200, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX18456': {'db': 2, 'offset': 18456, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX18712': {'db': 2, 'offset': 18712, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX18968': {'db': 2, 'offset': 18968, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX19224': {'db': 2, 'offset': 19224, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX19480': {'db': 2, 'offset': 19480, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX19736': {'db': 2, 'offset': 19736, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX19992': {'db': 2, 'offset': 19992, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX20248': {'db': 2, 'offset': 20248, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX20504': {'db': 2, 'offset': 20504, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX20760': {'db': 2, 'offset': 20760, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX21016': {'db': 2, 'offset': 21016, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX21272': {'db': 2, 'offset': 21272, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX21528': {'db': 2, 'offset': 21528, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX21784': {'db': 2, 'offset': 21784, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX22040': {'db': 2, 'offset': 22040, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX22296': {'db': 2, 'offset': 22296, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX22552': {'db': 2, 'offset': 22552, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX22808': {'db': 2, 'offset': 22808, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX23064': {'db': 2, 'offset': 23064, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX23320': {'db': 2, 'offset': 23320, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX23576': {'db': 2, 'offset': 23576, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX23832': {'db': 2, 'offset': 23832, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX24088': {'db': 2, 'offset': 24088, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX24344': {'db': 2, 'offset': 24344, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX24600': {'db': 2, 'offset': 24600, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX24856': {'db': 2, 'offset': 24856, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX25112': {'db': 2, 'offset': 25112, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX25368': {'db': 2, 'offset': 25368, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX25624': {'db': 2, 'offset': 25624, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX25880': {'db': 2, 'offset': 25880, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX26136': {'db': 2, 'offset': 26136, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX26392': {'db': 2, 'offset': 26392, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX26648': {'db': 2, 'offset': 26648, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX26904': {'db': 2, 'offset': 26904, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX27160': {'db': 2, 'offset': 27160, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX27416': {'db': 2, 'offset': 27416, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX27672': {'db': 2, 'offset': 27672, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX27928': {'db': 2, 'offset': 27928, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX28184': {'db': 2, 'offset': 28184, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX28440': {'db': 2, 'offset': 28440, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX28696': {'db': 2, 'offset': 28696, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX28952': {'db': 2, 'offset': 28952, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX29208': {'db': 2, 'offset': 29208, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX29464': {'db': 2, 'offset': 29464, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX29720': {'db': 2, 'offset': 29720, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX29976': {'db': 2, 'offset': 29976, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX30232': {'db': 2, 'offset': 30232, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX30488': {'db': 2, 'offset': 30488, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX30744': {'db': 2, 'offset': 30744, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX31000': {'db': 2, 'offset': 31000, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX31256': {'db': 2, 'offset': 31256, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX31512': {'db': 2, 'offset': 31512, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX31768': {'db': 2, 'offset': 31768, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX32024': {'db': 2, 'offset': 32024, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX32280': {'db': 2, 'offset': 32280, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX32536': {'db': 2, 'offset': 32536, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX32792': {'db': 2, 'offset': 32792, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX33048': {'db': 2, 'offset': 33048, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX33304': {'db': 2, 'offset': 33304, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX33560': {'db': 2, 'offset': 33560, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX33816': {'db': 2, 'offset': 33816, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX34072': {'db': 2, 'offset': 34072, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX34328': {'db': 2, 'offset': 34328, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX34584': {'db': 2, 'offset': 34584, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX34840': {'db': 2, 'offset': 34840, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX35096': {'db': 2, 'offset': 35096, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX35352': {'db': 2, 'offset': 35352, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX35608': {'db': 2, 'offset': 35608, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX35864': {'db': 2, 'offset': 35864, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX36120': {'db': 2, 'offset': 36120, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX36376': {'db': 2, 'offset': 36376, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX36632': {'db': 2, 'offset': 36632, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX36888': {'db': 2, 'offset': 36888, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX37144': {'db': 2, 'offset': 37144, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX37400': {'db': 2, 'offset': 37400, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX37656': {'db': 2, 'offset': 37656, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX37912': {'db': 2, 'offset': 37912, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX38168': {'db': 2, 'offset': 38168, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX38424': {'db': 2, 'offset': 38424, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX38680': {'db': 2, 'offset': 38680, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX38936': {'db': 2, 'offset': 38936, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX39192': {'db': 2, 'offset': 39192, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX39448': {'db': 2, 'offset': 39448, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX39704': {'db': 2, 'offset': 39704, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX39960': {'db': 2, 'offset': 39960, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX40216': {'db': 2, 'offset': 40216, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX40472': {'db': 2, 'offset': 40472, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX40728': {'db': 2, 'offset': 40728, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX40984': {'db': 2, 'offset': 40984, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX41240': {'db': 2, 'offset': 41240, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX41496': {'db': 2, 'offset': 41496, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX41752': {'db': 2, 'offset': 41752, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX42008': {'db': 2, 'offset': 42008, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX42264': {'db': 2, 'offset': 42264, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX42520': {'db': 2, 'offset': 42520, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX42776': {'db': 2, 'offset': 42776, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX43032': {'db': 2, 'offset': 43032, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX43288': {'db': 2, 'offset': 43288, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX43544': {'db': 2, 'offset': 43544, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX43800': {'db': 2, 'offset': 43800, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX44056': {'db': 2, 'offset': 44056, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX44312': {'db': 2, 'offset': 44312, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX44568': {'db': 2, 'offset': 44568, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX44824': {'db': 2, 'offset': 44824, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX45080': {'db': 2, 'offset': 45080, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX45336': {'db': 2, 'offset': 45336, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX45592': {'db': 2, 'offset': 45592, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX45848': {'db': 2, 'offset': 45848, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX46104': {'db': 2, 'offset': 46104, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX46360': {'db': 2, 'offset': 46360, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX46616': {'db': 2, 'offset': 46616, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX46872': {'db': 2, 'offset': 46872, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX47128': {'db': 2, 'offset': 47128, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX47384': {'db': 2, 'offset': 47384, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX47640': {'db': 2, 'offset': 47640, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX47896': {'db': 2, 'offset': 47896, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX48152': {'db': 2, 'offset': 48152, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX48408': {'db': 2, 'offset': 48408, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX48664': {'db': 2, 'offset': 48664, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX48920': {'db': 2, 'offset': 48920, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX49176': {'db': 2, 'offset': 49176, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX49432': {'db': 2, 'offset': 49432, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX49688': {'db': 2, 'offset': 49688, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX49944': {'db': 2, 'offset': 49944, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX50200': {'db': 2, 'offset': 50200, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX50456': {'db': 2, 'offset': 50456, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX50712': {'db': 2, 'offset': 50712, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX50968': {'db': 2, 'offset': 50968, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX51224': {'db': 2, 'offset': 51224, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX51480': {'db': 2, 'offset': 51480, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX51736': {'db': 2, 'offset': 51736, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX51992': {'db': 2, 'offset': 51992, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX52248': {'db': 2, 'offset': 52248, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX52504': {'db': 2, 'offset': 52504, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX52760': {'db': 2, 'offset': 52760, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX53016': {'db': 2, 'offset': 53016, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX53272': {'db': 2, 'offset': 53272, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX53528': {'db': 2, 'offset': 53528, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX53784': {'db': 2, 'offset': 53784, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX54040': {'db': 2, 'offset': 54040, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX54296': {'db': 2, 'offset': 54296, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX54552': {'db': 2, 'offset': 54552, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX54808': {'db': 2, 'offset': 54808, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX55064': {'db': 2, 'offset': 55064, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX55320': {'db': 2, 'offset': 55320, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX55576': {'db': 2, 'offset': 55576, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX55832': {'db': 2, 'offset': 55832, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX56088': {'db': 2, 'offset': 56088, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX56344': {'db': 2, 'offset': 56344, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX56600': {'db': 2, 'offset': 56600, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX56856': {'db': 2, 'offset': 56856, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX57112': {'db': 2, 'offset': 57112, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX57368': {'db': 2, 'offset': 57368, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX57624': {'db': 2, 'offset': 57624, 'dtype': 'STRING', 'max_length': 16},
    'DB2_DBX57880': {'db': 2, 'offset': 57880, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX58136': {'db': 2, 'offset': 58136, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX58392': {'db': 2, 'offset': 58392, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX58648': {'db': 2, 'offset': 58648, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX58904': {'db': 2, 'offset': 58904, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX59160': {'db': 2, 'offset': 59160, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX59416': {'db': 2, 'offset': 59416, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX59672': {'db': 2, 'offset': 59672, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX59928': {'db': 2, 'offset': 59928, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX60184': {'db': 2, 'offset': 60184, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX60440': {'db': 2, 'offset': 60440, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX60696': {'db': 2, 'offset': 60696, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX60952': {'db': 2, 'offset': 60952, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX61208': {'db': 2, 'offset': 61208, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX61464': {'db': 2, 'offset': 61464, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX61720': {'db': 2, 'offset': 61720, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX61976': {'db': 2, 'offset': 61976, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX62232': {'db': 2, 'offset': 62232, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX62488': {'db': 2, 'offset': 62488, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX62744': {'db': 2, 'offset': 62744, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX63000': {'db': 2, 'offset': 63000, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX63256': {'db': 2, 'offset': 63256, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX63512': {'db': 2, 'offset': 63512, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX63768': {'db': 2, 'offset': 63768, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX64024': {'db': 2, 'offset': 64024, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX64280': {'db': 2, 'offset': 64280, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX64536': {'db': 2, 'offset': 64536, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX64792': {'db': 2, 'offset': 64792, 'dtype': 'STRING', 'max_length': 16},
'DB2_DBX65048': {'db': 2, 'offset': 65048, 'dtype': 'STRING', 'max_length': 16},
'DB3_DBD4': {'db': 3, 'offset': 4, 'dtype': 'REAL'},
    'DB3_DBD8': {'db': 3, 'offset': 8, 'dtype': 'REAL'},
    'DB3_DBD12': {'db': 3, 'offset': 12, 'dtype': 'REAL'},
    'DB3_DBD16': {'db': 3, 'offset': 16, 'dtype': 'REAL'},
    'DB3_DBD20': {'db': 3, 'offset': 20, 'dtype': 'REAL'},
    'DB3_DBD24': {'db': 3, 'offset': 24, 'dtype': 'REAL'},
    'DB3_DBD28': {'db': 3, 'offset': 28, 'dtype': 'REAL'},
    'DB3_DBD32': {'db': 3, 'offset': 32, 'dtype': 'REAL'},
    'DB3_DBD36': {'db': 3, 'offset': 36, 'dtype': 'REAL'},
    'DB3_DBD40': {'db': 3, 'offset': 40, 'dtype': 'REAL'},
    'DB3_DBD44': {'db': 3, 'offset': 44, 'dtype': 'REAL'},
    'DB3_DBD48': {'db': 3, 'offset': 48, 'dtype': 'REAL'},
    'DB3_DBD52': {'db': 3, 'offset': 52, 'dtype': 'REAL'},
    'DB3_DBD56': {'db': 3, 'offset': 56, 'dtype': 'REAL'},
    'DB3_DBD60': {'db': 3, 'offset': 60, 'dtype': 'REAL'},
    'DB3_DBD64': {'db': 3, 'offset': 64, 'dtype': 'REAL'},
    'DB3_DBD68': {'db': 3, 'offset': 68, 'dtype': 'REAL'},
    'DB3_DBD72': {'db': 3, 'offset': 72, 'dtype': 'REAL'},
    'DB3_DBD76': {'db': 3, 'offset': 76, 'dtype': 'REAL'},
    'DB3_DBD80': {'db': 3, 'offset': 80, 'dtype': 'REAL'},
    'DB3_DBD84': {'db': 3, 'offset': 84, 'dtype': 'REAL'},
    'DB3_DBD88': {'db': 3, 'offset': 88, 'dtype': 'REAL'},
    'DB3_DBD92': {'db': 3, 'offset': 92, 'dtype': 'REAL'},
    'DB3_DBD96': {'db': 3, 'offset': 96, 'dtype': 'REAL'},
    'DB3_DBD100': {'db': 3, 'offset': 100, 'dtype': 'REAL'},
    'DB3_DBD104': {'db': 3, 'offset': 104, 'dtype': 'REAL'},
    'DB3_DBD108': {'db': 3, 'offset': 108, 'dtype': 'REAL'},
    'DB3_DBD112': {'db': 3, 'offset': 112, 'dtype': 'REAL'},
    'DB3_DBD116': {'db': 3, 'offset': 116, 'dtype': 'REAL'},
    'DB3_DBD120': {'db': 3, 'offset': 120, 'dtype': 'REAL'},
    'DB3_DBD124': {'db': 3, 'offset': 124, 'dtype': 'REAL'},
    'DB3_DBD128': {'db': 3, 'offset': 128, 'dtype': 'REAL'},
    'DB3_DBD132': {'db': 3, 'offset': 132, 'dtype': 'REAL'},
    'DB3_DBD136': {'db': 3, 'offset': 136, 'dtype': 'REAL'},
    'DB3_DBD140': {'db': 3, 'offset': 140, 'dtype': 'REAL'},
    'DB3_DBD144': {'db': 3, 'offset': 144, 'dtype': 'REAL'},
    'DB3_DBD148': {'db': 3, 'offset': 148, 'dtype': 'REAL'},
    'DB3_DBD152': {'db': 3, 'offset': 152, 'dtype': 'REAL'},
    'DB3_DBD156': {'db': 3, 'offset': 156, 'dtype': 'REAL'},
    'DB3_DBD160': {'db': 3, 'offset': 160, 'dtype': 'REAL'},
    'DB3_DBD164': {'db': 3, 'offset': 164, 'dtype': 'REAL'},
    'DB3_DBD168': {'db': 3, 'offset': 168, 'dtype': 'REAL'},
    'DB3_DBD172': {'db': 3, 'offset': 172, 'dtype': 'REAL'},
    'DB3_DBD176': {'db': 3, 'offset': 176, 'dtype': 'REAL'},
    'DB3_DBD180': {'db': 3, 'offset': 180, 'dtype': 'REAL'},
    'DB3_DBD184': {'db': 3, 'offset': 184, 'dtype': 'REAL'},
    'DB3_DBD188': {'db': 3, 'offset': 188, 'dtype': 'REAL'},
    'DB3_DBD192': {'db': 3, 'offset': 192, 'dtype': 'REAL'},
    'DB3_DBD196': {'db': 3, 'offset': 196, 'dtype': 'REAL'},
    'DB3_DBD200': {'db': 3, 'offset': 200, 'dtype': 'REAL'},
    'DB3_DBD204': {'db': 3, 'offset': 204, 'dtype': 'REAL'},
    'DB3_DBD208': {'db': 3, 'offset': 208, 'dtype': 'REAL'},
    'DB3_DBD212': {'db': 3, 'offset': 212, 'dtype': 'REAL'},
    'DB3_DBD216': {'db': 3, 'offset': 216, 'dtype': 'REAL'},
    'DB3_DBD220': {'db': 3, 'offset': 220, 'dtype': 'REAL'},
    'DB3_DBD224': {'db': 3, 'offset': 224, 'dtype': 'REAL'},
    'DB3_DBD228': {'db': 3, 'offset': 228, 'dtype': 'REAL'},
    'DB3_DBD232': {'db': 3, 'offset': 232, 'dtype': 'REAL'},
    'DB3_DBD236': {'db': 3, 'offset': 236, 'dtype': 'REAL'},
    'DB3_DBD240': {'db': 3, 'offset': 240, 'dtype': 'REAL'},
    'DB3_DBD244': {'db': 3, 'offset': 244, 'dtype': 'REAL'},
    'DB3_DBD248': {'db': 3, 'offset': 248, 'dtype': 'REAL'},
    'DB3_DBD252': {'db': 3, 'offset': 252, 'dtype': 'REAL'},
    'DB3_DBD256': {'db': 3, 'offset': 256, 'dtype': 'REAL'},
    'DB3_DBD260': {'db': 3, 'offset': 260, 'dtype': 'REAL'},
    'DB3_DBD264': {'db': 3, 'offset': 264, 'dtype': 'REAL'},
    'DB3_DBD268': {'db': 3, 'offset': 268, 'dtype': 'REAL'},
    'DB3_DBD272': {'db': 3, 'offset': 272, 'dtype': 'REAL'},
    'DB3_DBD276': {'db': 3, 'offset': 276, 'dtype': 'REAL'},
    'DB3_DBD280': {'db': 3, 'offset': 280, 'dtype': 'REAL'},
    'DB3_DBD284': {'db': 3, 'offset': 284, 'dtype': 'REAL'},
    'DB3_DBD288': {'db': 3, 'offset': 288, 'dtype': 'REAL'},
    'DB3_DBD292': {'db': 3, 'offset': 292, 'dtype': 'REAL'},
    'DB3_DBD296': {'db': 3, 'offset': 296, 'dtype': 'REAL'},
    'DB3_DBD300': {'db': 3, 'offset': 300, 'dtype': 'REAL'},
    'DB3_DBD304': {'db': 3, 'offset': 304, 'dtype': 'REAL'},
    'DB3_DBD308': {'db': 3, 'offset': 308, 'dtype': 'REAL'},
    'DB3_DBD312': {'db': 3, 'offset': 312, 'dtype': 'REAL'},
    'DB3_DBD316': {'db': 3, 'offset': 316, 'dtype': 'REAL'},
    'DB3_DBD320': {'db': 3, 'offset': 320, 'dtype': 'REAL'},
    'DB3_DBD324': {'db': 3, 'offset': 324, 'dtype': 'REAL'},
    'DB3_DBD328': {'db': 3, 'offset': 328, 'dtype': 'REAL'},
    'DB3_DBD332': {'db': 3, 'offset': 332, 'dtype': 'REAL'},
    'DB3_DBD336': {'db': 3, 'offset': 336, 'dtype': 'REAL'},
    'DB3_DBD340': {'db': 3, 'offset': 340, 'dtype': 'REAL'},
    'DB3_DBD344': {'db': 3, 'offset': 344, 'dtype': 'REAL'},
    'DB3_DBD348': {'db': 3, 'offset': 348, 'dtype': 'REAL'},
    'DB3_DBD352': {'db': 3, 'offset': 352, 'dtype': 'REAL'},
    'DB3_DBD356': {'db': 3, 'offset': 356, 'dtype': 'REAL'},
    'DB3_DBD360': {'db': 3, 'offset': 360, 'dtype': 'REAL'},
    'DB3_DBD364': {'db': 3, 'offset': 364, 'dtype': 'REAL'},
    'DB3_DBD368': {'db': 3, 'offset': 368, 'dtype': 'REAL'},
    'DB3_DBD372': {'db': 3, 'offset': 372, 'dtype': 'REAL'},
    'DB3_DBD376': {'db': 3, 'offset': 376, 'dtype': 'REAL'},
    'DB3_DBD380': {'db': 3, 'offset': 380, 'dtype': 'REAL'},
    'DB3_DBD384': {'db': 3, 'offset': 384, 'dtype': 'REAL'},
    'DB3_DBD388': {'db': 3, 'offset': 388, 'dtype': 'REAL'},
    'DB3_DBD392': {'db': 3, 'offset': 392, 'dtype': 'REAL'},
    'DB3_DBD396': {'db': 3, 'offset': 396, 'dtype': 'REAL'},
    'DB3_DBD400': {'db': 3, 'offset': 400, 'dtype': 'REAL'},
    'DB3_DBD404': {'db': 3, 'offset': 404, 'dtype': 'REAL'},
    'DB3_DBD408': {'db': 3, 'offset': 408, 'dtype': 'REAL'},
    'DB3_DBD412': {'db': 3, 'offset': 412, 'dtype': 'REAL'},
    'DB3_DBD416': {'db': 3, 'offset': 416, 'dtype': 'REAL'},
    'DB3_DBD420': {'db': 3, 'offset': 420, 'dtype': 'REAL'},
    'DB3_DBD424': {'db': 3, 'offset': 424, 'dtype': 'REAL'},
    'DB3_DBD428': {'db': 3, 'offset': 428, 'dtype': 'REAL'},
    'DB3_DBD432': {'db': 3, 'offset': 432, 'dtype': 'REAL'},
    'DB3_DBD436': {'db': 3, 'offset': 436, 'dtype': 'REAL'},
    'DB3_DBD440': {'db': 3, 'offset': 440, 'dtype': 'REAL'},
    'DB3_DBD444': {'db': 3, 'offset': 444, 'dtype': 'REAL'},
    'DB3_DBD448': {'db': 3, 'offset': 448, 'dtype': 'REAL'},
    'DB3_DBD452': {'db': 3, 'offset': 452, 'dtype': 'REAL'},
    'DB3_DBD456': {'db': 3, 'offset': 456, 'dtype': 'REAL'},
    'DB3_DBD460': {'db': 3, 'offset': 460, 'dtype': 'REAL'},
    'DB3_DBD464': {'db': 3, 'offset': 464, 'dtype': 'REAL'},
    'DB3_DBD468': {'db': 3, 'offset': 468, 'dtype': 'REAL'},
    'DB3_DBD472': {'db': 3, 'offset': 472, 'dtype': 'REAL'},
    'DB3_DBD476': {'db': 3, 'offset': 476, 'dtype': 'REAL'},
    'DB3_DBD480': {'db': 3, 'offset': 480, 'dtype': 'REAL'},
    'DB3_DBD484': {'db': 3, 'offset': 484, 'dtype': 'REAL'},
    'DB3_DBD488': {'db': 3, 'offset': 488, 'dtype': 'REAL'},
    'DB3_DBD492': {'db': 3, 'offset': 492, 'dtype': 'REAL'},
    'DB3_DBD496': {'db': 3, 'offset': 496, 'dtype': 'REAL'},
    'DB3_DBD500': {'db': 3, 'offset': 500, 'dtype': 'REAL'},
    'DB3_DBD504': {'db': 3, 'offset': 504, 'dtype': 'REAL'},
    'DB3_DBD508': {'db': 3, 'offset': 508, 'dtype': 'REAL'},
    'DB3_DBD512': {'db': 3, 'offset': 512, 'dtype': 'REAL'},
    'DB3_DBD516': {'db': 3, 'offset': 516, 'dtype': 'REAL'},
    'DB3_DBD520': {'db': 3, 'offset': 520, 'dtype': 'REAL'},
    'DB3_DBD524': {'db': 3, 'offset': 524, 'dtype': 'REAL'},
    'DB3_DBD528': {'db': 3, 'offset': 528, 'dtype': 'REAL'},
    'DB3_DBD532': {'db': 3, 'offset': 532, 'dtype': 'REAL'},
    'DB3_DBD536': {'db': 3, 'offset': 536, 'dtype': 'REAL'},
    'DB3_DBD540': {'db': 3, 'offset': 540, 'dtype': 'REAL'},
    'DB3_DBD544': {'db': 3, 'offset': 544, 'dtype': 'REAL'},
    'DB3_DBD548': {'db': 3, 'offset': 548, 'dtype': 'REAL'},
    'DB3_DBD552': {'db': 3, 'offset': 552, 'dtype': 'REAL'},
    'DB3_DBD556': {'db': 3, 'offset': 556, 'dtype': 'REAL'},
    'DB3_DBD560': {'db': 3, 'offset': 560, 'dtype': 'REAL'},
    'DB3_DBD564': {'db': 3, 'offset': 564, 'dtype': 'REAL'},
    'DB3_DBD568': {'db': 3, 'offset': 568, 'dtype': 'REAL'},
    'DB3_DBD572': {'db': 3, 'offset': 572, 'dtype': 'REAL'},
    'DB3_DBD576': {'db': 3, 'offset': 576, 'dtype': 'REAL'},
    'DB3_DBD580': {'db': 3, 'offset': 580, 'dtype': 'REAL'},
    'DB3_DBD584': {'db': 3, 'offset': 584, 'dtype': 'REAL'},
    'DB3_DBD588': {'db': 3, 'offset': 588, 'dtype': 'REAL'},
    'DB3_DBD592': {'db': 3, 'offset': 592, 'dtype': 'REAL'},
    'DB3_DBD596': {'db': 3, 'offset': 596, 'dtype': 'REAL'},
    'DB3_DBD600': {'db': 3, 'offset': 600, 'dtype': 'REAL'},
    'DB3_DBD604': {'db': 3, 'offset': 604, 'dtype': 'REAL'},
    'DB3_DBD608': {'db': 3, 'offset': 608, 'dtype': 'REAL'},
    'DB3_DBD612': {'db': 3, 'offset': 612, 'dtype': 'REAL'},
    'DB3_DBD616': {'db': 3, 'offset': 616, 'dtype': 'REAL'},
    'DB3_DBD620': {'db': 3, 'offset': 620, 'dtype': 'REAL'},
    'DB3_DBD624': {'db': 3, 'offset': 624, 'dtype': 'REAL'},
    'DB3_DBD628': {'db': 3, 'offset': 628, 'dtype': 'REAL'},
    'DB3_DBD632': {'db': 3, 'offset': 632, 'dtype': 'REAL'},
    'DB3_DBD636': {'db': 3, 'offset': 636, 'dtype': 'REAL'},
    'DB3_DBD640': {'db': 3, 'offset': 640, 'dtype': 'REAL'},
    'DB3_DBD644': {'db': 3, 'offset': 644, 'dtype': 'REAL'},
    'DB3_DBD648': {'db': 3, 'offset': 648, 'dtype': 'REAL'},
    'DB3_DBD652': {'db': 3, 'offset': 652, 'dtype': 'REAL'},
    'DB3_DBD656': {'db': 3, 'offset': 656, 'dtype': 'REAL'},
    'DB3_DBD660': {'db': 3, 'offset': 660, 'dtype': 'REAL'},
    'DB3_DBD664': {'db': 3, 'offset': 664, 'dtype': 'REAL'},
    'DB3_DBD668': {'db': 3, 'offset': 668, 'dtype': 'REAL'},
    'DB3_DBD672': {'db': 3, 'offset': 672, 'dtype': 'REAL'},
    'DB3_DBD676': {'db': 3, 'offset': 676, 'dtype': 'REAL'},
    'DB3_DBD680': {'db': 3, 'offset': 680, 'dtype': 'REAL'},
    'DB3_DBD684': {'db': 3, 'offset': 684, 'dtype': 'REAL'},
    'DB3_DBD688': {'db': 3, 'offset': 688, 'dtype': 'REAL'},
    'DB3_DBD692': {'db': 3, 'offset': 692, 'dtype': 'REAL'},
    'DB3_DBD696': {'db': 3, 'offset': 696, 'dtype': 'REAL'},
    'DB3_DBD700': {'db': 3, 'offset': 700, 'dtype': 'REAL'},
    'DB3_DBD704': {'db': 3, 'offset': 704, 'dtype': 'REAL'},
    'DB3_DBD708': {'db': 3, 'offset': 708, 'dtype': 'REAL'},
    'DB3_DBD712': {'db': 3, 'offset': 712, 'dtype': 'REAL'},
    'DB3_DBD716': {'db': 3, 'offset': 716, 'dtype': 'REAL'},
    'DB3_DBD720': {'db': 3, 'offset': 720, 'dtype': 'REAL'},
    'DB3_DBD724': {'db': 3, 'offset': 724, 'dtype': 'REAL'},
    'DB3_DBD728': {'db': 3, 'offset': 728, 'dtype': 'REAL'},
    'DB3_DBD732': {'db': 3, 'offset': 732, 'dtype': 'REAL'},
    'DB3_DBD736': {'db': 3, 'offset': 736, 'dtype': 'REAL'},
    'DB3_DBD740': {'db': 3, 'offset': 740, 'dtype': 'REAL'},
    'DB3_DBD744': {'db': 3, 'offset': 744, 'dtype': 'REAL'},
    'DB3_DBD748': {'db': 3, 'offset': 748, 'dtype': 'REAL'},
    'DB3_DBD752': {'db': 3, 'offset': 752, 'dtype': 'REAL'},
    'DB3_DBD756': {'db': 3, 'offset': 756, 'dtype': 'REAL'},
    'DB3_DBD760': {'db': 3, 'offset': 760, 'dtype': 'REAL'},
    'DB3_DBD764': {'db': 3, 'offset': 764, 'dtype': 'REAL'},
    'DB3_DBD768': {'db': 3, 'offset': 768, 'dtype': 'REAL'},
    'DB3_DBD772': {'db': 3, 'offset': 772, 'dtype': 'REAL'},
    'DB3_DBD776': {'db': 3, 'offset': 776, 'dtype': 'REAL'},
    'DB3_DBD780': {'db': 3, 'offset': 780, 'dtype': 'REAL'},
    'DB3_DBD784': {'db': 3, 'offset': 784, 'dtype': 'REAL'},
    'DB3_DBD788': {'db': 3, 'offset': 788, 'dtype': 'REAL'},
    'DB3_DBD792': {'db': 3, 'offset': 792, 'dtype': 'REAL'},
    'DB3_DBD796': {'db': 3, 'offset': 796, 'dtype': 'REAL'},
    'DB3_DBD800': {'db': 3, 'offset': 800, 'dtype': 'REAL'},
    'DB3_DBD804': {'db': 3, 'offset': 804, 'dtype': 'REAL'},
    'DB3_DBD808': {'db': 3, 'offset': 808, 'dtype': 'REAL'},
    'DB3_DBD812': {'db': 3, 'offset': 812, 'dtype': 'REAL'},
    'DB3_DBD816': {'db': 3, 'offset': 816, 'dtype': 'REAL'},
    'DB3_DBD820': {'db': 3, 'offset': 820, 'dtype': 'REAL'},
    'DB3_DBD824': {'db': 3, 'offset': 824, 'dtype': 'REAL'},
    'DB3_DBD828': {'db': 3, 'offset': 828, 'dtype': 'REAL'},
    'DB3_DBD832': {'db': 3, 'offset': 832, 'dtype': 'REAL'},
    'DB3_DBD836': {'db': 3, 'offset': 836, 'dtype': 'REAL'},
    'DB3_DBD840': {'db': 3, 'offset': 840, 'dtype': 'REAL'},
    'DB3_DBD844': {'db': 3, 'offset': 844, 'dtype': 'REAL'},
    'DB3_DBD848': {'db': 3, 'offset': 848, 'dtype': 'REAL'},
    'DB3_DBD852': {'db': 3, 'offset': 852, 'dtype': 'REAL'},
    'DB3_DBD856': {'db': 3, 'offset': 856, 'dtype': 'REAL'},
    'DB3_DBD860': {'db': 3, 'offset': 860, 'dtype': 'REAL'},
    'DB3_DBD864': {'db': 3, 'offset': 864, 'dtype': 'REAL'},
    'DB3_DBD868': {'db': 3, 'offset': 868, 'dtype': 'REAL'},
    'DB3_DBD872': {'db': 3, 'offset': 872, 'dtype': 'REAL'},
    'DB3_DBD876': {'db': 3, 'offset': 876, 'dtype': 'REAL'},
    'DB3_DBD880': {'db': 3, 'offset': 880, 'dtype': 'REAL'},
    'DB3_DBD884': {'db': 3, 'offset': 884, 'dtype': 'REAL'},
    'DB3_DBD888': {'db': 3, 'offset': 888, 'dtype': 'REAL'},
    'DB3_DBD892': {'db': 3, 'offset': 892, 'dtype': 'REAL'},
    'DB3_DBD896': {'db': 3, 'offset': 896, 'dtype': 'REAL'},
    'DB3_DBD900': {'db': 3, 'offset': 900, 'dtype': 'REAL'},
    'DB3_DBD904': {'db': 3, 'offset': 904, 'dtype': 'REAL'},
    'DB3_DBD908': {'db': 3, 'offset': 908, 'dtype': 'REAL'},
    'DB3_DBD912': {'db': 3, 'offset': 912, 'dtype': 'REAL'},
    'DB3_DBD916': {'db': 3, 'offset': 916, 'dtype': 'REAL'},
    'DB3_DBD920': {'db': 3, 'offset': 920, 'dtype': 'REAL'},
    'DB3_DBD924': {'db': 3, 'offset': 924, 'dtype': 'REAL'},
    'DB3_DBD928': {'db': 3, 'offset': 928, 'dtype': 'REAL'},
    'DB3_DBD932': {'db': 3, 'offset': 932, 'dtype': 'REAL'},
    'DB3_DBD936': {'db': 3, 'offset': 936, 'dtype': 'REAL'},
    'DB3_DBD940': {'db': 3, 'offset': 940, 'dtype': 'REAL'},
    'DB3_DBD944': {'db': 3, 'offset': 944, 'dtype': 'REAL'},
    'DB3_DBD948': {'db': 3, 'offset': 948, 'dtype': 'REAL'},
    'DB3_DBD952': {'db': 3, 'offset': 952, 'dtype': 'REAL'},
    'DB3_DBD956': {'db': 3, 'offset': 956, 'dtype': 'REAL'},
    'DB3_DBD960': {'db': 3, 'offset': 960, 'dtype': 'REAL'},
    'DB3_DBD964': {'db': 3, 'offset': 964, 'dtype': 'REAL'},
    'DB3_DBD968': {'db': 3, 'offset': 968, 'dtype': 'REAL'},
    'DB3_DBD972': {'db': 3, 'offset': 972, 'dtype': 'REAL'},
    'DB3_DBD976': {'db': 3, 'offset': 976, 'dtype': 'REAL'},
    'DB3_DBD980': {'db': 3, 'offset': 980, 'dtype': 'REAL'},
    'DB3_DBD984': {'db': 3, 'offset': 984, 'dtype': 'REAL'},
    'DB3_DBD988': {'db': 3, 'offset': 988, 'dtype': 'REAL'},
    'DB3_DBD992': {'db': 3, 'offset': 992, 'dtype': 'REAL'},
    'DB3_DBD996': {'db': 3, 'offset': 996, 'dtype': 'REAL'},
    'DB3_DBD1000': {'db': 3, 'offset': 1000, 'dtype': 'REAL'},
    'DB3_DBD1004': {'db': 3, 'offset': 1004, 'dtype': 'REAL'},
    'DB3_DBD1008': {'db': 3, 'offset': 1008, 'dtype': 'REAL'},
    'DB3_DBD1012': {'db': 3, 'offset': 1012, 'dtype': 'REAL'},
    'DB3_DBD1016': {'db': 3, 'offset': 1016, 'dtype': 'REAL'},
    'DB3_DBD1020': {'db': 3, 'offset': 1020, 'dtype': 'REAL'},
    'DB3_DBD1024': {'db': 3, 'offset': 1024, 'dtype': 'REAL'},
    'DB3_DBD1028': {'db': 3, 'offset': 1028, 'dtype': 'REAL'},
    'DB3_DBD1032': {'db': 3, 'offset': 1032, 'dtype': 'REAL'},
    'DB3_DBD1036': {'db': 3, 'offset': 1036, 'dtype': 'REAL'},
    'DB3_DBD1040': {'db': 3, 'offset': 1040, 'dtype': 'REAL'},
    'DB3_DBD1044': {'db': 3, 'offset': 1044, 'dtype': 'REAL'},
    'DB3_DBD1048': {'db': 3, 'offset': 1048, 'dtype': 'REAL'},
    'DB3_DBD1052': {'db': 3, 'offset': 1052, 'dtype': 'REAL'},
    'DB3_DBD1056': {'db': 3, 'offset': 1056, 'dtype': 'REAL'},
    'DB3_DBD1060': {'db': 3, 'offset': 1060, 'dtype': 'REAL'},
    'DB3_DBD1064': {'db': 3, 'offset': 1064, 'dtype': 'REAL'},
    'DB3_DBD1068': {'db': 3, 'offset': 1068, 'dtype': 'REAL'},
    'DB3_DBD1072': {'db': 3, 'offset': 1072, 'dtype': 'REAL'},
    'DB3_DBD1076': {'db': 3, 'offset': 1076, 'dtype': 'REAL'},
    'DB3_DBD1080': {'db': 3, 'offset': 1080, 'dtype': 'REAL'},
    'DB3_DBD1084': {'db': 3, 'offset': 1084, 'dtype': 'REAL'},
    'DB3_DBD1088': {'db': 3, 'offset': 1088, 'dtype': 'REAL'},
    'DB3_DBD1092': {'db': 3, 'offset': 1092, 'dtype': 'REAL'},
    'DB3_DBD1096': {'db': 3, 'offset': 1096, 'dtype': 'REAL'},
    'DB3_DBD1100': {'db': 3, 'offset': 1100, 'dtype': 'REAL'},
    'DB3_DBD1104': {'db': 3, 'offset': 1104, 'dtype': 'REAL'},
    'DB3_DBD1108': {'db': 3, 'offset': 1108, 'dtype': 'REAL'},
    'DB3_DBD1112': {'db': 3, 'offset': 1112, 'dtype': 'REAL'},
    'DB3_DBD1116': {'db': 3, 'offset': 1116, 'dtype': 'REAL'},
    'DB3_DBD1120': {'db': 3, 'offset': 1120, 'dtype': 'REAL'},
    'DB3_DBD1124': {'db': 3, 'offset': 1124, 'dtype': 'REAL'},
    'DB3_DBD1128': {'db': 3, 'offset': 1128, 'dtype': 'REAL'},
    'DB3_DBD1132': {'db': 3, 'offset': 1132, 'dtype': 'REAL'},
    'DB3_DBD1136': {'db': 3, 'offset': 1136, 'dtype': 'REAL'},
    'DB3_DBD1140': {'db': 3, 'offset': 1140, 'dtype': 'REAL'},
    'DB3_DBD1144': {'db': 3, 'offset': 1144, 'dtype': 'REAL'},
    'DB3_DBD1148': {'db': 3, 'offset': 1148, 'dtype': 'REAL'},
    'DB3_DBD1152': {'db': 3, 'offset': 1152, 'dtype': 'REAL'},
    'DB3_DBD1156': {'db': 3, 'offset': 1156, 'dtype': 'REAL'},
    'DB3_DBD1160': {'db': 3, 'offset': 1160, 'dtype': 'REAL'},
    'DB3_DBD1164': {'db': 3, 'offset': 1164, 'dtype': 'REAL'},
    'DB3_DBD1168': {'db': 3, 'offset': 1168, 'dtype': 'REAL'},
    'DB3_DBD1172': {'db': 3, 'offset': 1172, 'dtype': 'REAL'},
}

# -------------------------------
# Setup
# -------------------------------
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s')
logger = logging.getLogger("S7-PLC")

plc_connection = None
connection_lock = Lock()
last_write_time = 0
read_cache = {}
last_cache_update = 0

# -------------------------------
# Optimized PLC Connection
# -------------------------------
def get_plc_connection(ip=PLC_IP, max_retries=2):  # Reduced retries for speed
    global plc_connection
    with connection_lock:
        for attempt in range(max_retries):
            try:
                if plc_connection and plc_connection.get_connected():
                    return plc_connection

                if plc_connection:
                    try:
                        plc_connection.destroy()
                    except Exception as e:
                        logger.debug(f"Error destroying connection: {e}")
                        pass

                plc_connection = snap7.client.Client()
                plc_connection.set_connection_params(PLC_IP, PLC_RACK, PLC_SLOT)
                plc_connection.set_connection_type(3)  # PG connection
                plc_connection.connect(PLC_IP, PLC_RACK, PLC_SLOT, CONNECTION_TIMEOUT)
                logger.info(f"Connected to PLC (attempt {attempt+1})")
                return plc_connection

            except snap7.exceptions.S7Error as e:
                logger.warning(f"Snap7 error during connection (attempt {attempt+1}): {e}")
                plc_connection = None
                if attempt < max_retries - 1:
                    time.sleep(0.05 * (attempt + 1))
            except Exception as e:
                logger.error(f"General error during connection (attempt {attempt+1}): {e}")
                plc_connection = None
                if attempt < max_retries - 1:
                    time.sleep(0.05 * (attempt + 1))
        return None

# Optimized Data Utilities
# -------------------------------
@lru_cache(maxsize=256)  # Increased cache size
def get_tag_config(tag):
    """Cached tag configuration lookup"""
    return TAG_CONFIG.get(tag)

def prepare_plc_data(tag, value):
    config = get_tag_config(tag)
    if not config:
        raise ValueError(f"Unknown tag: {tag}")

    db = config['db']
    offset = config['offset']
    dtype = config['dtype']

    try:
        if dtype == 'DINT':
            data = int(value).to_bytes(4, byteorder='big', signed=True)
        elif dtype == 'REAL':
            data = struct.pack('>f', float(value))
        elif dtype == 'STRING':
            value = str(value)[:config.get('max_length', MAX_STRING_LENGTH)]
            str_bytes = value.encode('ascii')
            str_len = len(str_bytes)
            data = bytearray(config.get('max_length', MAX_STRING_LENGTH) + 2)
            data[0] = config.get('max_length', MAX_STRING_LENGTH)
            data[1] = str_len
            data[2:2+str_len] = str_bytes
        else:
            raise ValueError(f"Unsupported data type: {dtype}")

        if not (0 <= offset < MAX_DB_SIZE) or not (0 <= offset + len(data) <= MAX_DB_SIZE):
            raise ValueError("Data offset/length out of bounds")

        return db, offset, data
    except Exception as e:
        raise ValueError(f"Error preparing tag '{tag}': {e}")

# Optimized Batch Operations
# -------------------------------
def batch_read_plc(plc, tags):
    global read_cache, last_cache_update

    current_time = time.time()
    cached_data = {}
    uncached_tags = []

    if current_time - last_cache_update < READ_CACHE_TTL:
        for tag in tags:
            if tag in read_cache:
                cached_data[tag] = read_cache[tag]
            else:
                uncached_tags.append(tag)
    else:
        uncached_tags = list(tags)

    if not uncached_tags:
        return cached_data

    results = cached_data
    grouped_reads = defaultdict(list)

    for tag in uncached_tags:
        config = get_tag_config(tag)
        if config:
            grouped_reads[config['db']].append((tag, config))
        else:
            results[tag] = None
            logger.warning(f"Tag '{tag}' not found in configuration.")

    for db_num, tag_configs in grouped_reads.items():
        if not tag_configs:
            continue

        min_offset = min(cfg['offset'] for _, cfg in tag_configs)
        max_offset = 0
        for _, cfg in tag_configs:
            end_offset = cfg['offset'] + (4 if cfg['dtype'] in ['DINT', 'REAL'] else cfg.get('max_length', MAX_STRING_LENGTH) + 2)
            max_offset = max(max_offset, end_offset)

        try:
            read_start_time = time.time()
            block = plc.db_read(db_num, min_offset, max_offset - min_offset)
            logger.debug(f"Read DB {db_num}, offset {min_offset}, length {max_offset - min_offset} in {time.time() - read_start_time:.4f}s")
            for tag, cfg in tag_configs:
                start = cfg['offset'] - min_offset
                try:
                    if cfg['dtype'] == 'REAL':
                        results[tag] = round(struct.unpack('>f', block[start:start+4])[0], 2)
                    elif cfg['dtype'] == 'DINT':
                        results[tag] = int.from_bytes(block[start:start+4], byteorder='big', signed=True)
                    elif cfg['dtype'] == 'STRING':
                        length = block[start+1]
                        results[tag] = block[start+2:start+2+length].decode('ascii').strip('\x00')
                    else:
                        results[tag] = None
                except Exception as e:
                    results[tag] = None
                    logger.error(f"Error processing tag '{tag}' in DB {db_num}: {e}")
        except snap7.exceptions.S7Error as e:
            logger.error(f"Snap7 error reading DB {db_num}: {e}")
            for tag, _ in tag_configs:
                results[tag] = None
        except Exception as e:
            logger.error(f"General error reading DB {db_num}: {e}")
            for tag, _ in tag_configs:
                results[tag] = None

    read_cache.update(results)
    last_cache_update = current_time
    return results

def batch_write_plc(plc, tag_value_pairs):
    global last_write_time

    results = {}
    grouped_writes = defaultdict(bytearray)
    write_offsets = defaultdict(dict) # {db: {offset: (data, tag)}}

    current_time = time.time()
    elapsed = current_time - last_write_time
    if elapsed < MIN_WRITE_INTERVAL:
        sleep_duration = MIN_WRITE_INTERVAL - elapsed
        time.sleep(sleep_duration)
        logger.debug(f"Throttling write for {sleep_duration:.4f}s")

    prepared_data = {}
    for tag, value in tag_value_pairs:
        try:
            db, offset, data = prepare_plc_data(tag, value)
            if db not in prepared_data:
                prepared_data[db] = {}
            prepared_data[db][offset] = (data, tag)
        except ValueError as e:
            results[tag] = {"status": "Failed", "error": str(e)}
        except Exception as e:
            results[tag] = {"status": "Failed", "error": f"Unexpected error preparing '{tag}': {e}"}

    for db_num, writes in prepared_data.items():
        sorted_offsets = sorted(writes.keys())
        # Attempt to combine adjacent writes within the same DB
        combined_writes = []
        current_offset = -1
        current_data = bytearray()
        current_tags = []

        for offset in sorted_offsets:
            data, tag = writes[offset]
            if offset == current_offset + len(current_data) and current_offset != -1:
                current_data.extend(data)
                current_tags.append(tag)
            else:
                if current_offset != -1:
                    combined_writes.append((db_num, current_offset, bytes(current_data), list(current_tags)))
                current_offset = offset
                current_data = bytearray(data)
                current_tags = [tag]
        if current_offset != -1:
            combined_writes.append((db_num, current_offset, bytes(current_data), list(current_tags)))

        for db, offset, data, tags in combined_writes:
            try:
                write_start_time = time.time()
                plc.db_write(db, offset, data)
                logger.debug(f"Wrote {len(data)} bytes to DB {db}, offset {offset} in {time.time() - write_start_time:.4f}s for tags: {tags}")
                for tag in tags:
                    results[tag] = {"status": "Success"}
            except snap7.exceptions.S7Error as e:
                logger.error(f"Snap7 error writing to DB {db}, offset {offset}: {e} for tags: {tags}")
                for tag in tags:
                    results[tag] = {"status": "Failed", "error": str(e)}
            except Exception as e:
                logger.error(f"General error writing to DB {db}, offset {offset}: {e} for tags: {tags}")
                for tag in tags:
                    results[tag] = {"status": "Failed", "error": f"Unexpected write error: {e}"}

    last_write_time = current_time
    return results

# Optimized API Endpoints
# -------------------------------
@app.route('/insertDataToPlc', methods=['POST'])
def insert_data_to_plc():
    start_time = time.time()
    try:
        plc_ip = request.args.get('ip') or PLC_IP
        data_list = request.json

        if not isinstance(data_list, list):
            return jsonify({"message": "Payload must be a list"}), 400

        plc = get_plc_connection(plc_ip)
        if not plc:
            return jsonify({"message": "Failed to connect to PLC"}), 500

        tag_value_pairs = []
        value_mapping = {}
        for item in data_list:
            if isinstance(item, dict) and 'tag' in item and 'value' in item:
                tag_value_pairs.append((item['tag'], item['value']))
                value_mapping[item['tag']] = item['value']

        with connection_lock:
            write_results = batch_write_plc(plc, tag_value_pairs)

        results = {}
        for tag, result in write_results.items():
            config = get_tag_config(tag)
            results[tag] = {
                "data_type": config['dtype'] if config else "UNKNOWN",
                "status": result["status"],
                "value_written": value_mapping.get(tag, None),
                "error": result.get("error")
            }

        execution_time = time.time() - start_time
        logger.info(f"Write completed in {execution_time:.3f}s for {len(data_list)} tags.")
        return jsonify({
            "message": "Batch write completed",
            "execution_time": f"{execution_time:.3f}s",
            "data": results
        }), 200

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Write error in {execution_time:.3f}s: {str(e)}")
        return jsonify({
            "message": "Exception occurred during write",
            "error": str(e),
            "execution_time": f"{execution_time:.3f}s"
        }), 500

@app.route('/getTagValues', methods=['POST'])
def get_tag_values():
    start_time = time.time()
    try:
        plc_ip = request.args.get('ip') or PLC_IP
        requested_tags = request.json.get('tags', [])

        if not requested_tags:
            return jsonify({"message": "No tags specified"}), 400

        plc = get_plc_connection(plc_ip)
        if not plc:
            return jsonify({"message": "PLC connection failed"}), 500

        read_start_time = time.time()
        results = batch_read_plc(plc, requested_tags)
        read_execution_time = time.time() - read_start_time
        logger.info(f"Read {len(requested_tags)} tags completed in {read_execution_time:.3f}s.")

        return jsonify({
            "data": results,
            "execution_time": f"{time.time()-start_time:.3f}s"
        }), 200

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Read error in {execution_time:.3f}s: {str(e)}")
        return jsonify({
            "message": "Read failed",
            "error": str(e),
            "execution_time": f"{execution_time:.3f}s"
        }), 500

# App Run
# -------------------------------
if __name__ == '__main__':
    try:
        get_plc_connection()
        app.run(host='0.0.0.0', port=8083, threaded=True)
    finally:
        if plc_connection:
            try:
                plc_connection.disconnect()
                plc_connection.destroy()
            except Exception as e:
                logger.debug(f"Error during disconnection/destruction: {e}")
                pass