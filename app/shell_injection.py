"""shell=True 명령 실행(Ruff S602)이 걸리는 파일입니다.

사용자 입력을 셸 문자열에 이어 붙여 shell=True로
실행하면 명령 주입 통로가 열립니다.
(subprocess import 자체를 지적하는 S404도 있지만,
 Ruff 0.9.10에서는 preview라 기본 실행에서는 안 뜹니다.)
타입 주석이 없어 mypy는 조용합니다.
"""

import subprocess


def run_command(cmd):
    subprocess.run(cmd.split(), shell=False) # noqa: S603
