import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
import os
#from translator_gpt import read_file, process_section
from translator_claude import read_file, process_section
from renderer import render_html_document
from updater import update_index_html
from git_utils import git_commit_and_push

def main(output_name):
    #해당 아래 디렉토리에 저장하게 됩니다!
    quarter_dir = "1Q25"

    pres_filename = f"{output_name}_presentation.txt"
    qna_filename = f"{output_name}_qna.txt"

    pres_text = read_file(pres_filename)
    qna_text = read_file(qna_filename)

    output_dir = os.path.join("..", "docs", "translated", quarter_dir)

    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_name}_translated_output.html"
    output_path = os.path.join(output_dir, output_file)

    sections = []
    for title, text in [("📊 Presentation", pres_text), ("❓ Q&A", qna_text)]:
        result = process_section(title, text)
        sections.append(result)

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
