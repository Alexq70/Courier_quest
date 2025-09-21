# src/main.py

from ui.pygame_ui import GameUI

def main():
    """
    Punto de entrada de la aplicación Courier Quest.
    Inicializa la interfaz con Pygame y arranca el bucle de juego.
    """
    gui = GameUI()
    gui.run()

if __name__ == "__main__":
    main()