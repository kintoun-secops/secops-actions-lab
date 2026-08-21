# secops-actions-lab

fork해서 CI 파이프라인(GitHub Actions)을 PR 루프로 직접 조립해 보는 실습 레포입니다.
도구를 붙이고(조립), 빨간 PR을 막고(게이트), 결함을 하나씩 고치는(수리) 세 단계를 지나는 동안, 검증되지 않은 코드가 main으로 들어오는 길목이 어떻게 좁아지는지 따라가 볼 수 있습니다.

여기 도구는 두 가지 일을 합니다. 취약점·시크릿·CVE 같은 보안 결함을 찾는 쪽(Ruff S / Semgrep / gitleaks / pip-audit / Dependabot)과, 포맷·린트·타입·테스트로 코드의 일관성과 유지보수성을 챙기는 쪽(Ruff format·lint / mypy / pytest)입니다. 뒤쪽은 눈에 덜 띄지만 실용적입니다. 스타일이 한 가지로 고정되면 diff에 로직 변경만 남아, 리뷰가 로직에 집중되고 git 이력도 스타일 잡음 없이 읽힙니다.


## 빨간 CI의 의미

이 레포의 코드는 일부러 취약하게 짜여 있습니다. 처음 PR을 열면 도구 잡 여섯 개가 전부 빨간불이 되고 그 결과를 모으는 `summary` 잡도 함께 빨간불이 되는데, 각 도구가 자기 담당 결함을 검출했다는 뜻입니다. 1단계에서 빨간불은 검출이 작동하고 있다는 신호에 가깝습니다. 초록불은 3단계에서 결함을 하나씩 고쳐 나가며 얻게 됩니다.


## 이벤트별 역할

파이프라인의 입구는 `.github/workflows/07-ci-summary.yml` 하나입니다. 01~06은 도구 하나씩을 담당하는 재사용 워크플로가 되었고, 07이 이벤트를 받아 그 여섯을 불러 모읍니다. 이벤트마다 목적이 다르므로 도는 범위와 남는 리포트도 갈립니다.

| 이벤트 | 목적 | 도는 것 | 문서만 바뀐 경우 |
|---|---|---|---|
| `pull_request` | 빠른 피드백 | 여섯 도구 전부 | 도구 잡을 전부 건너뜁니다 |
| `push` (main) | 기준선 확립 | 여섯 도구 전부 | 도구 잡을 전부 건너뜁니다 |
| `schedule` (주 1회) | 시간에 대한 방어 | pip-audit과 Semgrep | 판정하지 않고 늘 돕니다 |
| `workflow_dispatch` | 수동 확인 | 여섯 도구 전부 | 판정하지 않고 늘 돕니다 |

PR과 main 푸시는 도는 도구가 같습니다. 갈리는 지점은 세 곳입니다.

- **코멘트 채널**: reviewdog 인라인 리뷰와 커버리지 스티키 코멘트는 PR에만 붙습니다. 붙을 PR이 있어야 의미가 있는 리포트라, main 푸시에서는 해당 스텝이 건너뛰어집니다.
- **SARIF의 의미**: 두 이벤트 모두 코드 스캐닝에 결과를 올리지만 읽히는 방식이 다릅니다. main 업로드가 기본 브랜치의 기준선이 되고, PR 업로드는 그 기준선과의 차이로 읽혀 PR에 알림으로 붙습니다. 기준선이 아직 없으면 PR 결과가 전부 신규로 보입니다.
- **실행 취소**: PR은 최신 커밋의 결과만 의미가 있어 `concurrency`가 앞선 실행을 버리고, main 기준선 실행은 SARIF가 올라갈 때까지 끝까지 돕니다.

문서만 고친 변경에서는 도구 잡이 전부 건너뛰어집니다. 07의 `changes` 잡이 `git diff --name-only`로 바뀐 파일을 뽑고, 마크다운·`LICENSE`·`.gitignore`·`_solution/`을 걷어내고도 남는 것이 있는지로 판정합니다. `_solution/`이 제외에 든 것은 그 폴더가 정답 문서이지 검사 대상 코드가 아니기 때문입니다. 이 판정은 `pull_request`와 `push`에만 걸립니다. 예약 실행과 수동 실행에는 비교할 이전 상태가 없어, 지정된 몫을 그대로 돕니다.

