__author__ = 'Priyanka'
import operator
import sys

#input from the file
f = open(sys.argv[-1], 'r')
#f=open('input.txt','r')
play_method = int(f.readline().rstrip('\n'))
if play_method!=4:
    my_player = f.readline().rstrip()
    depth = int(f.readline().rstrip('\n'))
    max_depth = depth
    if my_player == 'X':
        opponent = 'O'
    else:
        opponent = 'X'
else:
    player1 = f.readline().rstrip()
    player1_mode=f.readline().rstrip()
    player1_depth=int(f.readline().rstrip('\n'))
    player2=f.readline().rstrip()
    player2_mode=f.readline().rstrip()
    player2_depth=int(f.readline().rstrip('\n'))
    if player2_mode=='2':
        my_player=player2
        max_depth=player2_depth
    if player1_mode=='2':
        my_player=player1
        max_depth=player1_depth

range_size = range(5)
directions = [ (-1, 0),
              (0, -1), (0, 1),
              (1, 0)]
rows = [1, 2, 3, 4, 5]
columns = ['A', 'B', 'C', 'D', 'E']



n=1
board_value = []      #store value of baord
while n <= 5:
    line = f.readline();
    board_value.append(map(int,(line.split())))
    n += 1

n = 1
start_board = []        #store board state
while n <= 5:
    start_board.append(list(f.readline().rstrip()))
    n += 1

def greedy_best_first(board,player_me):
    board_final=board
    if player_me=="X":
        player_opponent="O"
    else:
        player_opponent="X"
    sneak_max=get_next_sneak_moves(board)

    raid_max=get_next_raid_moves(board,player_me)

    if sneak_max[1]>=raid_max[1]:
        i=sneak_max[0][0]
        #print i
        j=raid_max[0][1]
        if board[i-1][j]==player_opponent and i>=1:
                board_final[i-1][j]=player_me
        if i<4 and board[i+1][j]==player_opponent:
                board_final[i+1][j]=player_me
        if board[i][j-1]==player_opponent and j>=1:
                board_final[i][j-1]=player_me
        if j<4 and board[i][j+1]==player_opponent:
                board_final[i][j+1]=player_me

        board_final_state=writeToFile(board_final,sneak_max,player_me)
    else:
        i=raid_max[0][0]
        #print i
        j=raid_max[0][1]
        if board[i-1][j]==player_opponent and i>=1:
                board_final[i-1][j]=player_me
        if i<4 and board[i+1][j]==player_opponent:
                board_final[i+1][j]=player_me
        if board[i][j-1]==player_opponent and j>=1:
                board_final[i][j-1]=player_me
        if j<4 and board[i][j+1]==player_opponent:
                board_final[i][j+1]=player_me
        board_final_state=writeToFile(board_final,raid_max,player_me)

    #check if position of sneak value available
    return board_final_state

#gets next possible sneak moves
def get_next_sneak_moves(board):
    board_temp=board_value
    flag=0
    while flag==0:
        xyz = zip(*board_temp)
        sneak=map(max, xyz)
        #print sneak
        sneak_value= max(sneak)
        #print "Highest Sneak Vale",sneak_location,sneak_value
        sneak_location= search(board_value,sneak_value)
        if board[sneak_location[0]][sneak_location[1]]=='*':
            flag=1
            return sneak_location,sneak_value
        else:
            sneak_location_temp= search(board_temp,sneak_value)
            board_temp[sneak_location_temp[0]][sneak_location_temp[1]]=0
    return


#gets next possible raid moves
def get_next_raid_moves(board,player_me):
    board_initial_state=board
    max=0
    if player_me=="X":
        player_opponent="O"
    else:
        player_opponent="X"
    board_temp=board_value
    for i in range(len(board_initial_state)):
        part=board_initial_state[i]
        for j in range(len(part)):
            a,b,c,d=0,0,0,0
            if board_initial_state[i][j]=='*':
                if board_initial_state[i-1][j]==player_opponent and i>=1:
                    a=board_temp[i-1][j]
                if i<4 and board_initial_state[i+1][j]==player_opponent:
                    b=board_temp[i+1][j]
                if board_initial_state[i][j-1]==player_opponent and j>=1:
                    c=board_temp[i][j-1]
                if j<4 and board_initial_state[i][j+1]==player_opponent:
                    d=board_temp[i][j+1]
                if max<board_temp[i][j]+a+b+c+d:
                        max=board_temp[i][j]
        raid_location= search(board_value,max)
    return raid_location,max,a,b,c,d

#search and return a location
def search(lst, item):
    for i in range(len(lst)):
        part = lst[i]
        for j in range(len(part)):
            if part[j] == item: return (i, j)
    return None

