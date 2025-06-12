import snap7
import snap7.util
import snap7.types
from tag_config import TAG_CONFIG


def connect_to_plc(ip, rack=0, slot=1):
    plc = snap7.client.Client()
    plc.connect(ip, rack, slot)
    if not plc.get_connected():
        raise Exception("PLC connection failed")
    return plc


def write_to_plc(plc, tag_name, value):
    tag = TAG_CONFIG.get(tag_name)
    if not tag:
        raise ValueError("Tag '%s' not found in TAG_CONFIG" % tag_name)

    db = tag['db']
    offset = tag['offset']
    dtype = tag['dtype']

    if dtype == 'DINT':
        data = bytearray(4)
        snap7.util.set_dint(data, 0, int(value))
        plc.db_write(db, offset, data)

    elif dtype == 'REAL':
        data = bytearray(4)
        snap7.util.set_real(data, 0, float(value))
        plc.db_write(db, offset, data)

    elif dtype == 'STRING':
        length = tag.get('max_length', 254)
        data = bytearray(length + 2)
        snap7.util.set_string(data, 0, str(value), length)
        plc.db_write(db, offset, data)

    else:
        raise NotImplementedError("Write not supported for '%s'" % dtype)
