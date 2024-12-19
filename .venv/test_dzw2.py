import unittest
from dzw2 import DependencyVisualizer
from unittest.mock import patch, MagicMock, mock_open
import subprocess

class TestDependencyVisualizerWithPaths(unittest.TestCase):

    @patch("subprocess.run")
    @patch("builtins.open", new_callable=mock_open)
    def test_run_visualizer(self, mock_open_file, mock_run):
        # Настроим mock для subprocess.run
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "abc123|John Doe|2023-02-01 12:00:00 +0000|def456\n"
                "def456|Jane Doe|2023-01-15 08:00:00 +0000|\n"
            )
        )

        # Установим тестовые пути и дату
        repo_path = "C:/Users/alex/LearnEng"
        output_path = "C:/Users/alex/Desktop/pythonProject2/graph.puml"
        start_date = "2023-01-01"

        # Создадим экземпляр класса
        visualizer = DependencyVisualizer(repo_path=repo_path, output_path=output_path, start_date=start_date)

        # Запустим основной метод run()
        visualizer.run()

        # Проверим вызов subprocess.run
        mock_run.assert_called_once_with(
            ["git", "-C", repo_path, "log", "--pretty=format:%H|%an|%ad|%P", "--date=iso"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Проверим содержимое файла
        expected_uml = """@startuml
skinparam linetype ortho
node "abc123\\nJohn Doe\\n2023-02-01 12:00:00" as node_abc123
node "def456\\nJane Doe\\n2023-01-15 08:00:00" as node_def456
node_abc123 --> node_def456
@enduml"""

        # Проверяем, что файл был записан корректно
        mock_open_file.assert_called_once_with(output_path, "w")
        mock_open_file().write.assert_called_once_with(expected_uml)


if __name__ == "__main__":
    unittest.main()
