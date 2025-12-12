@echo off
setlocal

cd /d "%~dp0"
cls
echo =====================================
echo Earnings Transcript Generator - STEP 1
echo Make [TICKER_3Q25].txt
echo =====================================
echo.

:: 0-list.txt 파일 체크
if not exist 0-list.txt (
    echo 0-list.txt 파일을 찾을 수 없습니다.
    echo 예시 형식:
    echo XOM_3Q25
    echo ABBV_3Q25
    echo ...
    echo.
    pause
    exit /b
)

:: 0-list.txt 읽어서 [이름].txt 파일 생성
for /f "usebackq tokens=*" %%A in ("0-list.txt") do (
    if not "%%A"=="" (
        if not exist "%%A.txt" (
            echo %%A.txt 생성 중...
            type nul > "%%A.txt"
        ) else (
            echo %%A.txt 이미 존재함. 건너뜀.
        )
    )
)

echo.
echo ✅ STEP 1 완료: [이름].txt 파일 생성 끝.
pause
endlocal
