import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
import os
import shutil
#from translator_gpt import read_file, process_section
from translator_claude import read_file, process_section
from translator_qna_claude import process_qna_section
from renderer import render_html_document
from updater import update_index_html
from git_utils import git_commit_and_push

# 🔽 GPT 요약 모듈 임포트
from summary_presentation_gpt import run_presentation_summary
from summary_qna_gpt import run_qna_summary


def main(output_name):
    #해당 아래 디렉토리에 저장하게 됩니다!
    quarter_dir = "3Q25"

    pres_filename = f"./0-ready/{output_name}_presentation.txt"
    qna_filename = f"./0-ready/{output_name}_qna.txt"

    pres_text = read_file(pres_filename)
    qna_text = read_file(qna_filename)

    output_dir = os.path.join("..", "docs", "translated", quarter_dir)

    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_name}_translated_output.html"
    output_path = os.path.join(output_dir, output_file)

    sections = []
    # QnA 파트 분리
    # for title, text in [("📊 Presentation", pres_text), ("❓ Q&A", qna_text)]:
    #     result = process_section(title, text)
    #     sections.append(result)
    # Presentation 파트는 기존 방식으로 처리
    print("[📊] Presentation 파트 처리 중...")
    pres_result = process_section("📊 Presentation", pres_text)
    sections.append(pres_result)
    
    # Q&A 파트는 화자별 구분 방식으로 처리
    print("[❓] Q&A 파트 처리 중...")
    qna_result = process_qna_section("❓ Q&A", qna_text)
    sections.append(qna_result)
    
    html = render_html_document(sections)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[✔] HTML 저장 완료: {output_path}")

    update_index_html(output_file, quarter_dir)
    git_commit_and_push(output_file)

    # 20251206-GPT 기반 Presentation 요약 + 텔레그램
    print("[🤖] GPT Presentation 요약 + 텔레그램 전송 시작...")
    run_presentation_summary(output_name)

    # 20251206-GPT 기반 Q&A 요약 + 텔레그램
    print("[🤖] GPT Q&A 요약 + 텔레그램 전송 시작...")
    run_qna_summary(output_name)
    
    # 0-ready -> 1-done 으로 원문 파일 이동
    for suffix in ["_presentation.txt", "_qna.txt"]:
        src = f"./0-ready/{output_name}{suffix}"
        dst = f"./1-done/{output_name}{suffix}"
        if os.path.exists(src):
            os.makedirs("./1-done", exist_ok=True)
            shutil.move(src, dst)
            print(f"[📂] {src} -> {dst}")

    print("[✅] 전체 파이프라인 완료!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", help="파일명 (예: DPZ_4Q24)")
    args = parser.parse_args()

    main(args.output)
