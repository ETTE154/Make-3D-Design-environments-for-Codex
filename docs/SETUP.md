# Autodesk Fusion 작업 환경 구축 실행 명세

## 0. 실행 위치와 기본 경로
권장 초기 경로: **로컬 Windows Codex → Python 스크립트 파일 → 실행 중인 Fusion → 출력 파일 검증**.
MCP/화면 제어는 선택 확장이다. 계정별 기능 제공 여부와 도구 목록을 실제로 확인한다 [O1–O5].
출처 식별자는 [SOURCES.md](SOURCES.md)에 정의되어 있다.

## 1. 기존 환경 조사
```powershell
Get-Location
[System.Runtime.InteropServices.RuntimeInformation]::OSDescription
[System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
Get-Command git,code,codex,python,py,winget -ErrorAction SilentlyContinue
.\scripts\bootstrap.ps1
```

Fusion 실행 여부·버전·현재 미저장 문서를 사용자와 확인한다. 기존 문서를 닫거나 덮어쓰지 않는다.
CPU 아키텍처와 실제 Autodesk 시스템 요구사항이 맞는지 확인한다. Windows ARM에서 실행 가능성을 추측하지 않는다.
이미 Fusion이 설치되어 있으면 기존 설치와 사용 권한을 재사용한다.

## 2. 공통 도구
계획 검토 후 `scripts/bootstrap.ps1 -Apply`를 실행한다.
누락된 Git/Python/VS Code와 공식 Codex 확장 `openai.chatgpt`만 대상으로 한다 [O2, O3, W1].
기존 CPython 3.10 이상을 재사용한다. 별도 Python은 STL 검사/보고서용이며 **Fusion 내장 Python을 교체하지 않는다**.
CLI Codex를 쓰면 `-SkipEditor`를 적용할 수 있다.
설치 후 새 터미널에서 `python .\scripts\doctor.py`를 실행해 `.local/doctor.json`을 생성한다.

## 3. Fusion 공식 설치 및 인증 — 사용자 개입 경계
Fusion이 없다면 Autodesk 공식 제품/계정 페이지에서 설치 프로그램을 받는다.
검토되지 않은 설치 파일·무인 설치 스위치·제3자 재배포본을 사용하지 않는다.

1. 사용자가 설치 프로그램 실행/UAC 및 해당 약관을 검토한다.
2. Autodesk 계정 로그인과 사용 권한/라이선스 선택은 사용자가 직접 수행한다.
3. 첫 실행을 완료하고 새 빈 디자인을 만들 수 있는지 확인한다.
4. Help/About의 버전과 사용 중인 제품 이름을 기록한다.

Codex가 실제 GUI를 조작할 수 없으면 필요한 단계만 사용자에게 요청하고 `BLOCKED_USER_ACTION`으로 기록한다.
계정 비밀번호·인증 코드·라이선스 키를 저장소나 채팅에 기록하지 않는다.

## 4. Fusion Python API 실행 환경 [F1]
`adsk.core`와 `adsk.fusion`은 Fusion 프로세스 내부 API다.
일반 Python 가상환경에 같은 이름의 패키지를 설치해 대체하지 않는다.
VS Code의 `import adsk` 정적 분석 경고만으로 Fusion 실행 실패라고 판단하지 않는다.
기본 개발 순서는 **Fusion의 Scripts and Add-Ins → Python 스크립트 생성/등록 → VS Code 편집 → Fusion에서 Run**이다.

### A. 저장소의 스크립트 폴더를 직접 등록 — 권장
Fusion에서 **UTILITIES → Scripts and Add-Ins**를 연다. 버전에 따라 Shift+S로 접근할 수 있다.
기존 스크립트를 추가하는 `+` / Add 기능으로 이 저장소의 다음 폴더를 선택한다.

```text
fusion/AgentSmokeTest/
  AgentSmokeTest.py
  AgentSmokeTest.manifest
```

문서 UI가 새 생성과 기존 등록을 구분하는 경우 **기존 스크립트 추가**를 선택한다.
이 방법은 폴더를 복사하지 않으므로 Codex가 편집하는 파일과 Fusion이 실행하는 파일이 같은 원본이다.
실행 목록에 AgentSmokeTest가 표시되는지 확인한다. Run-on-startup은 사용하지 않는다.

