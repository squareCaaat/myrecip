"""
테스트 실행 스크립트
개발자가 로컬에서 테스트를 쉽게 실행할 수 있도록 돕는 스크립트
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(command, description, cwd=None, env=None):
    """명령어 실행 및 결과 출력"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"실행: {' '.join(command)}")
    if cwd:
        print(f"작업 디렉터리: {cwd}")

    try:
        result = subprocess.run(command, cwd=cwd, env=env, text=True)

        if result.returncode == 0:
            print(f"{description} 성공")
        else:
            print(f"{description} 실패 (exit code: {result.returncode})")

        return result.returncode == 0

    except subprocess.CalledProcessError as e:
        print(f"{description} 실패: {e}")
        return False
    except FileNotFoundError:
        print(f"명령어를 찾을 수 없습니다: {command[0]}")
        return False


def setup_service_environment(service_dir, base_env):
    """서비스별 환경 변수 설정"""
    service_env = base_env.copy()
    service_root = str(Path(service_dir).absolute())

    # OS별 경로 구분자 설정
    path_sep = ";" if os.name == "nt" else ":"
    current_pythonpath = service_env.get("PYTHONPATH", "")

    # 서비스 디렉터리를 PYTHONPATH에 추가
    if current_pythonpath:
        service_env["PYTHONPATH"] = f"{service_root}{path_sep}{current_pythonpath}"
    else:
        service_env["PYTHONPATH"] = service_root

    print(f"서비스 환경 설정 ({service_dir}): PYTHONPATH={service_env['PYTHONPATH']}")
    return service_env


def setup_test_environment():
    """테스트 환경 설정"""
    print("테스트 환경 설정 중...")

    # 현재 작업 디렉터리 (server 디렉터리)
    server_root = str(Path.cwd().absolute())

    # OS별 경로 구분자 설정
    path_sep = ";" if os.name == "nt" else ":"
    current_pythonpath = os.environ.get("PYTHONPATH", "")

    # PYTHONPATH에 server 디렉터리 추가
    if current_pythonpath:
        pythonpath = f"{server_root}{path_sep}{current_pythonpath}"
    else:
        pythonpath = server_root

    # 테스트용 환경 변수 설정
    test_env = os.environ.copy()
    test_env.update(
        {
            "DATABASE_URL": "postgresql://postgres:password123!@localhost:5432/cocktail_db_test",
            "REDIS_URL": "redis://localhost:6379",
            "SECRET_KEY": "test-secret-key-for-testing",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
            "PYTHONPATH": pythonpath,
        }
    )

    print(f"기본 PYTHONPATH 설정: {pythonpath}")
    return test_env


def check_test_dependencies():
    """테스트 의존성 확인"""
    print("테스트 의존성 확인 중...")

    dependencies = ["pytest"]
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


def check_test_database():
    """테스트 데이터베이스 연결 확인"""
    print("테스트 데이터베이스 연결 확인 중...")

    try:
        import psycopg2

        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="cocktail_db_test",
            user="postgres",
            password="password123!",
        )
        conn.close()
        print("PostgreSQL 연결 성공")
        return True
    except Exception as e:
        print(f"PostgreSQL 연결 실패: {e}")
        print("Docker Compose로 데이터베이스를 실행해주세요:")
        print("    docker-compose up -d postgres")
        return False


def check_test_redis():
    """테스트 Redis 연결 확인"""
    print("테스트 Redis 연결 확인 중...")

    try:
        import redis

        client = redis.Redis(
            host="localhost",
            port=6379,
            db=1,
            decode_responses=True,
            password="password123!",
        )
        client.ping()
        print("Redis 연결 성공")
        return True
    except Exception as e:
        print(f"Redis 연결 실패: {e}")
        print("Docker Compose로 Redis를 실행해주세요:")
        print("    docker-compose up -d redis")
        return False


def run_unit_tests(service_dir, test_env, coverage=True, verbose=True):
    """단위 테스트 실행"""
    test_dir = os.path.join(service_dir, "tests")

    if not os.path.exists(test_dir):
        print(f"테스트 디렉터리가 존재하지 않습니다: {test_dir}")
        return False

    # 서비스별 환경 변수 설정
    service_env = setup_service_environment(service_dir, test_env)

    pytest_cmd = ["pytest", "-m", "unit"]

    if verbose:
        pytest_cmd.append("-v")

    if coverage:
        pytest_cmd.extend(
            [f"--cov=app", "--cov-report=term-missing", "--cov-report=xml"]
        )

    return run_command(
        pytest_cmd, f"단위 테스트 실행 - {service_dir}", cwd=service_dir, env=service_env
    )


