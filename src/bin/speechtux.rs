#![feature(rustc_private)]
extern crate libc;
extern crate tempfile;

use  std::ptr;
use std::env;
use std::str;
use std::ffi;
use std::ffi::{CString, c_void};
use std::process::Command;


use libc::{c_char, c_uchar, c_int, c_long, c_short, malloc};
use tempfile::Builder;

type FfiPicoSystem = c_long;
type FfiPicoResource = c_long;
type FfiPicoRetString = c_char;
type FfiPicoChar = c_uchar;
type FfiPicoPE = c_long;

const SVOX_MEMORY_SIZE:i32 = 3145728;
const OUT_BUFFER_SIZE:i32  = 4096;
const PICO_STEP_BUSY:i16   = 201;

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
        pe: *mut FfiPicoPE,//*mut FfiPicoEngine
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

fn main() {
    let mut ps: FfiPicoSystem = 0;
    let mut pr: FfiPicoResource = 0;
    let mut sr: FfiPicoResource = 0;
    let mut pe: FfiPicoPE = 0;
    let out_buf = 4096 as usize;
    
    let named_temp_file = Builder::new()
                        .prefix("svoxpico_")
                        .suffix(".wav")
                        .rand_bytes(5)
                        .tempfile().unwrap();
    let wave_path = named_temp_file.path().to_str().unwrap();
    
    let value = "Trop bien !";
    let stream = format!(
        "<genfile file={path:?}>{data}</genfile>",
        path= wave_path,
        data= value
    );
    println!("{}", stream);
    let data   = CString::new(stream).expect("CString::new failed");
    let data_c = data.as_bytes_with_nul();
    let data_len = (data_c.len() + 1) as i16;
    println!("{:?}", data_len);
    
    let f_string = CString::new(get_path("fr-FR_ta.bin").unwrap()).expect("CString::new failed");
    let fpath = f_string.as_bytes_with_nul();
    
    let b_string = CString::new(get_path("fr-FR_nk0_sg.bin").unwrap()).expect("CString::new failed");
    let bpath = b_string.as_bytes_with_nul();

    let c_string = CString::new("PicoVoice").expect("CString::new failed");
    let name = c_string.as_bytes_with_nul();
    
    let lang_res_name_vec:Vec<u8> = vec![0; 200];
    let lang_res_name = lang_res_name_vec.as_slice();
    let speaker_res_vec:Vec<u8> = vec![0; 200];
    let speaker_res = speaker_res_vec.as_slice();
    
    let mut bytes_sent_vec:Vec<i32> = vec![0; OUT_BUFFER_SIZE as usize];
    let mut bytes_sent = bytes_sent_vec.as_slice();
    
    let mut bytes_received = 0;
    let mut data_type = 0;
    
    let mut ret_string: FfiPicoRetString = 0;
    
    let init = unsafe {
        pico_initialize(malloc(SVOX_MEMORY_SIZE as usize), SVOX_MEMORY_SIZE, &mut ps)
    };
    println!("{:?}", init);
    
    let load_one = unsafe {
        pico_loadResource(ps, fpath.as_ptr(), &mut pr)
    };
    println!("load_one {:?}", load_one);
    
    let get_one = unsafe {
        pico_getResourceName(ps, pr, lang_res_name.as_ptr())
    };
    println!("get_one {:?}", get_one);
    
    let load_two = unsafe {
        pico_loadResource(ps, bpath.as_ptr(), &mut sr)
    };
    println!("load_two {:?}", load_two); 

    let get_two = unsafe {
        pico_getResourceName(ps, sr, speaker_res.as_ptr())
    };
    println!("get_two {:?}", get_two);
    
    let create_voice = unsafe {
        pico_createVoiceDefinition(ps, name.as_ptr())
    };
    println!("create_voice {:?}", create_voice);
    
    let add_one = unsafe {
        pico_addResourceToVoiceDefinition(ps, name.as_ptr(), lang_res_name.as_ptr())
    };
    println!("add_one {:?}", add_one);
    
    let add_two = unsafe {
        pico_addResourceToVoiceDefinition(ps, name.as_ptr(), speaker_res.as_ptr())
    };
    println!("add_two {:?}", add_two);

    let n_e = unsafe {
        pico_newEngine(ps, name.as_ptr(), &mut pe)
    };
    println!("NewEngine {:?}", n_e);
    println!("{:?}", pe);
    

    let p_text = unsafe {
        let p_text = pico_putTextUtf8(
            pe,
            data_c.as_ptr(),
            data_len,
            bytes_sent.as_ptr() as *const i16
        );
        pico_getSystemStatusMessage(ps, p_text, &mut ret_string);
        println!("{:?}",  String::from_utf8_lossy(::std::ffi::CStr::from_ptr(&ret_string).to_bytes()).to_string());
        p_text
    };
    println!("p_text {:?}", p_text);
    
    let mut status = PICO_STEP_BUSY;
    while status == PICO_STEP_BUSY {
        status = unsafe {
            pico_getData(pe, malloc(out_buf), OUT_BUFFER_SIZE, &mut bytes_received, &mut data_type)
        };
    }
    
    println!("end");
    Command::new("aplay")
            .arg("-q")
            .arg(wave_path)
            .output()
            .expect("failed to execute process");
}
