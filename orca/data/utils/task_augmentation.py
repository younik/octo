"""
Contains basic logic for randomly zero-ing out keys in the task specification.
"""

from typing import Any, Dict, List, Tuple

import tensorflow as tf


def drop_keys_independent(
    traj: Dict[str, Any],
    drop_keys_probs: Dict[str, float],
    drop_key_groups_probs: List[Tuple[List[str], float]],
) -> Dict[str, Any]:
    """
    Independently drop keys in the tasks dictionary.

    :param traj: A dictionary containing trajectory data. should have a "tasks" key.
    :param drop_keys_probs: A dictionary specifying the dropout probability for each key in tasks.
    :return: A dictionary with keys dropped out according to the specified probabilities.
    """

    # don't drop keys if there is no language instruction
    if tf.math.reduce_all(traj["tasks"]["language_instruction"] == ""):
        return traj

    tasks = traj["tasks"]
    new_tasks = tasks.copy()

    for key in drop_keys_probs:
        if key not in tasks:
            raise KeyError(
                f"{key} is not present in tasks dictionary. tasks keys: {tasks.keys()}"
            )

        new_tasks[key] = tf.where(
            tf.random.uniform([]) < drop_keys_probs[key],
            tf.zeros_like(tasks[key]) if tf.is_numeric_tensor(tasks[key]) else "",
            tasks[key],
        )

    for key_group, prob in drop_key_groups_probs:
        if not all(key in tasks for key in key_group):
            raise KeyError(
                f"keys {key_group} are not all present in tasks dictionary. tasks keys: {tasks.keys()}"
            )

        drop_group = tf.random.uniform([]) < prob
        for key in key_group:
            new_tasks[key] = tf.where(
                drop_group,
                tf.zeros_like(tasks[key]) if tf.is_numeric_tensor(tasks[key]) else "",
                tasks[key],
            )

    traj["tasks"] = new_tasks

    return traj
