# 3D 모델링 작업 환경 구축 — Autodesk Fusion + Codex

**목적:** Codex Agent가 로컬 PC에 Fusion 기반 설계·스크립트 실행·출력 검증 환경을 구축하도록 한다.
3D 프린팅용 케이스·브래킷 설계가 목표이며, **Autodesk Fusion의 Python API**를 기본 자동화 경로로 사용한다.
작성/공식 문서 확인 기준일: **2026-09-15**.

## Codex에게 전달할 지시문
> AGENTS.md와 README.md를 읽고 docs/SETUP.md에 따라 이 PC의 Fusion 작업 환경을 구축하라.
> 실제 OS와 기존 Fusion/VS Code/Codex 설치를 먼저 점검하고 기존 모델·설정·라이선스를 보존하라.
> 공통 도구 설치와 스크립트 등록 준비는 자동화하고, Autodesk 로그인·라이선스·GUI 실행 등
> 사용자 개입이 필요한 단계만 구체적으로 안내하라.
> 새 시험 문서에서 AgentSmokeTest를 실행해 10×20×5 mm 형상, STEP/STL/F3D 출력,
> 독립적인 STL 치수 검증을 완료한 뒤 .local/setup-report.md에 실제 증거를 기록하라.
> 슬라이서/프린터 검증과 MCP 연결은 각각 별도 상태로 보고하라.

기본 문서는 **Windows 11 네이티브 로컬 실행**을 대상으로 한다.
사용자의 실제 운영체제나 Fusion 설치 여부가 이미 확인되었다는 뜻은 아니다.
macOS에서는 Autodesk 공식 설치와 실제 API 폴더를 따르고 Windows PowerShell 설치 스크립트는 사용하지 않는다.
Linux/WSL/cloud에서 Fusion GUI가 실행된 것으로 가정하지 않는다.

## 구성
| 파일 | 역할 |
|---|---|
| [AGENTS.md](AGENTS.md) | 에이전트 실행 규칙 |
| [docs/SETUP.md](docs/SETUP.md) | 공식 설치·인증·Python 스크립트 등록 |
| [docs/VALIDATION.md](docs/VALIDATION.md) | 치수·파일 출력·슬라이서 검증 기준 |
| [docs/OPTIONAL_MCP.md](docs/OPTIONAL_MCP.md) | 선택적 로컬 Fusion MCP 연결 |
| [fusion/AgentSmokeTest](fusion/AgentSmokeTest) | Fusion 내부에서만 실행하는 시험 스크립트 |
| [scripts/bootstrap.ps1](scripts/bootstrap.ps1) | 공통 도구 설치, Fusion 설치 자체는 제외 |
| [scripts/doctor.py](scripts/doctor.py) | OS·도구·API 폴더 후보 조사 |
| [scripts/verify_smoke.py](scripts/verify_smoke.py) | 실제 출력 STL의 독립적인 치수 검사 |
| [templates/print-requirements.md](templates/print-requirements.md) | 프린터·재료·공차·모델 요구사항 |
| [docs/SOURCES.md](docs/SOURCES.md) | 공식 근거와 버전 확인 범위 |

## 기본 명령
```powershell
.\scripts\bootstrap.ps1
.\scripts\bootstrap.ps1 -Apply
python .\scripts\doctor.py
```

Fusion은 **공식 Autodesk 설치 프로그램, 사용자 로그인, 유효한 사용 권한**을 거쳐야 한다.
미확인 WinGet ID, 추정한 무인 설치 옵션, 약관 자동 수락으로 이를 대체하지 않는다.
VS Code는 파일 편집 장소이며, `adsk` 기반 스크립트는 Fusion 내부에서 실행한다.
`python fusion/AgentSmokeTest/AgentSmokeTest.py`를 일반 터미널에서 실행하지 않는다.

## 완료 구분
`CAD_WORKSPACE_VERIFIED`: Fusion 실제 형상 생성과 STEP/STL/F3D 내보내기·치수 검증 완료.
`SLICER_PROFILE_VERIFIED`: 실제 프린터/노즐/재료에 맞춘 슬라이서 확인 완료.
두 상태를 구분한다. 시험 모델 생성만으로 실물 출력이나 강도가 검증되지는 않는다.
선택적 MCP를 설치하지 않아도 기본 Python API 경로는 사용할 수 있다.

## 이 패키지의 검증 상태
Python 구문과 STL 검증기 테스트는 이 저장소에서 검사할 수 있다.
**작성 환경에서는 실제 Windows/Fusion GUI 실행 및 사용자의 3D 프린터 출력을 수행하지 않았다.**
실제 결과는 로컬 에이전트가 새로운 실행 증거로 작성해야 한다.
