#![feature(proc_macro_hygiene, decl_macro)]

#[macro_use] extern crate rocket;
extern crate rocket_contrib;
extern crate uuid;
extern crate speechtux;

use rocket::http::{Cookie, Cookies, RawStr, Method};
use rocket_contrib::json::Json;
use uuid::Uuid;

use speechtux::cors::{CORS, PreflightCORS};
use speechtux::ffi::{Speech, Frame};

#[get("/signed/<app>")]
fn signed(mut cookies: Cookies, app: &RawStr) -> CORS<Json<bool>> {
    let my_uuid = Uuid::new_v4();
    cookies.add_private(Cookie::new(
        format!("speechtux-{}", app),
        my_uuid.to_string()
    ));
    CORS::any(Json(true))
}

#[options("/read")]
fn cors_preflight() -> PreflightCORS {
    CORS::preflight("*")
        .methods(vec![Method::Options, Method::Post])
        .headers(vec!["Content-Type"])
}

#[post("/read", format = "application/json", data = "<frame>")]
fn read(mut cookies: Cookies, frame: Json<Frame>) -> CORS<Json<bool>> {
    //let cookie = cookies.get_private("coucou");
    let speech = Speech::new();
    speech.read(frame.into_inner());
    CORS::any(Json(true))
}

fn main() {
    rocket::ignite().mount(
        "/",
        routes![signed, cors_preflight, read]
    ).launch();
}
