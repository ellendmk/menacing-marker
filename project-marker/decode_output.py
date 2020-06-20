import numpy as np
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib import colors

odds = [1,3,5,7,9,11,13,15,17,19]
evens = [0,2,4,6,8,10,12,14,16,18,20]


def load_file(folder):
	f=open(folder,'r')
	text=f.read()
	return text

def get_games(input_text):
	input_text=input_text.replace(' ','')
	input_text=input_text.split('\n\n')
	k = 0
	while k< len(input_text):
		if len(input_text[k])<3 :
			input_text.remove(input_text[k])
			k-=1
		elif len(input_text[k])>10000:
			input_text[k]=input_text[k][0:9997]+input_text[k][-3:]
			k-=1
		k+=1
	return input_text

def extract_moves(game):
	# Extract the following: board size; pieces left p1; pieces left p2; game outcome;
	# 						 list of dictionaries for moves:
	#						 Fields -> start_pos, end_pos, jumped
	format_issues = 0
	size = 0
	all_lines=game.split('\n')
	while (all_lines[0]==""):
		all_lines= all_lines[1:]
	try:
		size=int(all_lines[0])
	except Exception as error:
		f = open("output_file_test_log.txt","w+")
		f.write("Error in first line of output - size incorrectly recorded in output file.\n")
		f.close()

	#Extract all moves
	moves=[]
	all_lines = [x for x in all_lines if x!='']
	moves_lines = all_lines[0:-3]
	try:
		for i in range(1,len(moves_lines)):
			cur_line = moves_lines[i]
			
			# get player
			player = int(cur_line[1])

			cur_line = cur_line[2:]

			# jump or no jump?
			# is a jump
			if cur_line.find('x')>=0 or cur_line.find('x')>=0:
				#each jump gets own entry into moves
				num_jumps = cur_line.count('x') + cur_line.count('X')
				all_jumps = cur_line.split(')')

				for j in range(num_jumps):
					temp_jump = all_jumps[j].split('x')
					if all_jumps[j].find('x')<0:
						format_issues += 1
						temp_jump = all_jumps[j].split('X')

					start_pos = int(temp_jump[0])
					end_pos, jump = temp_jump[1].split('(')
					# Store current move
					moves.append({'player':player,'start_pos': int(start_pos), 'end_pos': int(end_pos), 'jump': int(jump)})

			# no jump

			elif cur_line.find('-')>=0:

				start_pos, end_pos = cur_line.split('-')
				# Store current move
				moves.append({'player':player,'start_pos': int(start_pos), 'end_pos': int(end_pos), 'jump': None})
	except Exception as error:
		f = open("output_file_test_log.txt","w+")
		f.write("Error in recording of moves of output file.\n")
		f.close()
		# 	
	#Get totals and game outcome
	result_lines = all_lines[-3:]
	results = {}
	try:
		
		for i in range(2):
			player = str(result_lines[i][2])
			total_pieces = int(result_lines[i][3:])
			if player=='1':
				results['player1'] = total_pieces
			elif player=='2':
				results['player2'] = total_pieces
			else:
				results['player1'] = -1
				results['player2'] = -1
		results['result'] = result_lines[2]
	except Exception as error:
		f = open("output_file_test_log.txt","w+")
		f.write("Error in final tally and result lines of output file.\n")
		f.close()
		results['player1']=-1
		results['player2']=-1
		results['result']='error'

	return [size, moves, results]

def label_to_coords(label, size):
	try:
		half = size/2
		row = int((label-1)/half)
		col = 0
		if row % 2 == 0:
			col = int(odds[int((label-1)%half)])
		else:
			col = int(evens[int((label-1)%half)])
		return [row,col]
	except Exception as exc:
		f = open("output_file_test_log.txt","w+")
		f.write("Error in labelling board.\n")
		f.close()
		return [0,0]

def check_label_invalid(label, size):
	upper = (size**2)/2
	total_invalid_labels = 0
	if label==None:
		return 0
	if label<0 or label>upper:
		return 1
	return 0

