#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import shutil
import platform
from typing import Union # Import Union from the typing module

def get_vscode_db_path() -> Union[str, None]: # Change str | None to Union[str, None]
    """
    根据操作系统确定 VSCode 数据库的路径。
    """
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            return os.path.expanduser("~/Library/Application Support/Code/User/globalStorage/state.vscdb")
        elif system == "Windows":
            appdata = os.getenv('APPDATA')
            if appdata:
                return os.path.join(appdata, "Code", "User", "globalStorage", "state.vscdb")
        elif system == "Linux":
            # 这是 VSCode 官方构建的常见路径
            return os.path.expanduser("~/.config/Code/User/globalStorage/state.vscdb")
    except Exception as e:
        print(f"获取数据库路径时出错: {e}")
    return None

def clean_vscode_db():
    """
    清理 VSCode 数据库中包含 'augment' 关键字的条目。
    """
    db_path = get_vscode_db_path()

    if not db_path:
        print("错误: 无法为当前操作系统确定 VSCode 数据库的路径。")
        print("请确认 VSCode 已安装，或手动修改脚本中的路径。")
        return

    if not os.path.exists(db_path):
        print(f"错误: 找不到数据库文件: {db_path}")
        print("请确认 VSCode 已安装或数据库文件位置正确。")
        return

    backup_path = f"{db_path}.{platform.system().lower()}.backup"

    conn = None
    try:
        print(f"正在备份数据库 {db_path} 到 {backup_path}...")
        shutil.copy2(db_path, backup_path)
        print(f"数据库已成功备份到: {backup_path}")

        print(f"连接到数据库: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        search_pattern_value = "augment"
        sql_like_pattern = f'%{search_pattern_value}%'

        cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE ?", (sql_like_pattern,))
        count = cursor.fetchone()[0]

        print(f"在 ItemTable 表中找到 {count} 条 'key' 包含 '{search_pattern_value}' 的记录。")

        if count > 0:
            print(f"准备删除 {count} 条记录...")
            cursor.execute("DELETE FROM ItemTable WHERE key LIKE ?", (sql_like_pattern,))
            conn.commit()

            rows_deleted = cursor.rowcount
            print(f"成功删除了 {rows_deleted} 条记录 (根据 cursor.rowcount)。")

            # 验证删除
            cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE ?", (sql_like_pattern,))
            remaining_count = cursor.fetchone()[0]
            print(f"删除操作后，ItemTable 表中剩余 {remaining_count} 条匹配记录。")

            if remaining_count == 0:
                print("所有匹配的记录已成功删除。")
            else:
                print(f"警告: 仍有 {remaining_count} 条匹配记录。请检查数据库。")
        else:
            print("未找到需要删除的记录。")

    except sqlite3.Error as e:
        print(f"数据库操作发生错误: {e}")
        if conn:
            try:
                conn.rollback()
                print("事务已回滚。")
            except sqlite3.Error as rb_e:
                print(f"回滚事务时发生错误: {rb_e}")
    except IOError as e:
        print(f"文件操作错误 (例如备份时): {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")
    finally:
        if conn:
            conn.close()
            print("数据库连接已关闭。")
        else:
            # 如果连接未成功建立，db_path 存在时会打印此信息
            if db_path and os.path.exists(db_path):
                print("数据库连接未能建立或已提前关闭。")

if __name__ == "__main__":
    clean_vscode_db()