import subprocess
import os

def git_commit_and_push(filename):
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    try:
        subprocess.run(["git", "add", "."], check=True, cwd=parent_dir)
        subprocess.run(["git", "commit", "-m", f"Add translated file: {filename}"], check=True, cwd=parent_dir)
        subprocess.run(["git", "push"], check=True, cwd=parent_dir)
        print("[🚀] Git push 성공")
    except subprocess.CalledProcessError as e:
        print(f"[!] Git 실패: {e}")