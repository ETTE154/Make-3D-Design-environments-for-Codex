# 공통 문제 해결 및 복구

## Codex가 CAD를 찾지 못함
에이전트가 실제 CAD가 설치된 PC에서 실행 중인지 먼저 확인한다. 클라우드/컨테이너/WSL에서
Windows GUI나 해당 환경의 PATH를 발견하지 못하는 것은 단순 설치 누락과 다르다.
네이티브 Windows용 Codex IDE/CLI 세션으로 옮긴다. 로컬 연결이 없으면 GUI 단계는 차단 상태로 남긴다.

## winget 또는 Python이 없음
`Get-Command winget -ErrorAction SilentlyContinue`, `Get-Command python,py -ErrorAction SilentlyContinue`로 확인한다.
winget이 없으면 Microsoft의 App Installer/WinGet 공식 안내를 이용한다. 관리형 PC 정책은 우회하지 않는다.
Python은 이미 있는 정상 CPython 3.10 이상을 우선 재사용한다. Windows Store 실행 별칭은 실제 인터프리터가 아니다.
설치 직후에는 새 PowerShell/VS Code 창을 열어 PATH를 다시 불러온다.

## PowerShell 실행 정책 차단
스크립트를 먼저 검토하고, 신뢰하는 다운로드 파일의 차단 표시만 `Unblock-File`로 해제할 수 있다.
기관 정책이 차단한다면 관리자에게 허용을 요청한다. `Set-ExecutionPolicy Unrestricted`나 영구 Bypass는 하지 않는다.
설치 스크립트는 관리자 셸 전체 실행을 전제로 하지 않는다. 개별 설치가 UAC를 요구할 수 있다.

## VS Code의 code 명령이 없음
기존 설치 경로를 먼저 확인한다. 새 터미널을 열거나 VS Code Extensions에서
OpenAI가 게시한 `openai.chatgpt`를 설치한다. 식별자가 비슷한 제3자 확장으로 대체하지 않는다.
CLI만 사용할 경우 VS Code/확장은 필수가 아니다. `-SkipEditor`로 제외하고 그 이유를 기록한다.

## 재실행·일부 실패
bootstrap은 발견한 기존 프로그램을 건너뛰고, 설치 결과와 후속 진단을 별도로 기록한다.
실패 뒤 반복적인 재설치/삭제를 하지 않는다. 실패한 단계의 반환 코드와 원인을 먼저 확인한다.
로그의 이전 성공 기록을 새 실행의 성공으로 재사용하지 않는다.

## 원복
새로 추가한 확장/패키지만 변경 로그에 따라 제거할 수 있다. 기존 설치까지 제거하지 않는다.
사용자 설정은 백업과 현재 상태를 비교해 바뀐 키만 복원한다. CAD/라이브러리 폴더 통째 삭제는 금지한다.
MCP 연결을 추가했다면 서버 등록 해제와 애드인 중지부터 하고, 리뷰된 설치 폴더만 제거한다.
