import argparse
import os
from translator import read_file, process_section
from renderer import render_html_document
from updater import update_index_html
from git_utils import git_commit_and_push

def main(pres_path, qna_path, output_name):
    pres_text = read_file(pres_path)
    qna_text = read_file(qna_path)

    output_dir = os.path.join("..", "docs", "translated", "4Q24")
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

    update_index_html(output_file)
    git_commit_and_push(output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("presentation", help="presentation.txt 파일")
    parser.add_argument("qna", help="qna.txt 파일")
    parser.add_argument("output", help="파일명 (예: DPZ_4Q24)")
    args = parser.parse_args()

    main(args.presentation, args.qna, args.output)
