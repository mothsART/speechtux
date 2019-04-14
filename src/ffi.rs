#![feature(rustc_private)]
extern crate libc;
extern crate tempfile;

use std::{env, str};
use std::ffi::{CString, c_void, CStr};
use std::process::Command;

use self::libc::{c_char, c_uchar, c_int, c_long, c_short, malloc};
use self::tempfile::Builder;

type FfiPicoSystem = c_long;
type FfiPicoResource = c_long;
type FfiPicoRetString = c_char;
type FfiPicoChar = c_uchar;
type FfiPicoPE = c_long;

const OUT_BUFFER_SIZE:i32 = 4096;
const PICO_STEP_BUSY:i16 = 201;

// the lib prefix and appropriate suffix is added automatically by the linker.
#[link(name = "ttspico")]
extern "C" {
    fn pico_initialize(
        mem: *mut c_void,
        mem_size: c_long,
        output: *mut FfiPicoSystem
    ) -> c_short;

    fn pico_loadResource(
        system: FfiPicoSystem,
        resourceFileName: *const FfiPicoChar,
        outResource: *mut FfiPicoResource
    ) -> c_short;

    fn pico_getResourceName(
        ps: FfiPicoSystem,
        pr: FfiPicoResource,
        langResName: *const FfiPicoChar
    ) -> c_short;

    fn pico_createVoiceDefinition(
        ps: FfiPicoSystem,
        name: *const FfiPicoChar
    ) -> c_short;

    fn pico_addResourceToVoiceDefinition(
        ps: FfiPicoSystem,
        name: *const FfiPicoChar,
        langResName: *const FfiPicoChar
    ) -> c_short;

    fn pico_newEngine(
        ps: FfiPicoSystem,
        name: *const FfiPicoChar,
        pe: *mut FfiPicoPE,
    ) -> c_short;
    
    fn pico_putTextUtf8(
        pe: FfiPicoPE,
        text: *const FfiPicoChar,
        remaining: c_short,
        outBytesPut: *const c_short
    ) -> c_short;

    fn pico_getData(
        pe: FfiPicoPE,
        outBuffer: *mut c_void,
        bufferSize: c_int,
        outBytesReceived: *mut c_int,
        outDataType: *mut c_int
    ) -> c_short;
    
    fn pico_getSystemStatusMessage(
        ps: FfiPicoSystem,
        ret: c_short,
        restring: *mut FfiPicoRetString
    ) -> c_short;
}

fn get_path(sub_dir: &str) -> Result<String, &'static str> {
    match env::current_dir() {
        Ok(mut dir) => {
            dir.push("svox-pico-data");
            dir.push(sub_dir);
            Ok(String::from(dir.to_str().unwrap()))
        },
        Err(_e) => Err("Did not exist")
    }
}

pub struct Speech {
    debug: bool,
    sound_path: String,
    ps: FfiPicoSystem,
    pe: FfiPicoPE,
    ret_string: FfiPicoRetString
}

#[derive(Deserialize)]
pub struct Frame {
    pub text: String,
    pub level: Option<i32>,
    pub volume: Option<i32>,
    pub speed: Option<i32>
}

impl Speech {
    pub fn new() -> Speech {
        let named_temp_file = Builder::new()
                            .prefix("svoxpico_")
                            .suffix(".wav")
                            .rand_bytes(5)
                            .tempfile().unwrap();
        let sound_path = named_temp_file.path().to_str().unwrap();
        Speech {
            debug: false,
            sound_path: sound_path.to_string(),
            ps: 0,
            pe: 0,
            ret_string: 0
        }
    }
    
    fn getStatus(&mut self, _status: i16) {
        if self.debug {
            unsafe {
                pico_getSystemStatusMessage(
                    self.ps,
                    _status,
                    &mut self.ret_string
                );
                println!(
                    "status : {} message: {:?}",
                    _status,
                    String::from_utf8_lossy(
                        CStr::from_ptr(
                            &self.ret_string
                        ).to_bytes()
                    ).to_string()
                );
            }
        }
    }

    fn init(&mut self) {
        const SVOX_MEMORY_SIZE:i32 = 3145728;
        let _status = unsafe {
            pico_initialize(
                malloc(SVOX_MEMORY_SIZE as usize),
                SVOX_MEMORY_SIZE,
                &mut self.ps
            )
        };
        self.getStatus(_status);
    }
    
    fn loadRessource(&mut self, path: &[u8], resource: &mut i32) {
        let _status = unsafe {
            pico_loadResource(self.ps, path.as_ptr(), resource)
        };
        self.getStatus(_status);
    }
    
