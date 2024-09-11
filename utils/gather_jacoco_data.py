import subprocess
import os


def generate_report(exec_file, class_files_dir, source_files_dir, report_dir):
    jacoco_cli_path = os.path.join(os.path.dirname(__file__), "org.jacoco.cli-0.8.7-nodeps.jar")
    cmd = [
        "java", "-jar", jacoco_cli_path,
        "report", exec_file,
        "--classfiles", class_files_dir,
        "--sourcefiles", source_files_dir,
        "--html", report_dir
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Report generated in {report_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating report: {e}")


if __name__ == "__main__":
    generate_report("jacoco_coverage.exec", "/path/to/class/files", "/path/to/source/files", "coverage_report")
