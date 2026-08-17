# _solution (정답 워크플로)

`.github/workflows/`의 스켈레톤에 대응하는 **완성본 워크플로**가 여기에 같은 파일명으로 들어 있습니다. 도구 실행 스텝과 이벤트 분기(`on:` / `concurrency` / `if:`)가 채워져 있고, 취약 코드 수리는 포함하지 않습니다.

| 파일 | 채워져 있는 것 |
|---|---|
| `01-ruff.yml` | Ruff format·lint 게이트, reviewdog 스텝의 PR 한정 조건 |
| `02-mypy.yml` | mypy 게이트 |
| `03-pytest.yml` | pytest + 커버리지 리포트, 코멘트 스텝의 `always()` + PR 한정 조건 |
| `04-pip-audit.yml` | 락파일 export + pip-audit 게이트 |
| `05-semgrep.yml` | Semgrep SARIF 생성 게이트, 업로드 스텝의 `always()` 조건 |
| `06-gitleaks.yml` | gitleaks 게이트 |
| `07-ci-summary.yml` | `on:` 네 이벤트와 cron, `concurrency`, 여섯 잡 호출과 `summary`, 그리고 도구 잡마다의 `if:` (변경 판정 + 예약 실행 분기) |

01~06은 `on: workflow_call`을 가진 재사용 워크플로이고, 07이 이벤트를 받아 여섯을 불러 모읍니다.

07의 `changes` 잡(문서만 바뀐 변경을 `git diff`로 걸러내는 부분)은 스켈레톤에도 완성된 채로 들어 있어 여기와 같습니다. 배관에 해당하는 부분이라, 그 판정을 어떻게 쓸지(`if:`)만 학습자의 몫으로 남겨 두었습니다.

## 쓰는 법

막혔을 때 스켈레톤과 정답을 비교합니다.

```bash
diff .github/workflows/01-ruff.yml _solution/workflows/01-ruff.yml
diff .github/workflows/07-ci-summary.yml _solution/workflows/07-ci-summary.yml
```

정답이 실제로 도는 것을 보고 싶으면, 해당 파일을 `.github/workflows/`로 복사하고 PR을 엽니다. 그러면 그 도구가 담당 파일을 빨간불로 잡아내는 것을 CI에서 확인할 수 있습니다.

`07-ci-summary.yml`은 `.github/workflows/`에 있는 01~06을 부릅니다. 07만 복사해 오면 아직 TODO가 남은 스켈레톤을 부르게 되므로, 07의 이벤트 설계와 여섯 도구를 함께 보려면 나머지도 같이 복사하면 됩니다.

이 폴더의 파일은 `.github/workflows/`에 있지 않아 GitHub Actions가 실행하지 않습니다. 참고용입니다.