#write to a file
def writeToFile(board_final,location,player_me):
    board_final_state=board_final
    board_final_state[location[0][0]][location[0][1]]=player_me
    #print board_final_state
    fopen = open("next_state.txt", "w")
    for item in board_final_state:
        for i in item:
            fopen.writelines(str(i))
        fopen.write("\n")
    return board_final_state

#deepcopy function
def deepcopy(A):
    rt = []
    for elem in A:
        if isinstance(elem,list):
            rt.append(deepcopy(elem))
        else:
            rt.append(elem)
    return rt

#opponent
def opponent1(player):
    if player == 'X':
        return 'O'
    else:
        return 'X'

#evaluate function
def evaluate(me, opponent, board):
    my_score, opponent_score = 0, 0
    i, j = 0, 0
    while i < 5:
        j = 0
        while j < 5:
            if board[i][j] == '*':
                pass
            elif board[i][j] == me:
                my_score += board_value[i][j]
            else:
                opponent_score += board_value[i][j]
            j += 1
        i += 1

    return my_score, opponent_score

#generate moves on a board for a move
def generate_moves(board, player):
        if player == 'X':
            opp = 'O'
        else:
            opp = 'X'
        moves = []
        i,j=0,0
        while i < 5:
            j=0
            while j <5:
                if board[i][j] == '*':
                    #print moves,i,j
                    moves.append((i, j))
                j+=1
            i+=1

        return moves
#print generate_moves(start_board,my_player)

#make moves
def make_move(board, move, player):
        board_copy = deepcopy(board)
        if move is None:
            return "NoValidMove"
        if player == 'X':
            opp = 'O'
        else:
            opp = 'X'
        i=move[0]
        j=move[1]
       # print i,j
        flag=0
        if i-1>=0 and j>=0 and j<5 and i<5:
            if board[i-1][j]==player:
                flag+=1
        if j-1>=0  and i>=0 and i<5 and j<5:
            if board[i][j-1]==player:
                flag+=1
        if i+1<5 and j>=0 and j<5 and i>=0:
            if board[i+1][j]==player:
                flag+=1
        if j+1<5 and i>=0 and i<5 and j>=0:
            if board[i][j+1]==player:
                flag+=1
        if flag>0:
            board_copy[move[0]][move[1]] = player
        #print "Make move",board_copy
            for d in directions:
                make_flips(move, player, board_copy, d)

        else:
            board_copy[move[0]][move[1]] = player

        return evaluate(player, opp, board_copy), board_copy, move

#make raids
def make_flips(move, player, board, direction):
    if player == 'X':
            opp = 'O'
    else:
            opp = 'X'
    square=tuple(map(operator.add, move, direction))
    i=square[0]
    j=square[1]
    flag=0
    #print square

    #print board[i][j],i,j
    if i-1>=0 and j>=0 and j<5 and i<5:
        if board[i-1][j]==player and board[i][j]==opp:
            flag+=1
            #print board[i-1][j],board[i][j],i,j,"a"
            board[i][j]=player
    if j-1>=0  and i>=0 and i<5 and j<5:
        if board[i][j-1]==player and board[i][j]==opp:
            flag+=1
            #print board[i][j-1],board[i][j],i,j,"b"
            board[i][j]=player

    if i+1<5 and j>=0 and j<5 and i>=0:
        if board[i+1][j]==player and board[i][j]==opp:
            flag+=1
            #print board[i+1][j],board[i][j],i,j,"c"
            board[i][j]=player

    if j+1<5 and i>=0 and i<5 and j>=0:
        if board[i][j+1]==player and board[i][j]==opp:
            flag+=1
            #print board[i][j+1],board[i][j],i,j,"d"
            board[i][j]=player

    if i>=0 and i<5 and j>=0 and j<5 and flag>0:
            if board[i][j]==opp:
                board[i][j]=player
                #print "hello#"
    return

log = str()
def minimax_decision(board, depth, player):
    global log
    if player == my_player:
        best = -99999
    else:
        best = 99999
    if player == 'X':
        opponent='O'
    else:
        opponent='X'
    moves = generate_moves(board, player)
    i = 0
    if moves[0] is not None:
        best_moves = list()
        while i < len(moves):
            b = deepcopy(board)
            mv = make_move(b, moves[i], player)
            b = mv[1]
            if depth == max_depth:
                log += '\n'+"root"+','+str(0)+','+str(best)
            if player == my_player:
                eval = minimax_value(b, depth-1, opponent, moves[i])
                val = max(eval, best)
            else:
                eval = minimax_value(b, depth-1, my_player, moves[i])
                val = min(eval, best)
            best = val
            best_moves.append([best, moves[i]])
            i += 1
        if max_depth - depth == 0:
            log += '\n'+"root"+','+str(0)+','+str(best)
    elif max_depth - depth == 0:
        outcome = evaluate(my_player, opponent, board)
        log += '\n'+"root"+','+str(0)+','+str(best)
        dec = minimax_decision(board, depth-1, opponent1(player))
        best = dec[0]
        best_moves = dec[1]
        log += '\n'+"pass"+','+str(1)+','+str(best)
        log += '\n'+"root"+','+str(0)+','+str(best)
    else:
        best_moves = None
    return best, best_moves

