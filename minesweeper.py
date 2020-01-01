
__author__ = "João Pedro Gonçalves Moreira - jpgmoreira19@gmail.com"

"""
 A simple minesweeper game, written in Python 3 using Tkinter.
"""

from random import randrange as rand
import tkinter as tk


WSIZE = "800x600"
WTITLE = "Minesweeper"

DF_GRIDSIZE = [20,30]

DF_BOMBSPROP = 3

NORMALBG = 'light sky blue'
PRESSEDBG = 'gray80'
BOMBBG = 'red2'
FIELDFRAMEBG = 'DodgerBlue4'
TOPFRAMEBG = 'RoyalBlue4'
HIDDENBOMBBG = 'SteelBlue1'
HIDDENCB     = 'cyan'
CLOCKBG = 'dodger blue'

PRESSEDRELIEF = tk.SUNKEN
NORMALRELIEF = tk.RAISED
GRIDPADDING = 0

PROP_ERROR_MSG = 'Enter a valid value! (0 to 100)'

FONT = ('Arial Black', -20, 'bold')
TOPFRAMEFONT = ('Calibri', -20)


#----------------------------------------------------------------------------------------------------
class Application:
  def __init__(self,master):

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # - Defaults: -

    master.title(WTITLE)
    master.geometry(WSIZE)

    self.master = master

    statusBar = tk.Label(master,bd=1,relief=tk.SUNKEN)
    statusBar.pack(side='bottom',fill=tk.X)

    # Carrega imagens:
    self.smile       = tk.PhotoImage(file='images/smile.png')
    self.scary       = tk.PhotoImage(file='images/scary.png')
    self.win         = tk.PhotoImage(file='images/win.png')
    self.gameover    = tk.PhotoImage(file='images/gameover.png')
    self.bomb        = tk.PhotoImage(file='images/bomb.png')
    self.crossbomb   = tk.PhotoImage(file='images/crossbomb.png')
    self.flag        = tk.PhotoImage(file='images/flag.png')

    # Menu:
    self.menu = tk.Menu(self.master)
    self.master.config(menu=self.menu)
    self.optionsmenu = tk.Menu(self.menu,tearoff=0)

    self.menu.add_cascade(label='Game',menu=self.optionsmenu)
    self.menu.add_command(label='About', command=self.show_about_info)
    self.optionsmenu.add_command(label='Change difficulty...',command=self.change_difficulty)

    # Configura topFrame:
    topframe = tk.Frame(self.master,bg=TOPFRAMEBG)
    topframe.pack(fill='x')

    self.clocklabel = tk.Label(topframe,relief=tk.GROOVE,bg=CLOCKBG,font=TOPFRAMEFONT)
    self.clocklabel.pack(side='left',expand=True)    

    self.smilebutton = tk.Button(topframe,bg=TOPFRAMEBG,activebackground=TOPFRAMEBG,image=self.smile,relief='flat',command=self.newGame)
    self.smilebutton.pack(side='left')

    flagsframe = tk.Frame(topframe,relief=tk.GROOVE,bg='bisque2')
    flagsframe.pack(side='left',expand=True)

    leftflag = tk.Label(flagsframe,image=self.flag,compound='left',text=':',font=TOPFRAMEFONT)
    leftflag.pack(side='left')

    numflags = tk.Label(flagsframe,font=TOPFRAMEFONT)
    numflags.pack(side='right')

    self.flagstext = tk.StringVar()
    numflags['textvariable'] = self.flagstext

    # Configura fieldFrame:
    self.fieldFrame = tk.Frame(self.master,bg=FIELDFRAMEBG)
    self.fieldFrame.pack(fill='both',expand=True)

    # Cores dos numeros de neighbors:
    self.neighborColors = {1:'blue',2:'forest green',3:'brown1',4:'navy',5:'firebrick',6:'medium turquoise',7:'black',8:'snow4'}
    self.neighborColors[0] = 'black'
    self.neighborColors[9] = 'black'

    # Dicionario de tiles:
    self.tilesDict = {}

    # Proporcao de bombas no campo, em %:
    self.bombsProp = DF_BOMBSPROP
    self.gridsize = DF_GRIDSIZE

    # Configura grid:
    self.configura_grid()

    # - A ser inicializado em newGame:
    self.gamestatus = None
    self.lasttile = None
    self.flagsremaining = None
    self.qtbombs = None
    self.normaltiles = None

    # Controle para primeiro click:
    self.firstclick = None

    # Clock:
    self.clockseconds = 0
    self.clockminuts = 0
    self.afterid = None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    # Inicializa novo jogo:
    self.newGame()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

  def newGame(self):
    print('newGame')
    # Inicializacoes:
    self.smilebutton['image'] = self.smile
    self.firstclick = True
    self.gamestatus = 'normal'
    self.lasttile = None
    self.flagsremaining = 0
    self.qtbombs = 0
    self.normaltiles = self.gridsize[0] * self.gridsize[1]
    self.flagstext.set('0')
    self.clockseconds = 0
    self.clockminuts = 0
    self.clocklabel.configure(text='00:00')
    # Para o clock:
    self.stop_clock()
    # Sorteia bombas no grid:
    self.inicializaGrid()
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def configura_grid(self):
    # Configura o grid:
    for i in range(self.gridsize[0]):
      self.fieldFrame.rowconfigure(i,weight=1,uniform=True)  
    for j in range(self.gridsize[1]):
      self.fieldFrame.columnconfigure(j,weight=1,uniform=True)
    # Preenche o grid: 
    for i in range(self.gridsize[0]):
      for j in range(self.gridsize[1]):
        self.tilesDict[i,j] = Tile(self.fieldFrame,i,j,self.eventsHandler)      
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def click_toplevel(self, event, toplevel, toplevel_widgets):
      widget = self.master.winfo_containing(event.x_root,event.y_root)
      if not widget in toplevel_widgets:
        toplevel.bell()
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def close_toplevel(self, toplevel):
      if self.gamestatus == 'normal' and not self.firstclick:
        self.update_clock()  
      toplevel.destroy()
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def change_difficulty(self):
    self.stop_clock()
    # - - - - - - - - -
    def check_changes(event=None):
      proptext = prop_entry.get()
      properror = False      
      # - - - - - 
      try:
        propint = int(proptext)
      except ValueError:
        prop_errormsg['text'] = PROP_ERROR_MSG
        print('bombsprop ValueError')
        properror = True
      # - - - - - 
      if not (properror or (0 <= propint <= 100)):
        prop_errormsg['text'] = PROP_ERROR_MSG
        print('bombsprop invalid value')
        properror=True

      if not properror:
        prop_errormsg['text'] = ''
      else:
        return
      self.bombsProp = propint
      print('bombsprop:',propint)
      self.close_toplevel(toplevel)
      self.newGame()  # Chama newGame sem retornar.
    # - - - - - - - - -

    # cria janela:
    toplevel = tk.Toplevel()
 
    # Proporcao de bombas no campo:
    proporcao_frame = tk.Frame(toplevel)
    proporcao_frame.pack(ipady=2)
    prop_msg = tk.Label(proporcao_frame,text='Mines ratio, in %:')
    prop_msg.pack(pady=1)
    prop_errormsg = tk.Label(proporcao_frame,fg='red')
    prop_errormsg.pack()
    prop_entry = tk.Entry(proporcao_frame)
    prop_entry.insert(0,self.bombsProp)
    prop_entry.bind("<Return>",check_changes)
    prop_entry.pack()  

    # Lista com todos os widgets associados a janela:
    toplevel_widgets = [toplevel] + toplevel.winfo_children() + proporcao_frame.winfo_children()

    # configura janela:
    toplevel.bind("<Button-1>", lambda event, tl=toplevel, tlw=toplevel_widgets : self.click_toplevel(event, tl, tlw))
    toplevel.title('Change difficulty')
    toplevel.protocol("WM_DELETE_WINDOW", lambda tl=toplevel : self.close_toplevel(tl))
    toplevel.minsize(300,170)
    toplevel.resizable(False,False)
    self.centerToplevel(toplevel)
    toplevel.grab_set()  # Atribui foco na janela.
    
    # New game button:
    ngbutton = tk.Button(toplevel,text='New Game',command=check_changes)
    ngbutton.bind("<Return>",check_changes)
    ngbutton.pack(pady=10)
 
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def centerToplevel(self,toplevel):
    toplevel.update_idletasks()
    root_x = self.master.winfo_x()
    root_y = self.master.winfo_y()
    root_w = self.master.winfo_width()
    root_h = self.master.winfo_height()
    top_w = toplevel.winfo_width()
    top_h = toplevel.winfo_height()
    dx = root_x + (root_w-top_w)/2
    dy = root_y + (root_h-top_h)/2
    toplevel.geometry("%dx%d+%d+%d" % (top_w,top_h,dx,dy))      

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update_clock(self):
    if self.afterid:  # Controle para o 1 segundo de delay no inicio do jogo.
      self.clockseconds+=1
      if self.clockseconds == 60:
        self.clockseconds = 0
        self.clockminuts+=1
      secondspart = str(self.clockseconds)
      minutspart = str(self.clockminuts)
      if self.clockseconds<10:
        secondspart = '0'+secondspart
      if self.clockminuts<10:    
        minutspart = '0'+minutspart
      now = minutspart + ":" + secondspart
      self.clocklabel.configure(text=now)    
    self.afterid = self.master.after(1000,self.update_clock)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def stop_clock(self):
    if self.afterid:
      self.master.after_cancel(self.afterid)
    self.afterid = None

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def eventsHandler(self,event):
    widget = self.master.winfo_containing(event.x_root,event.y_root)
    tilesfield = self.fieldFrame.children.values()
    etype = str(event.type)

    if widget in tilesfield:
      gridInfo = widget.grid_info()
      row = gridInfo['row']
      column = gridInfo['column']
      tile = self.tilesDict[row,column]
    # = = = = = = = = = = = = = = = = = = 
    if self.gamestatus == 'normal':
      if etype == "ButtonRelease":
        self.smilebutton['image'] = self.smile

      if widget in tilesfield:
        if etype == "ButtonPress":
          if event.num == 1:
            self.smilebutton['image'] = self.scary
            self.gamestatus = 'holding'
          elif event.num == 3 and not self.firstclick:
            if tile.status == 'normal' and self.flagsremaining>0:
              tile.status = 'flagged'
              self.flagsremaining-=1
              tile.label['image'] = self.flag
            elif tile.status == 'flagged':
              tile.status = 'normal'
              self.flagsremaining+=1
              tile.label['image'] = ''
            self.flagstext.set(self.flagsremaining)

        elif etype == "ButtonRelease":
          if tile.status == 'normal':
            tile.status = 'pressed'
            tile.label.config(relief=PRESSEDRELIEF,bg=PRESSEDBG)
            self.normaltiles -=1
            if self.normaltiles == self.qtbombs:
              self.gamewin()
          if self.firstclick:
            for i in range(row-1,row+2):
              for j in range(column-1,column+2):
                if (i,j) in  self.tilesDict.keys():
                  if self.tilesDict[i,j].bomb:
                    self.tilesDict[i,j].bomb = False
                    self.flagsremaining -=1
                    self.qtbombs -= 1
            self.setGridNeighbors()      
            self.flagstext.set(self.flagsremaining)
            # Inicializa clock:
            self.update_clock()
            self.zeroNeighborsTile(row,column)
            self.firstclick = False
          elif not tile.status == 'flagged':
              if tile.bomb:
                tile.label['bg'] = BOMBBG
                self.gameoverFunc()
              elif tile.neighbors:
                tile.text.set(tile.neighbors)
              else:
                self.zeroNeighborsTile(row,column)
    # = = = = = = = = = = = = = = = = = = 
    elif self.gamestatus == 'holding':
      if etype == "ButtonRelease":
        if self.lasttile and self.lasttile.status == 'normal':
          self.lasttile.label['relief'] = NORMALRELIEF         
        self.gamestatus = 'normal'
        self.eventsHandler(event)
      elif widget in tilesfield:
        if not self.lasttile:
          self.lasttile = tile
        elif tile != self.lasttile:
          if tile.status == 'normal':
            tile.label['relief'] = PRESSEDRELIEF
          if self.lasttile.status == 'normal':
            self.lasttile.label['relief'] = NORMALRELIEF
          self.lasttile = tile
    # = = = = = = = = = = = = = = = = = =  

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def gameoverFunc(self):
    print('gameover')
    self.smilebutton['image'] = self.gameover
    self.gamestatus = 'gameover'
    self.stop_clock()
    for t in self.tilesDict.values():
      if t.bomb:
        if t.status == 'normal':
          t.label.config(bg=HIDDENBOMBBG,image=self.bomb,relief=PRESSEDRELIEF)
        elif t.status == 'pressed':
          t.label['image'] = self.bomb
        elif t.status == 'flagged':
          t.label.config(bg=HIDDENCB,image=self.crossbomb,relief=PRESSEDRELIEF)
      t.status = 'locked'

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  # Game win:
  # - Todos os tiles nao-bomba estao em 'pressed'.
  def gamewin(self):
    print('gamewin')
    self.smilebutton['image'] = self.win
    self.gamestatus = 'gamewin'
    self.stop_clock()
    for t in self.tilesDict.values():
      if t.bomb and t.status == 'normal':
        t.label['image'] = self.flag
        t.status = 'flagged'
        self.flagsremaining -=1
      t.status = 'locked'
    self.flagstext.set(self.flagsremaining)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def inicializaGrid(self):
    for t in self.tilesDict.values():
      t.text.set('')
      t.label.config(relief=NORMALRELIEF,bg=NORMALBG,image='')
      t.neighbors = 0
      t.status = 'normal'
      if rand(100) < self.bombsProp:
        t.bomb = True
        self.flagsremaining+=1
        self.qtbombs += 1
      else:
        t.bomb = False  

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def setGridNeighbors(self):
    for i in range(self.gridsize[0]):
      for j in range(self.gridsize[1]):
        if self.tilesDict[i,j].bomb:
          for k in range(i-1,i+2):
            for l in range(j-1,j+2):
              if (k,l) in self.tilesDict.keys():
                self.tilesDict[k,l].neighbors += 1
    for t in self.tilesDict.values():
      color = self.neighborColors[t.neighbors]
      t.label['fg'] = color

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def zeroNeighborsTile(self,row,column):
    tile = self.tilesDict[row,column]
    for i in range(row-1,row+2):
      for j in range(column-1,column+2):
        if (i,j) in self.tilesDict.keys():
          neighbor = self.tilesDict[i,j]
          if neighbor.status == 'normal':
            neighbor.status = 'pressed'
            neighbor.label.config(bg=PRESSEDBG,relief=PRESSEDRELIEF)
            self.normaltiles -=1
            if self.normaltiles == self.qtbombs:
              self.gamewin()
            if neighbor.neighbors:
              neighbor.text.set(neighbor.neighbors)
            else:
              self.zeroNeighborsTile(i,j)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def show_about_info(self):
    print("Show about info")
    self.stop_clock()

    # cria janela:
    toplevel = tk.Toplevel()
    toplevel.title('About')
    toplevel.protocol("WM_DELETE_WINDOW", lambda tl=toplevel : self.close_toplevel(tl))
    toplevel.minsize(300,170)
    toplevel.resizable(False,False)
    self.centerToplevel(toplevel)
    toplevel.grab_set()  # Atribui foco na janela.

    # About text:
    about = """
    Python-Minesweeper\n
    A simple minesweeper game, written in Python 3 using tkinter.\n
    Author: João Pedro Gonçalves Moreira - jpgmoreira19@gmail.com

    """

    # Label with about text:
    aboutlabel = tk.Label(toplevel, text=about, wraplength=260)
    aboutlabel.pack()

    # Close button:
    closebutton = tk.Button(toplevel,text='Close',command= lambda tl=toplevel : self.close_toplevel(tl))
    closebutton.pack(pady=10)

    # Lista com todos os widgets associados a janela:
    toplevel_widgets = [toplevel] + toplevel.winfo_children()
    toplevel.bind("<Button-1>", lambda event, tl=toplevel, tlw=toplevel_widgets : self.click_toplevel(event, tl, tlw))
    
#----------------------------------------------------------------------------------------------------
class Tile:
  def __init__(self,master,row,column,eventsHandler):
    self.text = tk.StringVar()
    self.label = tk.Label(master,textvariable=self.text,relief=NORMALRELIEF,bg=NORMALBG,font=FONT)
    self.label.grid(row=row,column=column,sticky='nsew',padx=GRIDPADDING,pady=GRIDPADDING)
    self.neighbors = 0
    self.bomb = False
    # Status: 'normal', 'pressed', 'flagged', 'locked'.
    self.status = 'normal'
    # Events binding:
    eventsList = ["<B1-Motion>","<Button-1>","<Button-3>","<ButtonRelease-1>"]
    for e in eventsList:
      self.label.bind(e,eventsHandler)
#----------------------------------------------------------------------------------------------------


root = tk.Tk()
Application(root)
root.mainloop()
