import pymem
import pygetwindow as gw
import tkinter as tk
from tkinter import Label
import threading
import time

# Endereços de memória reais para o LifeSpan
LIFESPAN_CURRENT_ADDRESS = 0x00E56678  # Endereço para o LifeSpan atual
LIFESPAN_MAX_ADDRESS = 0x00E56694  # Endereço para o LifeSpan máximo


class MemoryReader(threading.Thread):
    def __init__(self, game, update_callback):
        threading.Thread.__init__(self)
        self.game = game
        self.update_callback = update_callback
        self.running = True

    def run(self):
        while self.running:
            try:
                # Pega o LifeSpan atual e máximo do monstro
                current_lifespan = self.game.read_int(LIFESPAN_CURRENT_ADDRESS)
                max_lifespan = self.game.read_short(LIFESPAN_MAX_ADDRESS)

                # Chama a função de atualização da interface gráfica
                self.update_callback(current_lifespan, max_lifespan)

                # Aguarda 1 segundo antes de atualizar novamente
                time.sleep(1)
            except Exception as e:
                print(f"Erro: {e}")
                self.running = False


def create_overlay():
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("200x100+10+10")  # Ajuste a posição conforme necessário
    root.attributes('-topmost', True)  # Garante que fique no topo

    label = Label(root, text="Inicializando...")
    label.pack()

    return root, label


def update_overlay(label, current_lifespan, max_lifespan):
    # Atualiza o texto na janela de sobreposição
    label.config(text=f"LifeSpan Atual: {
                 current_lifespan}\nLifeSpan Máximo: {max_lifespan}")
    label.update_idletasks()  # Atualiza a interface


def main():
    # Conecte-se ao processo do jogo
    game_name = "MF2.exe"  # Nome atualizado do executável do jogo
    game = pymem.Pymem(game_name)

    root, label = create_overlay()

    # Cria uma thread para ler a memória e atualizar a interface
    memory_reader = MemoryReader(
        game, lambda c, m: update_overlay(label, c, m))
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