def minimax_value(board, depth, player, move, passv = None):
    global log
    if player == my_player:
        best = -99999
    else:
        best = 99999
    if player == 'X':
        opponent='O'
    else:
        opponent='X'
    if depth == 0:
        outcome = evaluate(my_player, opponent, board)
        log += '\n'+str(columns[move[1]])+str(rows[move[0]])+','+str(max_depth)+','+str(outcome[0]-outcome[1])
        return outcome[0] - outcome[1]
    moves = generate_moves(board, player)
    if passv == None:
        log += "\n" + str(columns[move[1]]) + str(rows[move[0]]) + ',' + str(max_depth - depth) + ',' + str(best)
    if moves[0] is not None:
        i = 0
        while i < len(moves):
            b = deepcopy(board)
            mv = make_move(b, moves[i], player)
            b = mv[1]
            if player == my_player:
                mval = minimax_value(b, depth - 1, opponent, moves[i])
                val = max(mval, best)
            else:
                mval = minimax_value(b, depth - 1, my_player, moves[i])
                val = min(mval, best)
            best = val
            if passv == None:
                log += "\n" + str(columns[move[1]]) + str(rows[move[0]]) + ',' + str(max_depth - depth) + ',' + str(best)
            if passv == True:
                log += "\n" + "pass" + ',' + str(max_depth - depth) + ',' + str(best)
            i += 1
    else:
        log += "\npass,"+str(max_depth - depth + 1)+","+str(-1*best)
        if player == my_player:
            mval = minimax_value(board, depth - 1, opponent, move, True)
            val = max(mval, best)
            log += "\n" + str(columns[move[1]]) + str(rows[move[0]]) + ',' + str(max_depth - depth) + ',' + str(val)
        else:
            mval = minimax_value(board, depth - 1, my_player, move, True)
            val = min(mval, best)
            log += "\n" + str(columns[move[1]]) + str(rows[move[0]]) + ',' + str(max_depth - depth) + ',' + str(val)
        best = val
    return val

#ALPHA BETA PRUNING
log = log.replace("-99999", "-Infinity")
log = log.replace("99999", "Infinity")

def alphabeta_decision(board, depth, player):
    global log
    val = list()
    evalu = list()
    moves = generate_moves(board, player)
    i = 0
    if player == my_player:
        best = -99999
    else:
        best = 99999
    alpha = -99999
    beta = 99999
    if moves[0] is not None:
        best_moves = list()
        while i < len(moves):
            b = deepcopy(board)
            mv = make_move(b, moves[i], player)
            b = mv[1]
            if depth == max_depth:
                log += '\n'+"root"+','+str(0)+','+str(best) + "," + str(alpha) + "," + str(beta)
            else:
                log += '\n'+"pass"+','+str(max_depth - depth)+','+str(best) + "," + str(alpha) + "," + str(beta)
            if player == my_player:
                eval = alphabeta_value(b, depth-1, opponent, alpha, beta, moves[i])
                val = max(eval[0], best)
                alpha = max(eval[1], alpha)
            else:
                eval = alphabeta_value(b, depth-1, my_player, alpha, beta, moves[i])
                val = min(eval[0], best)
                beta = min(eval[1], beta)
            best = val
            best_moves.append([best, moves[i]])
            i += 1
        if max_depth - depth == 0:
            log += '\n'+"root"+','+str(0)+','+str(best) + "," + str(alpha) + "," + str(beta)
    elif max_depth - depth == 0:
        outcome = evaluate(my_player, opponent, board)
        log += '\n'+"root"+','+str(0)+','+str(best) + "," + str(alpha) + "," + str(beta)
        abd = alphabeta_decision(board, depth-1, opponent1(player))
        best = abd[0]
        best_moves = abd[1]
        log += '\n'+"pass"+','+str(1)+','+str(best) + "," + str(abd[2]) + "," + str(abd[3])
        log += '\n'+"root"+','+str(0)+','+str(best) + "," + str(abd[3]) + "," + str(-1*abd[2])
    else:
        best_moves = None
    return best, best_moves, alpha, beta