def count_invalid_labels(moves, size):
	upper = (size**2)/2
	total_invalid_labels = 0
	for move in moves:
		total_invalid_labels += check_label_invalid(move['start_pos'], size)
		total_invalid_labels += check_label_invalid(move['end_pos'], size)
		
		if (check_label_invalid(move['jump'], size)) and move['jump'] != None:
			total_invalid_labels += 1
	return total_invalid_labels

def invalid_move_check(move, board, size):
	# player 1 markers = 0
	# player 2 markers = 1
	# available block  = 2
	player = int(move['player'])
	start  = label_to_coords(move['start_pos'], size)
	end    = label_to_coords(move['end_pos'], size)
	jump   = move['jump']


	if jump != None:
		jump = label_to_coords(jump, size)
		# if start not current player pieces
		# or end not available
		# or jump not opponent
		if int(board[start[0]][start[1]])!=int(player-1) or int(board[end[0]][end[1]])!=int(2) or int(board[jump[0]][jump[1]]) != int(player%2):
			
			return 1	
	else:
		# if start not current player pieces
		# or end not available	

		if int(board[start[0]][start[1]]) != int(player-1) or int(board[end[0]][end[1]]) != int(2):
			return 1
	return 0

def count_compulsory_moves(board, player, size, direction):
	total_moves = 0
	for row in range(size):
		for col in range(size):
			if board[row][col] == (player-1):
				#check first diag has opponent and not at edge
				if ((col+2)<size and (row+2*direction)<size and (row+2*direction)>=0):
					if board[row+direction][col+1] == (player)%2:
					#check next along diag is empty
						if board[row+2*direction][col+2] == 2:
							total_moves += 1
				#check second diag has opponent and not at edge
				if ((col-2)>=0 and (row+2*direction)<size and (row+2*direction)>=0):
					if board[row+direction][col-1] == (player)%2:
						#check next along diag is empty
						if board[row+2*direction][col-2] == 2:
							total_moves += 1
	return total_moves

def init_gameboard(size):
	# 2 = available block
	# -1 = not available (checkerboard)
	# 0 = player 1
	# 1 = player 2
	board = np.ones((size,size))*2
	for r in range(size):
		for c in range(size):
			#leave middle two rows empty
			if (r+c)%2!=1: 
				board[r][c] = -1
			#populate p1 top
			if r<(size/2 - 1) and (r+c)%2==1:
				board[r][c] = 0
			#populate p2 bottom
			if r>(size/2 ) and (r+c)%2==1:
				board[r][c] = 1
	return(board)
			
def next_board(move, board, size):
	new_board = board.copy()
	start 	  = label_to_coords(move['start_pos'], size)
	end       = label_to_coords(move['end_pos'], size)
	jump      = move['jump']
	# Up or down 
	direction = end[0] - start[0]
	if direction < 0:
		direction = -1
	else:
		direction = 1


	comp_move_penalty     = 0
	invalid_move_penalty  = 0
	invalid_label_penalty = count_invalid_labels([move], size)
	
	if invalid_label_penalty > 0:
		f = open("output_file_test_log.txt","w+")
		f.write("Error invalid label.\n")
		f.close() 
		return {"board" : None, "comp_move_penalty": 0, "label_penalty": invalid_label_penalty, "invalid_move_penalty": 0, "direction": None}

	
	if jump == None:
		if count_compulsory_moves(new_board, move['player'], size, direction)!=0:
			comp_move_penalty += 1
		invalid_move_penalty += invalid_move_check(move, new_board, size)
		new_board[start[0]][start[1]] = 2
		new_board[end[0]][end[1]]   = move['player']-1
	else:
		jump = label_to_coords(jump, size)
		invalid_move_penalty += invalid_move_check(move, new_board, size)
		new_board[start[0]][start[1]] = 2
		new_board[jump[0]][jump[1]]  = 2
		new_board[end[0]][end[1]]   = move['player']-1
	#comp_move_penalty - comp move available but no jumps made
	#invalid_move_penalty - perfromed an invalid move
	return {"board":new_board, "comp_move_penalty": comp_move_penalty, "label_penalty": invalid_label_penalty, "invalid_move_penalty": invalid_move_penalty, "direction": direction}

