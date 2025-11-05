@echo off
setlocal

cd /d "%~dp0"
cls
echo =====================================
echo Earnings Transcript Generator
echo =====================================
echo.

:: list.txt 파일이 없으면 자동 생성 안내
if not exist list.txt (
    echo list.txt 파일을 찾을 수 없습니다.
    echo 예시 형식:
    echo XOM_3Q25
    echo ABBV_3Q25
    echo ...
    echo.
    pause
    exit /b
)

:: list.txt 읽어서 파일 생성
for /f "usebackq tokens=*" %%A in ("list.txt") do (
    set NAME=%%A
    if not exist %%A_presentation.txt (
        echo %%A_presentation.txt 생성 중...
        type nul > %%A_presentation.txt
    )
    if not exist %%A_qna.txt (
        echo %%A_qna.txt 생성 중...
        type nul > %%A_qna.txt
    )
)

echo.
echo ✅ 모든 파일 생성 완료.
pause
endlocal
