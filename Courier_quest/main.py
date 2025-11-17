from pathlib import Path
import pygame
from Presentation.view_game import View_game

SAVE_PATH = Path(__file__).resolve().parent / "saves" / "pause_save.json"
current_difficulty = "Medium"



def run_start_menu(allow_resume=True):
    """Ejecuta el menú principal del juego.
    
    Args:
        allow_resume: Si permite la opción de reanudar juego guardado
        
    Returns:
        tuple: (acción, nickname, dificultad) - acción puede ser "new", "resume" o "exit"
    """
    global current_difficulty
    pygame.init()
    screen = pygame.display.set_mode((640, 420))
    pygame.display.set_caption("Courier Quest")
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 28)
    clock = pygame.time.Clock()

    options = ["New Game", "Choose Difficulty", "Resume Game", "Exit"]
    selected = 0
    feedback = ""
    feedback_timer = 0

    while True:
        has_save = allow_resume and SAVE_PATH.exists()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "exit", None, current_difficulty
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    option = options[selected]
                    if option == "New Game":
                        nickname = prompt_for_name(screen, font, small_font)
                        if nickname:
                            pygame.quit()
                            return "new", nickname, current_difficulty
                        feedback = "Enter a name or press Esc to cancel"
                        feedback_timer = pygame.time.get_ticks()

                    elif option == "Choose Difficulty":
                        result = run_difficulty_menu(screen)
                        if result:
                            current_difficulty = result
                        continue

                    elif option == "Resume Game":
                        if has_save:
                            pygame.quit()
                            return "resume", None, current_difficulty
                        feedback = "No saved game available"
                        feedback_timer = pygame.time.get_ticks()

                    else:
                        pygame.quit()
                        return "exit", None, current_difficulty

                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return "exit", None, current_difficulty

        # -------------------- DRAW --------------------
        screen.fill((18, 24, 38))
        title = font.render("Courier Quest", True, (255, 255, 255))
        screen.blit(title, ((640 - title.get_width()) // 2, 60))

        for idx, option in enumerate(options):
            text_display = option
            if option == "Choose Difficulty":
                text_display = f"Choose Difficulty ({current_difficulty})"

            disabled = option == "Resume Game" and not has_save
            color = (255, 255, 255)
            if disabled:
                color = (130, 130, 130)
            elif idx == selected:
                color = (255, 215, 0)

            label = font.render(text_display, True, color)
            screen.blit(label, (130, 140 + idx * 60))

        instruction = small_font.render("Use arrow keys to navigate, Enter to select", True, (200, 200, 200))
        screen.blit(instruction, (320 - instruction.get_width() // 2, 370))

        if feedback and pygame.time.get_ticks() - feedback_timer < 2500:
            msg = small_font.render(feedback, True, (255, 140, 0))
            screen.blit(msg, (320 - msg.get_width() // 2, 370))

        pygame.display.flip()
        clock.tick(60)



def run_start_menu_once(allow_resume=True):
    """Ejecuta el menú principal una vez y retorna la selección.
    
    Args:
        allow_resume: Si permite la opción de reanudar juego guardado
        
    Returns:
        tuple: (acción, nickname, dificultad)
    """
    choice, nickname, difficulty = run_start_menu(allow_resume=allow_resume)
    return choice, nickname, difficulty



def run_difficulty_menu(screen):
    """Ejecuta el menú de selección de dificultad.
    
    Args:
        screen: Superficie de PyGame donde dibujar el menú
        
    Returns:
        str or None: Dificultad seleccionada o None si se cancela
    """
    # Fuentes: grande, mediana, pequeña
    title_font = pygame.font.SysFont(None, 54)
    option_font = pygame.font.SysFont(None, 40)
    small_font = pygame.font.SysFont(None, 26)

    clock = pygame.time.Clock()

    difficulties = ["Easy", "Medium", "Hard"]
    selected = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(difficulties)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(difficulties)
                elif event.key == pygame.K_RETURN:
                    return difficulties[selected]
                elif event.key == pygame.K_ESCAPE:
                    return None

        screen.fill((18, 24, 38))  # Fondo

        # ----- Título -----
        title = title_font.render("Select Difficulty", True, (255, 255, 255))
        screen.blit(title, (320 - title.get_width() // 2, 60))

        # ----- Opciones -----
        for idx, d in enumerate(difficulties):
            color = (255, 215, 0) if idx == selected else (255, 255, 255)
            text = option_font.render(d, True, color)
            screen.blit(text, (320 - text.get_width() // 2, 160 + idx * 60))

        # ----- Texto pequeño -----
        instruction = small_font.render("Press Enter to select, Esc to cancel", True, (200, 200, 200))
        screen.blit(instruction, (320 - instruction.get_width() // 2, 350))

        pygame.display.flip()
        clock.tick(60)



def prompt_for_name(screen, font, small_font):
    """Solicita al usuario que ingrese un nickname.
    
    Args:
        screen: Superficie de PyGame donde dibujar la interfaz
        font: Fuente para texto principal
        small_font: Fuente para texto secundario
        
    Returns:
        str or None: Nickname ingresado o None si se cancela
    """
    nickname = ""
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    cleaned = nickname.strip()
                    if cleaned:
                        return cleaned
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                else:
                    char = event.unicode
                    if char and char.isprintable() and not char.isspace() and len(nickname) < 16:
                        nickname += char

        screen.fill((18, 24, 38))
        prompt = font.render("Enter your nickname", True, (255, 255, 255))
        screen.blit(prompt, (320 - prompt.get_width() // 2, 120))

        input_box = pygame.Rect(140, 200, 360, 50)
        pygame.draw.rect(screen, (40, 40, 60), input_box, border_radius=6)
        pygame.draw.rect(screen, (255, 215, 0), input_box, 2, border_radius=6)

        name_surface = font.render(nickname or "_", True, (255, 255, 255))
        screen.blit(name_surface, (input_box.x + 10, input_box.y + 5))

        hint = small_font.render("Press Enter to confirm, Esc to cancel", True, (200, 200, 200))
        screen.blit(hint, (320 - hint.get_width() // 2, 280))

        pygame.display.flip()
        clock.tick(60)



def delete_existing_snapshot():
    """Elimina el archivo de guardado existente si existe."""
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SAVE_PATH.exists():
        try:
            SAVE_PATH.unlink()
        except OSError:
            pass



def main():
    """Función principal que ejecuta el bucle completo del juego."""
    global current_difficulty

    while True:
        allow_resume = SAVE_PATH.exists()

        #ahora recibimos también la dificultad
        choice, nickname, difficulty = run_start_menu(allow_resume=allow_resume)
        current_difficulty = difficulty  # mantener sincronizado

        if choice == "exit" or choice is None:
            break

        if choice == "new":
            delete_existing_snapshot()
            gui = View_game(player_name=nickname, resume=False, difficulty=difficulty)

        elif choice == "resume":
            if not SAVE_PATH.exists():
                continue
            gui = View_game(player_name=None, resume=True, difficulty=difficulty)

        else:
            break

        result = gui.run() or {}

        if result.get("exit_game"):
            break

    pygame.quit()



if __name__ == "__main__":
    main()
