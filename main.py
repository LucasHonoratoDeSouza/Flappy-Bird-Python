import pygame
import os
import random
from pygame import mixer

tela_largura = 500
tela_altura = 800
cano_imagem = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
chão_imagem = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
fundo_imagem = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
passaros_imagem = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

pygame.font.init()
contador_fonte = pygame.font.SysFont('arial', 30)

pygame.display.set_icon(passaros_imagem[0])
pygame.display.set_caption ('flappy bird - lucas honorato')


pygame.init()
class Passaro:
    IMGS = passaros_imagem
    rot_max = 25
    vel_max = 20
    animation_time = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.rot_max:
                self.angulo = self.rot_max
        else:
            if self.angulo > -90:
                self.angulo -= self.vel_max

    def desenhar(self, tela):
        self.contagem_imagem += 1

        if self.contagem_imagem < self.animation_time:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.animation_time*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.animation_time*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.animation_time*4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.animation_time*4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0


        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.animation_time*2

        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cano:
    DISTANCIA = 200
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(cano_imagem, False, True)
        self.CANO_BASE = cano_imagem
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:
    VELOCIDADE = 5
    LARGURA = chão_imagem.get_width()
    IMAGEM = chão_imagem

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(fundo_imagem, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = contador_fonte.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (tela_largura - 340 - texto.get_width(), 20))
    chao.desenhar(tela)
    pygame.display.update()


def main():
    passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((tela_largura, tela_altura))
    pontos = 0
    relogio = pygame.time.Clock()

    rodando = True
    while rodando:
        relogio.tick(30)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    for passaro in passaros:
                        passaro.pular()
                        pygame.mixer.init()
                        pygame.mixer.music.load(os.path.join('sounds', 'space.mp3'))
                        pygame.mixer.music.play()
                        pygame.mixer.music.set_volume (0.5)

        for passaro in passaros:
            passaro.mover()
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                    main()
                    
                    
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))
        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)
                main()

        desenhar_tela(tela, passaros, canos, chao, pontos)


if __name__ == '__main__':
    main()
