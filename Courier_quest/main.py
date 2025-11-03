from pathlib import Path

import pygame

from Presentation.view_game import View_game

SAVE_PATH = Path(__file__).resolve().parent / "saves" / "pause_save.json"


def run_start_menu(allow_resume=True):
    """Muestra el menú principal y gestiona la selección de opciones."""
    pygame.init()
    screen = pygame.display.set_mode((640, 420))
    pygame.display.set_caption("Courier Quest")
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 28)
    clock = pygame.time.Clock()

    options = ["New Game", "Resume Game", "Exit"]
    selected = 0
    feedback = ""
    feedback_timer = 0

    while True:
        has_save = allow_resume and SAVE_PATH.exists()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "exit", None
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
                            return "new", nickname
                        feedback = "Enter a name or press Esc to cancel"
                        feedback_timer = pygame.time.get_ticks()
                    elif option == "Resume Game":
                        if has_save:
                            pygame.quit()
                            return "resume", None
                        feedback = "No saved game available"
                        feedback_timer = pygame.time.get_ticks()
                    else:
                        pygame.quit()
                        return "exit", None
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return "exit", None

        screen.fill((18, 24, 38))
        title = font.render("Courier Quest", True, (255, 255, 255))
        screen.blit(title, ((640 - title.get_width()) // 2, 60))

        for idx, option in enumerate(options):
            disabled = option == "Resume Game" and not has_save
            color = (255, 255, 255)
            if disabled:
                color = (130, 130, 130)
            elif idx == selected:
                color = (255, 215, 0)
            label = font.render(option, True, color)
            screen.blit(label, (200, 140 + idx * 60))

        instruction = small_font.render(
            "Use arrow keys to navigate, Enter to select", True, (200, 200, 200)
        )
        screen.blit(instruction, (320 - instruction.get_width() // 2, 340))

        if feedback and pygame.time.get_ticks() - feedback_timer < 2500:
            msg = small_font.render(feedback, True, (255, 140, 0))
            screen.blit(msg, (320 - msg.get_width() // 2, 370))

        pygame.display.flip()
        clock.tick(60)


def run_start_menu_once(allow_resume=True):
    """Ejecuta el menú principal una sola vez."""
    choice, nickname = run_start_menu(allow_resume=allow_resume)
    return choice, nickname


def prompt_for_name(screen, font, small_font):
    """Solicita al usuario un nombre de jugador."""
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
                    if (
                        char
                        and char.isprintable()
                        and not char.isspace()
                        and len(nickname) < 16
                    ):
                        nickname += char

        screen.fill((18, 24, 38))
        prompt = font.render("Enter your nickname", True, (255, 255, 255))
        screen.blit(prompt, (320 - prompt.get_width() // 2, 120))
        input_box = pygame.Rect(140, 200, 360, 50)
        pygame.draw.rect(screen, (40, 40, 60), input_box, border_radius=6)
        pygame.draw.rect(screen, (255, 215, 0), input_box, 2, border_radius=6)
        name_surface = font.render(nickname or "_", True, (255, 255, 255))
        screen.blit(name_surface, (input_box.x + 10, input_box.y + 5))
        hint = small_font.render(
            "Press Enter to confirm, Esc to cancel", True, (200, 200, 200)
        )
        screen.blit(hint, (320 - hint.get_width() // 2, 280))

        pygame.display.flip()
        clock.tick(60)


def delete_existing_snapshot():
    """Elimina el archivo de guardado si existe."""
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SAVE_PATH.exists():
        try:
            SAVE_PATH.unlink()
        except OSError:
            pass

def main():

    while True:
        allow_resume = SAVE_PATH.exists()
        choice, nickname = run_start_menu(allow_resume=allow_resume)
        if choice == "exit" or choice is None:
            break

        if choice == "new":
            pygame.init()
            window = pygame.display.set_mode((1280, 720))
            pygame.display.set_caption("Courier Quest")
            
            delete_existing_snapshot()
            
            gui = View_game(window,player_name=nickname, resume=False)
        elif choice == "resume":
            if not SAVE_PATH.exists():
                continue
            gui = View_game(window,player_name=None, resume=True)
        else:
            break

        # ✅ Aquí NO cambiamos nada, gui.run() se sigue encargando
        result = gui.run() or {}

        if result.get("exit_game"):
            break

        # ✅ Después de run(), dibujamos el resultado final:
        window.blit(gui.get_surface(), (0, 0))
        pygame.display.update()

    pygame.quit()




if __name__ == "__main__":
    main()
