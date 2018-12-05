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
pub struct ModifyStep {
  file: String,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(untagged)]
pub enum Task {
  Questionnaire(HashMap<String, Value>),
  Task(Vec<ModifyStep>)
}

fn count_char(steps: &[ModifyStep], character: char) -> usize {
  steps.windows(2).map(|steps| {
    let (prev, curr) = (&steps[0].file, &steps[1].file);

    if curr.len() > prev.len() {
      curr.chars().skip(prev.len()).filter(|c| *c == character).count()
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

fn analyze_group(data_path: impl AsRef<Path>, group: &str) -> Result<HashMap<String, (usize, usize, usize)>> {
  let tasks = tasks_for_group(&data_path, group)?;

  let user_infos = user_info_for_group(&data_path, group)?.par_iter().map(|user_info| {
    let file = File::open(user_info)?;
    Ok(serde_json::from_reader(BufReader::new(file))?)
  }).collect::<Result<Vec<HashMap<String, Task>>>>()?;

  Ok(tasks.par_iter().map(|task| {
    let (delete_key_presses, tabs_key_presses, space_presses) = user_infos.iter().map(|user_info| {
      if let Some(Task::Task(steps)) = user_info.get(task) {
        (count_del_keys(&steps), count_char(&steps, '\t'), count_char(&steps, ' '))
      } else {
        (0, 0, 0)
      }
    }).fold((0, 0, 0), |(acc_a, acc_b, acc_c), (a, b, c)| (acc_a + a, acc_b + b, acc_c + c));

    (task.to_owned(), (delete_key_presses, tabs_key_presses, space_presses))
  }).collect())
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

fn write_json<T: ?Sized>(path: impl AsRef<Path>, data: &T) -> Result<()>
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
