import sys
import os
import yaml
from PyQt6.QtWidgets import QApplication
from ui_controller import MainWindow

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def main():
    # Setup paths
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_path, 'config')

    # Load configurations
    try:
        sim_config = load_config(os.path.join(config_dir, 'simulation.yaml'))
        vis_config = load_config(os.path.join(config_dir, 'visuals.yaml'))
    except FileNotFoundError as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName(sim_config['simulation']['title'])

    window = MainWindow(sim_config, vis_config)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
