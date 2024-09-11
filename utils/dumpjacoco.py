import subprocess
import time
import os


def dump_coverage(port, output_file):
    jacoco_cli_path = os.path.join(os.path.dirname(__file__), "org.jacoco.cli-0.8.7-nodeps.jar")
    cmd = [
        "java", "-jar", jacoco_cli_path,
        "dump", "--address", "host.docker.internal", "--port", str(port),
        "--destfile", output_file
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Coverage data dumped to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error dumping coverage: {e}")


if __name__ == "__main__":
    dump_coverage(6300, f"jacoco_coverage_{int(time.time())}.exec")
