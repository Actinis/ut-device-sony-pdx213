"""Wrap the generated Sony overlay in the qualified Android v0 DT table."""
import struct

def wrap(payload):
    if len(payload)<8 or struct.unpack_from('>I',payload)[0]!=0xd00dfeed:
        raise ValueError('Expected flattened device tree')
    if struct.unpack_from('>I',payload,4)[0]!=len(payload):
        raise ValueError('Truncated or extended FDT payload')
    header=struct.pack('>8I',0xd7b7ab1e,len(payload)+64,32,32,1,32,2048,0)
    entry=struct.pack('>8I',len(payload),64,0,0,0,0,0,0)
    return header+entry+payload