def gen_boards(size, moves):
	results = {}
	#Standard initialization
	board_init1  = init_gameboard(size)
	boards_1 = [board_init1.copy()]

	label_penalty = 0
	comp_move_penalty = 0
	invalid_move_penalty = 0
	directions = {1:[],2:[]}
	for i in range(len(moves)):
		cur_move = next_board(moves[i], boards_1[-1].copy(), size)

		label_penalty 			+= cur_move['label_penalty']
		if label_penalty==0:
			boards_1.append(cur_move['board'].copy())

		comp_move_penalty 		+= cur_move['comp_move_penalty']
		invalid_move_penalty 	+= cur_move['invalid_move_penalty']
		directions[moves[i]['player']].append(cur_move['direction'])

		# If a label is not in valid range cannot decipher output produced so exit
		if label_penalty>0:
			break
	
		
	total_pieces_p1 = np.sum(boards_1[-1] == 0)
	total_pieces_p2 = np.sum(boards_1[-1] == 1)

	results["board1"] = {'pieces_p1':total_pieces_p1, 'pieces_p2':total_pieces_p2, 'boards':boards_1, 'label_penalty':label_penalty, 'invalid_move_penalty': invalid_move_penalty, 'comp_move_penalty':comp_move_penalty,'directions':directions}

	#Opposite initialization
	board_init2 = np.rot90(np.rot90(board_init1))
	boards_2 = [board_init2]

	label_penalty = 0
	comp_move_penalty = 0
	invalid_move_penalty = 0
	
	directions = {1:[],2:[]}

	for i in range(len(moves)):
		cur_move = next_board(moves[i], boards_2[-1].copy(), size)


		label_penalty 			+= cur_move['label_penalty']
		if label_penalty == 0:
			boards_2.append(cur_move['board'].copy())
		comp_move_penalty 		+= cur_move['comp_move_penalty']

		invalid_move_penalty 	+= cur_move['invalid_move_penalty']
		directions[moves[i]['player']].append(cur_move['direction'])

		# If a label is not in valid range cannot decipher output produced so exit
		if label_penalty>0:
			break
		
	total_pieces_p1 = np.sum(boards_2[-1] == 0)
	total_pieces_p2 = np.sum(boards_2[-1] == 1)

	results["board2"] = {'pieces_p1':total_pieces_p1, 'pieces_p2':total_pieces_p2, 'boards':boards_2, 'label_penalty':label_penalty, 'invalid_move_penalty': invalid_move_penalty, 'comp_move_penalty':comp_move_penalty,'directions':directions}

	return results


def count_pieces_final(board, size):
	p1 = 0 #0 marker
	p2 = 0 #1 marker
	
	for i in range(size):
		for j in range(size):
			p1 += board[i][j]==0
			p2 += board[i][j]==1
	return {'pieces_p1':p1, 'pieces_p2':p2}


