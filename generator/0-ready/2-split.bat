@echo off
setlocal

REM 이 bat 파일이 있는 폴더로 이동
cd /d "%~dp0"

echo =====================================
echo Earnings Transcript Splitter - RUN
echo =====================================
echo 현재 폴더: %cd%
echo.

REM python 이 있는지 먼저 확인
where python >nul 2>&1
if %errorlevel%==0 (
    echo python 2-split.py 실행 중...
    python 2-split.py
) else (
    REM python 이라는 이름이 없으면 py 로 시도
    where py >nul 2>&1
    if %errorlevel%==0 (
        echo py 2-split.py 실행 중...
        py 2-split.py
    ) else (
        echo Python 실행 파일을 찾을 수 없습니다.
        echo PATH 에 python 또는 py 를 추가해 주세요.
    )
)

echo.
echo 작업 완료. 창을 닫으려면 아무 키나 누르세요.
pause >nul

endlocal