def run_integration_tests(service_dir, test_env, verbose=True):
    """통합 테스트 실행"""
    test_dir = os.path.join(service_dir, "tests")
    if not os.path.exists(test_dir):
        print(f"테스트 디렉터리가 존재하지 않습니다: {test_dir}")
        return True

    # 서비스별 환경 변수 설정
    service_env = setup_service_environment(service_dir, test_env)

    pytest_cmd = ["pytest", "-m", "integration"]

    if verbose:
        pytest_cmd.append("-v")

    return run_command(
        pytest_cmd, f"통합 테스트 실행 - {service_dir}", cwd=service_dir, env=service_env
    )


def run_all_tests(service_dir, test_env, coverage=True, verbose=True):
    """모든 테스트 실행"""
    test_dir = os.path.join(service_dir, "tests")
    if not os.path.exists(test_dir):
        print(f"테스트 디렉터리가 존재하지 않습니다: {test_dir}")
        return True

    # 서비스별 환경 변수 설정
    service_env = setup_service_environment(service_dir, test_env)

    # pytest 명령어 구성
    pytest_cmd = ["pytest", "tests/"]

    if verbose:
        pytest_cmd.append("-v")

    if coverage:
        pytest_cmd.extend(
            [
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-report=xml",
            ]
        )

    return run_command(
        pytest_cmd, f"전체 테스트 실행 - {service_dir}", cwd=service_dir, env=service_env
    )


def run_docker_tests(service=None):
    """Docker 환경에서 테스트 실행"""
    if service:
        cmd = [
            "docker-compose",
            "-f",
            "docker-compose.test.yml",
            "up",
            "--build",
            f"{service}-test",
            "--abort-on-container-exit",
        ]
        description = f"Docker 환경에서 {service} 테스트 실행"
    else:
        cmd = [
            "docker-compose",
            "-f",
            "docker-compose.test.yml",
            "up",
            "--build",
            "--abort-on-container-exit",
        ]
        description = "Docker 환경에서 전체 테스트 실행"

    return run_command(cmd, description)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="테스트 실행 도구")
    parser.add_argument(
        "--service",
        choices=["user-service", "recipe-service", "all"],
        default="all",
        help="실행할 서비스 (기본값: all)",
    )
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "all"],
        default="all",
        help="실행할 테스트 타입 (기본값: all)",
    )
    parser.add_argument("--no-coverage", action="store_true", help="커버리지 측정 비활성화")
    parser.add_argument("--quiet", action="store_true", help="간단한 출력")
    parser.add_argument("--skip-deps", action="store_true", help="의존성 검사 스킵")
    parser.add_argument("--docker", action="store_true", help="Docker 환경에서 테스트 실행")

    args = parser.parse_args()

    # 스크립트 실행 위치를 server 디렉터리로 설정
    # scripts 디렉터리가 server 안에 있으므로 parent만 하면 됨
    server_dir = Path(__file__).parent.parent
    os.chdir(server_dir)

    # 현재 디렉터리가 server인지 확인
    if not os.path.exists("user-service") or not os.path.exists("recipe-service"):
        print("Error: user-service와 recipe-service 디렉터리를 찾을 수 없습니다.")
        print(f"현재 디렉터리: {os.getcwd()}")
        print("server 디렉터리에서 실행해주세요.")
        sys.exit(1)

    print("칵테일 저장소 테스트 실행 도구")
    print(f"작업 디렉터리: {os.getcwd()}")
    print(f"대상 서비스: {args.service}")
    print(f"테스트 타입: {args.type}")

    # 의존성 검사
    if not args.skip_deps:
        if not check_test_dependencies():
            sys.exit(1)

        if not check_test_database():
            sys.exit(1)

        if not check_test_redis():
            sys.exit(1)

    # 테스트 환경 설정
    test_env = setup_test_environment()

    # 실행할 서비스 목록 설정
    if args.service == "all":
        services = ["user-service", "recipe-service"]
    else:
        services = [args.service]

    # 테스트 실행
    all_passed = True
    coverage = not args.no_coverage
    verbose = not args.quiet

    start_time = time.time()

    for service in services:
        print(f"\n{service} 테스트 시작")

        if args.type == "unit":
            result = run_unit_tests(service, test_env, coverage, verbose)
        elif args.type == "integration":
            result = run_integration_tests(service, test_env, verbose)
        else:  # all
            result = run_all_tests(service, test_env, coverage, verbose)

        if not result:
            all_passed = False
            print(f"{service} 테스트 실패")
        else:
            print(f"{service} 테스트 성공")

    # 결과 요약
    elapsed_time = time.time() - start_time
    print(f"\n{'='*60}")
    print("테스트 결과 요약")
    print(f"{'='*60}")
    print(f"실행 시간: {elapsed_time:.2f}초")
    print(f"테스트 서비스: {', '.join(services)}")
    print(f"테스트 타입: {args.type}")

    if all_passed:
        print("모든 테스트를 통과했습니다!")
        sys.exit(0)
    else:
        print("일부 테스트에 실패했습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()
