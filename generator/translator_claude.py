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
        system="You are a professional financial translator. Translate the following earnings call transcript into natural, accurate Korean while preserving financial terminology and the speaker's tone. Ensure that the translation is fluent and professional, suitable for Korean-speaking investors. Only return the summary content itself, without any introductory phrases like 'summary' or 'for professional investors.'Use a neutral, concise tone suitable for Korean-speaking investors, but do not include headers or labels.",
        messages=[
            {"role": "user", "content": f"\n\n{text}"}
        ]
    )
    return resp.content[0].text.strip()

def summarize_text(text, model="claude-3-5-sonnet-20241022"):
    resp = client.messages.create(
        model=model,
        max_tokens=500,
        temperature=0.3,
        system="You are a financial analyst specializing in corporate earnings calls. Summarize the following transcript in 3–5 concise, clear, and unbiased bullet points. Focus on key financial metrics, guidance updates, tone of management, and any implied risks or strengths. The summary should be written in Korean and tailored for professional investors. Only return the summary content itself, without any introductory phrases like 'summary' or 'for professional investors.'Use a neutral, concise tone suitable for Korean-speaking investors, but do not include headers or labels.",
        messages=[
            {"role": "user", "content": f"Summarize the following transcript:\n\n{text}"}
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
