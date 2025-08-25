import sublime
import sublime_plugin
import os
import time
import threading

REFRESH_INTERVAL = 3

watched_files = {}

def check_file_changes(view):
    file_path = view.file_name()

    print("Début du check pour", file_path)
    if not file_path:
        return

    while True:
        if not view.is_valid() or view.is_dirty():
            print("Fin du check pour", file_path)
            break
        try:
            current_mtime = os.path.getmtime(file_path)
        except (FileNotFoundError, OSError):
            break

        last_mtime = watched_files.get(file_path)
        if last_mtime is None:
            watched_files[file_path] = current_mtime
        elif current_mtime != last_mtime:
            print("Changement sur le fichier", file_path)
            watched_files[file_path] = current_mtime
            sublime.set_timeout(lambda: view.run_command("revert"), 0)
        time.sleep(REFRESH_INTERVAL)

class AutoRefreshListener(sublime_plugin.EventListener):
    def on_load(self, view):
        file_path = view.file_name()
        if not file_path:
            return

        try:
            watched_files[file_path] = os.path.getmtime(file_path)
        except (FileNotFoundError, OSError):
            return

        t = threading.Thread(target=check_file_changes, args=(view,), daemon=True)
        t.start()

    def on_close(self, view):
        file_path = view.file_name()
        if file_path in watched_files:
            watched_files.pop(file_path, None)
