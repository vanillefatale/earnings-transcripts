import subprocess

def git_commit_and_push(filename):
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Add translated file: {filename}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("[🚀] Git push 성공")
    except subprocess.CalledProcessError as e:
        print(f"[!] Git 실패: {e}")