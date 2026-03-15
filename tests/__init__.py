import sys
from pathlib import Path

# Добавляем корень проекта в sys.path чтобы пакет src был доступен
# независимо от того, как запущены тесты (PyCharm, командная строка и т.п.)
sys.path.insert(0, str(Path(__file__).parent.parent))