def alphabeta_value(board, depth, player, alpha, beta, move, passv = None):
    global log
    if depth == 0:
        outcome = evaluate(my_player, opponent, board)
        log += '\n'+str(columns[move[1]])+str(rows[move[0]])+','+str(max_depth)+','+str(outcome[0]-outcome[1]) + "," + str(alpha) + "," + str(beta)
        return outcome[0] - outcome[1], None, None
    if player == my_player:
        best = -99999
    else:
        best = 99999
    moves = generate_moves(board, player)
    #print moves
    #log += '\n' + str(columns[move[1]]) + str(rows[move[0]]) + ',' + str(max_depth - depth) + ',' + str(best) + "," + str(alpha) + "," + str(beta)
    if passv == None:
        log += "\n" + str(columns[move[1]]) + str(rows[move[0]]) + ',' + str(max_depth - depth) + ',' + str(best) + "," + str(alpha) + "," + str(beta)

    if moves[0] is not None:
        i = 0
        while i < len(moves):
            movebeta = beta
            movealpha = alpha
            if alpha < beta:
                b = deepcopy(board)
                mv = make_move(b, moves[i], player)
                b = mv[1]
                if player == my_player:
                    #best = -10000
                    mval = alphabeta_value(b, depth - 1, opponent, alpha, beta, moves[i])
                    val = max(mval[0], best)
                    if mval[1] == None:
                        alpha = max(alpha, mval[0])
                        #alpha = mval[0]
                    else:
                        alpha = max(alpha, mval[1])

                    #return max(best, val)
                else:
                    #best = 10000
                    mval = alphabeta_value(b, depth - 1, my_player, alpha, beta, moves[i])
                    val = min(mval[0], best)
                    if mval[1] == None:
                        beta = min(beta, mval[0])
                        #beta = mval[0]
                    else:
                        beta = min(beta, mval[1])


                    #beta = min(beta, mval[1])
                    #return min(best, val)
                best = val
                #return val
                if passv == None:
                    log += "\n" + str(columns[move[1]]) + str(rows[move[0]]) + ',' + str(max_depth - depth) + ',' + str(best) + "," + str(alpha) + "," + str(beta)#Priya
                if passv == True:
                    log += "\n" + "pass" + ',' + str(max_depth - depth) + ',' + str(best) + "," + str(movealpha) + "," + str(movebeta)
                    #log += "\n" + str(columns[move[1]]) + str(rows[move[0]]) + ',' + str(max_depth - depth - 1) + ',' + str(best) + "," + str(alpha) + "," + str(beta)

            else:

                val = best
                if player == my_player:
                    return val, alpha, beta
                else:
                    return val, beta, alpha
                #log += "\nPass"

            #log += "\n" + str(columns[move[1]]) + str(rows[move[0]]) + ',' + str(max_depth - depth) + ',' + str(val) + "," + str(alpha) + "," + str(beta) + "," + str(movealpha) + "," + str(movebeta)
            i += 1
    else:
        movealpha = alpha
        movebeta = beta
        log += "\npass,"+str(max_depth - depth + 1)+","+str(-1*best)+","+str(alpha)+","+str(beta)
        if player == my_player:
                #best = -10000
            mval = alphabeta_value(board, depth - 1, opponent, alpha, beta, move, True)
            val = max(mval[0], best)
            if mval[1] == None:
                alpha = max(alpha, mval[0])
            else:
                alpha = max(alpha, mval[1])
            printalpha = max(alpha, movealpha)
            printbeta = max(beta, movebeta)
            log += "\n" + str(columns[move[1]]) + str(rows[move[0]]) + ',' + str(max_depth - depth) + ',' + str(val) + "," + str(printalpha) + "," + str(printbeta)

                #return max(best, val)
        else:
            #best = 10000
            mval = alphabeta_value(board, depth - 1, my_player, alpha, beta, move, True)
            val = min(mval[0], best)
            if mval[1] == None:
                beta = min(beta, mval[0])
            else:
                beta = min(beta, mval[1])
            printalpha = min(movealpha, alpha)
            printbeta = max(movebeta, beta)

            log += "\n" + str(columns[move[1]]) + str(rows[move[0]]) + ',' + str(max_depth - depth) + ',' + str(val) + "," + str(printalpha) + "," + str(printbeta)
        #log += "\n" + str(columns[move[1]]) + str(rows[move[0]]) + ',' + str(max_depth - depth) + ',' + str(best) + "," + str(movealpha) + "," + str(movebeta)


    if player == my_player:
        return val, alpha, beta
    else:
        return val, beta, alpha