    fn getRessource(&mut self, resource: i32, outName: &[u8]) {
        let _status = unsafe {
            pico_getResourceName(self.ps, resource, outName.as_ptr())
        };
        self.getStatus(_status);
    }

    fn createVoice(&mut self, name: &[u8]) {
        let _status = unsafe {
            pico_createVoiceDefinition(self.ps, name.as_ptr())
        };
        self.getStatus(_status);
    }

    fn addRessource(&mut self, name: &[u8], res: &[u8]) {
        let _status = unsafe {
            pico_addResourceToVoiceDefinition(
                self.ps,
                name.as_ptr(),
                res.as_ptr()
            )
        };
        self.getStatus(_status);
    }

    fn newEngine(&mut self, name: &[u8]) {
        let _status = unsafe {
            pico_newEngine(
                self.ps,
                name.as_ptr(),
                &mut self.pe
            )
        };
        self.getStatus(_status);
    }

    fn putText(&mut self, pitch: String) {
        let data   = CString::new(pitch).expect("CString::new failed");
        let data_c = data.as_bytes_with_nul();
        let data_len = (data_c.len() + 1) as i16;
        let bytes_sent_vec:Vec<i32> = vec![0; OUT_BUFFER_SIZE as usize];
        let bytes_sent = bytes_sent_vec.as_slice();
        let _status = unsafe {
            pico_putTextUtf8(
                self.pe,
                data_c.as_ptr(),
                data_len,
                bytes_sent.as_ptr() as *const i16
            )
        };
        self.getStatus(_status);
    }
    
    pub fn read(mut self, frame: Frame) {
        self.init();
        
        let mut pr: FfiPicoResource = 0;
        let f_string = CString::new(
            get_path("fr-FR_ta.bin").unwrap()
        ).expect("CString::new failed");
        let fpath = f_string.as_bytes_with_nul();
        self.loadRessource(fpath, &mut pr);

        let lang_res_name_vec:Vec<u8> = vec![0; 200];
        let lang_res_name = lang_res_name_vec.as_slice();
        self.getRessource(pr, lang_res_name);

        let mut sr: FfiPicoResource = 0;
        let b_string = CString::new(
            get_path("fr-FR_nk0_sg.bin").unwrap()
        ).expect("CString::new failed");
        let bpath = b_string.as_bytes_with_nul();
        self.loadRessource(bpath, &mut sr);
        
        let speaker_res_vec:Vec<u8> = vec![0; 200];
        let speaker_res = speaker_res_vec.as_slice();
        self.getRessource(sr, speaker_res);

        let c_string = CString::new("PicoVoice").expect("CString::new failed");
        let name = c_string.as_bytes_with_nul();
        self.createVoice(name);

        self.addRessource(name, lang_res_name);
        
        self.addRessource(name, speaker_res);
        
        self.newEngine(name);

        let gen_file = format!(
            "<genfile file={path:?}>{data}</genfile>",
            path= self.sound_path,
            data= frame.text
        );
        let mut volume = 100;
        match frame.volume {
            Some(x) => {
                volume = x;
            },
            None => {}
        }
        let volume_conf = format!(
            "<volume level=\"{volume:?}\">{gen_file}</volume>",
            volume= volume,
            gen_file= gen_file
        );
        let mut speed = 100;
        match frame.speed {
            Some(x) => {
                speed = x;
            },
            None => {}
        }
        let speed_conf = format!(
            "<speed level=\"{speed:?}\">{volume_conf}</speed>",
            speed= speed,
            volume_conf= volume_conf
        );
        let mut level = 100;
        match frame.level {
            Some(x) => {
                level = x;
            },
            None => {}
        }
        let pitch = format!(
            "<pitch level=\"{level:?}\">{speed_conf}</pitch>",
            level= level,
            speed_conf= speed_conf
        );
        self.putText(pitch);
        
        let out_buf = 4096 as usize;
        let mut bytes_received = 0;
        let mut data_type = 0;
        let mut status = PICO_STEP_BUSY;
        while status == PICO_STEP_BUSY {
            status = unsafe {
                pico_getData(
                    self.pe,
                    malloc(out_buf),
                    OUT_BUFFER_SIZE,
                    &mut bytes_received,
                    &mut data_type
                )
            };
        }

        Command::new("aplay")
                .arg("-q")
                .arg(self.sound_path)
                .output()
                .expect("failed to execute process");
    }
}

