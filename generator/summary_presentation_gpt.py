# generator/summary_presentation_gpt.py

import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from telegram_notifier import send_telegram_message

# 환경 변수 로드
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY 가 .env 에 설정되어 있지 않습니다.")

# OpenAI 클라이언트
client = OpenAI(api_key=OPENAI_API_KEY)

# 디렉토리 설정
BASE_DIR = Path(__file__).resolve().parent
READY_DIR = BASE_DIR / "0-ready"       # 원문 위치: 0-ready/<output_name>_presentation.txt
SUMMARY_DIR = BASE_DIR / "2-summary"   # 요약 결과 저장 위치
SUMMARY_DIR.mkdir(exist_ok=True)


def read_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


PRESENTATION_PROMPT = """
아래 제공된 어닝콜 원문 또는 IR 자료만을 기반으로, 지정된 형식에 맞춰 한국어로 요약하라.

[출력 형식 규칙 – 매우 중요]
- 반드시 아래 구조와 순서, 헤더 문구를 그대로 따를 것.
- [ 어닝콜 요약 ] 과 [ 가이던스 요약 ] 헤더는 각각 정확히 한 번만 출력할 것.
- 어떠한 형태의 구분선(━, ─, -, =, _, *, # 등)도 절대 출력하지 말 것.
- 맨 위/맨 아래에 장식용 문장이나 구분선, 요약 설명 문구를 추가하지 말 것.
- 마크다운(볼드, 이탤릭, 코드블록 등)을 사용하지 말고, 순수 텍스트만 사용할 것.
- 아래 템플릿에서 대괄호 안의 설명은 실제 값으로 대체하되, 불필요한 문장은 만들지 말 것.

[ 어닝콜 요약 ]

매출 [증감률] YoY ($[금액]M 또는 B)
- [핵심 성장 동력 요약]
- [채널별/부문별 주요 변화]

Sales by segment
1) [세그먼트명] $[금액]M/B (YoY +[X]%)
   - [성장 동력 및 주요 내용]
   - [지역별/제품별 세부 실적]
   - [특이사항]

2) [세그먼트명] $[금액]M/B (YoY +[X]%)
   - [성장 동력 및 주요 내용]

[필요 시 3), 4) 등 추가 세그먼트를 동일한 형식으로 작성하되, 불필요하면 생략해도 된다.]

GPM [값]% (+/- [X] bps)
+ [긍정 요인]
- [부정 요인]

OPM [값]% (+/- [X] bps)
+ [긍정 요인]
- [부정 요인]

[ 가이던스 요약 ]

Guidance [기간: FY20XX 또는 4Q20XX 등] (updated)
- Revenue growth [X%] vs. 기존 [X%] [상향/하향/유지]
- Gross margin [X%] vs. 기존 [X%] [상향/하향/유지]
- Operating margin [X% 또는 $X] vs. 기존 [X% 또는 $X] [상향/하향/유지]
- EPS $[X.XX]-$[X.XX] vs. 기존 $[X.XX]-$[X.XX] [상향/하향/유지]
- [기타 주요 지표가 있으면 한 줄로 추가. 없으면 이 줄은 생략.]

주요 변화
- [가이던스 변경의 핵심 이유를 1–2줄로 요약. 관세, 수요, 채널 믹스, 비용 구조 등 핵심만.]

작성 원칙
1. 구조
   - 매출: 전체 증감률 → 핵심 성장 동력 → 세그먼트별 상세
   - 세그먼트: 성장률 → 성장 동력 → 지역/제품 세부 실적 → 특이사항
   - GPM/OPM: 각각 긍정 요인(+)과 부정 요인(-)을 나눠서 요약
   - 가이던스: 항목별로 기존 대비 변화(상향/하향/유지)를 명확히 표기

2. 내용
   - 매출 성장/감소의 이유를 원문에서 찾아 구체적으로 정리할 것.
   - 세그먼트별로 “무엇이 성장/부진을 만들었는지(가격, 물량, 채널, 지역, 제품 등)”를 명확히 작성.
   - 원문의 핵심 숫자와 용어(예: mid-single digit, low double digit, AUR, traffic 등)는 그대로 사용.
   - 숫자는 가능한 한 구체적으로 작성하되, 원문에 없는 수치는 새로 만들지 말 것.

3. 형식
   - 반드시 위에 제시된 헤더와 순서를 그대로 유지할 것.
   - 구분선(━, ─, -, =, _, *, # 등)은 어떤 형태로도 출력하지 말 것.
   - 마크다운 서식은 사용하지 말 것.
   - 들여쓰기는 "   - " 또는 "- " 형태의 일반 텍스트만 사용할 것.

4. 단위
   - 금액: M (million), B (billion) 사용 (예: $1.4B, $350M).
   - 마진: %, bps(실제 숫자와 함께, 예: +170 bps).
   - 퍼센트 포인트는 %p 대신 bps로 통일.

5. 간결성
   - 각 항목은 1–3줄 이내로 요약할 것.
   - 불필요한 수사(예: “매우”, “굉장히”)나 장식적인 문장은 제거.
   - 투자자가 바로 이해할 수 있도록 직설적이고 간단하게 작성.

================================================================================
작성 예시
================================================================================

[예시1: 신발/의류 브랜드 - 어닝콜 요약]

매출 +5.8% YoY ($1,643M)
- Direct-to-consumer channel +12% 성장이 주요 동력 (전체 매출의 46% 차지)
- Comparable store sales +3.7% 견조한 성장
- Wholesale channel -1% 소폭 감소로 전체 성장세 일부 상쇄

Sales by segment
1) Vans brand $1,461M (YoY +4%)
   - DTC +10%: 온라인 채널 강화 및 직영점 트래픽 증가
   - Wholesale -2%: 도매 채널 축소 전략 지속 (저마진 채널 정리)
   - 지역별: EMEA +8% (유럽 강세), APAC +5%, Americas +3%
   - 제품별: Footwear +4% (클래식 라인 및 신제품), Apparel +5%
   - Vans Family 로열티 프로그램 확대 및 프로모션 의존도 감소

2) Supreme brand $91M (YoY +29%)
   - 강력한 신제품 라인업과 협업 컬렉션 성공
   - Global 확장 지속

3) Other brands $91M (YoY +8%)

GPM 51.8% (+150 bps)
+ 프로모션 감소, 제품 믹스 개선, 가격 전략 효과
+ DTC 채널 성장으로 마진율 높은 채널 믹스 개선
- 물류비 및 운영비 일부 증가

OPM 10.1% (+280 bps)
+ 매출총이익 개선 효과
+ SG&A 효율화 ($765M, 매출 대비 46.6%)
- 브랜드 마케팅 투자 지속


[예시2: 신발/의류 브랜드 - 가이던스 요약]

Guidance FY2025 (updated)
- Revenue growth mid-single digit % vs. 기존 low-single digit to mid-single digit % [상향]
- Gross margin ~52% vs. 기존 51.5%-52% [유지]
- Operating margin ~10% vs. 기존 9%-10% [유지]
- EPS $2.20-$2.30 vs. 기존 $2.00-$2.20 [상향]

주요 변화
- Vans 브랜드 턴어라운드 진행 중. DTC 채널 강세와 Supreme 고성장으로 매출 가이던스 상향. 마진 개선세 지속되며 수익성 회복 본격화.


[예시3: 뷰티 리테일 - 어닝콜 요약]

매출 +13% YoY
- SSS +6.3% (qoq -40 bps)
- Transactions Growth 2.4% (qoq -130 bps)
- Average Ticket Growth 3.8% (qoq +90 bps)
- 전 카테고리·채널 성장. E-commerce mid-teen 성장, 실매장 +MSD%

Sales by segment
1) Cosmetics $1,172M (YoY +10%)
   - Mass Makeup: NYX, Morphe, L'Oreal 신제품 + 브랜드 가격 인상
   - Prestige Makeup: 21 Days of Beauty 이벤트 성공 (Estée Lauder, MAC), HOURGLASS, NARS 강세

2) Haircare $543M (YoY +2%)
   - Prestige Hair 강세: Moroccanoil, Nutrafol (신규), Redken, Matrix
   - Cécred (Beyoncé 헤어케어): Ulta 역사상 가장 성공적인 Prestige 헤어케어 런칭

3) Skincare $686M (YoY +23%)
   - Fenty 독점 런칭. Prestige·Mass 모두 성장
   - K-beauty 지속 성장: ANUA, medicube, TIRTIR 등 독점 브랜드 고성장

4) Fragrance $314M (YoY +38%)
   - Luxury 신제품(Valentino, D&G)과 Miu Miu 등 신규 브랜드 흥행
   - 매장 60%에서 진열공간 확대

5) Services $86M (YoY -15%)
   - Cut·Color·Brow 서비스 확대. 스타일리스트 생산성 개선 지속

GPM 40% (+70 bps)
+ 재고 손실 감소, 브랜드 가격 인상 + 프로모션 효율화로 마진 개선
- 디지털 채널 급성장으로 채널믹스 악화 효과 일부 상쇄

OPM 11% (-180 bps)
- 매장 인건비·운영비 증가, Space NK 인수, 기술 투자 집중(클라우드 시스템 상각비↑)

"""