def boardFull(start_board):
    i=0
    j=0
    while i<5:
        j=0
        while j<5:
            if start_board[i][j]=='*':
                return 1
            j+=1
        i+=1

    return 0

#print boardFull(start_board)

def battle_simulation(board,player1,player2,player1_depth,player2_depth,player1_mode,player2_mode):
    j=0
    fopen = open("trace_state.txt", "w")
    while j<=3 and boardFull(board)==1 :
        
        if player1_mode=='1':
            #print player1_mode,player1
            board=greedy_best_first(board,player1)
            #print board,"greedy"
            fopen.writelines("hhgjhkjkk \n")

            for item in board:
                for i in item:
                    fopen.writelines(str(i))
                fopen.write("\n")
            #print "********"
        if player2_mode=='2':
            minimax_moves = minimax_decision(board, player2_depth, player2)[1]

            if minimax_moves is not None:
                minimax_move = minimax_moves[0]
                i = 0
                while i < len(minimax_moves):
                    if minimax_moves[i][0] > minimax_move[0]:
                        minimax_move = minimax_moves[i]
                    i += 1
            minimaxboard = deepcopy(board)
            next_state = make_move(minimaxboard, minimax_move[1], player2)[1]
        else:
            next_state = board
            outcome = evaluate(my_player, opponent, board)
        j+=1

        next_state_str = str()
        i = 0
        #print next_state,"minimax"
        while i < len(next_state):
            line = str(next_state[i]).replace('[','')
            line = line.replace(']', '')
            line = line.replace(',','')
            line = line.replace("\'",'')
            line = line.replace(" ",'')
            next_state_str += line+'\n'
            i += 1
        #print next_state_str
        board=next_state
        fopen.write("Minimax \n")
        fopen.write(next_state_str)
    return

if play_method==1:
    greedy_best_first(start_board,my_player)



if play_method == 2:
    minimax_moves = minimax_decision(start_board, max_depth, my_player)[1]
    if minimax_moves is not None:
        minimax_move = minimax_moves[0]
        i = 0
        while i < len(minimax_moves):
            if minimax_moves[i][0] > minimax_move[0]:
                minimax_move = minimax_moves[i]
            i += 1
        minimaxboard = deepcopy(start_board)
        next_state = make_move(minimaxboard, minimax_move[1], my_player)[1]
        log = log.replace("-99999", "-Infinity")
        log = log.replace("99999", "Infinity")
    else:
        next_state = start_board
        outcome = evaluate(my_player, opponent, start_board)
        log = "\nroot,0,"+str(outcome[0]-outcome[1])
    next_state_str = str()
    i = 0
    while i < len(next_state):
        line = str(next_state[i]).replace('[','')
        line = line.replace(']', '')
        line = line.replace(',','')
        line = line.replace("\'",'')
        line = line.replace(" ",'')
        next_state_str += line+'\n'
        i += 1
    f = open("next_state.txt", "w")
    f.write(next_state_str)
    f.close()
    f = open("traverse_log.txt", "w")
    f.write("Node,Depth,Value"+log)
    f.close()

###############MINIMAX WORKS###########################


if play_method == 3:
    best_moves = alphabeta_decision(start_board, max_depth, my_player)[1]
    #print best_moves
    if best_moves is not None:
        best_move = best_moves[0]
        i = 0
        while i < len(best_moves):
            if best_moves[i][0] > best_move[0]:
                best_move = best_moves[i]
            i += 1

        board = deepcopy(start_board)
        next_state = make_move(board, best_move[1], my_player)[1]
        #print minimaxboard
        log = log.replace("-99999", "-Infinity")
        log = log.replace("99999", "Infinity")
        #print log

    else:
        next_state = start_board
        outcome = evaluate(my_player, opponent, start_board)
        log = "\nroot,0,"+str(outcome[0]-outcome[1])+",-Infinity,Infinity"

    next_state_str = str()
    i = 0
    while i < len(next_state):
        line = str(next_state[i]).replace('[','')
        line = line.replace(']', '')
        line = line.replace(',','')
        line = line.replace("\'",'')
        line = line.replace(" ",'')
        next_state_str += line+'\n'
        i += 1
    #next_state_str = next_state_str.rstrip('\n')
    f = open("next_state.txt", "w")
    f.write(next_state_str)
    f.close()
    f = open("traverse_log.txt", "w")
    f.write("Node,Depth,Value,Alpha,Beta"+log)
    #f.write(log)
    f.close()
if play_method == 4:
    battle_simulation(start_board,player1,player2,player1_depth,player2_depth,player1_mode,player2_mode)