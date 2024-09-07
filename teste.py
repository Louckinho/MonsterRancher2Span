import pymem
import tkinter as tk
from tkinter import font as tkfont
import threading
import time

# Endereços de memória reais para LifeSpan, Stress e Fatigue
LIFESPAN_CURRENT_ADDRESS = 0x00E16678  # Endereço para o LifeSpan atual
LIFESPAN_MAX_ADDRESS = 0x00E16694  # Endereço para o LifeSpan máximo
STRESS_ADDRESS = 0x00E1669F  # Endereço para o Stress
FATIGUE_ADDRESS = 0x00E1669B  # Endereço para o Fatigue


class MemoryReader(threading.Thread):
    def __init__(self, game, update_callback):
        threading.Thread.__init__(self)
        self.game = game
        self.update_callback = update_callback
        self.running = True

    def run(self):
        while self.running:
            try:
                # Pega o LifeSpan atual, LifeSpan máximo, Stress e Fatigue do monstro
                current_lifespan = self.game.read_int(LIFESPAN_CURRENT_ADDRESS)
                max_lifespan = self.game.read_short(
                    LIFESPAN_MAX_ADDRESS)  # Lê como 2 bytes

                # Lê 1 byte como um inteiro e converte para o intervalo de 0 a 100
                stress = self.game.read_int(STRESS_ADDRESS) & 0xFF
                fatigue = self.game.read_int(FATIGUE_ADDRESS) & 0xFF

                # Chama a função de atualização da interface gráfica
                self.update_callback(
                    current_lifespan, max_lifespan, stress, fatigue)

                # Aguarda 1 segundo antes de atualizar novamente
                time.sleep(1)
            except Exception as e:
                print(f"Erro: {e}")
                self.running = False


def get_fatigue_message(fatigue):
    if fatigue == 100:
        return "Pass Out"
    elif fatigue >= 61:
        return "Very Tired"
    elif fatigue >= 41:
        return "Pretty Tired"
    elif fatigue >= 21:
        return "Seems Tired"
    elif fatigue >= 2:
        return "Seems Well"
    elif fatigue == 1:
        return "Well"
    elif fatigue == 0:
        return "Very Well"


def get_stress_message(stress):
    if stress == 100:
        return "Full Stress"
    elif stress == 0:
        return "No Stress"
    else:
        return "Stress"


def create_overlay():
    root = tk.Tk()
    root.title("Monster Rancher 2 Status Monster")
    root.geometry("235x180+10+10")  # Tamanho inicial menor
    root.attributes('-topmost', True)  # Garante que fique no topo

    # Cria a área de controle no topo
    control_panel = tk.Frame(root, bg='lightgray')
    control_panel.pack(fill='x', padx=5, pady=5)

    # Cria a área para exibir o texto
    content = tk.Frame(root, bg='white')
    content.pack(fill='both', expand=True, padx=10, pady=10)

    # Fonte e tamanho padrão
    font_family = "Consolas"
    font_size = 12

    # Tenta usar a fonte Consolas, senão usa uma fonte padrão
    try:
        font = tkfont.Font(family=font_family, size=font_size)
    except tk.TclError:
        font_family = "Arial"  # Fallback para uma fonte padrão
        font = tkfont.Font(family=font_family, size=font_size)

    # Label para mostrar o texto
    label = tk.Label(content, text="Inicializando...", bg='white', font=font)
    label.pack(padx=10, pady=10, fill='both', expand=True)

    # Comentado para desativar a seleção de fonte
    # Fonte e tamanho padrão
    # font_family = tk.StringVar(value="Consolas")
    # font_size = tk.IntVar(value=12)

    # Menus de seleção de fonte e tamanho
    # font_choices = [
    #     "Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana",
    #     "Georgia", "Tahoma", "Trebuchet MS", "Comic Sans MS", "Lucida Console",
    #     "Impact", "Arial Black", "Garamond", "Palatino Linotype", "Consolas",
    #     "Frank Ruhl", "Fira Sans", "Roboto", "Open Sans", "Lato",
    #     "Montserrat", "Ubuntu", "Source Sans Pro", "PT Sans", "Noto Sans"
    # ]
    # size_choices = [8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]

    # font_menu = tk.OptionMenu(control_panel, font_family, *font_choices)
    # font_menu.config(width=15)  # Largura menor
    # font_menu.pack(side='left', padx=5)

    # size_menu = tk.OptionMenu(control_panel, font_size, *size_choices)
    # size_menu.config(width=8)  # Largura menor
    # size_menu.pack(side='left', padx=5)

    def update_font(*args):
        # Atualiza a fonte da label com base na seleção
        # label.config(font=(font_family.get(), font_size.get()))
        pass

    # Atualiza a fonte quando o usuário muda as opções
    # font_family.trace('w', update_font)
    # font_size.trace('w', update_font)

    # Função para mover a janela
    def move_window(event):
        root.geometry(f'+{event.x_root}+{event.y_root}')

    # Função para redimensionar a janela
    def resize_window(event):
        root.geometry(f'{event.width}x{event.height}')

    root.bind('<Button-1>', move_window)
    root.bind('<B1-Motion>', resize_window)

    return root, label


def update_overlay(label, current_lifespan, max_lifespan, stress, fatigue):
    # Atualiza o texto na janela de sobreposição
    fatigue_message = get_fatigue_message(fatigue)
    stress_message = get_stress_message(stress)

    label.config(text=(
        f"LifeSpan Atual: {current_lifespan}\n"
        f"LifeSpan Máximo: {max_lifespan}\n"
        f"Stress: {stress} ({stress_message})\n"
        f"Fatigue: {fatigue} ({fatigue_message})"
    ))
    label.update_idletasks()  # Atualiza a interface


def main():
    # Conecte-se ao processo do jogo
    game_name = "MF2.exe"  # Nome atualizado do executável do jogo
    try:
        game = pymem.Pymem(game_name)
    except Exception as e:
        print(f"Erro ao conectar ao processo do jogo: {e}")
        return

    root, label = create_overlay()

    # Cria uma thread para ler a memória e atualizar a interface
    memory_reader = MemoryReader(
        game, lambda c, m, s, f: update_overlay(label, c, m, s, f))
    memory_reader.start()

    # Loop principal do Tkinter para manter a interface aberta
    try:
        root.mainloop()
    finally:
        # Interrompe a thread ao fechar o programa
        memory_reader.running = False
        memory_reader.join()


if __name__ == "__main__":
    main()
