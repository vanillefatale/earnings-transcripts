import os

# 설정
LIST_FILE = "0-list.txt"
MARKER = "Question-and-Answer Session"

ROOT = os.path.dirname(os.path.abspath(__file__))


def read_text_with_fallback(path: str) -> str:
    """
    여러 인코딩을 시도해서 원본 텍스트를 그대로 읽는다.
    줄바꿈(\r\n)도 그대로 유지.
    """
    encodings = ["utf-8-sig", "utf-8", "cp1252", "cp949"]
    last_err = None

    for enc in encodings:
        try:
            with open(path, "r", encoding=enc, newline="") as f:
                return f.read()
        except UnicodeDecodeError as e:
            last_err = e
            continue

    raise last_err if last_err else RuntimeError(f"Cannot read file: {path}")


def main():
    list_path = os.path.join(ROOT, LIST_FILE)
    if not os.path.exists(list_path):
        print(f"[ERROR] {LIST_FILE} 파일을 찾을 수 없습니다.")
        return

    # 리스트 읽기 (빈 줄 제거)
    with open(list_path, "r", encoding="utf-8-sig", newline="") as f:
        names = [line.strip() for line in f if line.strip()]

    print("====================================")
    print("Earnings Transcript Splitter")
    print(f"Marker : '{MARKER}'")
    print("====================================\n")

    for name in names:
        input_path = os.path.join(ROOT, f"{name}.txt")
        if not os.path.exists(input_path):
            print(f"[{name}] 입력 파일 없음: {input_path}")
            continue

        print(f"[{name}] 처리 중...")

        text = read_text_with_fallback(input_path)

        idx = text.find(MARKER)
        if idx == -1:
            print(f"  -> 마커 '{MARKER}' 를 찾지 못했습니다. 건너뜀.")
            print()
            continue

        # 앞부분 / 뒷부분(마커 포함) 분리
        pre = text[:idx]
        post = text[idx:]  # MARKER 줄 포함

        pre_path = os.path.join(ROOT, f"{name}_presentation.txt")
        qna_path = os.path.join(ROOT, f"{name}_qna.txt")

        # UTF-8 로 저장 (줄바꿈 그대로 유지)
        with open(pre_path, "w", encoding="utf-8", newline="") as f:
            f.write(pre)

        with open(qna_path, "w", encoding="utf-8", newline="") as f:
            f.write(post)

        # --- 여기서 원본 input 파일 삭제 ---
        try:
            os.remove(input_path)
            print(f"  -> OK: {pre_path} / {qna_path} (원본 삭제: {input_path})\n")
        except OSError as e:
            print(f"  -> 분리는 성공했지만 원본 삭제 실패: {e}\n")


    print("\n✅ 모든 분리 작업 완료.")


if __name__ == "__main__":
    main()
