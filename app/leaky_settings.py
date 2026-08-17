# gitleaks 실습용 '가짜' GitHub PAT입니다.
# 실제 토큰은 꼬리에 CRC 체크섬이 있지만 이 값은
# 무작위라 GitHub push protection은 통과하고,
# gitleaks 정규식(ghp_[0-9a-zA-Z]{36})에는 걸립니다.
# 실제 자격증명이 아니라 재사용할 수 없는 값입니다.
#
# 이 대입은 하드코딩 시크릿(Ruff S105)에도 걸립니다.
# Ruff에도 시크릿 인접 규칙이 있다는 걸 보여 주려고,
# 이 파일만 pyproject.toml에서 S105를 per-file-ignore로 끕니다.
GITHUB_TOKEN = "ghp_FAKEfake0000GITHUBpat0000gitleaks000"
