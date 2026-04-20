# generator/prompt_facts.py

FACTS_PROMPT_TEMPLATE = """You are a corporate earnings analyst.

아래는 원문(PDF 또는 텍스트) 일부({idx}/{total})이다.
목표는 '요약'이 아니라 '추출'이다: 원문에 있는 사실/숫자/가이던스/세그먼트 관련 문장을 최대한 많이 정확하게 뽑아라.
추정/해석/추가 계산 금지.

[절대 규칙]
- 원문에 없는 숫자/단어를 만들지 말 것.
- '미기재', 'X', 'X개', 'X.X%', 'Xbps' 같은 placeholder/대체표현 금지.
- 마크다운/구분선 금지. 순수 텍스트.
- 가능하면 원문 문장을 그대로(또는 아주 짧게) 유지하라.

[출력 구조]
아래 4개 섹션만 출력하고, 각 섹션에는 "원문에서 그대로 발췌한 문장/라인"을 하이픈(-)으로 최대한 많이 나열하라.
(중복이 조금 있어도 괜찮다. 유실이 더 치명적이다.)

[ FACTS: Financial ]
- (Revenue, operating profit/income, net income, EPS, margins, FCF, cash, debt 등 숫자가 포함된 원문 라인/문장 위주로 최대한 발췌)

[ FACTS: Segment/Region ]
- (세그먼트/지역/브랜드명 + 매출/이익/마진/YoY/bps/SSS/comp/opened/closed/store 등 숫자 포함 라인을 최대한 발췌)

[ FACTS: Guidance/Outlook ]
- (FY/Q guidance, outlook, assumptions, FX, cost, capex/FCF 등 숫자/레인지/기간 포함 라인을 최대한 발췌)

[ FACTS: Strategy/Highlights ]
- (전략/이니셔티브/투자/신제품/구조조정/비용절감/M&A/자사주/배당 등 '사실' 위주 문장을 최대한 발췌. 숫자/타임라인이 있으면 우선)

[추출 팁(강제)]
- 숫자(%, bps, YoY/QoQ, ¥/$/JPY, million/billion/trillion, EPS, margin 등)가 포함된 라인은 우선적으로 발췌하라.
- 세그먼트명(UNIQLO Japan/International/GU/Global Brands 등) 근처의 숫자 라인은 우선 발췌하라.
- 표가 깨져 있어도 숫자/키워드가 보이면 그 라인을 그대로 발췌하라.

[파일명]
{pdf_name}

[원문 텍스트 - PART {idx}/{total}]
{chunk}
"""


def build_facts_prompt(pdf_name: str, chunk: str, idx: int, total: int) -> str:
    return FACTS_PROMPT_TEMPLATE.format(
        pdf_name=pdf_name,
        chunk=chunk,
        idx=idx,
        total=total,
    )
