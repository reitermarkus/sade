use std::fs;
use std::path::Path;
use std::result::Result;
use std::ffi::OsStr;
use std::error::Error;

extern crate serde_json;

fn is_json(path: &Path) -> bool {
    let extension = path.extension().and_then(OsStr::to_str).unwrap();

    extension == "json" 
}

fn read<P: AsRef<Path>>(path: P) -> Result<serde_json::Value, Box<Error>> {
    let file = fs::File::open(path)?;
    let json = serde_json::from_reader(file)?;

    Result::Ok(json)
}

fn iterate_over_files(path: &Path) -> std::io::Result<()> {
    for entry in fs::read_dir(path)? {
        let path = &entry?.path();

        if is_json(path) {
            match read(path) {
                Ok(_) => println!("{:?} read successfully", path),
                Err(_) => println!("{:?} can not be read", path),
            }
        }
    }

    Ok(())
}

fn main() -> std::io::Result<()> {
    let group_a = &"../data/Collected Data/group_a/";

    iterate_over_files(Path::new(group_a))?;

    Ok(())
}
