use std::error::Error;
use std::fs::{File, OpenOptions};
use std::io::{BufReader, Write};
use std::path::{Path, PathBuf};
use std::result::Result;
use std::collections::HashMap;

#[macro_use]
extern crate serde_derive;
extern crate serde;
extern crate serde_json;
use serde_json::Value;
use serde::ser::Serialize;

extern crate glob;
use glob::glob;

extern crate rayon;
use rayon::prelude::*;

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

#[derive(Serialize, Deserialize, Debug)]
pub struct ModifyErrorRangeInner {
  line: u64,
  character: u64,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ModifyErrorRange {
  start: ModifyErrorRangeInner,
  end: ModifyErrorRangeInner,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ModifyError {
  severity: u64,
  range: ModifyErrorRange,
  message: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ModifyStep {
  file: String,
  errors: Vec<ModifyError>,
  timestamp: u64,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(untagged)]
pub enum Task {
  Questionnaire(HashMap<String, Value>),
  Task(Vec<ModifyStep>)
}

fn count_del_keys(steps: &Vec<ModifyStep>) -> usize {
  let mut presses = 0;
  let mut prev_len = None;

  for step in steps {
    let curr_len = step.file.len();

    if let Some(prev_len) = prev_len {
      if curr_len < prev_len {
        presses += prev_len - curr_len;
      }
    }

    prev_len = Some(curr_len);
  }

  presses
}

fn user_info_for_group(data_path: impl AsRef<Path>, group: &str) -> Result<Vec<PathBuf>, Box<Error + Send + Sync>> {
  let paths = glob(&format!("{}/group_{}/user_*.json", data_path.as_ref().to_str().unwrap(), group))?
                .filter_map(|path| path.ok())
                .map(|path| PathBuf::from(path))
                .collect();

  Ok(paths)
}

fn tasks_for_group(data_path: impl AsRef<Path>, group: &str) -> Result<Vec<String>, Box<Error + Send + Sync>> {
  let meta_path = data_path.as_ref().join(format!("group_{}", group)).join(format!("exp_group_{}.meta", group));

  let file = File::open(meta_path)?;
  let meta: HashMap<String, Value> = serde_json::from_reader(BufReader::new(file))?;

  Ok(meta.get("tasks")
      .and_then(|tasks| tasks.as_object())
      .map(|tasks| tasks.keys().map(|s| s.to_owned()).collect())
      .unwrap_or(Vec::new()))
}

fn analyze_group(data_path: impl AsRef<Path>, group: &str) -> Result<HashMap<String, usize>, Box<Error + Send + Sync>> {
  let tasks = tasks_for_group(&data_path, group)?;

  let user_infos = user_info_for_group(&data_path, group)?.par_iter().map(|user_info| {
    let file = File::open(user_info)?;
    Ok(serde_json::from_reader(BufReader::new(file))?)
  }).collect::<Result<Vec<HashMap<String, Task>>, Box<Error + Send + Sync>>>().unwrap();

  Ok(tasks.par_iter().map(|task| {
    let delete_key_presses = user_infos.iter().map(|user_info| {
      if let Some(Task::Task(steps)) = user_info.get(task) {
        count_del_keys(&steps)
      } else {
        0
      }
    }).sum();

    (task.to_owned(), delete_key_presses)
  }).collect())
}

fn main() -> Result<(), Box<Error + Send + Sync>> {
  let data_path = "../data/Collected Data";

  vec!["a", "b"].par_iter().map(|group| {
    let analysis = analyze_group(data_path, group)?;
    write_json(format!("../analysis_group_{}.json", group), &analysis)?;
    Ok(())
  }).collect::<Result<Vec<_>, Box<Error + Send + Sync>>>()?;

  Ok(())
}

fn write_json<T: ?Sized>(path: impl AsRef<Path>, data: &T) -> Result<(), Box<Error + Send + Sync>>
where T: Serialize
{
  let mut file = OpenOptions::new()
                   .write(true)
                   .create_new(!path.as_ref().exists())
                   .open(path)?;

  let data = serde_json::to_string_pretty(data)?
               .as_bytes()
               .to_owned();

  file.write_all(&data)?;

  Ok(())
}