예약 실행은 코드가 아니라 바깥이 변하는 쪽을 봅니다. 어제 초록이던 커밋이 오늘 빨간불이 되는 경우가 있는데, 커밋은 그대로고 새 CVE가 공개되었거나 Semgrep 룰이 갱신된 것입니다. 포맷·타입·테스트·시크릿은 코드가 그대로면 결과도 그대로라 매주 다시 돌려도 새로 알게 되는 것이 없어, 예약 실행에서는 빠져 있습니다.

`.github/dependabot.yml`의 주간 갱신도 같은 축에 있습니다. 예약 스캔은 "지금 쓰는 버전이 위험해졌다"를 알리고, Dependabot은 "올릴 버전이 나왔다"를 PR로 가져옵니다. 3단계의 pip-audit 수리에서 둘을 함께 쓰게 됩니다.

cron은 UTC로 읽습니다. 07의 `'30 20 * * 0'`은 매주 일요일 20:30 UTC, 한국 시간으로 월요일 05:30입니다. 정시(00분)에는 실행이 몰려 지연이 잦아 어중간한 분에 두었습니다. 예약 실행은 기본 브랜치에 있는 워크플로 정의로만 돌고, 러너가 붐빌 때는 예정 시각보다 늦게 시작하기도 합니다.


## 체크 하나로 모으기

`needs:`는 같은 워크플로 파일 안의 잡끼리만 걸립니다. 01~06이 각자 트리거되어 따로 도는 동안에는 "여섯이 전부 끝났는지"를 판정할 방법이 없습니다. 파일을 넘나드는 `needs:`를 찾다 막히는 경우가 흔합니다.

`workflow_run` 이벤트로 다른 워크플로의 완료를 받을 수는 있습니다. 다만 이 이벤트는 기본 브랜치에 있는 정의로만 돌고 그 결과가 PR에 체크로 붙지 않아, PR을 막는 게이트로는 쓰이지 못합니다.

그래서 01~06은 `on: workflow_call`을 가진 재사용 워크플로가 되고, 07이 `uses:`로 여섯을 불러옵니다. 불려 온 잡은 07의 실행 그래프 안으로 들어오므로 `needs:`가 걸리고, 마지막 `summary` 잡이 여섯의 결과를 모아 표(도구 / 결과 / 담당 파일)를 `$GITHUB_STEP_SUMMARY`에 쓴 뒤 하나라도 실패했으면 exit 1이 됩니다. 도구 정의는 01~06에 한 벌만 남아 중복도 생기지 않습니다.

01~06에는 `workflow_dispatch`가 남아 있어 Actions 탭에서 도구 하나만 따로 돌려 볼 수 있습니다. `pull_request`·`push`·`schedule`은 07에만 두는데, 양쪽에 두면 같은 커밋에 체크가 두 벌 붙기 때문입니다.

### 건너뛰기와 보고하지 않기

필수 상태 체크를 하나로 모으고 나면 그 체크가 어떤 PR에서도 보고된다는 조건이 함께 따라옵니다. 문서만 바뀐 PR에서 도구를 건너뛰려고 워크플로 맨 위 `on:`에 `paths-ignore:`를 얹으면 그 조건이 깨집니다. `paths-ignore:`는 워크플로 실행 자체를 만들지 않으므로 `summary` 체크가 보고되지 않고, PR은 "Expected — Waiting for status to be reported"에 멈춘 채 머지되지 않습니다.

잡을 건너뛰는 것과 체크를 보고하지 않는 것은 다른 상태입니다. 건너뛴 잡은 결과가 `skipped`로 남아 필수 체크를 통과시키지만, 실행되지 않은 워크플로에는 통과시킬 결과 자체가 없습니다. 그래서 07은 걸러내는 조건을 워크플로가 아니라 잡에 둡니다. `summary`는 `if: always()`로 언제나 돌아 체크를 보고하고, 도구 잡만 `changes` 잡의 판정에 걸립니다. 문서만 바뀐 PR은 여섯 줄이 모두 '건너뜀'인 요약 표와 함께 초록으로 끝납니다.


