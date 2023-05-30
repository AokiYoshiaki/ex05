from typing import Any
import pygame as pg
import sys
import time
from pygame.sprite import AbstractGroup

WIDTH = 1600
HEIGHT = 900

class tower(pg.sprite.Sprite):
    """
    自分と敵のタワーに関するクラス
    1,init
    引数はHPと位置を示すタプル
    バベルの塔の画像を表示させ指定された位置に置く
    読み取り用属性は"Tower"である
    2,update
    HPが0になったときグループから消去する
    """
    def __init__(self, hp, xy: tuple[int, int]):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load("ex05/fig/tower.png"), 0.5, 0.5)
        self.hp = hp
        self.rect = self.image.get_rect()
        self.rect.center = xy #位置X,Y
        self.zokusei = "Tower" #読み取り用属性

    def update(self,screen: pg.Surface):
        if self.hp < 0:
            self.kill()

class Chara(pg.sprite.Sprite):
    """
    出撃するこうかとんに関するクラス
    1,init
    引数はHPと位置を示すタプルとdx
    こうかとんの画像を表示させ指定された位置に置く
    dxはこれの重さや強さを決める数値である
    大きいほど重く防御の堅いキャラクターになる
    読み取り用属性は"Chara"である
    2,update
    dxの量分移動する
    HPが0になるとグループから消える
    """
    def __init__(self, hp, xy: tuple[int, int], dx):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load("ex05/fig/2.png"), abs(dx)*0.1, abs(dx)*0.1)
        self.hp = hp
        self.rect = self.image.get_rect()
        self.rect.center = xy #位置X,Y
        self.dx = 20/dx #dxが小さいほど速い
        self.weight = abs(dx) #dxが大きいほど重い
        self.zokusei = "Chara" #読み取り用属性

    def update(self,screen: pg.Surface):
        self.rect.move_ip(self.dx, 0)
        screen.blit(self.image, self.rect)
        if self.hp < 0:
            self.kill()

class Hit(pg.sprite.Sprite):
    """
    当たり判定に関するクラス
    1,init
    引数はものとノックバック発生時間
    ヒットが発生したもののHPを5減らす
    2,update
    読み取り属性が"Chara"なら
    繰り返し当たらないよう､重さに応じてノックバックする
    ノックバック発生時間が終わるとグループから消える
    """
    def __init__(self, obj: "Chara|tower", life: int):
        super().__init__()
        self.obj = obj
        self.obj.hp -= 5
        self.life = life
    def update(self):
        self.life -= 1
        if self.obj.zokusei == "Chara":
            if self.obj.dx >= 0:
                self.obj.rect.centerx -= 5/self.obj.weight #dxが大きいほどノックバックしにくい
            else:
                self.obj.rect.centerx += 5/self.obj.weight #dxが大きいほどノックバックしにくい
        if self.life < 0:
            self.kill()


class Cooldown():
    """出撃タイマーの設定"""
    def __init__(self, cooltime):
        self.cooltime = cooltime
        self.timer = 0
        self.color = [240, 128, 128], [50, 50 , 50]
        
           
    def flag(self, now):
        if (now - self.timer >= self.cooltime) or self.timer == 0:
            self.timer = now
            print(self.timer)
            return True
        else:
            return False
        
    def update(self, now, surface, n):
        font1 = pg.font.SysFont("hg正楷書体pro", 150)#堤のと合わせて消して
        font2 = pg.font.SysFont(None, 30)#ここも
        n += 2
        text1 = font1.render(f"{n-2}", True, (255, 255, 255))
        if now - self.timer >= self.cooltime or self.timer == 0:
            surface.fill(self.color[0], (HEIGHT / 8 * n, 700, 100, 100))
        else:
            surface.fill(self.color[1], (HEIGHT / 8 * n, 700, 100, 100))
        surface.blit(text1, (HEIGHT / 8 * n, 676))

        
def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("ex05/fig/pg_bg.jpg")
    Pltower = pg.sprite.Group()
    Entower = pg.sprite.Group()
    cooltimes = [Cooldown(10), Cooldown(40), Cooldown(200)]
    Plchara = pg.sprite.Group()
    Enchara = pg.sprite.Group()

    hits = pg.sprite.Group()

    tmr = 0
    clock = pg.time.Clock()

    Pltower.add(tower(500, (100, 400)))
    Entower.add(tower(500, (1500, 400)))
    
    while True:

        key_lst = pg.key.get_pressed()
        """
        敵は一定時間でキャラクターが生まれる
        """    
        if tmr != 0 and tmr % 200 == 0:
            if tmr != 0 and tmr % 400 == 0:
                if tmr != 0 and tmr % 800 == 0:
                    Enchara.add(Chara(75, (1500, 400), -15))
                else:
                    Enchara.add(Chara(50, (1500, 400), -10))
            else:
                Enchara.add(Chara(50, (1500, 400), -5))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            """
            押したボタンの数値が大きいほど
            強いけど遅いキャラクターが生まれる
            """    
            if event.type == pg.KEYDOWN and event.key == pg.K_0 and cooltimes[0].flag(tmr):
                Plchara.add(Chara(50, (100, 400), 5))
            if event.type == pg.KEYDOWN and event.key == pg.K_1 and cooltimes[1].flag(tmr):
                Plchara.add(Chara(75, (100, 400), 10))
            if event.type == pg.KEYDOWN and event.key == pg.K_2 and cooltimes[2].flag(tmr):
                Plchara.add(Chara(100, (100, 400), 15))

        for plt in pg.sprite.groupcollide(Pltower, Enchara, False, False).keys():
            hits.add(Hit(plt, 20)) #敵に襲われて自分のタワーにダメージ

        for ply in pg.sprite.groupcollide(Plchara, Enchara, False, False).keys():
            hits.add(Hit(ply, 20)) #敵のキャラクターと戦って自分のキャラにダメージ

        for ply in pg.sprite.groupcollide(Plchara, Entower, False, False).keys():
            hits.add(Hit(ply, 20)) #敵のタワーの反撃で自分のキャラにダメージ
        
        for ent in pg.sprite.groupcollide(Entower, Plchara, False, False).keys():
            hits.add(Hit(ent, 20)) #自分のキャラが襲撃して敵のタワーにダメージ


        for enm in pg.sprite.groupcollide(Enchara, Plchara, False, False).keys():
            hits.add(Hit(enm, 20)) #自分のキャラクターと戦って敵のキャラにダメージ

            
        for enm in pg.sprite.groupcollide(Enchara, Pltower, False, False).keys():
            hits.add(Hit(enm, 20)) #自分のタワーの反撃で敵のキャラにダメージ
        
        if len(Pltower) == 0: #自分のタワーがやられたとき､少し止まって終了
            time.sleep(2) 
            return
        
        if len(Entower) == 0: #敵のタワーがやられたとき､少し止まって終了
            time.sleep(2)
            return


        screen.blit(bg_img, [0, 0])

        Pltower.update(screen)
        Pltower.draw(screen)
        for i in range(len(cooltimes)):
            cooltimes[i].update(tmr, screen, i)
        Entower.update(screen)
        Entower.draw(screen)
        
        Plchara.update(screen)
        Plchara.draw(screen)
        Enchara.update(screen)
        Enchara.draw(screen)

        hits.update()
        
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
