# derived from tetromino (a tetris clone)
# by al sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# released under a "simplified bsd" license

import random, time, pygame, sys
from pygame.locals import *

fps = 25
window_width = 900
window_height = 675
box_size = 15
board_width = 15
board_height = 50
blank = '.'

move_sideways_freq = 0.15
move_down_freq = 0.20

side_margin = ((window_width - box_size) - (board_width * (box_size // 2))) // 2
top_margin = window_height - (board_height * box_size) - 5

# lists RGB values
white = (255, 255, 255)
gray = (185, 185, 185)
black = (0, 0, 0)
olive = (128, 128, 0)
red = (155, 0, 0)
light_red = (175, 20, 20)
blue = (0, 0, 155)
light_blue = (20, 20, 175)
yellow = (155, 155, 0)
light_yellow = (218, 165, 32)

border_color = gray
bg_color = olive
text_color = white
text_shadow_color = gray
colors = (blue, red, yellow)
light_colors = (light_blue, light_red, light_yellow)
assert len(colors) == len(light_colors)  # each color must have light color

template_width = 5
template_height = 5

a_shape_template = [['OOOOO',
                     '...OO',
                     'OOOOO',
                     'O...O',
                     'OOOOO']]


c_shape_template = [['OOOOO',
                     'O....',
                     'O....',
                     'O....',
                     'OOOOO']]

d_shape_template = [['...OO',
                     '...OO',
                     'OOOOO',
                     'O...O',
                     'OOOOO']]

e_shape_template = [['OOOOO',
                     'O...O',
                     'OOOOO',
                     'OO...',
                     'OOOOO']]

g_shape_template = [['OOOOO',
                     'O...O',
                     'OOOOO',
                     '...OO',
                     'OOOOO']]


n_shape_template = [['OO...',
                     'OOOOO',
                     'O...O',
                     'O...O',
                     'O...O']]

o_shape_template = [['OOOOO',
                     'O...O',
                     'O...O',
                     'O...O',
                     'OOOOO']]

r_shape_template = [['O....',
                     'OOOOO',
                     'OO...',
                     'OO...',
                     'OO...']]

s_shape_template = [['..OOO',
                     '.OO..',
                     'OOO..',
                     '..OOO',
                     'OOOO.']]

t_shape_template = [['.OOO.',
                     'OOOOO',
                     '.OOO.',
                     '.OOO.',
                     '.OOO.']]

u_shape_template = [['O...O',
                     'O...O',
                     'O...O',
                     'O...O',
                     'OOOOO']]


pieces = {'A': a_shape_template,
          'C': c_shape_template,
          'D': d_shape_template,
          'E': e_shape_template,
          'G': g_shape_template,
          'N': n_shape_template,
          'O': o_shape_template,
          'R': r_shape_template,
          'S': s_shape_template,
          'T': t_shape_template,
          'U': u_shape_template}

words = {'cat': [['OOOOOOOOOO.OOO.',
                  'O.......OOOOOOO',
                  'O....OOOOO.OOO.',
                  'O....O...O.OOO.',
                  'OOOOOOOOOO.OOO.']],
         'dog': [['...OOOOOOOOOOOO',
                  '...OOO...OO...O',
                  'OOOOOO...OOOOOO',
                  'O...OO...O...OO',
                  'OOOOOOOOOOOOOOO']],
         'red': [['O....OOOOO...OO',
                  'OOOOOO...O...OO',
                  'OO...OOOOOOOOOO',
                  'OO...OO...O...O',
                  'OO...OOOOOOOOOO']],
         'run': [['O....O...OOO...',
                  'OOOOOO...OOOOOO',
                  'OO...O...OO...O',
                  'OO...O...OO...O',
                  'OO...OOOOOO...O']],
         'see': [['..OOOOOOOOOOOOO',
                  '.OO..O...OO...O',
                  'OOO..OOOOOOOOOO',
                  '..OOOOO...OO...',
                  'OOOO.OOOOOOOOOO']]}

word = random.choice(list(words.keys()))


def main():
    global fps_clock, display_surf, basic_font, big_font, subtitle_font
    pygame.init()
    fps_clock = pygame.time.Clock()
    display_surf = pygame.display.set_mode((window_width, window_height))
    subtitle_font = pygame.font.Font('freesansbold.ttf', 18)
    basic_font = pygame.font.Font('freesansbold.ttf', 15)
    big_font = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Textris')

    show_text_screen('Textris')

    while True:     
        # game loop
        if random.randint(0, 1) == 0:
            pygame.mixer.music.load('mozall.mid')
        else:
            pygame.mixer.music.load('tchaikovsky_nutcracker.mid')
        pygame.mixer.music.play(-1, 0.0)
        run_game()
        pygame.mixer.music.stop()
        show_text_screen('Game over :-(')


def run_game():
    # setup variables for the start of the game
    board = get_blank_board()
    last_move_down_time = time.time()
    last_move_sideways_time = time.time()
    last_fall_time = time.time()
    moving_down = False     # note: there is no movingUp variable
    moving_left = False
    moving_right = False
    score = 0
    level, fall_freq = calc_level_fall_freq(score)

    falling_piece = get_new_piece()
    next_piece = get_new_piece()



    while True:
        # game loop
        if falling_piece is None:
            # No falling piece in play, so start a new piece at the top
            falling_piece = next_piece
            next_piece = get_new_piece()
            last_fall_time = time.time()    # reset last_fall_time

            if not is_valid_pos(board, falling_piece):
                return          # can't fit a new piece on the board, so game over

        check_for_quit()
        for event in pygame.event.get():    # event handling loop
            if event.type == KEYUP:
                if event.key == K_p:
                    # Pausing the game
                    display_surf.fill(bg_color)
                    pygame.mixer.music.stop()
                    show_text_screen('Paused')    # pause until a key press
                    pygame.mixer.music.play(-1, 0.0)
                    last_fall_time = time.time()
                    last_move_down_time = time.time()
                    last_move_sideways_time = time.time()
                elif event.key == K_LEFT:
                    moving_left = False
                elif event.key == K_RIGHT:
                    moving_right = False
                elif event.key == K_DOWN:
                    moving_down = False

            elif event.type == KEYDOWN:
                # moving the piece sideways
                if (event.key == K_LEFT) and is_valid_pos(board, falling_piece, adjX=-1):
                    falling_piece['x'] -= 1
                    moving_left = True
                    moving_right = False
                    last_move_sideways_time = time.time()

                elif (event.key == K_RIGHT) and is_valid_pos(board, falling_piece, adjX=1):
                    falling_piece['x'] += 1
                    moving_right = True
                    moving_left = False
                    last_move_sideways_time = time.time()

                # making the piece fall faster with the down key
                elif event.key == K_DOWN:
                    moving_down = True
                    if is_valid_pos(board, falling_piece, adjY=1):
                        falling_piece['y'] += 1
                    last_move_down_time = time.time()

                # move the current piece all the way down
                elif event.key == K_SPACE:
                    moving_down = False
                    moving_left = False
                    moving_right = False
                    for i in range(1, board_height):
                        if not is_valid_pos(board, falling_piece, adjY=i):
                            break
                    falling_piece['y'] += i - 1

        # handle moving the piece because of user input
        if (moving_left or moving_right) and time.time() - last_move_sideways_time > move_sideways_freq:
            if moving_left and is_valid_pos(board, falling_piece, adjX=-1):
                falling_piece['x'] -= 1
            elif moving_right and is_valid_pos(board, falling_piece, adjX=1):
                falling_piece['x'] += 1
            last_move_sideways_time = time.time()

        if moving_down and time.time() - last_move_down_time > move_down_freq and is_valid_pos(board, falling_piece,
                                                                                               adjY=1):
            falling_piece['y'] += 1
            last_move_down_time = time.time()

        # let the piece fall if it is time to fall
        if (time.time() - last_fall_time) > fall_freq:
            # see if the piece has landed
            if not is_valid_pos(board, falling_piece, adjY=1):
                # falling piece has landed, set it on the board
                add_to_board(board, falling_piece)
                score += remove_complete_words(board, board_width, template_height)
                level, fall_freq = calc_level_fall_freq(score)
                falling_piece = None
            else:
                # piece did not land, just move the piece down
                falling_piece['y'] += 1
                last_fall_time = time.time()

        # drawing everything on the screen
        display_surf.fill(bg_color)
        draw_board(board)
        draw_status(score, level)
        draw_next_piece(next_piece)
        if falling_piece is not None:
            draw_piece(falling_piece)

        pygame.display.update()
        fps_clock.tick(fps)


def make_text_objs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()


def check_for_key_press():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    check_for_quit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def show_text_screen(text):
    # This function displays large text in the
    # center of the screen until a key is pressed.
    # Draw the text drop shadow
    title_surf, title_rect = make_text_objs(text, big_font, olive)
    title_rect.center = ((window_width // 2), ((window_height // 2) - 40))
    display_surf.blit(title_surf, title_rect)

    # Draw the text
    title_surf, title_rect = make_text_objs(text, big_font, text_color)
    title_rect.center = (((window_width // 2) - 3), ((window_height // 2) - 43))
    display_surf.blit(title_surf, title_rect)

    # Display instructions onscreen
    instructions1 = 'Instructions are as follows:'
    title_surf, title_rect = make_text_objs(instructions1, subtitle_font, olive)
    title_rect.center = ((window_width // 2), ((window_height // 2) + 30))
    display_surf.blit(title_surf, title_rect)

    instructions2 = '1) Press the left or right arrow keys to move the letters to either side of the board.'
    title_surf, title_rect = make_text_objs(instructions2, subtitle_font, text_color)
    title_rect.center = ((window_width // 2), (window_height // 2) + 60)
    display_surf.blit(title_surf, title_rect)

    instructions3 = 'Press P to pause the game or Q to quit.'
    title_surf, title_rect = make_text_objs(instructions3, subtitle_font, text_color)
    title_rect.center = ((window_width // 2), ((window_height // 2) + 80))
    display_surf.blit(title_surf, title_rect)

    instructions4 = '2) Press the down arrow key to make a letter move faster.'
    title_surf, title_rect = make_text_objs(instructions4, subtitle_font, text_color)
    title_rect.center = ((window_width // 2), ((window_height // 2) + 100))
    display_surf.blit(title_surf, title_rect)

    instructions5 = 'Press the space key to make a letter fall down right away.'
    title_surf, title_rect = make_text_objs(instructions5, subtitle_font, text_color)
    title_rect.center = ((window_width // 2), ((window_height // 2) + 120))
    display_surf.blit(title_surf, title_rect)

    instructions6 = '3) Try to make the word to the left of the board to level up!'
    title_surf, title_rect = make_text_objs(instructions6, subtitle_font, text_color)
    title_rect.center = ((window_width // 2), ((window_height // 2) + 140))
    display_surf.blit(title_surf, title_rect)

    # Draw the additional "Press a key to play." text.
    press_key_surf, press_key_rect = make_text_objs('press any key to play! ', basic_font, olive)
    press_key_rect.center = ((window_width // 2), (window_height // 2) + 200)
    display_surf.blit(press_key_surf, press_key_rect)

    while check_for_key_press() is None:
        pygame.display.update()
        fps_clock.tick()


def check_for_quit():
    for event in pygame.event.get(QUIT):    # get all the quit events
        terminate()     # terminate if any quit events are present
    for event in pygame.event.get(KEYUP):   # get all the KEYUP events
        if event.key == K_q:
            terminate()     # terminate if the KEYUP event was for the q key
        pygame.event.post(event)    # put the other KEYUP event objects back


def calc_level_fall_freq(score):
    # Based on the score, return the level the player is on and
    # how many seconds pass until a falling piece falls one space.
    level = int(score / 10) + 1
    fall_freq = 0.27 - (level * 0.02)
    return level, fall_freq


def get_new_piece():
    # return a random new piece in a random rotation and color
    shape = random.choice(list(pieces.keys()))
    new_piece = {'shape': shape,
                 'rotation': 0,
                 'x': int(board_width / 2) - int(template_width / 2),
                 'y': -1,   # start it above the board (i.e. less than 0)
                 'color': random.randint(0, len(colors)-1)}
    return new_piece


def add_to_board(board, piece):
    # fill in the board based on piece's location, shape, and rotation
    for x in range(template_width):
        for y in range(template_height):
            if pieces[piece['shape']][piece['rotation']][y][x] != blank:
                board[x + piece['x']][y + piece['y']] = piece['color']


def get_blank_board():
    # create and return a new blank board data structure

    board = []
    for i in range(board_width):
        board.append([blank] * board_height)
    return board


def is_on_board(x, y):
    return x >= 0 and x < board_width and y < board_height


def is_valid_pos(board, piece, adjX=0, adjY=0):
    # Return True if the piece is within the board and not colliding
    for x in range(template_width):
        for y in range(template_height):
            is_above_board = y + piece['y'] + adjY < 0
            if is_above_board or pieces[piece['shape']][piece['rotation']][y][x] == blank:
                continue
            if not is_on_board(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != blank:
                return False
    return True


def is_complete_line(board):
    # checks each 15x5 section of the board (there are 9) for one of five words
    str1 = ""
    for item in board:
        str1 += "".join(str(char) for char in item)
        print(item)
        print(str1)
    if str1[0:15] == ''.join(str(words[x]) for x in sorted(words))[0:15] or str1[0:15] == \
            ''.join(str(words[x]) for x in sorted(words))[45:60]:
        return True
    else:
        return False


def remove_complete_words(board, board_width, template_height):
    # Remove any completed words on the board, move everything above them down, and return the number of complete lines.
    num_words_removed = 0
    y = board_height - 1    # start y at the bottom of the board
    while y >= 0:
        if is_complete_line(board):
            # Remove the line and pull boxes down by one line.
            for pull_down_y in range(y, 0, -1):
                for x in range(board_width):
                    board[x][pull_down_y] = board[x][pull_down_y-1]
            # Set very top line to blank.
            for x in range(board_width):
                for y in range(template_height):
                    board[x][y] = blank
            num_words_removed += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1  # move on to check next row up
    return num_words_removed


def convert_to_pixel_coords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (side_margin + (boxx * box_size)), (top_margin + (boxy * box_size))


def draw_box(boxx, boxy, color, pixelx=None, pixely=None):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if color == blank:
        return
    if pixelx is None and pixely is None:
        pixelx, pixely = convert_to_pixel_coords(boxx, boxy)
    pygame.draw.rect(display_surf, colors[color], (pixelx + 1, pixely + 1, box_size - 1, box_size - 1))
    pygame.draw.rect(display_surf, light_colors[color], (pixelx + 1, pixely + 1, box_size - 4, box_size - 4))


def draw_board(board):
    # draw the border around the board
    pygame.draw.rect(display_surf, border_color, (side_margin - 3, top_margin - 7, (board_width * box_size) + 8,
                                                  (board_height * box_size) + 8), 5)

    # fill the background of the board
    pygame.draw.rect(display_surf, bg_color, (side_margin, top_margin, box_size * board_width, box_size * board_height))
    # draw the individual boxes on the board
    for x in range(board_width):
        for y in range(board_height):
            draw_box(x, y, board[x][y])


    # draw list of words
    word_surf = subtitle_font.render('You are looking for: %s' % word, True, black)
    word_rect = word_surf.get_rect()
    word_rect.topright = (window_width - 600, 75)
    display_surf.blit(word_surf, word_rect)


def draw_status(score, level):
    # draw the score text
    score_surf = subtitle_font.render('Score: %s' % score, True, black)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (window_width - 200, 50)
    display_surf.blit(score_surf, score_rect)

    # draw the level text
    level_surf = subtitle_font.render('Level: %s' % level, True, black)
    level_rect = level_surf.get_rect()
    level_rect.topleft = (window_width - 200, 75)
    display_surf.blit(level_surf, level_rect)


def draw_piece(piece, pixelx=None, pixely=None):
    shape_to_draw = pieces[piece['shape']][piece['rotation']]
    if pixelx is None and pixely is None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convert_to_pixel_coords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(template_width):
        for y in range(template_height):
            if shape_to_draw[y][x] != blank:
                draw_box(None, None, piece['color'], pixelx + (x * box_size), pixely + (y * box_size))


def draw_next_piece(piece):
    # draw the "next" text
    next_surf = subtitle_font.render('Next:', True, gray)
    next_rect = next_surf.get_rect()
    next_rect.topleft = (window_width - 200, 200)
    display_surf.blit(next_surf, next_rect)
    # draw the "next" piece
    draw_piece(piece, pixelx=window_width - 200, pixely=230)


if __name__ == '__main__':
    main()