def generate_presentation_summary(text: str) -> str:
    """
    어닝콜 Presentation 원문(text)을 받아서,
    프롬프트 형식에 맞는 요약 텍스트를 반환.
    (텔레그램에 그대로 전송 가능한 순수 텍스트)
    """
    full_prompt = (
        PRESENTATION_PROMPT
        + "\n\n"
        + "아래는 분석할 어닝콜 원문 또는 IR 자료 전문이다.\n"
        + "이 원문만을 근거로 위에서 정의한 형식에 정확히 맞춰 작성하라.\n"
        + "원문 시작\n"
        + "================================================================================\n"
        + text
        + "\n================================================================================\n"
        + "원문 끝\n"
    )

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL_SUMMARY", "gpt-4.1-mini"),
        input=full_prompt,
        max_output_tokens=1800,
        temperature=0.2,
    )

    return response.output_text.strip()

# summary_presentation_gpt.py 맨 아래쪽에 추가

from telegram_notifier import send_telegram_message  # 파일 상단에 이미 있으면 중복 추가 X

def run_presentation_summary(output_name: str):
    """
    earningscall_generator 에서 불러 쓰기 위한 헬퍼.
    0-ready/<output_name>_presentation.txt 를 읽어서
    GPT 요약 파일 생성 + 텔레그램 전송까지 수행함.
    """
    input_path = READY_DIR / f"{output_name}_presentation.txt"
    if not input_path.exists():
        raise FileNotFoundError(f"입력 파일이 없습니다: {input_path}")

    print(f"[🧠] GPT Presentation Summary 생성 중... ({input_path})")
    raw_text = read_file(input_path)
    summary_text = generate_presentation_summary(raw_text)

    # 1) 파일 저장
    output_path = SUMMARY_DIR / f"{output_name}_presentation_summary_gpt.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"[✔] Presentation 요약 저장 완료: {output_path}")

    # 2) 텔레그램 발송
    header = f"[{output_name}] Presentation Summary\n\n"
    full_msg = header + summary_text

    print("[📨] 텔레그램으로 Presentation 요약 전송 중...")

    chunk_size = 3800  # 텔레그램 메시지 제한 고려
    for i in range(0, len(full_msg), chunk_size):
        chunk = full_msg[i : i + chunk_size]
        send_telegram_message(chunk, use_markdown=False)

    return summary_text, str(output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output_name",
        help="파일 베이스 이름 (예: VSCO_3Q24 → 0-ready/VSCO_3Q24_presentation.txt 를 읽음)",
    )
    args = parser.parse_args()

    input_path = READY_DIR / f"{args.output_name}_presentation.txt"
    if not input_path.exists():
        raise FileNotFoundError(f"입력 파일이 없습니다: {input_path}")

    print(f"[📥] Presentation 원문 읽는 중: {input_path}")
    raw_text = read_file(input_path)

    print("[🧠] GPT Presentation Summary 생성 중...")
    summary_text = generate_presentation_summary(raw_text)

    # 1) 파일로 저장
    output_path = SUMMARY_DIR / f"{args.output_name}_presentation_summary_gpt.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"[✔] Presentation 요약 저장 완료: {output_path}")

    # 2) 텔레그램으로 전송
    header = f"[{args.output_name}] Presentation Summary \n\n"
    full_msg = header + summary_text

    print("[📨] 텔레그램으로 Presentation 요약 전송 중...")

    # 텔레그램 메시지는 최대 4096자 → 여유 있게 3800자로 끊어서 전송
    chunk_size = 3800
    for i in range(0, len(full_msg), chunk_size):
        chunk = full_msg[i : i + chunk_size]
        # GPT 프롬프트에서 이미 "순수 텍스트"로 만들고 있으니까 Markdown 끔
        send_telegram_message(chunk, use_markdown=False)

    # 콘솔 프리뷰
    print("\n===== PREVIEW (상위 40줄) =====\n")
    preview_lines = summary_text.splitlines()[:40]
    print("\n".join(preview_lines))


if __name__ == "__main__":
    main()
