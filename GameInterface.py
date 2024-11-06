
from tkinter import *
import random 

import Game
import AIPlayer

class GameInterface:
    def __init__(self,game,title="Default",geometry="750x500"):
        self.game = game
        self.currentState = self.game.initial

        ## Initialize environemnt
        self.root = Tk()
        self.root.title( title )
        self.root.geometry( geometry )

        ## Set up canvas for input window
        self.canvas = Canvas( self.root, width=500, height=500 )
        self.canvas.place(x=0,y=0)
        
        ## Bind mouse clicks to canvas
        self.canvas.bind("<Button-1>", self.click)
        #self.canvas.bind("<Button-3>", self.clear)
        self.waiting = BooleanVar()
        self.waiting.set(1)
        self.move = None

        ## set up radio button: opponent type, search depth
        self.control = Frame(self.root)
        self.control.place(x=510,y=10)

        Label(self.control, width=13, text="Computer play").pack(anchor=W)
        self.controlFrame1 = Frame(self.control,height=2,bd=1,relief=SUNKEN)
        self.controlFrame1.pack(fill=X, padx=5, pady=5)
        self.mode = IntVar()
        self.mode.set(1)

        self.depth = IntVar()
        self.depth.set(4)

        playouts_choices = [10,100,1000]
        self.nPlayouts = IntVar()        
        self.nPlayouts.set(playouts_choices[0])
        
        
        Radiobutton(self.controlFrame1, text="Random", variable=self.mode, value=1).pack(anchor=W)
        Radiobutton(self.controlFrame1, text="MiniMax", variable=self.mode, value=2).pack(anchor=W)
        Radiobutton(self.controlFrame1, text="AlphaBeta", variable=self.mode, value=3).pack(anchor=W)
        Radiobutton(self.controlFrame1, text="AlphaBeta with cutoff", variable=self.mode, value=4).pack(anchor=W)
        Radiobutton(self.controlFrame1, text="Pure Monte Carlo search", variable=self.mode, value=5).pack(anchor=W)
        Radiobutton(self.controlFrame1, text="Monte Carlo Tree Search", variable=self.mode, value=6).pack(anchor=W)


        self.controlFrame2 = Frame(self.control,height=2,bd=0,borderwidth=1,relief=SUNKEN)
        self.controlFrame2.pack(fill=X, padx=5, pady=10)
        Label(self.controlFrame2, text="Search tree depth").pack(anchor=W)        
        self.depthControl = Spinbox(self.controlFrame2,from_=1,to=10,width=2,textvariable=self.depth,state=DISABLED)
        self.depthControl.pack()

        Label(self.controlFrame2, text="MC Playouts").pack(anchor=W)
        self.nPlayoutsControl = OptionMenu(self.controlFrame2,self.nPlayouts,*playouts_choices)
        self.nPlayoutsControl.configure(state=DISABLED)
        self.nPlayoutsControl.pack()
        
        ## Disable depth spinbox unless cutoff is selected
        self.mode.trace("w", lambda name, index, mode: self.depthControl.configure(state=['normal' if self.mode.get()==4 else 'disabled']))

        ## Disable simulation count menu unless MC is selected
        self.mode.trace("w", lambda name, index, mode: self.nPlayoutsControl.configure(state=['normal' if (self.mode.get()==5 or self.mode.get() == 6) else 'disabled']))


        Button(self.control, text="Reset", command=self.reset).pack(anchor=W,fill=X)
        Button(self.control, text="Exit", command=self.exit).pack(anchor=W,fill=X)

        self.message = StringVar()
        self.message.set("")
        self.messageArea = Label(self.control,font=("Helvetica", 16),textvariable=self.message)
        self.messageArea.pack(fill=X, padx=5, pady=10)
        

        self.play()

    
    def draw(self):
        ## Draw the board lines  
        for i in range(0,500,int(500/self.game.v)):
            self.canvas.create_line(0,i,500,i);
        for i in range(0,500,int(500/self.game.h)):
            self.canvas.create_line(i,0,i,500);

        ## Draw the moves
        board = self.currentState.board
        for x in range(1, self.game.h+1):
            for y in range(1, self.game.v+1):
                self.canvas.create_text(((x-1)*(500/self.game.h)+(250/self.game.h),(y-1)*(500/self.game.v)+250/self.game.v),text=board.get((x,y),''),font=("Helvetica",44,"bold"));
        self.root.update_idletasks()
        self.root.update()

    def exit( self ):
        self.canvas.delete("all")
        self.waiting.set(0)
        self.currentState = self.game.initial
        self.root.destroy()

    def reset( self ):
        self.canvas.delete("all")
        self.message.set("")
        self.root.update_idletasks()
        self.root.update()
        self.play()
        
    def click( self, event ):
        if not self.waiting.get(): return
        self.move = (int(event.x/(500/self.game.h))+1,int(event.y/(500/self.game.v))+1)
        #print(self.move)
        #print(self.currentState.moves)
        self.waiting.set(0)
        
    def play(self):
        self.currentState = self.game.initial
        while True:

            ## Computer moves
            self.message.set("thinking...")
            self.draw()
            if self.mode.get() == 1:
                move = AIPlayer.random_decision(self.currentState, self.game)
            elif self.mode.get() == 2:
                move = AIPlayer.minimax_decision(self.currentState, self.game)
            elif self.mode.get() == 3:
                move = AIPlayer.alphabeta_decision(self.currentState, self.game)
            elif self.mode.get() == 4:
                move = AIPlayer.alphabeta_cutoff_decision(self.currentState, self.game, self.depth.get())
            elif self.mode.get() == 5:
                move = AIPlayer.pure_mc_decision(self.currentState, self.game, self.nPlayouts.get())
            elif self.mode.get() == 6:
                move = AIPlayer.mcts_decision(self.currentState, self.game, self.nPlayouts.get())

            self.currentState = self.game.make_move(move,self.currentState)
            self.draw()

            if self.game.terminal_test(self.currentState):
                self.processEndGame()
                self.draw()
                return

            ## Wait for player to move
            self.move = None
            while self.move not in self.game.legal_moves(self.currentState):
                self.waiting.set(1)
                self.message.set("waiting for player...")
                self.canvas.wait_variable(self.waiting)

            ## Update board with move and draw
            move = self.move
            self.currentState = self.game.make_move(move,self.currentState)
            self.draw()
            
            if self.game.terminal_test(self.currentState):
                self.processEndGame()
                self.draw()
                return


    def processEndGame(self):
        self.waiting.set(0)
        utility = self.game.utility(self.currentState,'X')
        if (utility == 1): self.message.set("X wins!")
        if (utility == 0): self.message.set("Draw!")
        if (utility == -1): self.message.set("O wins!")

        ## Draw a red line through the winning set of k moves 
        if utility != 0:
            ## Get list of k-in-a-row moves
            board = self.currentState.board
            move = self.currentState.winning_move
            player = board.get(move)
            for orientation in [(0,1),(1,0),(1,-1),(1,1)]:
                line = self.game.k_in_row(board, move, player, orientation)
                if len(line) >= self.game.k: break
            
            ## find min and max dimensions in the winning move set
            mins = list(map(min,zip(*line)))
            maxs = list(map(max,zip(*line)))
            
            ## swap y dimensions for falling diagonals
            if (mins[0],mins[1]) not in line:
                mins[1],maxs[1] = maxs[1],mins[1]
            ## draw the line
            self.canvas.create_line((mins[0]-1)*(500/self.game.h)+(250/self.game.h),
                                    (mins[1]-1)*(500/self.game.v)+(250/self.game.v),
                                    (maxs[0]-1)*(500/self.game.h)+(250/self.game.h),
                                    (maxs[1]-1)*(500/self.game.v)+(250/self.game.v),fill="red",width=4)
        self.root.update_idletasks()
        self.root.update()
        
if __name__ == "__main__":
    #app = GameInterface(Game.ConnectFour())
    app = GameInterface(Game.TicTacToe())
    app.root.mainloop()

