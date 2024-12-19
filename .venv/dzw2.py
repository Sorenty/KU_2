import os
import subprocess
import argparse
from datetime import datetime


class DependencyVisualizer:
    def __init__(self, repo_path, output_path, start_date):
        self.repo_path = repo_path
        self.output_path = output_path
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.commits = []

    def get_git_log(self):
        """Fetches the git log from the repository."""
        cmd = [
            "git",
            "-C",
            self.repo_path,
            "log",
            "--pretty=format:%H|%an|%ad|%P",
            "--date=iso",
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Error executing git log: {result.stderr}")
        return result.stdout.strip().split("\n")

    def parse_commits(self, log_data):
        """Parses git log data into a structured format."""
        for line in log_data:
            sha, author, date, parents = line.split("|")
            try:
                date_obj = datetime.strptime(date.strip(), "%Y-%m-%d %H:%M:%S %z").replace(tzinfo=None)
            except ValueError:
                date_obj = datetime.strptime(date.strip(), "%Y-%m-%d %H:%M:%S")
            if date_obj >= self.start_date:
                self.commits.append({
                    "sha": sha,
                    "author": author,
                    "date": date_obj,
                    "parents": parents.split() if parents else [],
                })

    def generate_plantuml(self):
        """Generates the PlantUML graph from parsed commits."""
        uml_lines = ["@startuml", "skinparam linetype ortho"]
        sha_to_node = {}
        for commit in self.commits:
            node_name = f"node_{commit['sha'][:7]}"
            sha_to_node[commit['sha']] = node_name
            uml_lines.append(
                f'node "{commit["sha"][:7]}\\n{commit["author"]}\\n{commit["date"].strftime("%Y-%m-%d %H:%M:%S")}" as {node_name}'
            )

        for commit in self.commits:
            for parent in commit["parents"]:
                if parent in sha_to_node:
                    uml_lines.append(f"{sha_to_node[commit['sha']]} --> {sha_to_node[parent]}")

        uml_lines.append("@enduml")
        return "\n".join(uml_lines)

    def save_output(self, uml_content):
        """Saves the PlantUML output to a file."""
        with open(self.output_path, "w") as file:
            file.write(uml_content)

    def run(self):
        """Main entry point for the visualizer."""
        log_data = self.get_git_log()
        self.parse_commits(log_data)
        uml_content = self.generate_plantuml()
        self.save_output(uml_content)


def main():
    parser = argparse.ArgumentParser(description="Dependency Graph Visualizer for Git Repositories")
    parser.add_argument("--repo", required=True, help="Path to the Git repository.")
    parser.add_argument("--output", required=True, help="Path to save the generated PlantUML file.")
    parser.add_argument("--date", required=True, help="Start date for commits (format: YYYY-MM-DD).")
    args = parser.parse_args()

    try:
        visualizer = DependencyVisualizer(args.repo, args.output, args.date)
        visualizer.run()
        print(f"Dependency graph saved to {args.output}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

#python C:\Users\alex\Desktop\pythonProject2\.venv\dzw2.py --repo C:\Users\alex\Learn-Eng-Game-main --output C:\Users\alex\Desktop\pythonProject2\graph.puml --date 2023-01-01