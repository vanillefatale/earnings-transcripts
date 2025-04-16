
# 📊 Earnings Call Transcript Translator

🔗 **Live Demo**: [https://vanillefatale.github.io/earnings-transcripts/](https://vanillefatale.github.io/earnings-transcripts/)

---

## 📁 준비물

아래와 같은 이름 형식을 가진 **2개의 텍스트 파일**이 필요합니다:

- `DPZ_1Q25_presentation.txt` : 실적 발표 프레젠테이션 텍스트
- `DPZ_1Q25_qna.txt` : Q&A 세션 텍스트

파일명은 자유롭게 바꿀 수 있지만, 반드시 다음과 같은 규칙을 따라야 합니다:

```
[기업심볼]_[분기]_presentation.txt
[기업심볼]_[분기]_qna.txt
```

예시: `DPZ_1Q25` → 도미노피자 2025년 1분기 실적 발표

---

## ▶️ 실행 방법

다음과 같이 파이썬 명령어로 실행합니다:

```bash
python earningscall_generator.py DPZ_1Q25
```

- `DPZ_1Q25`는 파일명에서 공통된 prefix로, `output_name` 역할을 합니다.
- 자동으로 번역 및 요약한 결과 HTML을 생성하고, index에 링크를 추가하며 Git push까지 진행합니다.

---

## 📂 출력 위치

- HTML 파일은 `docs/translated/[분기]/` 폴더에 저장됩니다.
- `index.html`에 자동으로 링크가 추가됩니다.

---

## ✅ 주요 기능 요약

- OpenAI / Claude 기반 전문 번역
- Presentation & Q&A 각각 분리 처리
- 자연스러운 한국어 요약 포함
- HTML 출력 및 Git 자동 반영

---

문의나 기여는 언제든지 환영합니다 🙌
