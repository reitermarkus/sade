use std::collections::HashMap;
use std::fs::{File, OpenOptions};
use std::io::{BufReader, Write};
use std::path::{Path, PathBuf};

#[macro_use]
extern crate serde_derive;
extern crate serde;
use serde::ser::Serialize;
extern crate serde_json;
use serde_json::Value;

extern crate glob;
use glob::glob;

extern crate rayon;
use rayon::prelude::*;

type Error = Box<std::error::Error + Send + Sync>;
type Result<T> = std::result::Result<T, Error>;

#[derive(Serialize, Deserialize, Debug)]
struct TaskInfo {
  name: String,
  delete_key_presses: usize,
  tab_key_presses: usize,
  space_key_presses: usize,
  characters_per_minute: f64
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ModifyStep {
  file: String,
  timestamp: usize
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(untagged)]
pub enum Task {
  Questionnaire(HashMap<String, Value>),
  Task(Vec<ModifyStep>)
}

fn count_characters_per_minute(steps: &[ModifyStep]) -> f64 {
  let mut iter = steps.iter().peekable();

  let mut time: u64 = 0;
  let mut characters: u64 = 0;

  while let Some(curr) = iter.next() {
    if let Some(&next) = iter.peek() {
      let (file_len_curr, file_len_next) = (&curr.file.len(), &next.file.len());

      if file_len_next > file_len_curr {
        let (ts_1, ts_2) = (&curr.timestamp, &next.timestamp);

        time += (ts_2 - ts_1) as u64;
        characters += (file_len_next - file_len_curr) as u64;
      }
    }
  }

  if time == 0 {
    return 0.0
  }

  characters as f64 / (time as f64 / 1000.0 / 60.0)
}

fn count_char(steps: &[ModifyStep], character: char) -> usize {
  steps.windows(2).map(|steps| {
    let (prev, curr) = (&steps[0].file, &steps[1].file);

    if curr.len() > prev.len() {
      let mut prev_char = prev.chars().last();
      let mut count = 0;

      for c in curr.chars().skip(prev.len()) {
        if c != character {
          continue
        }

        if c == ' ' {
          if prev_char == Some('\n') || prev_char == Some(' ') || prev_char == Some('\t') || prev_char == Some('\r') || prev_char.is_none() {
            count += 1;
          }

          prev_char = Some(c);
        } else {
          count += 1;
        }
      }

      count
    } else {
      0
    }
  }).sum()
}

fn count_del_keys(steps: &[ModifyStep]) -> usize {
  steps.windows(2).map(|steps| {
    let (prev, curr) = (&steps[0].file, &steps[1].file);

    if curr.len() < prev.len() {
      prev.len() - curr.len()
    } else {
      0
    }
  }).sum()
}

fn user_info_for_group(data_path: impl AsRef<Path>, group: &str) -> Result<Vec<PathBuf>> {
  let paths = glob(&format!("{}/group_{}/user_*.json", data_path.as_ref().to_str().unwrap(), group))?
                .filter_map(|path| path.ok())
                .collect();

  Ok(paths)
}

fn tasks_for_group(data_path: impl AsRef<Path>, group: &str) -> Result<Vec<String>> {
  let meta_path = data_path.as_ref().join(format!("group_{}", group)).join(format!("exp_group_{}.meta", group));

  let file = File::open(meta_path)?;
  let meta: HashMap<String, Value> = serde_json::from_reader(BufReader::new(file))?;

  Ok(meta.get("tasks")
      .and_then(|tasks| tasks.as_object())
      .map(|tasks| tasks.keys().map(|s| s.to_owned()).collect())
      .unwrap_or_default())
}

fn analyze_group(data_path: impl AsRef<Path>, group: &str) -> Result<Vec<TaskInfo>> {
  let tasks = tasks_for_group(&data_path, group)?;

  let user_infos = user_info_for_group(&data_path, group)?.par_iter().map(|user_info| {
    let file = File::open(user_info)?;
    Ok(serde_json::from_reader(BufReader::new(file))?)
  }).collect::<Result<Vec<HashMap<String, Task>>>>()?;

  Ok(tasks.par_iter().flat_map(|task| {
    user_infos.iter().filter_map(|user_info| {
      if let Some(Task::Task(steps)) = user_info.get(task) {
        Some(TaskInfo {
          name: task.to_owned(),
          delete_key_presses: count_del_keys(&steps),
          tab_key_presses: count_char(&steps, '\t'),
          space_key_presses:  count_char(&steps, ' '),
          characters_per_minute: count_characters_per_minute(&steps),
        })
      } else {
        None
      }
    }).collect::<Vec<_>>()
  }).collect())
}

fn write_json<T: ?Sized>(path: impl AsRef<Path>, data: &T) -> Result<()>
where T: Serialize
{
  let mut file = OpenOptions::new()
                   .write(true)
                   .create_new(!path.as_ref().exists())
                   .open(path)?;

  let data = serde_json::to_string_pretty(data)?;

  Ok(file.write_all(&data.as_bytes())?)
}

fn main() -> Result<()> {
  let data_path = "../data/Collected Data";

  vec!["a", "b"].par_iter().map(|group| {
    let analysis = analyze_group(data_path, group)?;
    write_json(format!("../analysis_group_{}.json", group), &analysis)?;
    Ok(())
  }).collect::<Result<Vec<_>>>()?;

  Ok(())
}
