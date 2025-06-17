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

def determine_speaker_type(speaker):
    """화자 유형을 더 정확하게 판별"""
    speaker_lower = speaker.lower()
    
    # Operator는 중립
    if 'operator' in speaker_lower:
        return None
        
    # 회사명이 포함된 경우 (– 또는 - 로 구분) = 애널리스트
    if ' – ' in speaker or ' - ' in speaker:
        return "question"
    
    # 일반적인 애널리스트 회사명들
    analyst_companies = ['sidoti', 'davenport', 'blackrock', 'deutsche', 'goldman', 'jpmorgan', 
                        'morgan stanley', 'wells fargo', 'credit suisse', 'barclays', 'citi']
    if any(company in speaker_lower for company in analyst_companies):
        return "question"
    
    # 임원 직책들
    exec_titles = ['ceo', 'cfo', 'president', 'chairman', 'chief', 'director']
    if any(title in speaker_lower for title in exec_titles):
        return "answer"
    
    # 기본적으로 단순 이름만 있으면 경영진으로 간주
    if len(speaker.split()) <= 3 and not any(char in speaker for char in ['-', '–', '(', ')']):
        return "answer"
    
    return None

def parse_qna_speakers(text):
    """Q&A 텍스트에서 화자별로 구분하여 파싱"""
    
    print(f"[🔍] 텍스트 샘플 (처음 300자):\n{text[:300]}...")
    
    speakers = []
    lines = text.split('\n')
    current_speaker = None
    current_text = ""
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 빈 줄 건너뛰기
        if not line:
            i += 1
            continue
            
        # 세션 헤더 건너뛰기
        if 'Question-and-Answer Session' in line:
            i += 1
            continue
            
        # Operator 처리 (특별 케이스)
        if line == "Operator":
            # 이전 화자 저장
            if current_speaker and current_text.strip():
                speakers.append((current_speaker, current_text.strip()))
            
            current_speaker = "Operator"
            current_text = ""
            i += 1
            
            # Operator 발언 수집
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                    
                # 다음 화자인지 확인
                if ((' – ' in next_line or ' - ' in next_line) or 
                    (next_line and not next_line.startswith('(') and 
                     len(next_line.split()) <= 3 and 
                     next_line[0].isupper() and 
                     ':' not in next_line and
                     next_line != "Operator")):
                    break
                else:
                    if current_text:
                        current_text += " " + next_line
                    else:
                        current_text = next_line
                    i += 1
            continue
            
        # 화자 라인 감지
        is_speaker_line = False
        
        # 회사명 포함 형식 확인
        if ' – ' in line or ' - ' in line:
            is_speaker_line = True
        # 단순 이름 형식 확인 (3단어 이하, 대문자 시작, 콜론 없음)
        elif (len(line.split()) <= 3 and line[0].isupper() and ':' not in line and 
              not line.startswith('(') and not line.startswith('Thank') and
              not any(word in line.lower() for word in ['thank', 'question', 'next', 'sir', 'madam'])):
            is_speaker_line = True
            
        if is_speaker_line:
            # 이전 화자 저장
            if current_speaker and current_text.strip():
                speakers.append((current_speaker, current_text.strip()))
            
            # 새 화자 시작
            current_speaker = line
            current_text = ""
            i += 1
            
            # 해당 화자의 발언 수집
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                    
                # 다음 화자인지 확인
                next_is_speaker = False
                if next_line == "Operator":
                    next_is_speaker = True
                elif ' – ' in next_line or ' - ' in next_line:
                    next_is_speaker = True
                elif (len(next_line.split()) <= 3 and next_line[0].isupper() and 
                      ':' not in next_line and not next_line.startswith('(') and 
                      not next_line.startswith('Thank') and
                      not any(word in next_line.lower() for word in ['thank', 'question', 'next', 'sir', 'madam'])):
                    next_is_speaker = True
                
                if next_is_speaker:
                    break
                else:
                    if current_text:
                        current_text += " " + next_line
                    else:
                        current_text = next_line
                    i += 1
        else:
            i += 1
    
    # 마지막 화자 저장
    if current_speaker and current_text.strip():
        speakers.append((current_speaker, current_text.strip()))
    
    print(f"[📊] 파싱 결과: {len(speakers)}명의 화자 발견")
    for i, (speaker, content) in enumerate(speakers[:5]):
        print(f"  {i+1}. {speaker}: {content[:80]}...")
    
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
        # 기본 Q&A 번역 (Operator 등)
        system_prompt = """You are a professional financial translator specializing in earnings call Q&A sessions. Translate the following Q&A content into natural, accurate Korean following these rules:

1. Speaker format: Use '**Name:**' format exactly as provided in English
2. Professional tone: Use formal, professional Korean suitable for financial reports  
3. Financial terminology: Use standard Korean financial terms, add English terms in parentheses for first occurrence
4. Numbers: Follow Korean number formatting conventions
5. Structure: Maintain clear speaker distinction and paragraph breaks
6. Output in Korean only

Translate maintaining the original tone and financial accuracy."""
    
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
            
        # 개선된 화자 유형 판별
        speaker_type = determine_speaker_type(speaker)
        
        # 긴 답변의 경우 청크로 분할
        if len(content) > 800:
            content_chunks = smart_split(content, max_chunk_size=800)
            translated_chunks = []
            
            for i, chunk in enumerate(content_chunks):
                # 모든 청크에 화자 정보 포함 (맥락 유지)
                translated_chunk = translate_qna_text(chunk, speaker_type)
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