# this final tested code for s7 1200 plc 
from datetime import datetime
import random
import snap7
import struct
from flask import Flask, Response, json, request, jsonify
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
MIN_WRITE_INTERVAL = 0.05  # 50ms minimum between writes
READ_CACHE_TTL = 0.1  # Cache reads for 100ms

TAG_CONFIG = {
    'DB11_DBD0': {'db': 11, 'offset': 0, 'dtype': 'DINT'},
    'DB11_DBD4': {'db': 11, 'offset': 4, 'dtype': 'DINT'},
    'DB11_DBD8': {'db': 11, 'offset': 8, 'dtype': 'DINT'},
    'DB11_DBD12': {'db': 11, 'offset': 12, 'dtype': 'DINT'},
    'DB11_DBD16': {'db': 11, 'offset': 16, 'dtype': 'DINT'},
    'DB11_DBD20': {'db': 11, 'offset': 20, 'dtype': 'DINT'},
    'DB11_DBD24': {'db': 11, 'offset': 24, 'dtype': 'DINT'},
    'DB11_DBD28': {'db': 11, 'offset': 28, 'dtype': 'DINT'},
    'DB11_DBD32': {'db': 11, 'offset': 32, 'dtype': 'DINT'},
    'DB11_DBD36': {'db': 11, 'offset': 36, 'dtype': 'DINT'},
    'DB11_DBD40': {'db': 11, 'offset': 40, 'dtype': 'DINT'},
    'DB11_DBD44': {'db': 11, 'offset': 44, 'dtype': 'DINT'},
    'DB11_DBD48': {'db': 11, 'offset': 48, 'dtype': 'DINT'},
    'DB11_DBD52': {'db': 11, 'offset': 52, 'dtype': 'DINT'},
    'DB11_DBD56': {'db': 11, 'offset': 56, 'dtype': 'DINT'},
    'DB11_DBD60': {'db': 11, 'offset': 60, 'dtype': 'DINT'},
    'DB11_DBD64': {'db': 11, 'offset': 64, 'dtype': 'DINT'},
    'DB11_DBD68': {'db': 11, 'offset': 68, 'dtype': 'DINT'},
    'DB11_DBD72': {'db': 11, 'offset': 72, 'dtype': 'DINT'},
    'DB11_DBD76': {'db': 11, 'offset': 76, 'dtype': 'DINT'},
    'DB11_DBD80': {'db': 11, 'offset': 80, 'dtype': 'DINT'},
    'DB11_DBD84': {'db': 11, 'offset': 84, 'dtype': 'DINT'},
    'DB11_DBD88': {'db': 11, 'offset': 88, 'dtype': 'DINT'},
    'DB11_DBD92': {'db': 11, 'offset': 92, 'dtype': 'DINT'},
    'DB11_DBD96': {'db': 11, 'offset': 96, 'dtype': 'DINT'},
    'DB11_DBD100': {'db': 11, 'offset': 100, 'dtype': 'DINT'},
    'DB4_DBD0': {'db': 4, 'offset': 0, 'dtype': 'DINT'},
    'DB4_DBD4': {'db': 4, 'offset': 4, 'dtype': 'DINT'},
    'DB4_DBD8': {'db': 4, 'offset': 8, 'dtype': 'DINT'},
    'DB4_DBD12': {'db': 4, 'offset': 12, 'dtype': 'DINT'},
    'DB4_DBD16': {'db': 4, 'offset': 16, 'dtype': 'DINT'},
    'DB4_DBD20': {'db': 4, 'offset': 20, 'dtype': 'DINT'},
    'DB4_DBD24': {'db': 4, 'offset': 24, 'dtype': 'DINT'},
    'DB4_DBD28': {'db': 4, 'offset': 28, 'dtype': 'DINT'},
    'DB4_DBD32': {'db': 4, 'offset': 32, 'dtype': 'DINT'},
    'DB4_DBD36': {'db': 4, 'offset': 36, 'dtype': 'DINT'},
    'DB4_DBD40': {'db': 4, 'offset': 40, 'dtype': 'DINT'},
    'DB4_DBD44': {'db': 4, 'offset': 44, 'dtype': 'DINT'},
    'DB4_DBD48': {'db': 4, 'offset': 48, 'dtype': 'DINT'},
    'DB4_DBD52': {'db': 4, 'offset': 52, 'dtype': 'DINT'},
    'DB4_DBD56': {'db': 4, 'offset': 56, 'dtype': 'DINT'},
    'DB4_DBD60': {'db': 4, 'offset': 60, 'dtype': 'DINT'},
    'DB4_DBD64': {'db': 4, 'offset': 64, 'dtype': 'DINT'},
    'DB4_DBD68': {'db': 4, 'offset': 68, 'dtype': 'DINT'},
    'DB4_DBD72': {'db': 4, 'offset': 72, 'dtype': 'DINT'},
    'DB4_DBD76': {'db': 4, 'offset': 76, 'dtype': 'DINT'},
    'DB4_DBD80': {'db': 4, 'offset': 80, 'dtype': 'DINT'},
    'DB4_DBD84': {'db': 4, 'offset': 84, 'dtype': 'DINT'},
    'DB4_DBD88': {'db': 4, 'offset': 88, 'dtype': 'DINT'},
    'DB4_DBD92': {'db': 4, 'offset': 92, 'dtype': 'DINT'},
    'DB4_DBD96': {'db': 4, 'offset': 96, 'dtype': 'DINT'},
    'DB4_DBD100': {'db': 4, 'offset': 100, 'dtype': 'DINT'},
    'DB4_DBD104': {'db': 4, 'offset': 104, 'dtype': 'DINT'},
    'DB4_DBD108': {'db': 4, 'offset': 108, 'dtype': 'DINT'},
    'DB4_DBD112': {'db': 4, 'offset': 112, 'dtype': 'DINT'},
    'DB4_DBD116': {'db': 4, 'offset': 116, 'dtype': 'DINT'},
    'DB4_DBD120': {'db': 4, 'offset': 120, 'dtype': 'DINT'},
    'DB4_DBD124': {'db': 4, 'offset': 124, 'dtype': 'DINT'},
    'DB4_DBD128': {'db': 4, 'offset': 128, 'dtype': 'DINT'},
    'DB4_DBD132': {'db': 4, 'offset': 132, 'dtype': 'DINT'},
    'DB4_DBD136': {'db': 4, 'offset': 136, 'dtype': 'DINT'},
    'DB4_DBD140': {'db': 4, 'offset': 140, 'dtype': 'DINT'},
    'DB4_DBD144': {'db': 4, 'offset': 144, 'dtype': 'DINT'},
    'DB4_DBD148': {'db': 4, 'offset': 148, 'dtype': 'DINT'},
    'DB4_DBD152': {'db': 4, 'offset': 152, 'dtype': 'DINT'},
    'DB4_DBD156': {'db': 4, 'offset': 156, 'dtype': 'DINT'},
    'DB4_DBD160': {'db': 4, 'offset': 160, 'dtype': 'DINT'},
    'DB4_DBD164': {'db': 4, 'offset': 164, 'dtype': 'DINT'},
    'DB4_DBD168': {'db': 4, 'offset': 168, 'dtype': 'DINT'},
    'DB4_DBD172': {'db': 4, 'offset': 172, 'dtype': 'DINT'},
    'DB4_DBD176': {'db': 4, 'offset': 176, 'dtype': 'DINT'},
    'DB4_DBD180': {'db': 4, 'offset': 180, 'dtype': 'DINT'},
    'DB4_DBD184': {'db': 4, 'offset': 184, 'dtype': 'DINT'},
    'DB4_DBD188': {'db': 4, 'offset': 188, 'dtype': 'DINT'},
    'DB4_DBD192': {'db': 4, 'offset': 192, 'dtype': 'DINT'},
    'DB4_DBD196': {'db': 4, 'offset': 196, 'dtype': 'DINT'},
    'DB4_DBD200': {'db': 4, 'offset': 200, 'dtype': 'DINT'},
    'DB4_DBD204': {'db': 4, 'offset': 204, 'dtype': 'DINT'},
    'DB4_DBD208': {'db': 4, 'offset': 208, 'dtype': 'DINT'},
    'DB4_DBD212': {'db': 4, 'offset': 212, 'dtype': 'DINT'},
    'DB4_DBD216': {'db': 4, 'offset': 216, 'dtype': 'DINT'},
    'DB4_DBD220': {'db': 4, 'offset': 220, 'dtype': 'DINT'},
    'DB4_DBD224': {'db': 4, 'offset': 224, 'dtype': 'DINT'},
    'DB4_DBD228': {'db': 4, 'offset': 228, 'dtype': 'DINT'},
    'DB4_DBD232': {'db': 4, 'offset': 232, 'dtype': 'DINT'},
    'DB4_DBD236': {'db': 4, 'offset': 236, 'dtype': 'DINT'},
    'DB4_DBD240': {'db': 4, 'offset': 240, 'dtype': 'DINT'},
    'DB4_DBD244': {'db': 4, 'offset': 244, 'dtype': 'DINT'},
    'DB4_DBD248': {'db': 4, 'offset': 248, 'dtype': 'DINT'},
    'DB4_DBD252': {'db': 4, 'offset': 252, 'dtype': 'DINT'},
    'DB4_DBD256': {'db': 4, 'offset': 256, 'dtype': 'DINT'},
    'DB4_DBD260': {'db': 4, 'offset': 260, 'dtype': 'DINT'},
    'DB4_DBD264': {'db': 4, 'offset': 264, 'dtype': 'DINT'},
    'DB4_DBD268': {'db': 4, 'offset': 268, 'dtype': 'DINT'},
    'DB4_DBD272': {'db': 4, 'offset': 272, 'dtype': 'DINT'},
    'DB4_DBD276': {'db': 4, 'offset': 276, 'dtype': 'DINT'},
    'DB4_DBD280': {'db': 4, 'offset': 280, 'dtype': 'DINT'},
    'DB4_DBD284': {'db': 4, 'offset': 284, 'dtype': 'DINT'},
    'DB4_DBD288': {'db': 4, 'offset': 288, 'dtype': 'DINT'},
    'DB4_DBD292': {'db': 4, 'offset': 292, 'dtype': 'DINT'},
    'DB4_DBD296': {'db': 4, 'offset': 296, 'dtype': 'DINT'},
    'DB4_DBD300': {'db': 4, 'offset': 300, 'dtype': 'DINT'},
    'DB4_DBD304': {'db': 4, 'offset': 304, 'dtype': 'DINT'},
    'DB4_DBD308': {'db': 4, 'offset': 308, 'dtype': 'DINT'},
    'DB4_DBD312': {'db': 4, 'offset': 312, 'dtype': 'DINT'},
    'DB4_DBD316': {'db': 4, 'offset': 316, 'dtype': 'DINT'},
    'DB4_DBD320': {'db': 4, 'offset': 320, 'dtype': 'DINT'},
    'DB4_DBD324': {'db': 4, 'offset': 324, 'dtype': 'DINT'},
    'DB4_DBD328': {'db': 4, 'offset': 328, 'dtype': 'DINT'},
    'DB4_DBD332': {'db': 4, 'offset': 332, 'dtype': 'DINT'},
    'DB4_DBD336': {'db': 4, 'offset': 336, 'dtype': 'DINT'},
    'DB4_DBD340': {'db': 4, 'offset': 340, 'dtype': 'DINT'},
    'DB4_DBD344': {'db': 4, 'offset': 344, 'dtype': 'DINT'},
    'DB4_DBD348': {'db': 4, 'offset': 348, 'dtype': 'DINT'},
    'DB4_DBD352': {'db': 4, 'offset': 352, 'dtype': 'DINT'},
    'DB4_DBD356': {'db': 4, 'offset': 356, 'dtype': 'DINT'},
    'DB4_DBD360': {'db': 4, 'offset': 360, 'dtype': 'DINT'},
    'DB4_DBD364': {'db': 4, 'offset': 364, 'dtype': 'DINT'},
    'DB4_DBD368': {'db': 4, 'offset': 368, 'dtype': 'DINT'},
    'DB4_DBD372': {'db': 4, 'offset': 372, 'dtype': 'DINT'},
    'DB4_DBD376': {'db': 4, 'offset': 376, 'dtype': 'DINT'},
    'DB4_DBD380': {'db': 4, 'offset': 380, 'dtype': 'DINT'},
    'DB4_DBD384': {'db': 4, 'offset': 384, 'dtype': 'DINT'},
    'DB4_DBD388': {'db': 4, 'offset': 388, 'dtype': 'DINT'},
    'DB4_DBD392': {'db': 4, 'offset': 392, 'dtype': 'DINT'},
    'DB4_DBD396': {'db': 4, 'offset': 396, 'dtype': 'DINT'},
    'DB4_DBD400': {'db': 4, 'offset': 400, 'dtype': 'DINT'},
    'DB4_DBD404': {'db': 4, 'offset': 404, 'dtype': 'DINT'},
    'DB4_DBD408': {'db': 4, 'offset': 408, 'dtype': 'DINT'},
    'DB4_DBD412': {'db': 4, 'offset': 412, 'dtype': 'DINT'},
    'DB4_DBD416': {'db': 4, 'offset': 416, 'dtype': 'DINT'},
    'DB4_DBD420': {'db': 4, 'offset': 420, 'dtype': 'DINT'},
    'DB4_DBD424': {'db': 4, 'offset': 424, 'dtype': 'DINT'},
    'DB4_DBD428': {'db': 4, 'offset': 428, 'dtype': 'DINT'},
    'DB4_DBD432': {'db': 4, 'offset': 432, 'dtype': 'DINT'},
    'DB4_DBD436': {'db': 4, 'offset': 436, 'dtype': 'DINT'},
    'DB4_DBD440': {'db': 4, 'offset': 440, 'dtype': 'DINT'},
    'DB4_DBD444': {'db': 4, 'offset': 444, 'dtype': 'DINT'},
    'DB4_DBD448': {'db': 4, 'offset': 448, 'dtype': 'DINT'},
    'DB4_DBD452': {'db': 4, 'offset': 452, 'dtype': 'DINT'},
    'DB4_DBD456': {'db': 4, 'offset': 456, 'dtype': 'DINT'},
    'DB4_DBD460': {'db': 4, 'offset': 460, 'dtype': 'DINT'},
    'DB4_DBD464': {'db': 4, 'offset': 464, 'dtype': 'DINT'},
    'DB4_DBD468': {'db': 4, 'offset': 468, 'dtype': 'DINT'},
    'DB4_DBD472': {'db': 4, 'offset': 472, 'dtype': 'DINT'},
    'DB4_DBD476': {'db': 4, 'offset': 476, 'dtype': 'DINT'},
    'DB4_DBD480': {'db': 4, 'offset': 480, 'dtype': 'DINT'},
    'DB4_DBD484': {'db': 4, 'offset': 484, 'dtype': 'DINT'},
    'DB4_DBD488': {'db': 4, 'offset': 488, 'dtype': 'DINT'},
    'DB4_DBD492': {'db': 4, 'offset': 492, 'dtype': 'DINT'},
    'DB4_DBD496': {'db': 4, 'offset': 496, 'dtype': 'DINT'},
    'DB4_DBD500': {'db': 4, 'offset': 500, 'dtype': 'DINT'},
    'DB4_DBD504': {'db': 4, 'offset': 504, 'dtype': 'DINT'},
    'DB4_DBD508': {'db': 4, 'offset': 508, 'dtype': 'DINT'},
    'DB4_DBD512': {'db': 4, 'offset': 512, 'dtype': 'DINT'},
    'DB4_DBD516': {'db': 4, 'offset': 516, 'dtype': 'DINT'},
    'DB4_DBD520': {'db': 4, 'offset': 520, 'dtype': 'DINT'},
    'DB4_DBD524': {'db': 4, 'offset': 524, 'dtype': 'DINT'},
    'DB4_DBD528': {'db': 4, 'offset': 528, 'dtype': 'DINT'},
    'DB4_DBD532': {'db': 4, 'offset': 532, 'dtype': 'DINT'},
    'DB4_DBD536': {'db': 4, 'offset': 536, 'dtype': 'DINT'},
    'DB4_DBD540': {'db': 4, 'offset': 540, 'dtype': 'DINT'},
    'DB4_DBD544': {'db': 4, 'offset': 544, 'dtype': 'DINT'},
    'DB4_DBD548': {'db': 4, 'offset': 548, 'dtype': 'DINT'},
    'DB4_DBD552': {'db': 4, 'offset': 552, 'dtype': 'DINT'},
    'DB4_DBD556': {'db': 4, 'offset': 556, 'dtype': 'DINT'},
    'DB4_DBD560': {'db': 4, 'offset': 560, 'dtype': 'DINT'},
    'DB4_DBD564': {'db': 4, 'offset': 564, 'dtype': 'DINT'},
    'DB4_DBD568': {'db': 4, 'offset': 568, 'dtype': 'DINT'},
    'DB4_DBD572': {'db': 4, 'offset': 572, 'dtype': 'DINT'},
    'DB4_DBD576': {'db': 4, 'offset': 576, 'dtype': 'DINT'},
    'DB4_DBD580': {'db': 4, 'offset': 580, 'dtype': 'DINT'},
    'DB4_DBD584': {'db': 4, 'offset': 584, 'dtype': 'DINT'},
    'DB4_DBD588': {'db': 4, 'offset': 588, 'dtype': 'DINT'},
    'DB4_DBD592': {'db': 4, 'offset': 592, 'dtype': 'DINT'},
    'DB4_DBD596': {'db': 4, 'offset': 596, 'dtype': 'DINT'},
    'DB4_DBD600': {'db': 4, 'offset': 600, 'dtype': 'DINT'},
    'DB4_DBD604': {'db': 4, 'offset': 604, 'dtype': 'DINT'},
    'DB4_DBD608': {'db': 4, 'offset': 608, 'dtype': 'DINT'},
    'DB4_DBD612': {'db': 4, 'offset': 612, 'dtype': 'DINT'},
    'DB4_DBD616': {'db': 4, 'offset': 616, 'dtype': 'DINT'},
    'DB4_DBD620': {'db': 4, 'offset': 620, 'dtype': 'DINT'},
    'DB4_DBD624': {'db': 4, 'offset': 624, 'dtype': 'DINT'},
    'DB4_DBD628': {'db': 4, 'offset': 628, 'dtype': 'DINT'},
    'DB4_DBD632': {'db': 4, 'offset': 632, 'dtype': 'DINT'},
    'DB4_DBD636': {'db': 4, 'offset': 636, 'dtype': 'DINT'},
    'DB4_DBD640': {'db': 4, 'offset': 640, 'dtype': 'DINT'},
    'DB4_DBD644': {'db': 4, 'offset': 644, 'dtype': 'DINT'},
    'DB4_DBD648': {'db': 4, 'offset': 648, 'dtype': 'DINT'},
    'DB4_DBD652': {'db': 4, 'offset': 652, 'dtype': 'DINT'},
    'DB4_DBD656': {'db': 4, 'offset': 656, 'dtype': 'DINT'},
    'DB4_DBD660': {'db': 4, 'offset': 660, 'dtype': 'DINT'},
    'DB4_DBD664': {'db': 4, 'offset': 664, 'dtype': 'DINT'},
    'DB4_DBD668': {'db': 4, 'offset': 668, 'dtype': 'DINT'},
    'DB4_DBD672': {'db': 4, 'offset': 672, 'dtype': 'DINT'},
    'DB4_DBD676': {'db': 4, 'offset': 676, 'dtype': 'DINT'},
    'DB4_DBD680': {'db': 4, 'offset': 680, 'dtype': 'DINT'},
    'DB4_DBD684': {'db': 4, 'offset': 684, 'dtype': 'DINT'},
    'DB4_DBD688': {'db': 4, 'offset': 688, 'dtype': 'DINT'},
    'DB4_DBD692': {'db': 4, 'offset': 692, 'dtype': 'DINT'},
    'DB4_DBD696': {'db': 4, 'offset': 696, 'dtype': 'DINT'},
    'DB4_DBD700': {'db': 4, 'offset': 700, 'dtype': 'DINT'},
    'DB4_DBD704': {'db': 4, 'offset': 704, 'dtype': 'DINT'},
    'DB4_DBD708': {'db': 4, 'offset': 708, 'dtype': 'DINT'},
    'DB4_DBD712': {'db': 4, 'offset': 712, 'dtype': 'DINT'},
    'DB4_DBD716': {'db': 4, 'offset': 716, 'dtype': 'DINT'},
    'DB4_DBD720': {'db': 4, 'offset': 720, 'dtype': 'DINT'},
    'DB4_DBD724': {'db': 4, 'offset': 724, 'dtype': 'DINT'},
    'DB4_DBD728': {'db': 4, 'offset': 728, 'dtype': 'DINT'},
    'DB4_DBD732': {'db': 4, 'offset': 732, 'dtype': 'DINT'},
    'DB4_DBD736': {'db': 4, 'offset': 736, 'dtype': 'DINT'},
    'DB4_DBD740': {'db': 4, 'offset': 740, 'dtype': 'DINT'},
    'DB4_DBD744': {'db': 4, 'offset': 744, 'dtype': 'DINT'},
    'DB4_DBD748': {'db': 4, 'offset': 748, 'dtype': 'DINT'},
    'DB4_DBD752': {'db': 4, 'offset': 752, 'dtype': 'DINT'},
    'DB4_DBD756': {'db': 4, 'offset': 756, 'dtype': 'DINT'},
    'DB4_DBD760': {'db': 4, 'offset': 760, 'dtype': 'DINT'},
    'DB4_DBD764': {'db': 4, 'offset': 764, 'dtype': 'DINT'},
    'DB4_DBD768': {'db': 4, 'offset': 768, 'dtype': 'DINT'},
    'DB4_DBD772': {'db': 4, 'offset': 772, 'dtype': 'DINT'},
    'DB4_DBD776': {'db': 4, 'offset': 776, 'dtype': 'DINT'},
    'DB4_DBD780': {'db': 4, 'offset': 780, 'dtype': 'DINT'},
    'DB4_DBD784': {'db': 4, 'offset': 784, 'dtype': 'DINT'},
    'DB4_DBD788': {'db': 4, 'offset': 788, 'dtype': 'DINT'},
    'DB4_DBD792': {'db': 4, 'offset': 792, 'dtype': 'DINT'},
    'DB4_DBD796': {'db': 4, 'offset': 796, 'dtype': 'DINT'},
    'DB4_DBD800': {'db': 4, 'offset': 800, 'dtype': 'DINT'}, 

    'DB5_DBD0': {'db': 5, 'offset': 0, 'dtype': 'REAL'},
    'DB5_DBD4': {'db': 5, 'offset': 4, 'dtype': 'REAL'},
    'DB5_DBD8': {'db': 5, 'offset': 8, 'dtype': 'REAL'},
    'DB5_DBD12': {'db': 5, 'offset': 12, 'dtype': 'REAL'},
    'DB5_DBD16': {'db': 5, 'offset': 16, 'dtype': 'REAL'},
    'DB5_DBD20': {'db': 5, 'offset': 20, 'dtype': 'REAL'},
    'DB5_DBD24': {'db': 5, 'offset': 24, 'dtype': 'REAL'},
    'DB5_DBD28': {'db': 5, 'offset': 28, 'dtype': 'REAL'},
    'DB5_DBD32': {'db': 5, 'offset': 32, 'dtype': 'REAL'},
    'DB5_DBD36': {'db': 5, 'offset': 36, 'dtype': 'REAL'},
    'DB5_DBD40': {'db': 5, 'offset': 40, 'dtype': 'REAL'},
    'DB5_DBD44': {'db': 5, 'offset': 44, 'dtype': 'REAL'},
    'DB5_DBD48': {'db': 5, 'offset': 48, 'dtype': 'REAL'},
    'DB5_DBD52': {'db': 5, 'offset': 52, 'dtype': 'REAL'},
    'DB5_DBD56': {'db': 5, 'offset': 56, 'dtype': 'REAL'},
    'DB5_DBD60': {'db': 5, 'offset': 60, 'dtype': 'REAL'},
    'DB5_DBD64': {'db': 5, 'offset': 64, 'dtype': 'REAL'},
    'DB5_DBD68': {'db': 5, 'offset': 68, 'dtype': 'REAL'},
    'DB5_DBD72': {'db': 5, 'offset': 72, 'dtype': 'REAL'},
    'DB5_DBD76': {'db': 5, 'offset': 76, 'dtype': 'REAL'},
    'DB5_DBD80': {'db': 5, 'offset': 80, 'dtype': 'REAL'},
    'DB5_DBD84': {'db': 5, 'offset': 84, 'dtype': 'REAL'},
    'DB5_DBD88': {'db': 5, 'offset': 88, 'dtype': 'REAL'},
    'DB5_DBD92': {'db': 5, 'offset': 92, 'dtype': 'REAL'},
    'DB5_DBD96': {'db': 5, 'offset': 96, 'dtype': 'REAL'},
    'DB5_DBD100': {'db': 5, 'offset': 100, 'dtype': 'REAL'},
    'DB5_DBD104': {'db': 5, 'offset': 104, 'dtype': 'REAL'},
    'DB5_DBD108': {'db': 5, 'offset': 108, 'dtype': 'REAL'},
    'DB5_DBD112': {'db': 5, 'offset': 112, 'dtype': 'REAL'},
    'DB5_DBD116': {'db': 5, 'offset': 116, 'dtype': 'REAL'},
    'DB5_DBD120': {'db': 5, 'offset': 120, 'dtype': 'REAL'},
    'DB5_DBD124': {'db': 5, 'offset': 124, 'dtype': 'REAL'},
    'DB5_DBD128': {'db': 5, 'offset': 128, 'dtype': 'REAL'},
    'DB5_DBD132': {'db': 5, 'offset': 132, 'dtype': 'REAL'},
    'DB5_DBD136': {'db': 5, 'offset': 136, 'dtype': 'REAL'},
    'DB5_DBD140': {'db': 5, 'offset': 140, 'dtype': 'REAL'},
    'DB5_DBD144': {'db': 5, 'offset': 144, 'dtype': 'REAL'},
    'DB5_DBD148': {'db': 5, 'offset': 148, 'dtype': 'REAL'},
    'DB5_DBD152': {'db': 5, 'offset': 152, 'dtype': 'REAL'},
    'DB5_DBD156': {'db': 5, 'offset': 156, 'dtype': 'REAL'},
    'DB5_DBD160': {'db': 5, 'offset': 160, 'dtype': 'REAL'},
    'DB5_DBD164': {'db': 5, 'offset': 164, 'dtype': 'REAL'},
    'DB5_DBD168': {'db': 5, 'offset': 168, 'dtype': 'REAL'},
    'DB5_DBD172': {'db': 5, 'offset': 172, 'dtype': 'REAL'},
    'DB5_DBD176': {'db': 5, 'offset': 176, 'dtype': 'REAL'},
    'DB5_DBD180': {'db': 5, 'offset': 180, 'dtype': 'REAL'},
    'DB5_DBD184': {'db': 5, 'offset': 184, 'dtype': 'REAL'},
    'DB5_DBD188': {'db': 5, 'offset': 188, 'dtype': 'REAL'},
    'DB5_DBD192': {'db': 5, 'offset': 192, 'dtype': 'REAL'},
    'DB5_DBD196': {'db': 5, 'offset': 196, 'dtype': 'REAL'},
    'DB5_DBD200': {'db': 5, 'offset': 200, 'dtype': 'REAL'},
    'DB5_DBD204': {'db': 5, 'offset': 204, 'dtype': 'REAL'},
    'DB5_DBD208': {'db': 5, 'offset': 208, 'dtype': 'REAL'},
    'DB5_DBD212': {'db': 5, 'offset': 212, 'dtype': 'REAL'},
    'DB5_DBD216': {'db': 5, 'offset': 216, 'dtype': 'REAL'},
    'DB5_DBD220': {'db': 5, 'offset': 220, 'dtype': 'REAL'},
    'DB5_DBD224': {'db': 5, 'offset': 224, 'dtype': 'REAL'},
    'DB5_DBD228': {'db': 5, 'offset': 228, 'dtype': 'REAL'},
    'DB5_DBD232': {'db': 5, 'offset': 232, 'dtype': 'REAL'},
    'DB5_DBD236': {'db': 5, 'offset': 236, 'dtype': 'REAL'},
    'DB5_DBD240': {'db': 5, 'offset': 240, 'dtype': 'REAL'},
    'DB5_DBD244': {'db': 5, 'offset': 244, 'dtype': 'REAL'},
    'DB5_DBD248': {'db': 5, 'offset': 248, 'dtype': 'REAL'},
    'DB5_DBD252': {'db': 5, 'offset': 252, 'dtype': 'REAL'},
    'DB5_DBD256': {'db': 5, 'offset': 256, 'dtype': 'REAL'},
    'DB5_DBD260': {'db': 5, 'offset': 260, 'dtype': 'REAL'},
    'DB5_DBD264': {'db': 5, 'offset': 264, 'dtype': 'REAL'},
    'DB5_DBD268': {'db': 5, 'offset': 268, 'dtype': 'REAL'},
    'DB5_DBD272': {'db': 5, 'offset': 272, 'dtype': 'REAL'},
    'DB5_DBD276': {'db': 5, 'offset': 276, 'dtype': 'REAL'},
    'DB5_DBD280': {'db': 5, 'offset': 280, 'dtype': 'REAL'},
    'DB5_DBD284': {'db': 5, 'offset': 284, 'dtype': 'REAL'},
    'DB5_DBD288': {'db': 5, 'offset': 288, 'dtype': 'REAL'},
    'DB5_DBD292': {'db': 5, 'offset': 292, 'dtype': 'REAL'},
    'DB5_DBD296': {'db': 5, 'offset': 296, 'dtype': 'REAL'},
    'DB5_DBD300': {'db': 5, 'offset': 300, 'dtype': 'REAL'},
    'DB5_DBD304': {'db': 5, 'offset': 304, 'dtype': 'REAL'},
    'DB5_DBD308': {'db': 5, 'offset': 308, 'dtype': 'REAL'},
    'DB5_DBD312': {'db': 5, 'offset': 312, 'dtype': 'REAL'},
    'DB5_DBD316': {'db': 5, 'offset': 316, 'dtype': 'REAL'},
    'DB5_DBD320': {'db': 5, 'offset': 320, 'dtype': 'REAL'},
    'DB5_DBD324': {'db': 5, 'offset': 324, 'dtype': 'REAL'},
    'DB5_DBD328': {'db': 5, 'offset': 328, 'dtype': 'REAL'},
    'DB5_DBD332': {'db': 5, 'offset': 332, 'dtype': 'REAL'},
    'DB5_DBD336': {'db': 5, 'offset': 336, 'dtype': 'REAL'},
    'DB5_DBD340': {'db': 5, 'offset': 340, 'dtype': 'REAL'},
    'DB5_DBD344': {'db': 5, 'offset': 344, 'dtype': 'REAL'},
    'DB5_DBD348': {'db': 5, 'offset': 348, 'dtype': 'REAL'},
    'DB5_DBD352': {'db': 5, 'offset': 352, 'dtype': 'REAL'},
    'DB5_DBD356': {'db': 5, 'offset': 356, 'dtype': 'REAL'},
    'DB5_DBD360': {'db': 5, 'offset': 360, 'dtype': 'REAL'},
    'DB5_DBD364': {'db': 5, 'offset': 364, 'dtype': 'REAL'},
    'DB5_DBD368': {'db': 5, 'offset': 368, 'dtype': 'REAL'},
    'DB5_DBD372': {'db': 5, 'offset': 372, 'dtype': 'REAL'},
    'DB5_DBD376': {'db': 5, 'offset': 376, 'dtype': 'REAL'},
    'DB5_DBD380': {'db': 5, 'offset': 380, 'dtype': 'REAL'},
    'DB5_DBD384': {'db': 5, 'offset': 384, 'dtype': 'REAL'},
    'DB5_DBD388': {'db': 5, 'offset': 388, 'dtype': 'REAL'},
    'DB5_DBD392': {'db': 5, 'offset': 392, 'dtype': 'REAL'},
    'DB5_DBD396': {'db': 5, 'offset': 396, 'dtype': 'REAL'},
    'DB5_DBD400': {'db': 5, 'offset': 400, 'dtype': 'REAL'},
    'DB5_DBD404': {'db': 5, 'offset': 404, 'dtype': 'REAL'},
    'DB5_DBD408': {'db': 5, 'offset': 408, 'dtype': 'REAL'},
    'DB5_DBD412': {'db': 5, 'offset': 412, 'dtype': 'REAL'},
    'DB5_DBD416': {'db': 5, 'offset': 416, 'dtype': 'REAL'},
    'DB5_DBD420': {'db': 5, 'offset': 420, 'dtype': 'REAL'},
    'DB5_DBD424': {'db': 5, 'offset': 424, 'dtype': 'REAL'},
    'DB5_DBD428': {'db': 5, 'offset': 428, 'dtype': 'REAL'},
    'DB5_DBD432': {'db': 5, 'offset': 432, 'dtype': 'REAL'},
    'DB5_DBD436': {'db': 5, 'offset': 436, 'dtype': 'REAL'},
    'DB5_DBD440': {'db': 5, 'offset': 440, 'dtype': 'REAL'},
    'DB5_DBD444': {'db': 5, 'offset': 444, 'dtype': 'REAL'},
    'DB5_DBD448': {'db': 5, 'offset': 448, 'dtype': 'REAL'},
    'DB5_DBD452': {'db': 5, 'offset': 452, 'dtype': 'REAL'},
    'DB5_DBD456': {'db': 5, 'offset': 456, 'dtype': 'REAL'},
    'DB5_DBD460': {'db': 5, 'offset': 460, 'dtype': 'REAL'},
    'DB5_DBD464': {'db': 5, 'offset': 464, 'dtype': 'REAL'},
    'DB5_DBD468': {'db': 5, 'offset': 468, 'dtype': 'REAL'},
    'DB5_DBD472': {'db': 5, 'offset': 472, 'dtype': 'REAL'},
    'DB5_DBD476': {'db': 5, 'offset': 476, 'dtype': 'REAL'},
    'DB5_DBD480': {'db': 5, 'offset': 480, 'dtype': 'REAL'},
    'DB5_DBD484': {'db': 5, 'offset': 484, 'dtype': 'REAL'},
    'DB5_DBD488': {'db': 5, 'offset': 488, 'dtype': 'REAL'},
    'DB5_DBD492': {'db': 5, 'offset': 492, 'dtype': 'REAL'},
    'DB5_DBD496': {'db': 5, 'offset': 496, 'dtype': 'REAL'},
    'DB5_DBD500': {'db': 5, 'offset': 500, 'dtype': 'REAL'},
    'DB5_DBD504': {'db': 5, 'offset': 504, 'dtype': 'REAL'},
    'DB5_DBD508': {'db': 5, 'offset': 508, 'dtype': 'REAL'},
    'DB5_DBD512': {'db': 5, 'offset': 512, 'dtype': 'REAL'},
    'DB5_DBD516': {'db': 5, 'offset': 516, 'dtype': 'REAL'},
    'DB5_DBD520': {'db': 5, 'offset': 520, 'dtype': 'REAL'},
    'DB5_DBD524': {'db': 5, 'offset': 524, 'dtype': 'REAL'},
    'DB5_DBD528': {'db': 5, 'offset': 528, 'dtype': 'REAL'},
    'DB5_DBD532': {'db': 5, 'offset': 532, 'dtype': 'REAL'},
    'DB5_DBD536': {'db': 5, 'offset': 536, 'dtype': 'REAL'},
    'DB5_DBD540': {'db': 5, 'offset': 540, 'dtype': 'REAL'},
    'DB5_DBD544': {'db': 5, 'offset': 544, 'dtype': 'REAL'},
    'DB5_DBD548': {'db': 5, 'offset': 548, 'dtype': 'REAL'},
    'DB5_DBD552': {'db': 5, 'offset': 552, 'dtype': 'REAL'},
    'DB5_DBD556': {'db': 5, 'offset': 556, 'dtype': 'REAL'},
    'DB5_DBD560': {'db': 5, 'offset': 560, 'dtype': 'REAL'},
    'DB5_DBD564': {'db': 5, 'offset': 564, 'dtype': 'REAL'},
    'DB5_DBD568': {'db': 5, 'offset': 568, 'dtype': 'REAL'},
    'DB5_DBD572': {'db': 5, 'offset': 572, 'dtype': 'REAL'},
    'DB5_DBD576': {'db': 5, 'offset': 576, 'dtype': 'REAL'},
    'DB5_DBD580': {'db': 5, 'offset': 580, 'dtype': 'REAL'},
    'DB5_DBD584': {'db': 5, 'offset': 584, 'dtype': 'REAL'},
    'DB5_DBD588': {'db': 5, 'offset': 588, 'dtype': 'REAL'},
    'DB5_DBD592': {'db': 5, 'offset': 592, 'dtype': 'REAL'},
    'DB5_DBD596': {'db': 5, 'offset': 596, 'dtype': 'REAL'},
    'DB5_DBD600': {'db': 5, 'offset': 600, 'dtype': 'REAL'},
    'DB5_DBD604': {'db': 5, 'offset': 604, 'dtype': 'REAL'},
    'DB5_DBD608': {'db': 5, 'offset': 608, 'dtype': 'REAL'},
    'DB5_DBD612': {'db': 5, 'offset': 612, 'dtype': 'REAL'},
    'DB5_DBD616': {'db': 5, 'offset': 616, 'dtype': 'REAL'},
    'DB5_DBD620': {'db': 5, 'offset': 620, 'dtype': 'REAL'},
    'DB5_DBD624': {'db': 5, 'offset': 624, 'dtype': 'REAL'},
    'DB5_DBD628': {'db': 5, 'offset': 628, 'dtype': 'REAL'},
    'DB5_DBD632': {'db': 5, 'offset': 632, 'dtype': 'REAL'},
    'DB5_DBD636': {'db': 5, 'offset': 636, 'dtype': 'REAL'},
    'DB5_DBD640': {'db': 5, 'offset': 640, 'dtype': 'REAL'},
    'DB5_DBD644': {'db': 5, 'offset': 644, 'dtype': 'REAL'},
    'DB5_DBD648': {'db': 5, 'offset': 648, 'dtype': 'REAL'},
    'DB5_DBD652': {'db': 5, 'offset': 652, 'dtype': 'REAL'},
    'DB5_DBD656': {'db': 5, 'offset': 656, 'dtype': 'REAL'},
    'DB5_DBD660': {'db': 5, 'offset': 660, 'dtype': 'REAL'},
    'DB5_DBD664': {'db': 5, 'offset': 664, 'dtype': 'REAL'},
    'DB5_DBD668': {'db': 5, 'offset': 668, 'dtype': 'REAL'},
    'DB5_DBD672': {'db': 5, 'offset': 672, 'dtype': 'REAL'},
    'DB5_DBD676': {'db': 5, 'offset': 676, 'dtype': 'REAL'},
    'DB5_DBD680': {'db': 5, 'offset': 680, 'dtype': 'REAL'},
    'DB5_DBD684': {'db': 5, 'offset': 684, 'dtype': 'REAL'},
    'DB5_DBD688': {'db': 5, 'offset': 688, 'dtype': 'REAL'},
    'DB5_DBD692': {'db': 5, 'offset': 692, 'dtype': 'REAL'},
    'DB5_DBD696': {'db': 5, 'offset': 696, 'dtype': 'REAL'},
    'DB5_DBD700': {'db': 5, 'offset': 700, 'dtype': 'REAL'},
    'DB5_DBD704': {'db': 5, 'offset': 704, 'dtype': 'REAL'},
    'DB5_DBD708': {'db': 5, 'offset': 708, 'dtype': 'REAL'},
    'DB5_DBD712': {'db': 5, 'offset': 712, 'dtype': 'REAL'},
    'DB5_DBD716': {'db': 5, 'offset': 716, 'dtype': 'REAL'},
    'DB5_DBD720': {'db': 5, 'offset': 720, 'dtype': 'REAL'},
    'DB5_DBD724': {'db': 5, 'offset': 724, 'dtype': 'REAL'},
    'DB5_DBD728': {'db': 5, 'offset': 728, 'dtype': 'REAL'},
    'DB5_DBD732': {'db': 5, 'offset': 732, 'dtype': 'REAL'},
    'DB5_DBD736': {'db': 5, 'offset': 736, 'dtype': 'REAL'},
    'DB5_DBD740': {'db': 5, 'offset': 740, 'dtype': 'REAL'},
    'DB5_DBD744': {'db': 5, 'offset': 744, 'dtype': 'REAL'},
    'DB5_DBD748': {'db': 5, 'offset': 748, 'dtype': 'REAL'},
    'DB5_DBD752': {'db': 5, 'offset': 752, 'dtype': 'REAL'},
    'DB5_DBD756': {'db': 5, 'offset': 756, 'dtype': 'REAL'},
    'DB5_DBD760': {'db': 5, 'offset': 760, 'dtype': 'REAL'},
    'DB5_DBD764': {'db': 5, 'offset': 764, 'dtype': 'REAL'},
    'DB5_DBD768': {'db': 5, 'offset': 768, 'dtype': 'REAL'},
    'DB5_DBD772': {'db': 5, 'offset': 772, 'dtype': 'REAL'},
    'DB5_DBD776': {'db': 5, 'offset': 776, 'dtype': 'REAL'},
    'DB5_DBD780': {'db': 5, 'offset': 780, 'dtype': 'REAL'},
    'DB5_DBD784': {'db': 5, 'offset': 784, 'dtype': 'REAL'},
    'DB5_DBD788': {'db': 5, 'offset': 788, 'dtype': 'REAL'},
    'DB5_DBD792': {'db': 5, 'offset': 792, 'dtype': 'REAL'},
    'DB5_DBD796': {'db': 5, 'offset': 796, 'dtype': 'REAL'},
    'DB5_DBD800': {'db': 5, 'offset': 800, 'dtype': 'REAL'},

    
    'DB6_DBX0': {'db': 6, 'offset': 0, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX256': {'db': 6, 'offset': 256, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX512': {'db': 6, 'offset': 512, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX768': {'db': 6, 'offset': 768, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX1024': {'db': 6, 'offset': 1024, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX1280': {'db': 6, 'offset': 1280, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX1536': {'db': 6, 'offset': 1536, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX1792': {'db': 6, 'offset': 1792, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX2048': {'db': 6, 'offset': 2048, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX2304': {'db': 6, 'offset': 2304, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX2560': {'db': 6, 'offset': 2560, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX2816': {'db': 6, 'offset': 2816, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX3072': {'db': 6, 'offset': 3072, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX3328': {'db': 6, 'offset': 3328, 'dtype': 'STRING', 'max_length': 20},
    'DB6_DBX3584': {'db': 6, 'offset': 3584, 'dtype': 'STRING', 'max_length': 20} 
}

# -------------------------------
# Setup
# -------------------------------
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("S7-PLC")

plc_connection = None
connection_lock = Lock()
last_write_time = 0
read_cache = {}
last_cache_update = 0

# -------------------------------
# Optimized PLC Connection
# -------------------------------
def get_plc_connection(ip=PLC_IP, max_retries=3):
    global plc_connection
    with connection_lock:
        for attempt in range(max_retries):
            try:
                if plc_connection and plc_connection.get_connected():
                    return plc_connection
                
                if plc_connection:
                    try:
                        plc_connection.destroy()
                    except:
                        pass
                
                plc_connection = snap7.client.Client()
                # Optimize connection parameters
                plc_connection.set_connection_params(PLC_IP, PLC_RACK, PLC_SLOT)
                plc_connection.set_connection_type(3)  # PG connection (more stable)
                plc_connection.connect(PLC_IP, PLC_RACK, PLC_SLOT)
                logger.info(f"Connected to PLC (attempt {attempt+1})")
                return plc_connection
                
            except Exception as e:
                logger.warning(f"Connection attempt {attempt+1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
        return None

# -------------------------------
# Optimized Data Utilities
# -------------------------------
@lru_cache(maxsize=128)
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
    
def read_plc_value(plc, db, offset, dtype, max_length=None):
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
        logger.error(f"Read error: {str(e)}")
        return None    

# -------------------------------
# Optimized Batch Operations
# -------------------------------
def batch_read_plc(plc, tags):
    global read_cache, last_cache_update
    
    # Check cache first
    current_time = time.time()
    if current_time - last_cache_update < READ_CACHE_TTL:
        cached_results = {}
        for tag in tags:
            if tag in read_cache:
                cached_results[tag] = read_cache[tag]
        if len(cached_results) == len(tags):
            return cached_results
    
    results = {}
    grouped = defaultdict(list)
    
    # Group and filter tags
    for tag in tags:
        config = get_tag_config(tag)
        if config:
            grouped[config['db']].append((tag, config))
        else:
            results[tag] = None

    # Process each DB
    for db_num, tag_list in grouped.items():
        tag_list.sort(key=lambda x: x[1]['offset'])
        min_offset = tag_list[0][1]['offset']
        max_cfg = max(tag_list, key=lambda x: x[1]['offset'] + (x[1].get('max_length', 0) + 2 if x[1]['dtype'] == 'STRING' else 4))
        max_offset = max_cfg[1]['offset'] + (max_cfg[1].get('max_length', 0) + 2 if max_cfg[1]['dtype'] == 'STRING' else 4)
        
        try:
            # Read entire block once
            block = plc.db_read(db_num, min_offset, max_offset - min_offset)
            
            # Process all tags in this block
            for tag, cfg in tag_list:
                start = cfg['offset'] - min_offset
                try:
                    if cfg['dtype'] == 'REAL':
                        results[tag] = round(struct.unpack('>f', bytes(block[start:start+4]))[0], 2)
                    elif cfg['dtype'] == 'DINT':
                        results[tag] = int.from_bytes(block[start:start+4], byteorder='big', signed=True)
                    elif cfg['dtype'] == 'STRING':
                        length = block[start+1]
                        results[tag] = block[start+2:start+2+length].decode('ascii').strip('\x00')
                    else:
                        results[tag] = None
                except Exception:
                    results[tag] = None
                    
        except Exception:
            for tag, _ in tag_list:
                results[tag] = None
    
    # Update cache
    read_cache.update(results)
    last_cache_update = current_time
    return results

def batch_write_plc(plc, tag_value_pairs):
    global last_write_time
    
    results = {}
    grouped = defaultdict(list)
    value_mapping = {}  # Track values for response
    
    # Rate limiting
    current_time = time.time()
    elapsed = current_time - last_write_time
    if elapsed < MIN_WRITE_INTERVAL:
        time.sleep(MIN_WRITE_INTERVAL - elapsed)
    
    # Group and prepare writes
    for tag, value in tag_value_pairs:
        config = get_tag_config(tag)
        if not config:
            results[tag] = {"status": "Failed", "error": "Tag not found"}
            continue
            
        try:
            db, offset, data = prepare_plc_data(tag, value)
            grouped[db].append((offset, data, tag))
            value_mapping[tag] = value  # Store original value
        except Exception as e:
            results[tag] = {"status": "Failed", "error": str(e)}
    
    # Process writes by DB
    for db_num, write_list in grouped.items():
        write_list.sort(key=lambda x: x[0])
        combined_writes = []
        current_offset = None
        current_data = bytearray()
        current_tags = []
        
        # Combine adjacent writes
        for offset, data, tag in write_list:
            if current_offset is not None and offset == current_offset + len(current_data):
                current_data.extend(data)
                current_tags.append(tag)
            else:
                if current_offset is not None:
                    combined_writes.append((current_offset, bytes(current_data), current_tags))
                current_offset = offset
                current_data = bytearray(data)
                current_tags = [tag]
        
        if current_offset is not None:
            combined_writes.append((current_offset, bytes(current_data), current_tags))
        
        # Execute combined writes
        for offset, data, tags in combined_writes:
            try:
                plc.db_write(db_num, offset, data)
                for tag in tags:
                    results[tag] = {"status": "Success"}
            except Exception as e:
                for tag in tags:
                    results[tag] = {"status": "Failed", "error": str(e)}
    
    last_write_time = time.time()
    return results
# -------------------------------
# Optimized API Endpoints
# -------------------------------
@app.route('/readDataTagsFromPlc', methods=['GET'])
def read_tags():
    return jsonify({"tags": list(TAG_CONFIG.keys())}), 200

@app.route('/readDataFromPlcByTags', methods=['GET'])
def read_all_data():
    try:
        plc_ip = request.args.get('ip') or PLC_IP
        plc = get_plc_connection(plc_ip)
        if not plc:
            return jsonify({"message": "PLC connection failed"}), 500

        results = {}
        for tag_name, config in TAG_CONFIG.items():
            value = read_plc_value(plc, config['db'], config['offset'], config['dtype'], config.get('max_length'))
            results[tag_name] = {"value": value, "data_type": config['dtype']}

        plc.disconnect()
        return jsonify({"message": "Read successful", "data": results}), 200
    except Exception as e:
        return jsonify({"message": "Read failed", "error": str(e)}), 500

import re  # Add this import at the top

import re




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

        # Create a mapping of tags to their original values for the response
        value_mapping = {item['tag']: item['value'] 
                        for item in data_list 
                        if isinstance(item, dict) and 'tag' in item and 'value' in item}

        tag_value_pairs = list(value_mapping.items())

        with connection_lock:
            write_results = batch_write_plc(plc, tag_value_pairs)

        # Build enhanced response without additional PLC operations
        results = {}
        for tag, result in write_results.items():
            config = get_tag_config(tag)
            results[tag] = {
                "data_type": config['dtype'] if config else "UNKNOWN",
                "status": result["status"],
                "value_written": value_mapping.get(tag, None),
                "error": result.get("error")
            }

        logger.info(f"Write completed in {time.time()-start_time:.3f}s")
        return jsonify({
            "message": "Batch write completed",
            "execution_time": f"{time.time()-start_time:.3f}s",
            "data": results
        }), 200

    except Exception as e:
        logger.error(f"Write error: {str(e)}")
        return jsonify({
            "message": "Exception occurred",
            "error": str(e),
            "execution_time": f"{time.time()-start_time:.3f}s"
        }), 500
    
# @app.route('/getTagValuesByInterval', methods=['GET'])
# def get_tag_values_by_interval():
#     try:
#         interval = int(request.args.get('interval', 1))
#         tags_param = request.args.get('tags', '')
#         requested_tags = [tag.strip() for tag in tags_param.split(',') if tag.strip()]

#         if not requested_tags:
#             return jsonify({"message": "No tags specified"}), 400

#         def generate_dummy_data():
#             while True:
#                 results = {
#                     tag: round(random.uniform(0, 100), 2) for tag in requested_tags
#                 }

#                 # Proper SSE format with double newlines
#                 yield f"data: {json.dumps({
#                     'data': results,
#                     'timestamp': datetime.now().isoformat()
#                 })}\n\n"

#                 time.sleep(interval)


#         return Response(generate_dummy_data(), mimetype='text/event-stream')

#     except Exception as e:
#         return jsonify({
#             "message": "Initialization failed",
#             "error": str(e),
#             "error": True
#         }), 500


@app.route('/getTagValuesByInterval', methods=['GET'])
def get_tag_values_by_interval():
    try:
        plc_ip = request.args.get('ip', PLC_IP)
        interval = int(request.args.get('interval', 1))
        tags_param = request.args.get('tags', '')
        requested_tags = [tag.strip() for tag in tags_param.split(',') if tag.strip()]

        if not requested_tags:
            return jsonify({"message": "No tags specified"}), 400

        plc = get_plc_connection(plc_ip)
        if not plc:
            error_msg = f"Failed to connect to PLC at {plc_ip}. Check if PLC is reachable and credentials are correct."
            logger.error(error_msg)
            return jsonify({
                "message": "PLC connection failed",
                "details": error_msg
            }), 500

        def generate():
            try:
                while True:
                    start_time = time.time()
                    results = batch_read_plc(plc, requested_tags)
                    
                    if None in results.values():
                        error_msg = "One or more tags returned None. Check tag configurations."
                        yield f"data: {json.dumps({'message': error_msg, 'error': True})}\n\n"
                    else:
                        yield f"data: {json.dumps({
                            'data': results,
                            'timestamp': datetime.now().isoformat()
                        })}\n\n"

                    if interval > 0:
                        time.sleep(interval)
            except Exception as e:
                yield f"data: {json.dumps({
                    'message': 'SSE stream failed',
                    'error': str(e),
                    'error': True
                })}\n\n"
            finally:
                if plc:
                    plc.disconnect()

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}")
        return jsonify({
            "message": "Initialization failed",
            "error": str(e),
            "error": True
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

        results = batch_read_plc(plc, requested_tags)
        
        logger.info(f"Read completed in {time.time()-start_time:.3f}s")
        return jsonify({
            "data": results,
            "execution_time": f"{time.time()-start_time:.3f}s"
        }), 200
        
    except Exception as e:
        logger.error(f"Read error: {str(e)}")
        return jsonify({
            "message": "Read failed", 
            "error": str(e),
            "execution_time": f"{time.time()-start_time:.3f}s"
        }), 500    

    
    
# -------------------------------
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
            except:
                pass