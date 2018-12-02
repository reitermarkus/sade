use std::error::Error;
use std::ffi::OsStr;
use std::fs;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::Path;
use std::result::Result;

mod meta_info;
use meta_info::*;

#[macro_use]
extern crate serde_derive;
extern crate serde;
extern crate serde_json;

use serde_json::Value;

fn is_json(path: &Path) -> bool {
    let extension = path.extension().and_then(OsStr::to_str).unwrap();

    extension == "json"
}

fn read(path: &Path) -> Result<Value, Box<Error>> {
    let file = fs::File::open(path)?;
    let json = serde_json::from_reader(file)?;

    Result::Ok(json)
}


fn create_missing_data_file(group: &str, missing_data: &Vec<MissingTasks>) {
    let mut f = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(Path::new(&format!("../missing_tasks_{}.json", group)))
        .unwrap();

    let data = serde_json::to_string(&missing_data).unwrap();
    f.write(data.as_bytes()).unwrap();
}

fn find(
    path: &Path,
    group: &str,
    tasks: &Vec<String>,
    missing_data: &mut Vec<MissingTasks>,
) -> std::io::Result<()> {
    for entry in fs::read_dir(path)? {
        let path = &entry?.path();

        if is_json(path) {
            match read(path) {
                Ok(json) => {
                    let user = path
                        .file_stem()
                        .and_then(OsStr::to_str)
                        .unwrap()
                        .to_string();

                    check_tasks(user, group, &tasks, json, missing_data);
                }
                Err(_) => println!("{:?} can not be read", path),
            }
        }
    }

    Ok(())
}

fn check_tasks(
    user: String,
    group: &str,
    tasks: &Vec<String>,
    user_data: Value,
    missing_data: &mut Vec<MissingTasks>,
) {
    let mut missing = vec![];

    for i in tasks.iter() {
        let task: String = format!("{0}{1}", group, i.to_string());

        if user_data.get(&task) == None {
            missing.push(task);
        }
    }

    if missing.len() > 0 {
        missing_data.push(MissingTasks {
            user: user,
            missing: missing,
        });
    }
}

fn find_missing_tasks(path: &Path, group_name: &str, tasks: &Vec<String>) {
    let mut missing_tasks: Vec<MissingTasks> = Vec::new();

    find(path, group_name, &tasks, &mut missing_tasks).unwrap();

    create_missing_data_file(group_name, &missing_tasks);
}

fn main() {
    find_missing_tasks(
        Path::new("../data/Collected Data/group_a/"),
        "group_a",
        &meta_info::tasks_group_a(),
    );

    find_missing_tasks(
        Path::new("../data/Collected Data/group_b/"),
        "group_b",
        &meta_info::tasks_group_b(),
    );
}
