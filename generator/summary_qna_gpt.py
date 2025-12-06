# generator/summary_qna_gpt.py

import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from telegram_notifier import send_telegram_message

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY 가 .env 에 설정되어 있지 않습니다.")

client = OpenAI(api_key=OPENAI_API_KEY)

BASE_DIR = Path(__file__).resolve().parent
READY_DIR = BASE_DIR / "0-ready"       # 0-ready/<output_name>_qna.txt
SUMMARY_DIR = BASE_DIR / "2-summary"   # 2-summary/<output_name>_qna_summary_gpt.txt
SUMMARY_DIR.mkdir(exist_ok=True)


def read_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

QNA_PROMPT = """
You are a corporate earnings call analyst focused on Q&A segments.

When the user provides an earnings call transcript, automatically extract and summarize ALL Q&A pairs in a single response without asking for confirmation or pausing.

Critical Instructions:
- NEVER ask how many Q&A pairs exist
- NEVER ask if user wants to continue
- NEVER provide partial results
- ALWAYS complete full analysis of ALL Q&A pairs in one response
- NO formatting marks (asterisks, hashtags, dashes, bullets, bold, italic, etc.)
- Plain text only for Telegram compatibility

Workflow:
1. Read entire transcript and locate the Q&A section
2. Count total Q&A pairs
3. Extract and summarize ALL Q&A pairs immediately in a single response

Output Format:
For each Q&A pair, provide:

Q. [핵심 질문 내용]
[답변을 2-3문장으로 간결하게 요약하되, ~임, ~함, ~중임 등의 명사형 종결어미 사용]

Example:

Q. 브랜드별 가격 인상 추세?
여러 브랜드들이 가격 인상을 발표했으나 이번 분기는 특별히 크지 않았음. 관세와 원가 상승을 감안해 브랜드들과 협의 중이나, 소비자 부담을 고려해 가치를 유지하려고 함.

Q. 온라인 성장 관련?
여전히 80% 매출은 오프라인 매장이며, 스토어와 이커머스 모두 성장 중임.

Q. 2026년 브랜드 파이프라인?
구체적인 이름과 규모는 3월에 공유 예정이나, 현재 보이는 2026 파이프라인에 대해 매우 긍정적으로 평가하고 있음.

Q. 홀리데이 시즌 모멘텀?
Black Friday와 Cyber Monday 실적에 만족하고 있으며, 분기 내내 컴프 성장이 고르게 나타났음.

Requirements:
- Keep each answer to 2-3 sentences maximum
- Use Korean business language with ~임, ~함, ~중임 등 명사형 종결어미를 일관되게 사용할 것
- Focus on key points only and exclude unnecessary 세부사항, 에피소드, 반복 설명
- No special characters or formatting marks in the output (no asterisks, hashtags, dashes, bullets, bold, italic, 구분선 등)
- Plain text only
- Process entire Q&A section in a single response
- Maintain a professional yet concise tone
- Include ALL Q&A pairs without stopping or truncating

중요 출력 형식 규칙 (반드시 지킬 것):
- 각 Q&A는 정확히 두 블록으로 구성함
  첫 줄: Q. 로 시작하는 질문 요약 한 줄
  둘째 줄: 답변 요약 한 단락 (2-3문장, 모두 ~임 / ~함 / ~중임으로 끝나도록 작성함)
- Q. 와 답변 사이에는 빈 줄을 넣지 않음
- 서로 다른 Q&A 쌍 사이에는 빈 줄 하나만 넣음
- 맨 위/맨 아래에 구분선, 요약 설명 문구, 추가 장식 텍스트를 추가하지 않음
"""


def generate_qna_summary(text: str) -> str:
    """
    어닝콜 Q&A 원문(text)을 받아서,
    QNA_PROMPT 형식에 맞는 Q&A 요약 텍스트를 반환.
    (텔레그램에 그대로 전송 가능한 순수 텍스트)
    """
    full_prompt = (
        QNA_PROMPT
        + "\n\n"
        + "아래는 분석할 어닝콜 전체 원문이다. 이 중 Q&A 섹션을 스스로 찾아서 위 지시를 모두 만족하는 출력만 생성하라.\n"
        + "원문 시작\n"
        + "================================================================================\n"
        + text
        + "\n================================================================================\n"
        + "원문 끝\n"
    )

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL_SUMMARY", "gpt-4.1-mini"),
        input=full_prompt,
        max_output_tokens=4000,  # Q&A 페어가 많을 수 있으니 넉넉하게
        temperature=0.2,
    )

    return response.output_text.strip()

# summary_qna_gpt.py 맨 아래쪽에 추가

from telegram_notifier import send_telegram_message  # 상단에 이미 있으면 생략

def run_qna_summary(output_name: str):
    """
    earningscall_generator 에서 불러 쓰기 위한 헬퍼.
    0-ready/<output_name>_qna.txt 를 읽어서
    GPT Q&A 요약 파일 생성 + 텔레그램 전송까지 수행함.
    """
    input_path = READY_DIR / f"{output_name}_qna.txt"
    if not input_path.exists():
        raise FileNotFoundError(f"입력 파일이 없습니다: {input_path}")

    print(f"[🧠] GPT Q&A Summary 생성 중... ({input_path})")
    raw_text = read_file(input_path)
    summary_text = generate_qna_summary(raw_text)

    # 1) 파일 저장
    output_path = SUMMARY_DIR / f"{output_name}_qna_summary_gpt.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"[✔] Q&A 요약 저장 완료: {output_path}")

    # 2) 텔레그램 발송
    header = f"[{output_name}] Q&A Summary\n\n"
    full_msg = header + summary_text

    print("[📨] 텔레그램으로 Q&A 요약 전송 중...")

    chunk_size = 3800  # 텔레그램 메시지 제한 고려
    for i in range(0, len(full_msg), chunk_size):
        chunk = full_msg[i : i + chunk_size]
        send_telegram_message(chunk, use_markdown=False)

    return summary_text, str(output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output_name",
        help="파일 베이스 이름 (예: VSCO_3Q25 → 0-ready/VSCO_3Q25_qna.txt 를 읽음)",
    )
    args = parser.parse_args()

    input_path = READY_DIR / f"{args.output_name}_qna.txt"
    if not input_path.exists():
        raise FileNotFoundError(f"입력 파일이 없습니다: {input_path}")

    print(f"[📥] Q&A 원문 읽는 중: {input_path}")
    raw_text = read_file(input_path)

    print("[🧠] GPT Q&A Summary 생성 중...")
    summary_text = generate_qna_summary(raw_text)

    # 1) 파일 저장
    output_path = SUMMARY_DIR / f"{args.output_name}_qna_summary_gpt.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"[✔] Q&A 요약 저장 완료: {output_path}")

    # 2) 텔레그램 전송 (헤더도 최대한 심플한 플레인 텍스트)
    header = f"[{args.output_name}] Q&A Summary\n\n"
    full_msg = header + summary_text

    print("[📨] 텔레그램으로 Q&A 요약 전송 중...")

    # 텔레그램 메시지 길이 제한 고려 (여유 있게 3,800자로 나눔)
    chunk_size = 3800
    for i in range(0, len(full_msg), chunk_size):
        chunk = full_msg[i : i + chunk_size]
        send_telegram_message(chunk, use_markdown=False)

    print("\n===== PREVIEW (상위 40줄) =====\n")
    preview_lines = summary_text.splitlines()[:40]
    print("\n".join(preview_lines))


if __name__ == "__main__":
    main()
