# 출처와 확인 범위

**문서 확인 기준일: 2026-09-15.** 설치 시점의 실제 배포 버전과 `--help`를 다시 확인한다.
이 목록은 문서/API 근거이며, 사용자의 PC에서 실행되었다는 증거가 아니다.
아래의 기본 경로는 공식 문서에 기반하며, 환경별 실제 경로가 우선한다.

| ID | 공식 문서 | 이 저장소에서의 용도 |
|---|---|---|
| O1 | [OpenAI — Codex on Windows](https://developers.openai.com/codex/windows) | 로컬 Windows 작업 환경과 격리 |
| O2 | [OpenAI — Codex IDE](https://developers.openai.com/codex/ide) | VS Code/로컬·클라우드 작업 구분 |
| O3 | [OpenAI 공식 VS Code 확장](https://marketplace.visualstudio.com/items?itemName=openai.chatgpt) | 정확한 확장 식별자 |
| O4 | [OpenAI — AGENTS.md](https://developers.openai.com/codex/guides/agents-md) | 에이전트 지침 읽기 |
| O5 | [OpenAI — MCP](https://developers.openai.com/codex/mcp) | 로컬 MCP 등록과 구성 |
| W1 | [Microsoft — WinGet install](https://learn.microsoft.com/en-us/windows/package-manager/winget/install) | 정확한 ID 설치, no-upgrade, 약관 옵션 |
| V1 | [Microsoft — VS Code CLI](https://code.visualstudio.com/docs/configure/command-line) | 확장 설치와 버전 조회 |

OpenAI 문서 URL은 공식 학습 문서 도메인으로 리디렉션될 수 있다.
WinGet의 패키지 ID는 실행 시 공식 카탈로그 조회로 검증하고, 불일치 시 설치하지 않는다.

## Autodesk Fusion
| ID | 공식 문서 | 용도 |
|---|---|---|
| F1 | [Creating a Script or Add-In / Writing and Debugging](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/WritingDebugging_UM.htm) | 스크립트 등록, 실행 위치, API 폴더 |
| F2 | [Understanding Units in Fusion](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Units_UM.htm) | 내부 cm/radian 단위 |
| F3 | [createSTEPExportOptions](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ExportManager_createSTEPExportOptions.htm) | STEP 내보내기 |
| F4 | [createSTLExportOptions](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ExportManager_createSTLExportOptions.htm) | STL 내보내기 |
| F5 | [createFusionArchiveExportOptions](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ExportManager_createFusionArchiveExportOptions.htm) | F3D 아카이브 |
| F6 | [ExtrudeFeatures.addSimple](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ExtrudeFeatures_addSimple.htm) | 시험 형상 돌출 |
| P1 | [Prusa — Configuration Wizard](https://help.prusa3d.com/article/configuration-wizard_1754) | 슬라이서 프린터/노즐/재료 설정 참고 |

P1은 슬라이서 구성 방법의 예시이며 PrusaSlicer를 필수로 설치하라는 뜻은 아니다.
사용자가 실제 사용할 장비의 공식 요구사항과 프로파일을 다시 확인한다.

## 선택적 제3자 MCP
| ID | 출처 | 한계 |
|---|---|---|
| M1 | [Fusion360 MCP Server README](https://github.com/faust-machines/fusion360-mcp-server/blob/main/README.md) | 제3자 베타, 무인증 로컬 TCP, 임의 코드 실행 도구 |

M1의 확인 당시 README blob SHA: `ce21b0d2ebfd6c744518f7094c4c3f5a3e56047f`.
이 SHA는 **README 내용의 식별자**이며 설치할 서버 릴리스나 커밋 pin이 아니다.
서버/애드인 설치는 별도 버전 검토·고정 후 수행한다.
