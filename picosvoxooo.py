#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import threading
import tempfile
import ctypes
import os
import sys
import subprocess
from urllib.request import pathname2url
from urllib.request import url2pathname
from urllib.parse import urlparse
from urllib.parse import unquote

SVOX_MEMORY_SIZE=3*1024**2
OUT_BUFFER_SIZE=4096
PICO_STEP_IDLE=200
PICO_STEP_BUSY=201


def read(bpath = None, data = None):
    dll=ctypes.cdll.LoadLibrary('libttspico.so.0.0.0')
    
    _svox_memory=ctypes.create_string_buffer(SVOX_MEMORY_SIZE)
    ps=ctypes.c_void_p()
    dll.pico_initialize(_svox_memory, SVOX_MEMORY_SIZE, ctypes.byref(ps))

    name = 'PicoVoice'
    langData = 'fr-FR_ta.bin'
    speakerData = 'fr-FR_nk0_sg.bin'
    
    langRes=ctypes.c_void_p()
    bLangRes=ctypes.byref(langRes)
    fpath = os.sep.join([bpath,'svox-pico-data',langData])
    fpath = fpath.encode('utf-8')
    print(dll.pico_loadResource(ps,fpath,bLangRes))
    
    
    langResName=ctypes.create_string_buffer(200)
    print("langResName", langResName)
    dll.pico_getResourceName(ps,langRes,langResName)
    print("langResName", langResName)
    
    speakerRes=ctypes.c_void_p()
    print(type(speakerRes))
    npath = os.sep.join([bpath,'svox-pico-data',speakerData])
    npath = npath.encode('utf-8')
    print(npath)
    dll.pico_loadResource(ps,npath,ctypes.byref(speakerRes))
    
    
    speakerResName=ctypes.create_string_buffer(200)
    dll.pico_getResourceName(ps,speakerRes,speakerResName)
    
    print(type(name))
    dll.pico_createVoiceDefinition(ps,name)
    print(name)
    dll.pico_addResourceToVoiceDefinition(ps,name,langResName)
    print(name)
    dll.pico_addResourceToVoiceDefinition(ps,name,speakerResName)
    print(name)
    
    pico_engine=ctypes.c_void_p()
    print(pico_engine)
    print(dll.pico_newEngine(ps,name,ctypes.byref(pico_engine)))
    print(pico_engine)

    bytes_sent=ctypes.c_int16()
    out_buffer=ctypes.create_string_buffer(OUT_BUFFER_SIZE)
    bytes_received=ctypes.c_int16()
    data_type=ctypes.c_int16()

    data = data.encode('utf-8')
    remaining=len(data)+1
    print(data)
    print(remaining)

    print(dll.pico_putTextUtf8(pico_engine,data,remaining,ctypes.byref(bytes_sent)))
    status = PICO_STEP_BUSY
    while status == PICO_STEP_BUSY:
        status=dll.pico_getData(pico_engine,out_buffer,OUT_BUFFER_SIZE,ctypes.byref(bytes_received),ctypes.byref(data_type))
    
    #dll.pico_resetEngine(pico_engine,0)
    #if pico_engine:
    #    dll.pico_disposeEngine(ps,ctypes.byref(pico_engine))
    #dll.pico_terminate(ctypes.byref(ps))
    #del dll

if __name__ == "__main__":
    txt = 'Bla bla !'
    __temp_wav_file__ = tempfile.mkstemp(suffix=".wav", prefix="svoxpico_")[1]
    url = urlparse(__file__)
    #base_path = os.path.dirname(os.path.abspath(url2pathname(url.path)))
    #base_path = unquote(base_path)
    #base_path = os.sep.join([base_path, 'pythonpath'])
    b_path = "/home/jferry/projects/speechtux/"
    data = '<genfile file="'+__temp_wav_file__+'">'+txt+'</genfile>'
    read(b_path, data)
    player = subprocess.Popen(["aplay", "-q", __temp_wav_file__])
