import tkinter as tk
from tkinter import filedialog, messagebox
import os
from earningscall_generator import main  # 기존 main 함수 가져오기

class TranslatorApp:
    def __init__(self, master):
        self.master = master
        master.title("Earnings Call 번역 도구")
        master.geometry("500x250")

        self.presentation_path = None
        self.qna_path = None

        tk.Label(master, text="📊 Presentation 파일 선택:").pack(pady=5)
        tk.Button(master, text="Select Presentation File", command=self.select_presentation).pack()

        tk.Label(master, text="❓ Q&A 파일 선택:").pack(pady=5)
        tk.Button(master, text="Select Q&A File", command=self.select_qna).pack()

        self.run_button = tk.Button(master, text="🚀 번역 실행", state=tk.DISABLED, command=self.run_translation)
        self.run_button.pack(pady=20)

        self.status_label = tk.Label(master, text="파일을 선택하세요.", fg="blue")
        self.status_label.pack(pady=5)

    def select_presentation(self):
        self.presentation_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.update_status()

    def select_qna(self):
        self.qna_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.update_status()

    def update_status(self):
        if self.presentation_path and self.qna_path:
            self.run_button.config(state=tk.NORMAL)
            self.status_label.config(text="✅ 준비 완료! '번역 실행'을 누르세요.")
        else:
            self.status_label.config(text="📁 두 파일을 모두 선택해야 실행할 수 있습니다.")

    def run_translation(self):
        try:
            output_name = self.get_common_output_name()
            self.status_label.config(text=f"⏳ 처리 중... ({output_name})", fg="orange")
            self.master.update()

            # 번역 실행
            main(output_name)

            self.status_label.config(text=f"✅ 완료: {output_name}", fg="green")
            messagebox.showinfo("성공", f"{output_name} 번역 완료!")
        except Exception as e:
            self.status_label.config(text=f"❌ 오류: {str(e)}", fg="red")
            messagebox.showerror("에러 발생", str(e))

    def get_common_output_name(self):
        # 예: "ATZAF_3Q25_presentation.txt" → "ATZAF_3Q25"
        pres_file = os.path.basename(self.presentation_path)
        return pres_file.replace("_presentation.txt", "")

# 앱 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
