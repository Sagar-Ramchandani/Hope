import numpy as np
from pprint import pprint
'''For board representation I use piece centric approach
using a Bitmap.
The positions are to be thought of using vectors in 2D space
The mapping is A-H maps as 0-7 X axis
1-8 maps as 0-7 Y Axis
'''

'''
Listing the piece types:

Pawn 0b?0000
Knight 0b?0001
Bishop 0b?0010
Rook 0b?0011
Queen 0b?0100
King 0b?0101
King Can Castle 0b?0111
Rook Can Castle 0b?1000
Pawn First Move 0b?1001
Pawn En Passant 0b?1010
'''
standardFEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

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
    return board

def boardCentrictoFEN(currentBoard):
    fenString=''
    for i in range(len(currentBoard)):
        counter=0
        for j in range(len(i)):
            char=currentBoard[i][j]
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
    fenString=fenString[:-1]
    return fenString

#Converts to Board Centric View
def convertBoardCentric(pieces):
    board=[[0 for i in range(8)] for i in range(8)]
    for pos,pieceType in pieces.pieces:
        x,y=pos
        board[y][x]=binaryToPiece[pieceType]
    pprint(board)
    return board

def convertPieceCentric(board):
    currentPieces=[P,p,N,n,B,b,R,r,Q,q,K,k,Kc,kc,Rc,rc,Pf,pf,Pe,pe]=[[] for i in range(20)]
    for i in range(8):
        for j in range(8):
            pieceType=board[i][j]
            if pieceType!=0:
                command=pieceType+".append(("+str(j)+","+str(i)+"))"
                eval(command)
    pieces=pieceSetup(*currentPieces)
    return pieces

class pieceSetup:
    def __init__(self,P,p,N,n,B,b,R,r,Q,q,K,k,Kc,kc,Rc,rc,Pf,pf,Pe,pe):
        '''
        NOTE: Need to refactor this to only use the variables of whitePieces and blackPieces
        and to elimiate all the different variables that are not of use
        '''
        self.pawnW=[(np.array(i),0b00000) for i in P]
        self.pawnB=[(np.array(i),0b10000) for i in p]
        self.knightW=[(np.array(i),0b00001) for i in N]
        self.knightB=[(np.array(i),0b10001) for i in n]
        self.bishopW=[(np.array(i),0b00010) for i in B]
        self.bishopB=[(np.array(i),0b10010) for i in b]
        self.rookW=[(np.array(i),0b00011) for i in R]
        self.rookB=[(np.array(i),0b10011) for i in r]
        self.queenW=[(np.array(i),0b00100) for i in Q]
        self.queenB=[(np.array(i),0b10100) for i in q]
        self.kingW=[(np.array(i),0b00101) for i in K]
        self.kingB=[(np.array(i),0b10101) for i in k]
        self.kingCW=[(np.array(i),0b00111) for i in Kc]
        self.kingCB=[(np.array(i),0b10111) for i in kc]
        self.rookCW=[(np.array(i),0b01000) for i in Rc]
        self.rookCB=[(np.array(i),0b11000) for i in rc]
        self.pawnWf=[(np.array(i),0b01001) for i in Pf]
        self.pawnBf=[(np.array(i),0b11001) for i in pf]
        self.pawnWe=[(np.array(i),0b01010) for i in Pe]
        self.pawnBe=[(np.array(i),0b11010) for i in pe]
        self.whitePieces=[*self.pawnW,*self.knightW,*self.bishopW,*self.rookW,*self.queenW,*self.kingW,
                *self.kingCW,*self.rookCW,*self.pawnWf,*self.pawnWe]
        self.blackPieces=[*self.pawnB,*self.knightB,*self.bishopB,*self.rookB,*self.queenB,*self.kingB,
                *self.kingCB,*self.rookCB,*self.pawnBf,*self.pawnBe]
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

#moves=MovePatterns()
