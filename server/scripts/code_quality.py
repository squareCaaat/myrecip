#!/usr/bin/env python3
"""
코드 품질 검사 스크립트
Black, isort, flake8을 사용하여 코드 품질을 검사하고 자동 수정합니다.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description, check=True):
    """명령어 실행 및 결과 출력"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"실행: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=check)

        if result.stdout:
            print(f"출력:\n{result.stdout}")

        if result.stderr:
            print(f"경고:\n{result.stderr}")

        if result.returncode == 0:
            print(f"{description} 완료")
        else:
            print(f"{description} 실패 (exit code: {result.returncode})")

        return result.returncode == 0

    except subprocess.CalledProcessError as e:
        print(f"{description} 실패: {e}")
        if e.stdout:
            print(f"출력:\n{e.stdout}")
        if e.stderr:
            print(f"에러:\n{e.stderr}")
        return False
    except FileNotFoundError:
        print(f"명령어를 찾을 수 없습니다: {command[0]}")
        print("필요한 패키지를 설치해주세요: pip install -r requirements-test.txt")
        return False


def check_dependencies():
    """필요한 도구들이 설치되어 있는지 확인"""
    print("의존성 검사 중...")

    dependencies = ["black", "isort", "flake8"]
    missing = []

    for dep in dependencies:
        try:
            subprocess.run([dep, "--version"], capture_output=True, check=True)
            print(f"{dep} 설치됨")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(dep)
            print(f"{dep} 설치되지 않음")

    if missing:
        print(f"\n누락된 의존성: {', '.join(missing)}")
        print("다음 명령어로 설치하세요:")
        print("pip install -r requirements-test.txt")
        return False

    return True


def format_code(target_dirs, fix=False):
    """코드 포맷팅 (Black + isort)"""
    results = []

    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            print(f"디렉터리가 존재하지 않습니다: {target_dir}")
            continue

        # Black 포맷팅
        black_cmd = ["black"]
        if not fix:
            black_cmd.extend(["--check", "--diff"])
        black_cmd.append(target_dir)

        black_result = run_command(
            black_cmd, f"Black 포맷팅 {'적용' if fix else '검사'} - {target_dir}", check=False
        )
        results.append(black_result)

        # isort import 정렬
        isort_cmd = ["isort"]
        if not fix:
            isort_cmd.extend(["--check-only", "--diff"])
        isort_cmd.append(target_dir)

        isort_result = run_command(
            isort_cmd,
            f"isort import 정렬 {'적용' if fix else '검사'} - {target_dir}",
            check=False,
        )
        results.append(isort_result)

    return all(results)


def lint_code(target_dirs):
    """코드 린팅 (flake8)"""
    results = []

    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            print(f"디렉터리가 존재하지 않습니다: {target_dir}")
            continue

        # 기본 flake8 검사
        flake8_cmd = [
            "flake8",
            target_dir,
            "--count",
            "--select=E9,F63,F7,F82",
            "--show-source",
            "--statistics",
        ]

        flake8_result = run_command(
            flake8_cmd, f"Flake8 기본 검사 - {target_dir}", check=False
        )
        results.append(flake8_result)

        # 상세 flake8 검사
        flake8_detailed_cmd = [
            "flake8",
            target_dir,
            "--count",
            "--exit-zero",
            "--max-complexity=10",
            "--max-line-length=88",
            "--statistics",
        ]

        flake8_detailed_result = run_command(
            flake8_detailed_cmd, f"Flake8 상세 검사 - {target_dir}", check=False
        )
        results.append(flake8_detailed_result)

    return all(results)


def run_tests(target_dirs):
    """테스트 실행"""
    results = []

    for target_dir in target_dirs:
        test_dir = os.path.join(target_dir, "tests")
        if not os.path.exists(test_dir):
            print(f"테스트 디렉터리가 존재하지 않습니다: {test_dir}")
            continue

        # pytest 실행
        pytest_cmd = [
            "pytest",
            test_dir,
            "-v",
            "--cov=" + os.path.join(target_dir, "app"),
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--cov-fail-under=80",
        ]

        pytest_result = run_command(pytest_cmd, f"테스트 실행 - {target_dir}", check=False)
        results.append(pytest_result)

    return all(results)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="코드 품질 검사 도구")
    parser.add_argument("--fix", action="store_true", help="코드 자동 수정 (Black, isort)")
    parser.add_argument("--no-test", action="store_true", help="테스트 실행 스킵")
    parser.add_argument(
        "--dirs",
        nargs="*",
        default=["user-service", "recipe-service", "api-gateway"],
        help="검사할 디렉터리 목록",
    )

    args = parser.parse_args()

    # 스크립트 실행 위치를 server 디렉터리로 설정
    server_dir = Path(__file__).parent.parent
    os.chdir(server_dir)

    print("칵테일 저장소 코드 품질 검사 도구")
    print(f"작업 디렉터리: {os.getcwd()}")
    print(f"대상 디렉터리: {', '.join(args.dirs)}")

    # 의존성 검사
    if not check_dependencies():
        sys.exit(1)

    all_passed = True

    # 1. 코드 포맷팅 검사/수정
    print(f"\n코드 포맷팅 {'수정' if args.fix else '검사'}")
    format_result = format_code(args.dirs, fix=args.fix)
    all_passed = all_passed and format_result

    # 2. 린팅 검사
    print(f"\n코드 린팅 검사")
    lint_result = lint_code(args.dirs)
    all_passed = all_passed and lint_result

    # 3. 테스트 실행 (옵션)
    if not args.no_test:
        print(f"\n테스트 실행")
        test_result = run_tests(args.dirs)
        all_passed = all_passed and test_result

    # 결과 요약
    print(f"\n{'='*60}")
    print("검사 결과 요약")
    print(f"{'='*60}")

    if all_passed:
        print("모든 검사를 통과했습니다!")
        sys.exit(0)
    else:
        print("일부 검사에 실패했습니다.")
        if not args.fix:
            print("--fix 옵션을 사용하여 자동 수정을 시도해보세요.")
        sys.exit(1)


if __name__ == "__main__":
    main()