### B. 등록 UI 대신 API Scripts 폴더에 넣어야 하는 경우
공식 문서의 현재 기본 후보는 다음과 같지만, **Preferences의 실제 API 경로가 우선**이다 [F1].

| OS | 현재 공식 문서의 기본 후보 |
|---|---|
| Windows | `%APPDATA%\Autodesk\Autodesk Fusion\API\Scripts` |
| macOS | `$HOME/Library/Application Support/Autodesk/Autodesk Fusion/API/Scripts` |

이전 설치나 제3자 문서에는 `Autodesk Fusion 360` 경로가 있을 수 있다.
존재 여부만 보고 임의 선택하지 말고 실제 설정된 API Scripts 경로를 확인한다.
복사할 때는 대상 `AgentSmokeTest` 폴더가 없는지 확인하고 기존 폴더를 덮어쓰지 않는다.
코드를 갱신할 때 등록 원본/복사본의 해시가 다르면 실행하지 않는다.
**복사본 실행 시 출력도 복사된 폴더의 부모 경로에 생성되므로**, 스크립트가 표시하는 실제 출력 경로를 사용한다.
가능하면 A 방식으로 되돌려 저장소 하나를 원본으로 유지한다.

## 5. 단위와 시험 문서 [F2]
Fusion 화면의 mm 설정과 API의 내부 cm/radian 단위는 다르다.
제공 스크립트는 `10 mm`, `20 mm`, `5 mm`를 내부 단위로 변환해 XY 평면에 직사각형과 돌출을 만든다.
시험 결과는 X=10, Y=20, Z=5 mm, 부피=1000 mm³다.

- 기존 활성 문서를 수정하는 대신 새 디자인 문서를 생성한다.
- 형상 생성 후 bounding box·부피를 읽어 요구값과 비교한다.
- 재실행할 때 별도의 타임스탬프 출력 폴더를 사용한다.
- 원본 자동 닫기·삭제·클라우드 덮어쓰기를 수행하지 않는다.

## 6. 실행과 출력
Fusion에서 AgentSmokeTest를 선택해 **Run**을 누른다.
완료/실패 메시지의 **실제 출력 폴더**를 기록한다.
저장소 폴더를 직접 등록했다면 기본 출력은 다음 위치다.

```text
.local/fusion-smoke/<실행ID>/
  smoke.step
  smoke.stl
  smoke.f3d
  fusion-report.json
```

오류가 나면 `fusion-report.json`의 예외와 Fusion 버전을 확인한다.
코드 생성·구문 검사만 통과한 경우 실제 실행 성공으로 바꾸지 않는다.
출력 API의 라이선스/버전 제약으로 일부 형식이 실패하면 그 형식은 미완료로 기록한다 [F3–F5].

## 7. 독립 검증 및 슬라이서
```powershell
python .\scripts\verify_smoke.py --run-dir '.\.local\fusion-smoke\실제실행ID'
```

검증기는 STL 자체의 좌표를 읽어 mm 기준 10×20×5인지 확인한다.
STL에는 표준화된 단위 메타데이터가 없으므로 Fusion 보고서의 숫자만 신뢰하지 않는다.
크기가 10배/0.1배로 다르면 **실패**로 보고하고 내보내기/단위 설정을 수정해 다시 생성한다.
검증기가 STL 크기를 몰래 보정하지 않는다.

그다음 실제 장비의 공식 슬라이서 또는 사용 중인 슬라이서를 준비하고 프린터·노즐·재료를 확인한다.
`templates/print-requirements.md`를 채운다. 사용자의 프린터가 미확정이면 특정 프로파일을 임의 선택하지 않는다.
프로파일 적용과 경로 미리보기는 `docs/VALIDATION.md`에 따라 별도 확인한다.

## 8. 보고
`.local/setup-report.md`에 현재 실행 결과, 실제 Fusion 버전, 등록한 스크립트 경로,
STEP/STL/F3D 생성 및 검증 결과, 슬라이서 미완료 여부를 기록한다.
MCP를 추가하려면 기본 검증 후 `docs/OPTIONAL_MCP.md`를 따르며 별도 상태로 관리한다.
