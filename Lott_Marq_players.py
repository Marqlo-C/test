import random
import pygame
import math
import sys
import time

# 1. Define Constants at the top level
SQUARESIZE = 100
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
P1COLOR = (255, 0, 0)
P2COLOR = (255, 255, 0)
ROW_COUNT = 6
COLUMN_COUNT = 7
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
RADIUS = int(SQUARESIZE / 2 - 5)

# Initialize screen as None; it will be filled when the game starts
screen = None

class connect4Player(object):
    def __init__(self, position, seed=0, CVDMode=False):
        self.position = position
        self.opponent = None
        self.seed = seed
        random.seed(seed)
        if CVDMode:
            global P1COLOR, P2COLOR
            P1COLOR = (227, 60, 239)
            P2COLOR = (0, 255, 0)

    def play(self, env, move_dict):
        move_dict["move"] = -1

class humanConsole(connect4Player):
    def play(self, env, move_dict):
        move_dict['move'] = int(input('Select next move: '))
        while True:
            if 0 <= int(move_dict['move']) <= 6 and env.topPosition[int(move_dict['move'])] >= 0:
                break
            move_dict['move'] = int(input('Index invalid. Select next move: '))

class humanGUI(connect4Player):
    def play(self, env, move_dict):
        global screen
        # If screen isn't set, grab the surface created by main.py
        if screen is None:
            screen = pygame.display.get_surface()

        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                    posx = event.pos[0]
                    if self.position == 1:
                        pygame.draw.circle(screen, P1COLOR, (posx, int(SQUARESIZE / 2)), RADIUS)
                    else:
                        pygame.draw.circle(screen, P2COLOR, (posx, int(SQUARESIZE / 2)), RADIUS)
                pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    posx = event.pos[0]
                    col = int(math.floor(posx / SQUARESIZE))
                    move_dict['move'] = col
                    done = True

class randomAI(connect4Player):
    def play(self, env, move_dict):
        possible = env.topPosition >= 0
        indices = [i for i, p in enumerate(possible) if p]
        move_dict['move'] = random.choice(indices)

class stupidAI(connect4Player):
    def play(self, env, move_dict):
        possible = env.topPosition >= 0
        indices = [i for i, p in enumerate(possible) if p]
        for pref in [3, 2, 1, 5, 6, 0]:
            if pref in indices:
                move_dict['move'] = pref
                return

