import anthropic, time, re
from tqdm import tqdm
import os
from dotenv import load_dotenv

# API 키 설정 (Claude)
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def smart_split(text, max_chunk_size=700):
    sentences = re.split(r'(?<=[.?!])\s+', text.strip())
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) < max_chunk_size:
            current += s + " "
        else:
            chunks.append(current.strip())
            current = s + " "
    if current: chunks.append(current.strip())
    return chunks

def translate_text(text, model="claude-3-5-sonnet-20241022"):
    resp = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0.3,
        system="너는 금융 전문 번역가야. 영어 텍스트를 자연스럽고 정확한 한국어로 번역해줘. 문맥과 어투를 잘 살려줘.",
        messages=[
            {"role": "user", "content": f"다음 텍스트를 한국어로 번역해줘:\n\n{text}"}
        ]
    )
    return resp.content[0].text.strip()

def summarize_text(text, model="claude-3-5-sonnet-20241022"):
    resp = client.messages.create(
        model=model,
        max_tokens=500,
        temperature=0.3,
        system="너는 금융 실적 발표 요약 전문가야. 다음 내용을 간결하고 명확하게 핵심만 요약해줘. 중립적인 어조로 3~5줄이면 충분해.",
        messages=[
            {"role": "user", "content": f"다음 내용을 요약해줘:\n\n{text}"}
        ]
    )
    return resp.content[0].text.strip()

def process_section(title, text):
    print(f"[📄] '{title}' 파트 번역 시작")
    chunks = smart_split(text)
    translations = []

    for chunk in tqdm(chunks, desc=title):
        translations.append(translate_text(chunk))
        time.sleep(0.5)

    summary = summarize_text(text)
    return (title, chunks, translations, summary)
