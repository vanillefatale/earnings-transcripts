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

def parse_qna_speakers(text):
    """Q&A 텍스트에서 화자별로 구분하여 파싱"""
    patterns = [
        r'(Analyst|Question|Q):\s*(.+?)(?=(?:Analyst|Question|Q|Answer|A|Management|CEO|CFO|Executive):|$)',
        r'(Answer|A|Management|CEO|CFO|Executive|[A-Z][a-z]+ [A-Z][a-z]+):\s*(.+?)(?=(?:Analyst|Question|Q|Answer|A|Management|CEO|CFO|Executive):|$)',
        r'([A-Z][a-z]+ [A-Z][a-z]+):\s*(.+?)(?=(?:[A-Z][a-z]+ [A-Z][a-z]+):|$)'
    ]
    
    speakers = []
    lines = text.split('\n')
    current_speaker = None
    current_text = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 화자 패턴 매칭
        speaker_match = None
        for pattern in patterns:
            match = re.match(pattern, line, re.DOTALL | re.IGNORECASE)
            if match:
                speaker_match = match
                break
        
        if speaker_match:
            # 이전 화자 내용 저장
            if current_speaker and current_text.strip():
                speakers.append((current_speaker, current_text.strip()))
            
            # 새로운 화자 시작
            current_speaker = speaker_match.group(1)
            current_text = speaker_match.group(2) if len(speaker_match.groups()) > 1 else ""
        else:
            # 기존 화자 내용에 추가
            if current_text:
                current_text += " " + line
            else:
                current_text = line
    
    # 마지막 화자 내용 저장
    if current_speaker and current_text.strip():
        speakers.append((current_speaker, current_text.strip()))
    
    return speakers

def translate_qna_text(text, speaker_type, model="claude-sonnet-4-20250514"):
    """Q&A 전용 번역 함수"""
    
    if speaker_type == "question":
        system_prompt = """You are a professional financial translator specializing in earnings call Q&A sessions. Translate the following analyst question into natural, accurate Korean following these rules:

1. Speaker format: Use '**Name (Company):**' format exactly as provided in English
2. Professional tone: Use formal, professional Korean suitable for financial reports
3. Financial terminology: Use standard Korean financial terms, add English terms in parentheses for first occurrence of important terms
4. Numbers: Follow Korean number formatting conventions
5. Output in Korean only

Translate the analyst question maintaining the questioning tone and financial accuracy."""
        
    elif speaker_type == "answer":
        system_prompt = """You are a professional financial translator specializing in earnings call Q&A sessions. Translate the following management response into natural, accurate Korean following these rules:

1. Speaker format: Use '**Name:**' format exactly as provided in English
2. Professional tone: Use formal, professional Korean suitable for financial reports
3. Financial terminology: Use standard Korean financial terms, add English terms in parentheses for first occurrence of important terms
4. Numbers: Follow Korean number formatting conventions
5. Paragraph breaks: Use natural paragraph breaks for long responses
6. Preserve authoritative tone of executives
7. Output in Korean only

Translate the management response maintaining the authoritative tone and financial accuracy."""
        
    else:
        # 기본 Q&A 번역
        system_prompt = """You are a professional financial translator specializing in earnings call Q&A sessions. Translate the following Q&A content into natural, accurate Korean following these rules:

1. Speaker format: Use '**Name (Company):**' or '**Name:**' format exactly as provided in English
2. Professional tone: Use formal, professional Korean suitable for financial reports  
3. Financial terminology: Use standard Korean financial terms, add English terms in parentheses for first occurrence
4. Numbers: Follow Korean number formatting conventions
5. Structure: Maintain clear speaker distinction and paragraph breaks
6. Output in Korean only

Translate maintaining speaker tones and financial accuracy."""
    
    for attempt in range(3):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=1500,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": f"\n\n{text}"}]
            )
            return resp.content[0].text.strip()
        except anthropic._exceptions.OverloadedError as e:
            print(f"[🔁] Claude 서버 과부하. {attempt + 1}번째 재시도 중...")
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("Claude 서버가 과부하 상태입니다. 잠시 후 다시 시도해주세요.")

def summarize_qna_text(text, model="claude-3-5-sonnet-20241022"):
    """Q&A 요약 함수"""
    resp = client.messages.create(
        model=model,
        max_tokens=500,
        temperature=0.3,
        system="You are a financial analyst specializing in corporate earnings calls. Summarize the following transcript in 3–5 concise, clear, and unbiased bullet points. Focus on key financial metrics, guidance updates, tone of management, and any implied risks or strengths. The summary should be written in Korean and tailored for professional investors.",
        messages=[
            {"role": "user", "content": f"Summarize the following transcript:\n\n{text}"}
        ]
    )
    return resp.content[0].text.strip()

def process_qna_section(title, text):
    """Q&A 섹션 전용 처리 함수"""
    print(f"[📄] '{title}' 파트 번역 시작 (화자별 구분)")
    
    # 화자별로 파싱
    speakers = parse_qna_speakers(text)
    
    if not speakers:
        # 파싱 실패시 기본 방식으로 처리
        print("[⚠️] 화자 구분 실패, 기본 Q&A 번역 방식 사용")
        chunks = smart_split(text)
        translations = []
        
        for chunk in tqdm(chunks, desc="Q&A 기본 번역"):
            if not chunk.strip():
                translations.append("")
            else:
                translations.append(translate_qna_text(chunk, None))
            time.sleep(0.5)
        
        summary = summarize_qna_text(text)
        return (title, chunks, translations, summary)
    
    translations = []
    chunks = []
    
    for speaker, content in tqdm(speakers, desc="Q&A 화자별 번역"):
        if not content.strip():
            continue
            
        # 화자 유형 판별
        speaker_lower = speaker.lower()
        if any(keyword in speaker_lower for keyword in ['analyst', 'question', 'q']):
            speaker_type = "question"
        elif any(keyword in speaker_lower for keyword in ['answer', 'a', 'management', 'ceo', 'cfo', 'executive']) or len(speaker.split()) == 2:
            speaker_type = "answer"
        else:
            speaker_type = None
            
        # 긴 답변의 경우 청크로 분할
        if len(content) > 800:
            content_chunks = smart_split(content, max_chunk_size=800)
            translated_chunks = []
            
            for i, chunk in enumerate(content_chunks):
                # 첫 번째 청크만 화자 정보 포함
                chunk_speaker_type = speaker_type if i == 0 else None
                translated_chunk = translate_qna_text(chunk, chunk_speaker_type)
                translated_chunks.append(translated_chunk)
                time.sleep(0.5)
            
            # 청크들을 합침
            full_translation = " ".join(translated_chunks)
            chunks.append(f"{speaker}: {content}")
            translations.append(full_translation)
        else:
            # 짧은 내용은 한 번에 번역
            translation = translate_qna_text(content, speaker_type)
            chunks.append(f"{speaker}: {content}")
            translations.append(translation)
            time.sleep(0.5)
    
    # Q&A 전용 요약 생성
    summary = summarize_qna_text(text)
    return (title, chunks, translations, summary)