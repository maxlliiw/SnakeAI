from time import sleep
from random import randint
from random import choice
import numpy as np
from Tkinter import *

class SnakeGame(Tk):
    UP=0
    RIGHT=1
    DOWN=2
    LEFT=3
    def __init__(self, *args, **kwargs):
	Tk.__init__(self, *args, **kwargs)
        self.width = 20
        self.height = 20
        self.board = self.width*self.height*[0]
	self.score = 0
        self.head = 22
        self.snake = [self.head,self.head+self.width,self.head+(2*self.width)]
        self.food = [10]
        self.last_input = None
       	self.scale = 16
	self.root = Tk()
	self.root.title("SnA*ke")
	self.grid = []
	self.sidebar = Frame(self.root, width=200, bg='white', height=500, relief='sunken', borderwidth=2)
	self.sidebar.pack(expand=True, fill='y', side='left', anchor='nw')	
	self.mainarea = Frame(self.root, bg='#CCC', width=500, height=500)
	self.mainarea.pack(expand=True, fill='both', side='right')
	self.w = Canvas(self.mainarea, width=self.width*self.scale, height=self.height*self.scale)
	self.w.pack()
	for i in range(self.width*self.height):
	    x= (i%self.width)*self.scale
	    y= (i/self.width)*self.scale
	    self.grid.append(self.w.create_rectangle(x,y,x+self.scale,y+self.scale, fill="white"))
	self.scoreboard = Label(self.sidebar, text="0")
	self.scoreboard.pack()
	self.on = True
	self.redraw(100)

    def update(self,cmd):
	if cmd == None:
	    cmd = self.last_input
	self.last_input = cmd
        #Update head location and check for wall collision
        if cmd==SnakeGame.UP and self.head>self.width-1:
            self.head-=self.width
        elif cmd==SnakeGame.RIGHT and self.head%self.width!=self.width-1:
            self.head+=1
        elif cmd==SnakeGame.DOWN and self.head<((self.width-1)*self.height)-1:
            self.head+=self.width
        elif cmd==SnakeGame.LEFT and self.head%self.width!=0:
            self.head-=1
        else:
            self.gameover()
            return
        #Update Snake location
        #By removing the last location the array now represent the new location of
        #the snake body without the new head locaiton
        #If the snake head is on a food tile then retain the end of the snake body
        #and removee the food from the board
        if self.head in self.food:
	    self.score += 1
            self.food.remove(self.head)
            r = randint(0,399)
	    while r in self.snake or r in self.food:
        	r = randint(0,399)
            self.food.append(r)
        else:
            self.snake.pop()
        #Check for Snake on Snake collision
        #If the new head position is already in the snake's
        #collection then there is a collision
        if self.head in self.snake:
            self.gameover()
            return
        #Add the new snake head to the snake
        self.snake.insert(0,self.head)

    def ai(self):
        frontier = [[0,self.head]]
        closed = []
        path = self.astar(frontier,closed)
        if path == None:
            return self.idle() 
	print(path)
        move = path[2]
        diff = self.head - move
        if diff == self.width:
            return SnakeGame.UP
        if diff == -self.width:
            return SnakeGame.DOWN
        if diff == -1:
            return SnakeGame.RIGHT
        if diff == 1:
            return SnakeGame.LEFT
        return None
        
        
    def idle(self):            
	print "idled"
	h = self.head
	moves = []
	if h-self.width>0 and not h-self.width in self.snake:
		moves.append(SnakeGame.UP)
	if h%self.width!=self.width and not h+1 in self.snake:
		moves.append(SnakeGame.RIGHT)
	if h+self.width<self.height*self.width-1 and not h+self.width in self.snake:
		moves.append(SnakeGame.DOWN)
	if h%self.width!=0 and not h-1 in self.snake:
		moves.append(SnakeGame.LEFT)
	if not moves:
		return None
	return choice(moves)
	

    def astar(self,frontier,closed):
        if not frontier:
            return None
        #Explore frontier for shortest path
        shortest = frontier[0]
        for p in frontier:
            if p[0] < shortest[0]:
                shortest = p
        frontier.remove(shortest)
	if len(frontier)<3 and len(closed) > 3:
		return choice(frontier)
        #Expand upon the shortest path
        #Do not include paths that lead into a wall, snake or indexes in closed
        #When a possible path is found update its score and add it to the frontier
	#Update snake
	snake = self.snake[:]
	for i in shortest[2:]:
		snake.pop()
		snake.insert(0, i)
	
        #Expansion of shortest path BEGIN
        #End of shortest path index
        n = shortest[len(shortest)-1]
        #If n is food, we found the shortest path to food
        if n in self.food:
            return shortest
        #close this index
        if not n in closed:
            closed.append(n)
            #UP
            if n>self.width and not n-self.width in self.snake and not n-self.width in closed:
                up = shortest[:]
                up[0] = len(up) + self.h(n-self.width)
                up.append(n-self.width)
                frontier.append(up)
            #DOWN
            if n<(self.width-1)*self.height-1 and not n+self.width in self.snake and not n+self.width in closed:
                down = shortest[:]
                down[0] = len(down) + self.h(n+self.width)
                down.append(n+self.width)
                frontier.append(down)
            #LEFT
            if n%self.width!=0 and not n-1 in self.snake and not n-1 in closed:
                left = shortest[:]
                left[0] = len(left) + self.h(n-1)
                left.append(n-1)
                frontier.append(left)
            #RIGHT
            if n%self.width!=self.width-1 and not n+1 in self.snake and not n+1 in closed:
                right = shortest[:]
                right[0] = len(right) + self.h(n+1)
                right.append(n+1)
                frontier.append(right)
            #END
        return self.astar(frontier,closed)

        
    def h(self, n, snake=None):
	if snake == None:
		snake = self.snake
	#Implement a heuristic that uses the position of the snake

        h_rows = self.height*self.width
        h_cols = self.height*self.width
        for f in self.food:
            #number of rows from n to f
            rows = abs(n/self.width-f/self.width)
            #' ' cols ' ' ' '
            cols = abs(n%self.width-f%self.width)
            if rows<h_rows and cols<h_cols:
                h_rows = rows
                h_cols = cols
        return h_cols + h_rows        
                
    def gameover(self):
        print("Game Over")
	print(self.last_input)
        self.on = False

    def redraw(self, delay):
	self.scoreboard.configure(text=str(self.score))
	if self.on:	
		self.update(self.ai())
		for i in range(len(self.board)):
			color = "white"
			if i in self.snake:
			    color = "black"
			elif i in self.food:
			    color = "gray"
			self.w.itemconfig(self.grid[i], fill=color)
					
		self.after(delay, lambda: self.redraw(delay))

if __name__ == '__main__':
    game = SnakeGame()
    game.mainloop()