class connect4AI(connect4Player):
    def is_game_over(self, env, last_move, last_player):
        if last_move < 0:
            return False
        
        i = env.topPosition[last_move] + 1
        j = last_move
        
        if i >= env.shape[0]:
            return False
        
        count = 0
        for col in range(max(0, j-3), min(env.shape[1], j+4)):
            if env.board[i][col] == last_player:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        count = 0
        for row in range(max(0, i-3), min(env.shape[0], i+4)):
            if env.board[row][j] == last_player:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        count = 0
        start_row = i - min(i, j)
        start_col = j - min(i, j)
        for offset in range(7):
            r = start_row + offset
            c = start_col + offset
            if r >= env.shape[0] or c >= env.shape[1]:
                break
            if env.board[r][c] == last_player:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        count = 0
        start_row = i + min(env.shape[0] - 1 - i, j)
        start_col = j - min(env.shape[0] - 1 - i, j)
        for offset in range(7):
            r = start_row - offset
            c = start_col + offset
            if r < 0 or c >= env.shape[1]:
                break
            if env.board[r][c] == last_player:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        if all(env.topPosition < 0):
            return True
        
        return False
    
    def evaluate(self, env, last_move, last_player):
        if last_move >= 0 and self.is_game_over(env, last_move, last_player):
            if last_player == self.position:
                return 1000000
            else:
                return -1000000
        
        score = 0
        opponent = 3 - self.position
        
        for row in range(env.shape[0]):
            for col in range(env.shape[1] - 3):
                window = [env.board[row][col+i] for i in range(4)]
                score += self.evaluate_window(window, self.position, opponent)
        
        for row in range(env.shape[0] - 3):
            for col in range(env.shape[1]):
                window = [env.board[row+i][col] for i in range(4)]
                score += self.evaluate_window(window, self.position, opponent)
        
        for row in range(env.shape[0] - 3):
            for col in range(env.shape[1] - 3):
                window = [env.board[row+i][col+i] for i in range(4)]
                score += self.evaluate_window(window, self.position, opponent)
        
        for row in range(3, env.shape[0]):
            for col in range(env.shape[1] - 3):
                window = [env.board[row-i][col+i] for i in range(4)]
                score += self.evaluate_window(window, self.position, opponent)
        
        center_col = env.shape[1] // 2
        center_count = sum(1 for row in range(env.shape[0]) if env.board[row][center_col] == self.position)
        score += center_count * 3
        
        return score
    
    def evaluate_window(self, window, player, opponent):
        score = 0
        player_count = window.count(player)
        opponent_count = window.count(opponent)
        empty_count = window.count(0)
        
        if player_count == 4:
            score += 100000
        elif player_count == 3 and empty_count == 1:
            score += 100
        elif player_count == 2 and empty_count == 2:
            score += 10
        
        if opponent_count == 3 and empty_count == 1:
            score -= 80
        elif opponent_count == 2 and empty_count == 2:
            score -= 5
        
        return score
    
    def check_immediate_move(self, env):
        valid_moves = [col for col in range(env.shape[1]) if env.topPosition[col] >= 0]
        opponent = 3 - self.position
        
        for move in valid_moves:
            test_env = env.getEnv()
            row = test_env.topPosition[move]
            test_env.board[row][move] = self.position
            test_env.topPosition[move] -= 1
            if self.is_game_over(test_env, move, self.position):
                return move
        
        for move in valid_moves:
            test_env = env.getEnv()
            row = test_env.topPosition[move]
            test_env.board[row][move] = opponent
            test_env.topPosition[move] -= 1
            if self.is_game_over(test_env, move, opponent):
                return move
        
        return None

class minimaxAI(connect4AI):
    def play(self, env, move_dict):
        self.start_time = time.time()

        if len(env.history[0]) + len(env.history[1]) == 0:
            move_dict['move'] = 3
            return
        
        
        immediate_move = self.check_immediate_move(env)
        if immediate_move is not None:
            move_dict['move'] = immediate_move
            return
        
        depth = 3  # depth for time limit
        best_move = self.minimax_decide(env, depth)
        move_dict['move'] = best_move
    
    def minimax_decide(self, env, depth):

        best_score = float('-inf')
        best_move = 3  # center column as default
        
        valid_moves = [col for col in range(env.shape[1]) if env.topPosition[col] >= 0]
        
        for move in valid_moves:
            if time.time() - self.start_time > 2.95:
                break
            new_env = env.getEnv()
            row = new_env.topPosition[move]
            new_env.board[row][move] = self.position
            new_env.topPosition[move] -= 1
            
            # get score for this move
            score = self.min_value(new_env, depth - 1, move, self.position)
            
            if score > best_score:
                best_score = score
                best_move = move
        

        return best_move
    
    def max_value(self, env, depth, last_move, last_player):
        if time.time() - self.start_time > 2.95:
            return self.evaluate(env, last_move, last_player)
        
        if self.is_game_over(env, last_move, last_player):
            return self.evaluate(env, last_move, last_player)
        
        if depth == 0:
            return self.evaluate(env, last_move, last_player)
        
        value = float('-inf')
        valid_moves = [col for col in range(env.shape[1]) if env.topPosition[col] >= 0]
        
        for move in valid_moves:
            new_env = env.getEnv()
            row = new_env.topPosition[move]
            new_env.board[row][move] = self.position
            new_env.topPosition[move] -= 1
            
            value = max(value, self.min_value(new_env, depth - 1, move, self.position))
        
        return value
    
    def min_value(self, env, depth, last_move, last_player):
        if time.time() - self.start_time > 2.95:
            return self.evaluate(env, last_move, last_player)

        if self.is_game_over(env, last_move, last_player):
            return self.evaluate(env, last_move, last_player)
        

        if depth == 0:
            return self.evaluate(env, last_move, last_player)
        
        value = float('inf')
        opponent_position = 3 - self.position  # 1->2, 2->1
        valid_moves = [col for col in range(env.shape[1]) if env.topPosition[col] >= 0]
        
        for move in valid_moves:
            new_env = env.getEnv()
            row = new_env.topPosition[move]
            new_env.board[row][move] = opponent_position
            new_env.topPosition[move] -= 1
            
            value = min(value, self.max_value(new_env, depth - 1, move, opponent_position))
        
        return value


