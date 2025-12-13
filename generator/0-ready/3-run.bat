@echo off
setlocal

REM 3-run.bat 이 있는 폴더(= 0-ready) 기준에서 한 단계 올라가서 generator 로 이동
cd /d "%~dp0.."

echo =====================================
echo STEP 3 - Run earningscall_generator.py
echo BASE DIR : %cd%   (generator)
echo =====================================
echo.

REM 0-ready\0-list.txt 존재 확인
if not exist "0-ready\0-list.txt" (
    echo 0-ready\0-list.txt 파일을 찾을 수 없습니다.
    echo.
    pause
    exit /b 1
)

REM earningscall_generator.py 존재 확인
if not exist "earningscall_generator.py" (
    echo earningscall_generator.py 파일을 찾을 수 없습니다.
    echo generator 폴더 기준 경로를 확인해 주세요.
    echo.
    pause
    exit /b 1
)

REM 0-ready\0-list.txt 의 각 이름에 대해 generator 실행
for /f "usebackq tokens=*" %%A in ("0-ready\0-list.txt") do (
    if not "%%A"=="" (
        echo 실행: python earningscall_generator.py %%A
        python "earningscall_generator.py" %%A
        echo.
    )
)

echo =====================================
echo 모든 작업 실행 완료.
echo =====================================
echo.
pause
endlocal
