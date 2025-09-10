#!/usr/bin/env python3
"""
개발환경 실행 스크립트
각 서비스를 개별적으로 실행하거나 전체를 실행할 수 있습니다.
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def run_service(service_name: str, port: int) -> subprocess.Popen:
    """개별 서비스 실행"""
    service_path = Path(f"{service_name}/app")

    if not service_path.exists():
        print(f"❌ {service_name} 디렉터리가 존재하지 않습니다.")
        return None

    print(f"🚀 {service_name} 시작 중... (Port: {port})")

    # 환경 변수 설정
    env = os.environ.copy()
    env.update({"PYTHONPATH": str(service_path.parent), "DEBUG": "True"})

    # 서비스 실행
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
        ],
        cwd=service_name,
        env=env,
    )

    return process


def run_all_services():
    """모든 서비스 실행"""
    print("🌟 모든 서비스 시작 중...")

    services = [("user-service", 8001), ("recipe-service", 8002), ("api-gateway", 8000)]

    processes = []

    try:
        for service_name, port in services:
            process = run_service(service_name, port)
            if process:
                processes.append((service_name, process))
                time.sleep(2)  # 서비스 간 시작 간격

        print("\n✅ 모든 서비스가 시작되었습니다!")
        print("📚 API 문서:")
        print("  - API Gateway: http://localhost:8000/docs")
        print("  - User Service: http://localhost:8001/docs")
        print("  - Recipe Service: http://localhost:8002/docs")
        print("\n🛑 종료하려면 Ctrl+C를 누르세요.")

        # 프로세스 모니터링
        while True:
            time.sleep(1)
            for service_name, process in processes:
                if process.poll() is not None:
                    print(f"❌ {service_name}가 종료되었습니다.")

    except KeyboardInterrupt:
        print("\n🛑 서비스 종료 중...")
        for service_name, process in processes:
            print(f"⏹️  {service_name} 종료 중...")
            process.terminate()
            process.wait()
        print("✅ 모든 서비스가 종료되었습니다.")


def show_help():
    """도움말 출력"""
    print(
        """
🍸 칵테일 저장소 개발 서버 실행 도구

사용법:
    python run_dev.py [옵션]

옵션:
    all             모든 서비스 실행 (기본값)
    user-service    User Service만 실행 (포트: 8001)
    recipe-service  Recipe Service만 실행 (포트: 8002)
    api-gateway     API Gateway만 실행 (포트: 8000)
    help            이 도움말 출력

예시:
    python run_dev.py                    # 모든 서비스 실행
    python run_dev.py user-service       # User Service만 실행
    python run_dev.py api-gateway        # API Gateway만 실행
    """
    )


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        command = "all"
    else:
        command = sys.argv[1]

    if command == "help":
        show_help()
    elif command == "all":
        run_all_services()
    elif command == "user-service":
        process = run_service("user-service", 8001)
        if process:
            try:
                process.wait()
            except KeyboardInterrupt:
                process.terminate()
    elif command == "recipe-service":
        process = run_service("recipe-service", 8002)
        if process:
            try:
                process.wait()
            except KeyboardInterrupt:
                process.terminate()
    elif command == "api-gateway":
        process = run_service("api-gateway", 8000)
        if process:
            try:
                process.wait()
            except KeyboardInterrupt:
                process.terminate()
    else:
        print(f"❌ 알 수 없는 명령: {command}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