## 실습의 3단계 구조

### 0단계. 준비

1. 이 레포를 fork 합니다.
2. `git clone` 후 `uv sync` 로 환경을 맞춥니다. (uv 설치는 https://docs.astral.sh/uv/ 참고)
3. 워크플로를 채우기 전에 아래 [로컬에서 먼저 돌리기](#로컬에서-먼저-돌리기)로 각 도구를 손으로 한 번씩 돌려 보면, 도구가 무엇을 어떻게 출력하는지 감이 잡힙니다.

### 1단계. 조립 (검출)

- 브랜치를 하나 만들고 `.github/workflows/*.yml` 의 TODO를 공식 문서를 참고해 채웁니다. TODO는 두 종류입니다.
  - **도구 실행** (01~06): 도구를 부르는 스텝이 비어 있습니다. checkout / setup-uv / `uv sync --frozen` 은 채워져 있습니다.
  - **이벤트 분기** (07 그리고 01·03·05): `on:` 트리거와 `concurrency`, 그리고 스텝과 잡의 `if:` 조건이 비어 있습니다. 실행 명령은 이미 들어 있어, 채울 것은 실행 조건입니다. 07의 `changes` 잡은 배관이라 완성된 채로 들어 있고, 그 판정을 도구 잡의 `if:`에 어떻게 엮을지가 과제입니다.
- PR을 열면 도구 잡 여섯 개와 `summary`가 빨간불이 되고, 커버리지 스티키 코멘트가 붙고, Security 탭에 SARIF 알림이 뜹니다. 채점표는 `_solution/workflows/`의 완성본과 대조하면 됩니다.
- 그런 다음 그 PR을 그대로 머지해 봅니다. 빨간불인데도 머지가 되는데, 아직 게이트가 없기 때문입니다. 이 지점이 2단계의 출발점입니다.

### 2단계. 게이트

- Settings -> Rules -> Rulesets(또는 Branch protection)에서 required status checks 를 설정합니다. 등록할 것은 `summary` 하나입니다.
- 도구 체크를 여섯 개 따로 등록해도 결과는 같지만, 워크플로를 하나 늘릴 때마다 룰셋을 다시 손봐야 합니다. 07이 여섯을 모아 두면 새 도구는 07에 잡 하나를 더하는 것으로 끝나고, 게이트 설정은 그대로입니다.
- fork에는 원본의 규칙이 자동으로 따라오지 않습니다. 게이트를 직접 세워 보는 것이 이 단계의 몫입니다.
- 이제 빨간 PR은 머지되지 않습니다. "안전한 코드만 main에"가 여기서부터 강제됩니다.
- 게이트를 세운 뒤 README만 한 줄 고친 PR을 하나 열어 보면, 도구 잡이 전부 '건너뜀'인 채로 `summary`가 초록이 되어 머지가 열립니다. `paths-ignore:`가 왜 같은 결과를 내지 못하는지는 위 [건너뛰기와 보고하지 않기](#건너뛰기와-보고하지-않기)에 적어 두었습니다.

### 3단계. 수리 루프

수리는 **브랜치 하나에 커밋을 쌓는 방식**으로 진행합니다. 게이트로 쓰는 `summary`는 여섯이 모두 초록일 때만 초록이 되므로, 도구마다 PR을 따로 열면 어느 PR도 머지되지 않습니다. 수리용 브랜치를 하나 만들어 PR을 열어 두고, 그 위에 커밋을 하나씩 올리는 흐름이 게이트와 맞물립니다.

```bash
git switch -c fix/repair-loop
```

브랜치를 만들고 PR을 하나 엽니다. 이 PR은 수리가 끝날 때까지 열어 둡니다.

- **커밋 하나에 도구 하나**를 고치고 push 합니다. push할 때마다 07이 다시 돌고, 잡 요약 표에서 '통과'가 한 줄씩 늘어납니다. 표가 그대로 진척판이 됩니다.
- 여섯이 모두 통과로 바뀌면 `summary`가 초록이 되고 그때 머지가 열립니다. 커밋 히스토리에는 도구별 수리가 한 단계씩 남습니다.
- 이미 초록인 잡은 회귀 감시자 역할을 합니다. semgrep을 고치다 ruff를 깨면 다음 push에서 ruff가 그 자리에서 잡아냅니다. 같은 PR 안에서 계속 돌기 때문에 회귀가 바로 드러납니다.
- push를 연달아 하면 `concurrency` 설정 덕분에 앞선 실행이 취소됩니다. 2단계까지 채운 `cancel-in-progress`가 실제로 동작하는 것을 여기서 볼 수 있습니다.
- 코드를 건드리는 커밋이 쌓이므로 reviewdog 인라인 코멘트도 이 단계에서 제 역할을 합니다. 변경한 줄에 지적이 직접 달립니다.

수리 순서 예시: pytest(버그) -> mypy -> ruff lint -> ruff S(md5/pickle/shell) -> taint(파라미터 바인딩) -> 시크릿(로테이션 + `.gitleaksignore`) -> pip-audit(핀 업그레이드 + constraint 제거, Dependabot PR 관찰).


## 로컬에서 먼저 돌리기

여기 도구는 Dependabot 하나를 빼면 전부 로컬에서 먼저 돌아갑니다. CI에서 처음 만나면 PR을 열고 결과를 기다렸다 고치는 왕복이 반복되므로, 커밋 전에 손으로 돌려 보는 편이 빠릅니다. 아래 명령은 이 레포에서 실제로 실행해 본 것이고, 괄호 안은 그때 나온 결과입니다.

### 네이티브로 도는 것 (Windows / macOS / Linux 공통)

```bash
uv run ruff check app/
```

린트와 보안 규칙을 함께 봅니다. (13건: `lint_playground.py` 7건, `insecure_hash.py` S324, `shell_injection.py` S602, `unsafe_pickle.py` S301, `sqli_fstring.py` S608)

```bash
uv run ruff check app/ --output-format=concise
```

한 줄에 하나씩 나옵니다. 자동 수정이 가능한 항목은 `--fix`로 고칠 수 있습니다.

```bash
uv run ruff check app/ --statistics
```

`S608` 같은 코드가 안 읽힐 때 씁니다. 코드 옆에 이름을, 앞에 건수를, `[*]`로 자동 수정 여부를 함께 보여 줍니다. (코드와 이름 대조는 아래 [매핑 테이블](#매핑-테이블) 참고)

```bash
uv run ruff format --check .
```

포맷이 어긋난 파일을 찾기만 합니다(고치지는 않음). CI에서는 이 검사가 실패하면 PR이 빨간불이 되어 머지가 막힙니다. (`messy_format.py` 1건)

```bash
uv run ruff format .
```

실제로 정리합니다. 홑따옴표를 겹따옴표로 맞추는 식으로 스타일을 한 가지로 통일해, 이후 diff에는 로직 변경만 남습니다. 무엇이 바뀌는지 미리 보려면 `--diff`를 붙입니다.

```bash
uv run mypy app/
```

정적 타입 검사입니다. (`type_confusion.py`에서 `return-value`, `arg-type` 2건)

```bash
uv run pytest
```

회귀 테스트입니다. (`test_bulk_discount_applies_at_exactly_ten` 1건 실패 — `order_total(10)`이 9000이어야 하는데 10000을 돌려줍니다)

```bash
uv run pytest --cov=app --cov-report=term-missing
```

커버리지까지 봅니다. CI의 스티키 코멘트가 보여 주는 것과 같은 정보입니다.

```bash
uv export --format requirements-txt --no-emit-project -o requirements.txt
```

락파일에서 전이 의존성까지 고정된 목록을 뽑습니다.

```bash
uvx pip-audit -r requirements.txt --no-deps
```

의존성 CVE 감사입니다. (5개 패키지 18건 — 이 중 `werkzeug`는 `pyproject.toml`의 `dependencies`에 없는데도 7건이 뜹니다. flask가 끌어온 전이 의존성이라 그렇습니다. 락파일을 스캔하면 이런 항목까지 들어옵니다)

### Docker가 필요한 것 (Semgrep, gitleaks)

두 도구는 Windows 네이티브 실행이 없습니다. CI가 쓰는 이미지를 그대로 돌리면 결과도 CI와 맞습니다. (macOS/Linux라면 `pip install semgrep`, `brew install gitleaks`로 네이티브 설치도 됩니다.)

```bash
docker run --rm -v "${PWD}:/src" -w /src semgrep/semgrep semgrep scan --config .semgrep/rules.yml --error
```

이 레포의 커스텀 taint 룰만 돌립니다. (`sqli_taint_only.py:24`에서 `lab-taint-sql-concat` 1건. `--error`가 붙어 발견이 있으면 exit 1이라 CI 게이트와 같게 동작합니다)

```bash
docker run --rm -v "${PWD}:/src" -w /src semgrep/semgrep semgrep scan --config p/python --config .semgrep/rules.yml --error
```

레지스트리 팩까지 포함한 전체 스캔입니다. (152개 룰 실행, `.semgrepignore`가 파일 4개 스킵, 발견 2건 — 둘 다 `sqli_taint_only.py` 한 파일에 뜹니다)

2건 중 하나는 우리가 쓴 `lab-taint-sql-concat`이고, 다른 하나는 팩에 원래 있는 `python.flask.security.injection.tainted-sql-string`입니다. 잘 만든 팩에는 taint 룰이 이미 들어 있는 경우가 많아, 룰을 직접 쓰기 전에 팩을 먼저 돌려 보면 중복을 줄일 수 있습니다. 그래도 이 레포에 커스텀 룰을 둔 이유는 두 가지입니다. 레지스트리 내용이 바뀌어도 이 레슨의 검출이 유지되도록 고정해 두는 것, 그리고 taint 룰의 source/sink/sanitizer 구조를 직접 읽어 보게 하는 것입니다.

```bash
docker run --rm -v "${PWD}:/repo" zricethezav/gitleaks:latest detect --source /repo -v
```

히스토리 스캔입니다. CI의 gitleaks-action과 같은 일을 합니다. (`github-pat` + `private-key` 2건, 각각 핑거프린트가 함께 나옵니다 — `.gitleaksignore`에 넣을 값이 이것입니다)

```bash
docker run --rm -v "${PWD}:/repo" zricethezav/gitleaks:latest detect --source /repo --no-git -v
```

워킹트리 스캔입니다. 아직 커밋하지 않은 파일까지 봅니다. 아래 "gitleaks 검출의 두 가지 함정"에서 보듯 두 모드의 결과가 갈릴 수 있어, 커밋 전에는 이쪽도 함께 돌려 두면 놓치는 경우가 줄어듭니다.

### 포맷을 로컬에서 자동으로 맞추기

포맷 검사는 대개 CI에서 실패하면 머지를 막는 게이트로 씁니다(이 레포도 그렇습니다). 그런데 CI에서 빨간불을 보고 나서 포맷을 고치면 왕복이 생기므로, 로컬에서 저장·커밋 시점에 자동으로 맞춰 두면 애초에 CI에서 막힐 일이 없습니다. 보통 세 겹으로 둡니다.

**1. 에디터 저장 시 자동 포맷 (첫 번째 겹).** VS Code는 Ruff 확장(`charliermarsh.ruff`)을 설치하고 `settings.json`에 아래를 넣으면 저장할 때마다 포맷이 맞춰집니다.

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff"
}
```

PyCharm은 Ruff 플러그인(2024.2+는 내장)에서 "저장 시 ruff format 실행"을 켜면 같은 효과가 납니다.

**2. 커밋 훅 (두 번째 겹).** 에디터 설정을 안 한 사람이 있어도, `pre-commit`으로 `ruff-format`을 걸면 포맷이 어긋난 커밋이 만들어지기 전에 자동으로 정리됩니다.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.10
    hooks:
      - id: ruff-format          # 포맷 자동 정리
      - id: ruff-check           # 린트 검사
        args: [--fix]            # 자동 수정 가능한 린트는 고침
```

```bash
uvx pre-commit install
```

훅에는 빠른 것만 거는 편이 오래갑니다. mypy·pytest·Semgrep처럼 수 초 이상 걸리는 도구를 훅에 넣으면 `--no-verify`를 쓰는 습관이 생기고, 그러면 훅 전체가 힘을 잃습니다. 느린 검사는 CI에 맡기고, 훅은 1초 안에 끝나는 위생 점검(ruff)으로 두는 구성이 흔합니다.

**3. CI (마지막 겹).** 앞의 둘을 건너뛴 변경이 올라와도 워크플로의 `ruff format --check`가 PR을 빨간불로 막습니다. 로컬 자동화는 편의고, CI 게이트는 최종 안전망입니다.


## 매핑 테이블

파일 하나가 도구 하나에만 걸리도록 구성돼 있습니다. 어떤 체크가 울리면 파일 이름이 그대로 레슨을 가리킵니다. 규칙은 코드보다 이름이 먼저 읽히도록 `문자열 조립 SQL(S608)`처럼 자연어를 앞세우고 코드는 괄호에 넣었습니다. 코드는 검색용 열쇠 정도로 보면 됩니다.

| 파일 | 도구 | 걸리는 규칙 (자연어 + 코드) |
|---|---|---|
| `app/messy_format.py` | Ruff (format) | 포맷 스타일 불일치 — 홑따옴표 등 (ruff format --check) |
| `app/lint_playground.py` | Ruff (E/F/I/UP/B/SIM) | 위생 린트 7종 — None 비교(E711), 미사용 import(F401), import 미정렬(I001), 구식 타입 표기(UP006), 폐기된 import(UP035), 가변 기본 인자(B006), 중첩 if(SIM102) |
| `app/insecure_hash.py` | Ruff (S) | 취약 해시 md5(S324) |
| `app/shell_injection.py` | Ruff (S) | shell=True 명령 실행(S602) |
| `app/unsafe_pickle.py` | Ruff (S) | 신뢰 불가 pickle 역직렬화(S301) |
| `app/sqli_fstring.py` | Ruff (S) | 문자열 조립 SQL(S608) — 패턴 매칭이 잡는 대조군 |
| `app/sqli_taint_only.py` | Semgrep (taint) | 데이터 흐름 SQLi(lab-taint-sql-concat) — 센터피스, S608은 지나침 |
| `app/type_confusion.py` | mypy | 반환 타입 오류(return-value) + 인자 타입 오류(arg-type) |
| `app/price_logic.py` | pytest | 경계값(off-by-one) 로직 버그 — 테스트 1건 실패 |
| `app/leaky_settings.py` | gitleaks | 가짜 GitHub PAT(github-pat) — Ruff S105는 억제 |
| `deploy/fake_deploy_key.pem` | gitleaks | 가짜 RSA 키(private-key) |

> 위 규칙은 핀된 도구 버전(`ruff==0.9.10`, `mypy==1.15.0`)으로 실제 돌려 확인한 값입니다. 도구 버전이 다르면 세부 코드가 조금 달라질 수 있습니다.

괄호 안 코드를 더 보고 싶으면 터미널에서 펼칠 수 있습니다.

```bash
uv run ruff check app/ --statistics   # 코드 + 이름 + 건수
uv run ruff rule S608                 # 규칙 하나를 이름·이유·예시까지
```

접두사가 출신 린터를 가리킵니다. `E`/`W`는 pycodestyle, `F`는 pyflakes, `I`는 isort, `UP`은 pyupgrade, `B`는 flake8-bugbear, `SIM`은 flake8-simplify, `S`는 flake8-bandit(보안)입니다. 그래서 `S`로 시작하면 보안 규칙입니다. 전체 목록: https://docs.astral.sh/ruff/rules/

> **버전에 따라 갈리는 예:** `import subprocess`(S404)와 `import pickle`(S403)은 flake8-bandit에는 있지만 Ruff 0.9.10에서는 preview라 기본 실행에서 뜨지 않습니다. 그래서 위 표에는 실제로 뜬 S602·S301만 적었습니다. `--preview`를 붙이면 보입니다. 문서에 실린 규칙과 지금 설정에서 도는 규칙이 늘 같지는 않다는 점도 여기서 드러납니다.

### 도구 간 격리 방식

- **mypy**: 취약 코드는 타입 주석 없는 함수 안에 둡니다. 기본 설정(`check_untyped_defs=false`)이 그 본문을 건너뛰므로, 주석 있는 함수와 모듈 레벨 호출을 가진 `type_confusion.py`만 2건을 냅니다.
- **Ruff**: 나머지 파일은 정렬된 import에 unused도 없어 자연히 조용합니다. `leaky_settings.py`만 `S105`를 per-file-ignore로 끄는데, Ruff에도 시크릿 인접 규칙이 있다는 걸 보여 주려고 남겨 둔 설정입니다.
- **Semgrep**: `.semgrepignore`로 Ruff-S가 맡는 파일 4개를 뺍니다. `p/python` 팩이 bandit 계열과 겹쳐 같은 결함을 두 번 리포트하는 건 실제로 일어나는 일이고, 여기서는 학습을 위해 눌러 둔 것입니다.
- **gitleaks**: 나머지 파일에는 키워드 인접 고엔트로피 문자열이 없습니다.


## 패턴 매칭과 taint 분석의 검출 범위 차이

패턴 매칭(Ruff S608 / bandit B608)은 문자열 조립 지점에 SQL 키워드 리터럴이 있을 때 발화합니다.

**`sqli_fstring.py` (대조군 — S608 발화):**

```python
cur.execute(f"SELECT * FROM users WHERE name = '{name}'")
#            └ 조립 지점 리터럴에 SELECT 키워드가 그대로 있음 -> 매칭
```

**`sqli_taint_only.py` (센터피스 — S608 침묵):**

```python
q = request.args.get("q")
prefix = "SELECT * FROM users WHERE name LIKE '%"   # 순수 리터럴 대입 -> 미검사
query = prefix + q + "%'"                            # (prefix + q) + "%'"
cur.execute(query)                                   # 조립식의 유일한 리터럴은 "%'" -> 키워드 없음
```

- SQL 키워드가 든 문자열이 `prefix`에 먼저 담기고, 실제 조립(`prefix + q + "%'"`)에는 SQL 키워드 리터럴이 없습니다. 그래서 S608은 이 파일을 지나칩니다.
- 이 흐름은 데이터 흐름(taint)을 따라가는 Semgrep 커스텀 룰(`.semgrep/rules.yml`)이 잡습니다. 사용자 입력(`request.args.get`)이 source, `cursor.execute(...)`가 sink이고, 그 사이로 값이 흐르면 문자열 조립을 거쳐도 발화합니다.
- 패턴 매칭은 빠르고 가볍지만 표면의 모양을 봅니다. taint는 느린 대신 값의 여정을 따라갑니다. 같은 SQLi를 두 도구가 서로 다른 층위에서 봅니다.


## 도구별 공식 문서

- **Ruff** (린트 + 보안 규칙): https://docs.astral.sh/ruff/linter/ · https://docs.astral.sh/ruff/rules/
- **mypy** (정적 타입): https://mypy.readthedocs.io/en/stable/command_line.html
- **pytest** (회귀 테스트): https://docs.pytest.org/en/stable/how-to/usage.html
- **pytest-coverage-comment** (커버리지 스티키 코멘트): https://github.com/MishaKav/pytest-coverage-comment
- **pip-audit** (의존성 CVE): https://github.com/pypa/pip-audit
- **uv export** (락파일 -> requirements): https://docs.astral.sh/uv/reference/cli/#uv-export
- **Semgrep** (SAST + taint): https://semgrep.dev/docs/semgrep-ci/sample-ci-configs · https://semgrep.dev/docs/writing-rules/data-flow/taint-mode
- **upload-sarif** (코드 스캐닝): https://github.com/github/codeql-action
- **gitleaks-action** (시크릿 스캔): https://github.com/gitleaks/gitleaks-action
- **reviewdog** (PR 인라인 리뷰): https://github.com/reviewdog/reviewdog
- **Dependabot**: https://docs.github.com/code-security/dependabot
- **Rulesets** (필수 상태 체크): https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets

### GitHub Actions 문서

- **이벤트 목록** (워크플로를 트리거하는 것들): https://docs.github.com/actions/reference/workflows-and-actions/events-that-trigger-workflows
- **cron 구문 / schedule**: https://docs.github.com/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- **워크플로 문법** (`concurrency` 포함): https://docs.github.com/actions/reference/workflows-and-actions/workflow-syntax
- **컨텍스트** (`github`, `needs` 등): https://docs.github.com/actions/reference/contexts-reference
- **표현식과 상태 확인 함수** (`always()` 등): https://docs.github.com/actions/reference/evaluate-expressions-in-workflows-and-actions
- **재사용 워크플로** (`workflow_call`): https://docs.github.com/actions/sharing-automations/reusing-workflows
- **잡 요약** (`$GITHUB_STEP_SUMMARY`): https://docs.github.com/actions/reference/workflows-and-actions/workflow-commands#adding-a-job-summary
- **GITHUB_TOKEN 권한**: https://docs.github.com/actions/how-tos/write-workflows/choose-what-workflows-do/control-permissions-for-github_token

여기서 다루지 않은 다음 걸음으로는 matrix(여러 버전·OS 동시 실행), artifacts(실행 결과물 보관), caching(의존성 재사용)이 있습니다.


## 정답: _solution 폴더

정답은 `_solution/workflows/` 폴더에 있습니다. `.github/workflows/`의 각 스켈레톤에 대응하는 완성본이 같은 파일명으로 들어 있습니다(코드 수리는 없고, 도구 실행 스텝과 이벤트 분기만 채워져 있습니다).

막혔을 때 스켈레톤과 정답을 비교하려면:

```bash
diff .github/workflows/01-ruff.yml _solution/workflows/01-ruff.yml
diff .github/workflows/07-ci-summary.yml _solution/workflows/07-ci-summary.yml
```

차이는 도구 실행 스텝과 `on:`·`concurrency`·`if:` 뿐입니다. 먼저 스스로 채워 본 다음 맞춰 보면 됩니다. 정답이 실제로 도는 걸 보고 싶으면 `_solution/workflows/`의 파일을 `.github/workflows/`로 복사하고 PR을 열면 됩니다. 그러면 그 도구가 담당 파일을 빨간불로 잡아내는 것을 CI에서 확인할 수 있습니다.

### 리뷰 채널별 특성

- **reviewdog(인라인)**: `github-pr-review` 리포터는 PR diff에 든 줄에만 인라인 코멘트를 답니다. 그래서 워크플로만 바꾸는 1단계 PR에서는 인라인이 잘 안 뜨고, 코드를 건드리는 3단계 fix PR에서 제 역할을 합니다. PR이 리뷰하는 대상이 변경분이라는 점이 여기서 드러납니다.
- **pip-audit `--no-deps`**: `uv export`가 이미 완전히 고정된 전이 폐포를 뽑으므로, 그 목록을 그대로 감사합니다.
- **Semgrep `--error`**: 발견이 있으면 exit 1로 게이트가 빨개집니다.
- **gitleaks-action v2**: 개인(user) 계정 레포는 무료입니다. org 레포라면 바이너리를 직접 받아 `gitleaks detect`로 대신할 수 있습니다.
- **액션 버전 핀**: 이 레포는 `@v4`, `@v5` 같은 메이저 태그를 씁니다. 공급망 관점에서는 커밋 SHA로 고정하는 편이 더 엄격하고, `.github/dependabot.yml`의 `github-actions` 항목이 그 갱신을 돕습니다.


## 안전상 유의사항

- 여기 담긴 가짜 시크릿(`app/leaky_settings.py`의 PAT, `deploy/fake_deploy_key.pem`의 RSA 키)은 교육용 무효값입니다. 실제 자격증명이 아니라 재사용할 수 없습니다.
- 취약한 의존성 핀(flask/jinja2/requests/werkzeug 구버전)도 CVE를 재현하려고 일부러 고정한 값이라, 실제 프로젝트로 가져가면 그 취약점을 함께 들고 가게 됩니다.
- 이 레포는 실무 파이프라인의 축소 모형입니다.
- gitleaks 수리에 관해: full-history 스캔이라 파일을 지워도 과거 커밋에 남아 있으면 계속 잡힙니다. 실제라면 값을 즉시 로테이션(무효화)하는 것이 먼저고, 스캐너에는 `.gitleaksignore`에 핑거프린트를 적어 알립니다. 히스토리 재작성은 강력하지만 협업 중에는 다른 사람의 클론을 깨뜨립니다.

## 라이선스

MIT License. 자세한 내용은 [`LICENSE`](./LICENSE)를 참고하세요.
테스트 코멘트
