import os
import re

def update_index_html(filename, quarter_dir):
    match = re.search(r'_(\dQ\d{2})', filename)
    if not match:
        print(f"[!] 파일명에서 분기 추출 실패: {filename}")
        return
    quarter = match.group(1)
    company = filename.split('_')[0]
    label = f"{company} {quarter}"
    link_path = f'translated/{quarter_dir}/{filename}'
    new_link = f'      <li><a href="{link_path}">{label}</a></li>'

    index_path = os.path.join("..", "docs", "index.html")
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if new_link.strip() in content:
        print(f"[i] 이미 index.html에 존재함: {label}")
        return

    pattern = rf'(<h2>{quarter_dir}</h2>\s*<ul>)(.*?)(</ul>)'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        before, items, after = match.group(1), match.group(2), match.group(3)
        new_items = items + "\n" + new_link
        updated_section = before + new_items + "\n" + after
        updated_content = content.replace(match.group(0), updated_section)
    else:
        new_section = f'\n    <h2>{quarter_dir}</h2>\n    <ul>\n{new_link}\n    </ul>\n'
        updated_content = content.replace("</div>", new_section + "  </div>")

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"[✔] index.html에 추가 완료: {label}")