def create_log_entry_and_get_rating(size, results, pieces, output_file_name, game_results):
	match_total_penalty     = 0
	win_condition_penalty   = 0
	alternating_dir_penalty = 0

	directions = results['directions']

	# text =  "\n------------------------------------------\n"
	text  = "\nBoard size:              " + str(size) + "\n"
	text += "\nRecorded pieces left p1: " + str(results['pieces_p1'])
	text += "\nActual pieces left p1:   " + str(pieces['pieces_p1']) 
	text += "\nDirections of p1:        UP = " + str(directions[1].count(-1)) + "  DOWN = " + str(directions[1].count(1)) + "\n"


	#Check win condition correct according to their tally
	students_piecesp1 = game_results['player1']
	students_piecesp2 = game_results['player2']
	students_result   = game_results['result']
	
	if students_piecesp1!=0 and students_piecesp2!=0 and students_result!='d':
		win_condition_penalty+=1
	if students_piecesp1==0 and students_result.find('1')<0:
		win_condition_penalty+=1
	if students_piecesp2==0 and students_result.find('2')<0:
		win_condition_penalty+=1

	# check no alternating direction - if there is manually check for kings implementation
	if directions[1].count(-1)!=0 and directions[1].count(1) !=0:
		alternating_dir_penalty += 1
	if directions[2].count(-1)!=0 and directions[2].count(1) !=0:
		alternating_dir_penalty += 1


	text += "\nRecorded pieces left p2: " + str(results['pieces_p2'])
	text += "\nActual pieces left p2:   " + str(pieces['pieces_p2'])
	text += "\nDirections of p2:        UP = " + str(directions[2].count(-1)) + "  DOWN = " + str(directions[2].count(1)) + "\n"

	if (results['pieces_p1']==pieces['pieces_p1']) and (results['pieces_p2']==pieces['pieces_p2']):
		text += "\nTotals match:            Yes"
	else:
		text += "\nTotals match:            No"
		match_total_penalty += 1



	text += "\n\nPenalties:\n" 
	text += "\nLabel penalty:           " + str(results['label_penalty'])
	text += "\nInvalid moves made:      " + str(results['invalid_move_penalty'])
	text += "\nCompulsory move penalty: " + str(results['comp_move_penalty'])
	text += "\nTotals match penalty:    " + str(match_total_penalty)
	text += "\nWin condition penalty:   " + str(win_condition_penalty)
	text += "\nAlternating dir penalty: " + str(alternating_dir_penalty)
	if alternating_dir_penalty > 0:
		text += " check for kings implementation"

	# Criteria for code rating
	# ----if label issues - auto poor or unacceptable
	# ----if other issues between 1 and 5 - G
	# ----if other issues between 5 and 10 - A
	# ----if other issues more than 10 - P
	num_aspects_penalised = results['invalid_move_penalty']!=0 +\
							results['comp_move_penalty']!=0 + \
							match_total_penalty!=0 + \
							win_condition_penalty!=0 +\
							int(output_file_name != "results.txt")



	total_penalties = results['invalid_move_penalty'] + results['comp_move_penalty'] + match_total_penalty + win_condition_penalty
	
	# check writing to correct file name
	if output_file_name != "results.txt":
		total_penalties += 5
	score = ""
	#Ratings -> E=4, G=3, A=2, P=1, U=0
	rating = 0
	# Determine code rating for functionality
	if results['label_penalty']>0:
		score = "\nFunctionalty rating:  P or U"
		rating = 1
	elif total_penalties == 0:
		score ="\nFunctionalty rating:  E"
		rating = 4
	elif total_penalties > 0 and total_penalties<=20 and num_aspects_penalised < 2 and results['invalid_move_penalty']==0:
		rating = 3
		score ="\nFunctionalty rating:  G"
	elif total_penalties<=30 or num_aspects_penalised < 3 and results['invalid_move_penalty']==0:
		rating = 2
		score ="\nFunctionalty rating:  A"
	elif total_penalties > 30:
		rating = 1
		score ="\nFunctionalty rating:  P"

		
	text += "\n\n" + score + "\n"
	return {'text':text,'rating':rating}


