import numpy as np
from pprint import pprint

'''For board representation I use piece centric approach
using a Bitmap.
The positions are to be thought of using vectors in 2D space
The mapping is A-H maps as 0-7 X axis
1-8 maps as 0-7 Y Axis

Also as a backup is a board centric approach
'''

'''
Listing the piece types:

Pawn 0b?0000
Knight 0b?0001
Bishop 0b?0010
Rook 0b?0011
Queen 0b?0100
King 0b?0101

#Most likely removal of the following states
#as they are not necessary
#neither are they defined 
#in standard notation

King Can Castle 0b?0111
Rook Can Castle 0b?1000
Pawn First Move 0b?1001
Pawn En Passant 0b?1010
'''
standardFEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
backupFEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

binaryToPiece={0b00000:"P",0b10000:"p",0b00001:"N",0b10001:"n",0b00010:"B",0b10010:"b",
        0b00011:"R",0b10011:"r",0b00100:"Q",0b10100:"q",0b00101:"K",0b10101:"k",
        0b00111:"Kc",0b10111:"kc",0b01000:"Rc",0b11000:"rc",
        0b01001:"Pf",0b11001:"pf",0b01010:"Pe",0b11010:"pe"}
 
pieceToBinary={v:k for k,v in binaryToPiece.items()}

def fenToBoardCentric(fenString):
    board=[[0 for i in range(8)] for i in range(8)]
    initialPos=(-1,7)
    currentPos=np.array(initialPos)
    state=fenString.split(' ')
    pieces,turn,castle,enPassant,halfMove,fullMove=state
    lines=pieces.split('/')
    for line in lines:
        for char in line:
            if char.isnumeric():
                currentPos+=int(char)*np.array([1,0])
            else:
                currentPos+=np.array([1,0])
                x,y=currentPos
                board[y][x]=char
            #print(char,currentPos)
        currentPos+=np.array([-8,-1])
    #pprint(board)
    return (board,turn,castle,enPassant,halfMove,fullMove)
'''
This is partial support at the moment. 
Need to add support for states such as 
castling, enPassant and turns
'''
def boardCentrictoFEN(currentBoard):
    pieces=currentBoard[0]
    fenString=''
    '''
    Please note that range goes from max to min because it has 
    to follow the FEN definition which has initial point at (7,0)
    '''
    for i in range(len(pieces)-1,-1,-1):
        counter=0
        for j in range(len(pieces[0])):
            char=pieces[i][j]
            if char!=0:
                if counter!=0:
                    fenString+=str(counter)
                fenString+=char
                counter=0
            else:
                counter+=1
        if counter!=0:
            fenString+=str(counter)
        fenString+='/'
    #We remove the last '/' because we only need it as a spacer
    fenString=fenString[:-1]+' '
    fenString+=' '.join(currentBoard[1::])
    return fenString

#Converts to Board Centric View
def convertBoardCentric(pieces):
    board=[[0 for i in range(8)] for i in range(8)]
    for pos,pieceType in pieces.pieces:
        x,y=pos
        board[y][x]=binaryToPiece[pieceType]
    state=pieces.gameState
    return (board,*state)

def convertPieceCentric(currentBoard):
    board=currentBoard[0]
    currentPieces=[]
    for i in range(len(board)):
        for j in range(len(board[0])):
            pieceType=board[i][j]
            if pieceType!=0:
                currentPieces.append((np.array([j,i]),pieceToBinary[pieceType]))
    pieces=pieceSetup((currentPieces,*currentBoard[1::]))
    return pieces

class pieceSetup:
    def __init__(self,currentGame):
        currentPieces=currentGame[0]
        self.whitePieces=[]
        self.blackPieces=[]
        self.gameState=currentGame[1::]
        for position,piece in currentPieces:
            if piece>>4:
                self.blackPieces.append((position,piece))
            else:
                self.whitePieces.append((position,piece))
        self.pieces=[*self.whitePieces,*self.blackPieces]

class MovePatterns:
    def __init__(self):
        dirKing=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        self.slidingMobility=8
        dirQueen=[]
        for j in dirKing:
            for i in range(1,self.slidingMobility):
                dirQueen.append((i*j[0],i*j[1]))
        plusDir=[(-1,0),(1,0),(0,-1),(0,1)]
        plusRook=[]
        for j in plusDir:
            for i in range(1,self.slidingMobility):
                plusRook.append((i*j[0],i*j[1]))
        crossDir=[(-1,-1),(1,1),(-1,1),(1,-1)]
        crossBishop=[]
        for j in crossDir:
            for i in range(1,self.slidingMobility):
                crossBishop.append((i*j[0],i*j[1]))
        dirKnight=[(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]
 
        '''
        NOTE: Pawn En Passant is the same as regular pawn but can only
        be activated under certain checks
        '''
        self.pawnW=[np.array(pos) for pos in [(0,1),(-1,1),(1,1)]]
        self.pawnWf=[np.array(pos) for pos in [(0,1),(-1,1),(1,1),(0,2)]]
        self.pawnB=[np.array(pos) for pos in [(0,-1),(-1,-1),(1,-1)]]
        self.pawnBf=[np.array(pos) for pos in [(0,-1),(-1,-1),(1,-1),(0,-2)]]

        self.king=[np.array(pos) for pos in dirKing]
        self.queen=[np.array(pos) for pos in dirQueen]
        self.rook=[np.array(pos) for pos in plusRook]
        self.bishop=[np.array(pos) for pos in crossBishop]
        self.knight=[np.array(pos) for pos in dirKnight]

        '''
        CASTLING: This is now a special move that falls outside the moves 
        of the king and the rook
        The first vector is movement of king and second the movement of the rook
        '''
        self.castleKingSide=[np.array(2,0),np.array([-2,0])]
        self.castleQueenSide=[np.array(-2,0),np.array([+3,0])]

standardBoard=fenToBoardCentric(standardFEN)
standardPiece=convertPieceCentric(standardBoard)
standardBoard=convertBoardCentric(standardPiece)
standardFEN=boardCentrictoFEN(standardBoard)
print(standardFEN)
print(backupFEN)
print(standardFEN==backupFEN)
