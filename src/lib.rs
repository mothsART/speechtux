#[macro_use] extern crate serde_derive;

pub mod cors;
pub mod ffi;

use std::ffi::CStr;

#[no_mangle]
pub extern "C" fn read(
    text: *const libc::c_char,
    speed: libc::size_t,
    level: libc::size_t,
    volume: libc::size_t
) {
    let speech = ffi::Speech::new();
    let text = unsafe {
    String::from_utf8_lossy(
            CStr::from_ptr(
                text
            ).to_bytes()
        ).to_string()
    };
    let mut new_level = Some(100);
    if (level >= 1 && level <= 200) {
        new_level = Some(level as i32);
    }
    let mut new_volume = Some(200);
    if (volume >= 1 && volume <= 200) {
        new_volume = Some(volume as i32);
    }
    let mut new_speed = Some(100);
    if (speed >= 1 && speed <= 300) {
        new_speed = Some(speed as i32);
    }
    let frame = ffi::Frame {
        text: text,
        level: new_level,
        volume: new_volume,
        speed: new_speed
    };
    speech.read(frame);
}