def plotGrid(boards, gameNo, folder, initialisation):
	boards_to_plot  = len(boards)
	grid_size = math.ceil(math.sqrt(boards_to_plot))
	mpl.rcParams['figure.figsize'] = 10,10
	
	fig=ax=None



	row_count = 0
	col_count = 0
	fig, ax = plt.subplots(grid_size,grid_size)

	# color map for plotting games - to cath any issues
	# unavailable blocks -1: Grey (128,128,128)
	# available blocks 2:    White (255,255,255)
	# player 1:    			 Cyan (0,255,255)
	# player 2:    			 Green (0,204,0)

	colormap={-1:(128,128,128), 2:(255,255,255), 0:(0,255,255), 1:(0,204,0) }
	for b in range(grid_size*grid_size):
		test_rgb = []

		if b<boards_to_plot:
			test_rgb = [[colormap[int(i)] for i in row] for row in boards[b]]
		else:
			temp = [[2,2],[2,2]]
			test_rgb = [[colormap[int(i)] for i in row] for row in temp]

		ax[row_count,col_count].set_xticklabels([])
		ax[row_count,col_count].set_xticks([])
		ax[row_count,col_count].set_yticklabels([])				
		ax[row_count,col_count].set_yticks([])				
		ax[row_count,col_count].grid(b=True,which='major',axis='both')
		ax[row_count,col_count].imshow(test_rgb, interpolation = 'none')
		# ax[row_count,col_count].yaxis.set_major_locator(MultipleLocator(1)) 

		
		col_count+=1
		if col_count >= grid_size:
			col_count = 0
			row_count += 1
	plt.savefig(folder+'/games_'+str(gameNo)+'_init'+str(initialisation)+'.pdf')

def test_output_file(file_path, filename):
	print("DECODE SCRIPT")
	text 			= load_file(file_path+"/"+filename)
	games 			= get_games(text)
	if len(games)<1:
		f = open("game_results_log.txt",'w+')
		f.write("Output format or contents not valid - no games recorded.")
		f.close()
		return 
	game_text_results 	= []
	ratings = {'init1':[],'init2':[]}
	# try:
	for i in range(len(games)):
		game = games[i]
		[size, moves, game_results] = extract_moves(game)
		
		test_results = gen_boards(size, moves)
		board1_results = test_results['board1']
		board2_results = test_results['board2']

		pieces 		 =  count_pieces_final(board1_results['boards'][-1], size)
		text_results =  "###########################################\n"
		text_results += "\nINITIALIZATION 1\n"

		temp 		 =  create_log_entry_and_get_rating(size, board1_results, pieces, filename, game_results)

		text_results += temp['text']
		ratings['init1'].append(temp['rating'])

		pieces 		 = count_pieces_final(board2_results['boards'][-1], size)
		text_results += "\n------------------------------------------\n"
		text_results += "\nINITIALIZATION 2\n"
		temp         =  create_log_entry_and_get_rating(size, board2_results, pieces, filename, game_results)
		text_results += temp['text']
		ratings['init2'].append(temp['rating'])
		text_results += "\n###########################################"

		game_text_results.append(text_results)
		try:
			plotGrid(board1_results['boards'],i,file_path,1)
			plotGrid(board2_results['boards'],i,file_path,2)
		except Exception as error:
			f = open("output_file_test_log.txt","w+")
			f.write("Error producing plots of boards.\n")
			f.close() 


	rating_symbols = ['U','P','A','G','E']

	game_text_results.append(filename+" contents \n\n"+text[0:2000])

	ratings_text = "Ratings for init 1:  [" + ",".join([str(x) for x in ratings['init1']]) + "]  avg = " + str(sum(ratings['init1'])/len(ratings['init1'])) + " Functionality: " + rating_symbols[int(sum(ratings['init1'])/len(ratings['init1']))] 
	
	ratings_text += "\nRatings for init 2:  [" + ",".join([str(x) for x in ratings['init2']]) + "]  avg = " + str(sum(ratings['init2'])/len(ratings['init2'])) + " Functionality: " + rating_symbols[int(sum(ratings['init2'])/len(ratings['init2']))] 

	max_scores = []
	for i in range(len(ratings['init1'])):
		if ratings['init1'][i] >= ratings['init2'][i]:
			max_scores.append(ratings['init1'][i])
		else:
			max_scores.append(ratings['init2'][i])


	ratings_text += "\n\nRatings max:  [" + ",".join([str(x) for x in max_scores]) + "]  avg = " + str(sum(max_scores)/len(max_scores)) + " Functionality: " + rating_symbols[int(sum(max_scores)/len(max_scores))]


	game_text_results = [ratings_text] + game_text_results

	f = open("game_results_log.txt",'w')
	f.write("\n\n".join(game_text_results))

	f.close()
	