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

#[derive(Serialize, Deserialize, Debug)]
struct TaskInfo {
  name: String,
  del_key_pressed: usize,
}

#[derive(Serialize, Deserialize, Debug)]
struct DeleteKeyInfo {
  user: String,
  total_pressed: usize,
  task_infos: Vec<TaskInfo>,
}

// General Purpose
fn is_json(path: &Path) -> bool {
  if extract_file_stem(path).contains(".") {
    return false;
  }

  let extension = path.extension().and_then(OsStr::to_str).unwrap();

  extension == "json"
}
fn read(path: &Path) -> Result<Value, Box<Error>> {
  let file = fs::File::open(path)?;
  let json = serde_json::from_reader(file)?;

  Result::Ok(json)
}

fn extract_file_stem(path: &Path) -> String {
  path
    .file_stem()
    .and_then(OsStr::to_str)
    .unwrap()
    .to_owned()
    .to_string()
}

// Delete Key Analysis
fn delete_key_analysis(path: &Path, group: String) -> std::io::Result<()> {
  let mut del_key_infos: Vec<DeleteKeyInfo> = Vec::new();

  for entry in fs::read_dir(path)? {
    let path = &entry?.path();

    if is_json(path) {
      match read(path) {
        Ok(json) => {
          let ref user = extract_file_stem(path);

          del_key_infos.push(analyze_json(&user.to_string(), &json));

          println!("group_{}_{} analyzed", group, user);
        }
        Err(_) => println!("{:?} can not be read", path),
      }
    }
  }

  let p = &format!("../delete_key_analysis_{}.json", group);

  let mut file;

  if Path::new(p).exists() {
    file = OpenOptions::new().write(true).open(p).unwrap();
  } else {
    file = OpenOptions::new()
      .write(true)
      .create_new(true)
      .open(p)
      .unwrap();
  }

  let data = serde_json::to_string_pretty(&del_key_infos)
    .unwrap()
    .as_bytes()
    .to_owned();

  file.write_all(&data).unwrap();

  Ok(())
}

fn analyze_json(user: &String, user_data: &Value) -> DeleteKeyInfo {
  let mut del_info = DeleteKeyInfo {
    user: user.to_string(),
    total_pressed: 0,
    task_infos: vec![],
  };

  let mut task_info = TaskInfo {
    name: "".to_string(),
    del_key_pressed: 0,
  };

  match user_data.as_object() {
    None => panic!("user data is None"),
    Some(m) => {
      for i in m.keys() {
        let mut task: &str = i;

        task_info.name = i.to_string();

        if is_modify_task(&task.to_string()) {
          match count_delete_keys(&user_data, task) {
            Ok(res) => {
              task_info = res;
              del_info.total_pressed += task_info.del_key_pressed;
              del_info.task_infos.push(task_info);
            }
            Err(_) => (),
          }
        }
      }
    }
  }

  del_info
}

fn count_delete_keys(user_data: &Value, task: &str) -> Result<TaskInfo, ()> {
  let data = user_data.get(task).unwrap().as_array().unwrap();

  if data.len() == 0 {
    return Err(());
  };

  let mut previous_file: String = data[0]["file"].to_owned().to_string();

  let mut task_info = TaskInfo {
    name: task.to_string(),
    del_key_pressed: 0,
  };

  for i in 1..data.len() {
    let current_file = data[i]["file"].to_owned().to_string();

    if current_file.len() < previous_file.len() {
      task_info.del_key_pressed += previous_file.len() - current_file.len();
    }

    previous_file = data[i]["file"].to_owned().to_string();
  }

  Ok(task_info)
}

fn is_modify_task(task_name: &String) -> bool {
  task_name.ends_with("modify")
}

// Find Missing Tasks
fn create_missing_data_file(group: &str, missing_data: &Vec<MissingTasks>) {
  let p = &format!("../missing_tasks_{}.json", group);
  let mut file;

  if Path::new(p).exists() {
    file = OpenOptions::new().write(true).open(p).unwrap();
  } else {
    file = OpenOptions::new()
      .write(true)
      .create_new(true)
      .open(p)
      .unwrap();
  }

  let data = serde_json::to_string_pretty(&missing_data).unwrap();
  file.write_all(data.as_bytes()).unwrap();
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
          let ref user = extract_file_stem(path);

          check_tasks(&user.to_string(), group, &tasks, json, missing_data);
        }
        Err(_) => println!("{:?} can not be read", path),
      }
    }
  }

  Ok(())
}

fn check_tasks(
  user: &String,
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
      user: user.to_string(),
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
  let path_a = Path::new("../data/Collected Data/group_a/");
  let path_b = Path::new("../data/Collected Data/group_b/");

  delete_key_analysis(path_a, "a".to_string()).unwrap();
  delete_key_analysis(path_b, "b".to_string()).unwrap();

  find_missing_tasks(path_a, "a", &meta_info::tasks_group_a());
  find_missing_tasks(path_b, "b", &meta_info::tasks_group_b());
}
