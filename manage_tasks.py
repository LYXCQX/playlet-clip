# #!/usr/bin/python
# # -*- coding: UTF-8 -*-
# # @author:anning
# # @email:anningforchina@gmail.com
# # @time:2024/05/23 14:28
# # @file:manage_tasks.py
import sqlite3
import argparse

from utils import TaskStatus

DATABASE = "tasks.db"


def list_failed_tasks():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE status = ?", (TaskStatus.failed,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_task_status(task_ids, new_status):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if task_ids:
        cursor.executemany(
            "UPDATE tasks SET status = ? WHERE id = ?",
            [(new_status, task_id) for task_id in task_ids],
        )
    else:
        cursor.execute(
            "UPDATE tasks SET status = ? WHERE status = ?",
            (new_status, TaskStatus.failed),
        )

    conn.commit()
    conn.close()


def update_all_failed_to_pending():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = ? WHERE status = ?",
        (TaskStatus.pending, TaskStatus.failed),
    )
    conn.commit()
    conn.close()
    print("所有失败的任务都已更新为挂起。")


def delete_task(task_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        return False
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return True


def delete_all_failed_tasks():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE status = ?", (TaskStatus.failed,))
    conn.commit()
    conn.close()
    print("所有失败的任务都已删除。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage tasks in the database")
    parser.add_argument(
        "-l", "--list", action="store_true", help="List all failed tasks"
    )
    parser.add_argument(
        "-u",
        "--update",
        nargs="+",
        metavar=("NEW_STATUS", "TASK_ID"),
        help="更新任务状态（可选）针对特定任务 ID",
    )
    parser.add_argument("-d", "--delete", metavar="TASK_ID", help="Delete a task")
    parser.add_argument(
        "-r",
        "--reset-failed",
        action="store_true",
        help="将所有失败的任务重置为挂起",
    )
    parser.add_argument(
        "--delete-all-failed", action="store_true", help="Delete all failed tasks"
    )

    args = parser.parse_args()

    if args.list:
        failed_tasks = list_failed_tasks()
        if not failed_tasks:
            print("未发现失败的任务。")
        else:
            for task in failed_tasks:
                print(
                    f"ID: {task[0]}, Video Path: {task[1]}, Video Path: {task[2]}, SRT Path: {task[3]}, Blur Height: {task[4]}, Blur Y: {task[5]}, MarginV: {task[6]}, Status: {task[7]}"
                )

    if args.update:
        new_status = args.update[0]
        task_ids = (
            [int(task_id) for task_id in args.update[1:]]
            if len(args.update) > 1
            else None
        )

        if new_status not in (
            TaskStatus.pending,
            TaskStatus.in_progress,
            TaskStatus.completed,
            TaskStatus.failed,
        ):
            print(f"无效状态: {new_status}")
        else:
            update_task_status(task_ids, new_status)
            if task_ids:
                print(f"将任务 {task_ids} 更新为状态 {new_status}.")
            else:
                print(f"已将所有失败的任务更新为状态 {new_status}.")

    if args.delete:
        task_id = int(args.delete)
        success = delete_task(task_id)
        if success:
            print(f"任务 {task_id} 已删除.")
        else:
            print(f"未找到任务 {task_id}.")

    if args.reset_failed:
        update_all_failed_to_pending()

    if args.delete_all_failed:
        delete_all_failed_tasks()
