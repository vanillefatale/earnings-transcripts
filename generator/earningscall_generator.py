import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
import os
#from translator_gpt import read_file, process_section
from translator_claude import read_file, process_section
from translator_qna_claude import process_qna_section
from renderer import render_html_document
from updater import update_index_html
from git_utils import git_commit_and_push

def main(output_name):
    #해당 아래 디렉토리에 저장하게 됩니다!
    quarter_dir = "2Q25"

    pres_filename = f"{output_name}_presentation.txt"
    qna_filename = f"{output_name}_qna.txt"

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", help="파일명 (예: DPZ_4Q24)")
    args = parser.parse_args()

    main(args.output)
