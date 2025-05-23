from pathlib import Path

# List of filenames to create
files = [
    "ui.py",
    "theme.py",
    "components.py",
    "events.py",
    "states.py",
    "rating.py",
    "constants.py"
]

# Create each file
for file in files:
    path = Path(file)
    path.touch(exist_ok=True)
    print(f"Created: {path}")