class alphaBetaAI(connect4AI):
    def play(self, env, move_dict):
        self.start_time = time.time()
        
        # first move hardcoded
        if len(env.history[0]) + len(env.history[1]) == 0:
            move_dict['move'] = 3
            return
        

        immediate_move = self.check_immediate_move(env)
        if immediate_move is not None:
            move_dict['move'] = immediate_move
            return
        
        depth = 5  

        best_move = self.alphbet_decide(env, depth)
        move_dict['move'] = best_move
    
    def alphbet_decide(self, env, depth):
        
        best_score = float('-inf')
        best_move = 3  # center column as default
        alpha = float('-inf')
        beta = float('inf')
        
        
        valid_moves = [col for col in range(env.shape[1]) if env.topPosition[col] >= 0]
        
        center = env.shape[1] // 2
        valid_moves.sort(key=lambda x: abs(x - center))
        
        for move in valid_moves:
            if time.time() - self.start_time > 2.95:
                break
            new_env = env.getEnv()
            row = new_env.topPosition[move]
            new_env.board[row][move] = self.position
            new_env.topPosition[move] -= 1
            
        
            score = self.min_value(new_env, depth - 1, alpha, beta, move, self.position)
            
        
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
        
        return best_move
    
    def max_value(self, env, depth, alpha, beta, last_move, last_player):
        if time.time() - self.start_time > 2.955:
            return self.evaluate(env, last_move, last_player)

        if self.is_game_over(env, last_move, last_player):
            return self.evaluate(env, last_move, last_player)
        
        if depth == 0:
            return self.evaluate(env, last_move, last_player)
        
        value = float('-inf')
        valid_moves = [col for col in range(env.shape[1]) if env.topPosition[col] >= 0]
        
        for move in valid_moves:
            new_env = env.getEnv()
            row = new_env.topPosition[move]
            new_env.board[row][move] = self.position
            new_env.topPosition[move] -= 1
            
            value = max(value, self.min_value(new_env, depth - 1, alpha, beta, move, self.position))
            
            if value >= beta:
                return value  # beta cuttoff
            alpha = max(alpha, value)
        
        return value
    
    def min_value(self, env, depth, alpha, beta, last_move, last_player):
        if time.time() - self.start_time > 2.95:
            return self.evaluate(env, last_move, last_player)
        
        if self.is_game_over(env, last_move, last_player):
            return self.evaluate(env, last_move, last_player)
        
        if depth == 0:
            return self.evaluate(env, last_move, last_player)
        
        value = float('inf')
        opponent_position = 3 - self.position  
        valid_moves = [col for col in range(env.shape[1]) if env.topPosition[col] >= 0]
        
        for move in valid_moves:
            new_env = env.getEnv()
            row = new_env.topPosition[move]
            new_env.board[row][move] = opponent_position
            new_env.topPosition[move] -= 1
            
            value = min(value, self.max_value(new_env, depth - 1, alpha, beta, move, opponent_position))
            
            if value <= alpha:
                return value  # alpha cuttoff
            beta = min(beta, value)
        
        return value

# This block ensures the screen only initializes if you run players.py directly
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    print("Running local test mode...")