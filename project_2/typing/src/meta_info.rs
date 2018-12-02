#[derive(Serialize, Deserialize, Debug)]
pub struct MissingTasks {
  pub user: String,
  pub missing: Vec<String>,
}

pub fn tasks_group_a() -> Vec<String> {
  let tasks: Vec<String> = vec![
    "_task_0_demography".to_string(),
    "_task_1_internal_read".to_string(),
    "_task_2_1_internal_modify".to_string(),
    "_task_2_2_internal_modify".to_string(),
    "_task_2_3_internal_modify".to_string(),
    "_task_3_1_internal_create".to_string(),
    "_task_3_2_internal_create".to_string(),
    "_task_3_3_internal_create".to_string(),
    "_task_4_feedback".to_string(),
    "_task_5_external_read".to_string(),
    "_task_6_1_external_modify".to_string(),
    "_task_6_2_external_modify".to_string(),
    "_task_6_3_external_modify".to_string(),
    "_task_7_1_external_create".to_string(),
    "_task_7_2_external_create".to_string(),
    "_task_7_3_external_create".to_string(),
    "_task_8_feedback".to_string(),
    "_task_9_final".to_string(),
  ];

  return tasks;
}

pub fn tasks_group_b() -> Vec<String> {
  let tasks: Vec<String> = vec![
    "_task_0_demography".to_string(),
    "_task_1_external_read".to_string(),
    "_task_2_1_external_modify".to_string(),
    "_task_2_2_external_modify".to_string(),
    "_task_2_3_external_modify".to_string(),
    "_task_3_1_external_create".to_string(),
    "_task_3_2_external_create".to_string(),
    "_task_3_3_external_create".to_string(),
    "_task_4_feedback".to_string(),
    "_task_5_internal_read".to_string(),
    "_task_6_1_internal_modify".to_string(),
    "_task_6_2_internal_modify".to_string(),
    "_task_6_3_internal_modify".to_string(),
    "_task_7_1_internal_create".to_string(),
    "_task_7_2_internal_create".to_string(),
    "_task_7_3_internal_create".to_string(),
    "_task_8_feedback".to_string(),
    "_task_9_final".to_string(),
  ];

  return tasks;
}
