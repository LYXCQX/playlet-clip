#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2024/05/23 14:16
# @file:create_task.py
import os
import sqlite3
from pathlib import Path
import argparse
from enum import Enum

from conf import Config

DATABASE = "tasks.db"


class TaskStatus(str, Enum):
    pending = "待处理"
    in_progress = "处理中"
    completed = "已完成"
    failed = "异常"


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        style TEXT NOT NULL,
        video_path TEXT NOT NULL,
        srt_path TEXT NOT NULL,
        blur_height INTEGER NOT NULL,
        blur_y INTEGER NOT NULL,
        MarginV INTEGER NOT NULL,
        status TEXT NOT NULL
    )
    """
    )
    conn.commit()
    conn.close()


def get_task_files(directory, blur_height, blur_y, MarginV):
    tasks = []
    for root, _, files in os.walk(directory):
        mp4_files = {f.stem: f for f in Path(root).glob("*.mp4")}
        srt_files = {f.stem: f for f in Path(root).glob("*.srt")}
        common_stems = mp4_files.keys() & srt_files.keys()

        for stem in common_stems:
            for style in Config.style_list:
                tasks.append(
                    {
                        "style": style,
                        "video_path": str(mp4_files[stem]),
                        "srt_path": str(srt_files[stem]),
                        "blur_height": blur_height,
                        "blur_y": blur_y,
                        "MarginV": MarginV,
                        "status": TaskStatus.pending.value,
                    }
                )
    return tasks


def load_tasks_to_db(tasks):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    for task in tasks:
        cursor.execute(
            "SELECT * FROM tasks WHERE style = ? AND video_path = ?  AND srt_path = ?",
            (task["style"], task["video_path"], task["srt_path"]),
        )
        if cursor.fetchone() is None:
            cursor.execute(
                """
            INSERT INTO tasks (style, video_path, srt_path, blur_height, blur_y, MarginV, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task["style"],
                    task["video_path"],
                    task["srt_path"],
                    task["blur_height"],
                    task["blur_y"],
                    task["MarginV"],
                    task["status"],
                ),
            )
            conn.commit()

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="将任务从目录加载到数据库中"
    )
    parser.add_argument(
        "-d", "--directory", required=True, help="要扫描任务的目录"
    )
    parser.add_argument(
        "-e", "--blur_height", type=int, required=True, help="模糊区域的高度"
    )
    parser.add_argument(
        "-b", "--blur_y", type=int, required=True, help="模糊区域的 Y 位置"
    )
    parser.add_argument(
        "-m", "--MarginV", type=int, required=True, help="字幕的垂直边距"
    )

    args = parser.parse_args()

    init_db()
    tasks = get_task_files(args.directory, args.blur_height, args.blur_y, args.MarginV)
    load_tasks_to_db(tasks)
    print(f"任务已从目录加载到数据库中: {args.directory}")
