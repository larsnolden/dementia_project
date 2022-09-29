import pygame

def playSound(mp3file):
    pygame.mixer.init()
    pygame.mixer.music.load(mp3file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

playSound("sound_files/Wake up.mp3")