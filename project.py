import os
import sys
import pygame
from button import Button
from pygame.locals import *

pygame.init()

screen_width = 600
screen_height = 600
screen_size = (screen_width, screen_height)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Breakout')

# определяем цвет фона для игры
bg = (234, 218, 184)

# цвета блоков
block_red = (242, 85, 96)
block_green = (86, 174, 87)
block_blue = (69, 177, 232)

# цвет платформы
paddle_col = (142, 135, 123)
paddle_outline = (100, 100, 100)

# цвет текста
text_col1 = (220, 20, 60)
text_col2 = (127, 72, 112)

# основные игровые переменные
cols = 6
rows = 6
clock = pygame.time.Clock()
fps = 60


# возвращаем шрифт нужного размера
def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)


# основной шрифт
font = get_font(30)


# импортируем фон - картинку
def load_image(name, color_key=None):
    fullname = os.path.join('assets', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print("Не удаётся загрузить:", name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


# в случае ошибки завершаем игру
def terminate():
    pygame.quit()
    sys.exit()


# формируем экран
def se_screen(intro_text):
    fon = pygame.transform.scale(load_image('fon.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    text_coord = 200
    for line in intro_text:
        string_rendered = font.render(line, 1, text_col1)
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 120
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(fps)


# определяем стартовый экран
def start_screen():
    intro_text = ["  BREAKOUT", "",
                  "PYGAME PROJECT"]
    se_screen(intro_text)


# определяем конечный экран при выигрыше
def end_screen_win():
    intro_text = ["  GAME OVER",
                  "  YOU WON!", "",
                  "", "", "",
                  "CLICK ANYWHERE",
                  "TO PLAY AGAIN"]
    se_screen(intro_text)


# определяем конечный экран при проигрыше
def end_screen_loss():
    intro_text = ["  GAME OVER",
                  "  YOU LOSE", "",
                  "", "", "",
                  "CLICK ANYWHERE",
                  "TO PLAY AGAIN"]
    se_screen(intro_text)


# запускаем основной игровой цикл
def play():
    live_ball = False
    game_over = 0

    # функция вывода текста на экран
    def draw_text(text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))

    # класс кирпичной стены
    class wall():
        def __init__(self):
            self.width = screen_width // cols
            self.height = 50

        # создаём стену из кирпичей
        def create_wall(self):
            self.blocks = []
            # определяем пустой список для отдельного блока
            block_individual = []

            for row in range(rows):
                # сбрасываем список заблокированных строк
                block_row = []

                # перебираем каждый столбец в этой строке
                for col in range(cols):
                    # генерируем позиции x и y для каждого блока и создаем прямоугольник из этого
                    block_x = col * self.width
                    block_y = row * self.height
                    rect = pygame.Rect(block_x, block_y, self.width, self.height)

                    # назначаем силу блока в зависимости от ряда
                    if row < 2:
                        strength = 3
                    elif row < 4:
                        strength = 2
                    elif row < 6:
                        strength = 1

                    # создаём список для хранения данных прямоугольника и цвета
                    block_individual = [rect, strength]
                    # добавляем отдельный блок в строку блока
                    block_row.append(block_individual)
                # добавляем строку в полный список блоков
                self.blocks.append(block_row)

        # выводим нашу стену на экран
        def draw_wall(self):
            for row in self.blocks:
                for block in row:
                    # назначаем цвет в зависимости от силы блока
                    if block[1] == 3:
                        block_col = block_blue
                    elif block[1] == 2:
                        block_col = block_green
                    elif block[1] == 1:
                        block_col = block_red
                    pygame.draw.rect(screen, block_col, block[0])
                    pygame.draw.rect(screen, bg, (block[0]), 2)

    # класс платформы-ракетки
    class paddle():
        def __init__(self):
            self.reset()

        # сбрасываем направление движения
        def move(self):
            self.direction = 0
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT] and self.rect.left > 0:
                self.rect.x -= self.speed
                self.direction = -1
            if key[pygame.K_RIGHT] and self.rect.right < screen_width:
                self.rect.x += self.speed
                self.direction = 1

        # рисуем платформу
        def draw(self):
            pygame.draw.rect(screen, paddle_col, self.rect)
            pygame.draw.rect(screen, paddle_outline, self.rect, 3)

        # определяем параметры платформы
        def reset(self):
            self.height = 20
            self.width = int(screen_width / cols)
            self.x = int((screen_width / 2) - (self.width / 2))
            self.y = screen_height - (self.height * 2)
            self.speed = 10
            self.rect = Rect(self.x, self.y, self.width, self.height)
            self.direction = 0

    # класс шара
    class game_ball():
        def __init__(self, x, y):
            self.reset(x, y)

        def move(self):

            # порог столкновения
            collision_thresh = 5

            # допустим, что стена полностью разрушена
            wall_destroyed = 1
            row_count = 0

            for row in wall.blocks:
                item_count = 0
                for item in row:
                    # проверка столкновений
                    if self.rect.colliderect(item[0]):

                        # проверяем, было ли столкновение сверху
                        if abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0:
                            self.speed_y *= -1

                        # проверяем, было ли столкновение снизу
                        if abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0:
                            self.speed_y *= -1

                        # проверяем, было ли столкновение слева
                        if abs(self.rect.right - item[0].left) < collision_thresh and self.speed_x > 0:
                            self.speed_x *= -1

                        # проверяем, было ли столкновение справа
                        if abs(self.rect.left - item[0].right) < collision_thresh and self.speed_x < 0:
                            self.speed_x *= -1

                        # уменьшаем прочность блока, нанося ему урон
                        if wall.blocks[row_count][item_count][1] > 1:
                            wall.blocks[row_count][item_count][1] -= 1

                        else:
                            wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)

                    # проверяем, существует ли еще блок, и в этом случае стена не разрушается
                    if wall.blocks[row_count][item_count][0] != (0, 0, 0, 0):
                        wall_destroyed = 0

                    # увеличиваем счетчик предметов
                    item_count += 1
                # увеличиваем счетчик строк
                row_count += 1

            # после перебора всех блоков проверяем, не разрушена ли стена
            if wall_destroyed == 1:
                self.game_over = 1

            # проверка на столкновение со стенами
            if self.rect.left < 0 or self.rect.right > screen_width:
                self.speed_x *= -1

            # проверка на столкновение с верхом и низом экрана
            if self.rect.top < 0:
                self.speed_y *= -1
            if self.rect.bottom > screen_height:
                self.game_over = -1

            # проверяем на столкновение с платформой
            if self.rect.colliderect(player_paddle):

                # проверяем, нет ли столкновения сверху
                if abs(self.rect.bottom - player_paddle.rect.top) < collision_thresh and self.speed_y > 0:
                    self.speed_y *= -1
                    self.speed_x += player_paddle.direction
                    if self.speed_x > self.speed_max:
                        self.speed_x = self.speed_max
                    elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                        self.speed_x = -self.speed_max
                else:
                    self.speed_x *= -1

            self.rect.x += self.speed_x
            self.rect.y += self.speed_y

            return self.game_over

        # рисуем шар
        def draw(self):
            pygame.draw.circle(screen, paddle_col, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad),
                               self.ball_rad)
            pygame.draw.circle(screen, paddle_outline, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad),
                               self.ball_rad, 3)

        def reset(self, x, y):
            self.ball_rad = 10
            self.x = x - self.ball_rad
            self.y = y
            self.rect = Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
            self.speed_x = 4
            self.speed_y = -4
            self.speed_max = 5
            self.game_over = 0

    # создаём стену
    wall = wall()
    wall.create_wall()

    # создаём платформу
    player_paddle = paddle()

    # создаём шар
    ball = game_ball(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)

    run = True
    while run:

        clock.tick(fps)

        screen.fill(bg)

        # рисуем объекты
        wall.draw_wall()
        player_paddle.draw()
        ball.draw()

        if live_ball:
            # рисуем платформу
            player_paddle.move()
            # рисуем шар
            game_over = ball.move()
            if game_over != 0:
                live_ball = False

        # выводим инструкцию для игрока
        if not live_ball:
            if game_over == 0:
                draw_text('CLICK ANYWHERE', font, text_col2, 100, screen_height // 2 + 100)
                draw_text('TO START', font, text_col2, 200, screen_height // 2 + 150)
            # осуществляем переходы на экраны завершения игры
            elif game_over == 1:
                end_screen_win()
                main_menu()
            elif game_over == -1:
                end_screen_loss()
                main_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and live_ball == False:
                live_ball = True
                ball.reset(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)
                player_paddle.reset()
                wall.create_wall()

        pygame.display.update()


# вызываем окно с инструкцией к игре
def options():
    while True:
        options_mouse_pos = pygame.mouse.get_pos()

        screen.fill("white")

        texts = ["В начале Breakout шесть строк кирпичей, по две строки ",
                 "одного цвета. Порядок цветов игры снизу вверх: красный, зелёный ",
                 "и голубой. С помощью одного шара игрок должен сбить ",
                 "максимальное количество кирпичей, используя ",
                 "стены и управляемую платформу-ракетку внизу, чтобы рикошетом ",
                 "направлять мяч в кирпичи и уничтожать их. ",
                 "Небольшую платформу игрок может передвигать горизонтально от ",
                 "одной стенки до другой, подставляя её под шарик, предотвращая ",
                 "его падение вниз. Удар шарика по кирпичу приводит к разрушению ",
                 "кирпича. Чтобы выиграть необходимо уничтожить все кирпичи. ",
                 "Есть и некоторое разнообразие: определённые кирпичи нужно ",
                 "ударять несколько раз. Так, чтобы разрушить красные кирпичи - ",
                 "необходимо ударить каждый из них один раз, зелёные - два раза, ",
                 "голубые - три раза "]

        # выводим текст инструкции
        a = 310
        b = 50
        for text in texts:
            options_text = get_font(9).render(text, True, "Black")
            options_rect = options_text.get_rect(center=(a, b))
            screen.blit(options_text, options_rect)
            b += 20

        # выводим кнопку на экран
        options_back = Button(image=None, pos=(300, 500),
                              text_input="BACK", font=get_font(30), base_color="Black", hovering_color="Green")

        # изменяем цвет в зависимости от взаимодействия
        options_back.changeColor(options_mouse_pos)
        options_back.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if options_back.checkForInput(options_mouse_pos):
                    main_menu()

        pygame.display.update()


# вызываем основное меню игры
def main_menu():
    while True:
        fon = pygame.transform.scale(load_image('fon.jpg'), screen_size)
        screen.blit(fon, (0, 0))

        menu_mouse_pos = pygame.mouse.get_pos()

        # выводим текст заголовка
        menu_text = get_font(40).render("MAIN MENU", True, "#dc143c")
        menu_rect = menu_text.get_rect(center=(300, 100))

        # выводим кнопки на экран
        play_button = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(300, 200),
                             text_input="PLAY", font=get_font(30), base_color="#4169e1", hovering_color="White")
        options_button = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(300, 320),
                                text_input="OPTIONS", font=get_font(30), base_color="#4169e1", hovering_color="White")
        quit_button = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(300, 440),
                             text_input="QUIT", font=get_font(30), base_color="#4169e1", hovering_color="White")

        screen.blit(menu_text, menu_rect)

        # изменяем цвет в зависимости от взаимодействия
        for button in [play_button, options_button, quit_button]:
            button.changeColor(menu_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(menu_mouse_pos):
                    play()
                if options_button.checkForInput(menu_mouse_pos):
                    options()
                if quit_button.checkForInput(menu_mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


start_screen()
main_menu()
