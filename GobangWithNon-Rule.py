# -*- coding:utf-8 -*-
from Tkinter import *
import os,sys
import re
from time import sleep as delay

#初始化定义#
PosLEFT=28 #棋盘左
PosRIGHT=770 #棋盘右
PosTOP=28 #棋盘顶
PosBOTTOM=770 #棋盘底
LineStep=53 #棋盘线间隔
LineWidth=2 #棋盘线宽
StarSize=4 #天元与星半径
TouchRange=18 #触发范围/xy长宽
CheckFrameLength=51 #鼠标选择框边长,必须为3的倍数且大于6
CheckFrameWidth=2 #鼠标选择框厚度
CheckFrameColor='black' #鼠标选择框颜色
MouseReInto=False #鼠标重入
MousePos=[0,0] #鼠标坐标
NowMousePos=[None,None] #当前鼠标坐标
ChessSize=14 #棋子尺寸半径
CB_Travarse_Line=[] #棋盘横线句柄
CB_Upright_Line=[] #棋盘竖线句柄
CB_Tengen_Point=None #棋盘天元句柄
CB_Star_Point=[] #棋盘星句柄
CB_Point=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #棋盘点位坐标
ChessPoint=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #棋子位置
MemChessPoint=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #记忆棋子位置
ChessOrder=1 #执棋顺序 1:黑  2:百
#棋盘点位
for x in range(0,15):
    for y in range(0,15):
        CB_Point[x].append([PosLEFT+x*LineStep,PosTOP+y*LineStep])
#棋子初始化
for x in range(0,15):
    for y in range(0,15):
        ChessPoint[x].append(-1)
for x in range(0,15):
    for y in range(0,15):
        MemChessPoint[x].append(-1)
#初始化定义#
        
#鼠标判断区域计算
def MouseIn(x,y):
    relx=None
    rely=None
    #x判断
    for Xline in range(0,15):
        if CB_Point[Xline][0][0]-TouchRange <= x <= CB_Point[Xline][0][0]+TouchRange:
            relx=Xline
            break
    #y判断
    for Yline in range(0,15):
        if CB_Point[0][Yline][1]-TouchRange <= y <= CB_Point[0][Yline][1]+TouchRange:
            rely=Yline
            break
    if relx==None or rely==None:
        return None
    else:
        return [relx,rely]
        #return CB_Point[relx][rely]
#=====五子棋规则=====#
class GobangRule():
    @staticmethod
    def BaseRule():
        global ChessPoint
        pass
#=====五子棋规则=====#   
#创建root窗口对象
root=Tk()
root.wm_title('Gobang')
root.resizable(False,False)
root.geometry('800x800+200+20')
#创建画布
ChessBoard=Canvas(root,bg='#EEE8AA',width=800,height=800,highlightthickness=0)
ChessBoard.pack()
#==棋盘绘制==#
#横线绘制
for LineNum in range(0,15):
    CB_Travarse_Line.append(ChessBoard.create_line(PosLEFT,PosTOP+LineNum*LineStep,PosRIGHT,PosTOP+LineNum*LineStep,width=LineWidth,tag='Travarse'))
#竖线绘制
for LineNum in range(0,15):    
    CB_Upright_Line.append(ChessBoard.create_line(PosLEFT+LineNum*LineStep,PosTOP,PosLEFT+LineNum*LineStep,PosBOTTOM,width=LineWidth,tag='Travarse'))
#天元与星绘制
CB_Tengen_Point=ChessBoard.create_oval(PosLEFT+7*LineStep-StarSize-1,PosTOP+7*LineStep-StarSize,PosLEFT+7*LineStep+StarSize-1,PosTOP+7*LineStep+StarSize,fill='black')
CB_Star_Point.append(ChessBoard.create_oval(PosLEFT+3*LineStep-StarSize-1,PosTOP+3*LineStep-StarSize,PosLEFT+3*LineStep+StarSize-1,PosTOP+3*LineStep+StarSize,fill='black'))
CB_Star_Point.append(ChessBoard.create_oval(PosLEFT+3*LineStep-StarSize-1,PosTOP+11*LineStep-StarSize,PosLEFT+3*LineStep+StarSize-1,PosTOP+11*LineStep+StarSize,fill='black'))
CB_Star_Point.append(ChessBoard.create_oval(PosLEFT+11*LineStep-StarSize-1,PosTOP+3*LineStep-StarSize,PosLEFT+11*LineStep+StarSize-1,PosTOP+3*LineStep+StarSize,fill='black'))
CB_Star_Point.append(ChessBoard.create_oval(PosLEFT+11*LineStep-StarSize-1,PosTOP+11*LineStep-StarSize,PosLEFT+11*LineStep+StarSize-1,PosTOP+11*LineStep+StarSize,fill='black'))
#==棋盘绘制==#
#棋子事件
def ChessGenerator(): #棋子生成
    global ChessPoint,MemChessPoint
    if ChessPoint != MemChessPoint:
        for x in range(0,15):
            for y in range(0,15):
                MemChessPoint[x][y]=ChessPoint[x][y]
        ChessBoard.delete('Chess')
        for x in range(0,15):
            for y in  range(0,15):
                if ChessPoint[x][y]==1:
                    ChessBoard.create_oval(CB_Point[x][y][0]-ChessSize,CB_Point[x][y][1]-ChessSize,CB_Point[x][y][0]+ChessSize,CB_Point[x][y][1]+ChessSize,fill='black',outline='black',tag='Chess')
                if ChessPoint[x][y]==2:
                    ChessBoard.create_oval(CB_Point[x][y][0]-ChessSize,CB_Point[x][y][1]-ChessSize,CB_Point[x][y][0]+ChessSize,CB_Point[x][y][1]+ChessSize,fill='white',outline='white',tag='Chess')
    root.after(10,ChessGenerator)            
#鼠标事件
def MouseCheckFrame(LineX,LineY): #选择框生成
    Tmplength=CheckFrameLength    
    Length=Tmplength / 3
    Interval=Tmplength / 3
    ChessBoard.create_line(CB_Point[LineX][LineY][0]-Tmplength/2,CB_Point[LineX][LineY][1]-Tmplength/2,CB_Point[LineX][LineY][0]-Interval/2,CB_Point[LineX][LineY][1]-Tmplength/2,tag='MouseCheck',width=CheckFrameWidth,fill=CheckFrameColor)
    ChessBoard.create_line(CB_Point[LineX][LineY][0]+Tmplength/2,CB_Point[LineX][LineY][1]-Tmplength/2,CB_Point[LineX][LineY][0]+Interval/2,CB_Point[LineX][LineY][1]-Tmplength/2,tag='MouseCheck',width=CheckFrameWidth,fill=CheckFrameColor)
    ChessBoard.create_line(CB_Point[LineX][LineY][0]-Tmplength/2,CB_Point[LineX][LineY][1]+Tmplength/2,CB_Point[LineX][LineY][0]-Interval/2,CB_Point[LineX][LineY][1]+Tmplength/2,tag='MouseCheck',width=CheckFrameWidth,fill=CheckFrameColor)
    ChessBoard.create_line(CB_Point[LineX][LineY][0]+Tmplength/2,CB_Point[LineX][LineY][1]+Tmplength/2,CB_Point[LineX][LineY][0]+Interval/2,CB_Point[LineX][LineY][1]+Tmplength/2,tag='MouseCheck',width=CheckFrameWidth,fill=CheckFrameColor)
    ChessBoard.create_line(CB_Point[LineX][LineY][0]-Tmplength/2,CB_Point[LineX][LineY][1]-Tmplength/2,CB_Point[LineX][LineY][0]-Tmplength/2,CB_Point[LineX][LineY][1]-Interval/2,tag='MouseCheck',width=CheckFrameWidth,fill=CheckFrameColor)
    ChessBoard.create_line(CB_Point[LineX][LineY][0]+Tmplength/2,CB_Point[LineX][LineY][1]-Tmplength/2,CB_Point[LineX][LineY][0]+Tmplength/2,CB_Point[LineX][LineY][1]-Interval/2,tag='MouseCheck',width=CheckFrameWidth,fill=CheckFrameColor)
    ChessBoard.create_line(CB_Point[LineX][LineY][0]-Tmplength/2,CB_Point[LineX][LineY][1]+Tmplength/2,CB_Point[LineX][LineY][0]-Tmplength/2,CB_Point[LineX][LineY][1]+Interval/2,tag='MouseCheck',width=CheckFrameWidth,fill=CheckFrameColor)
    ChessBoard.create_line(CB_Point[LineX][LineY][0]+Tmplength/2,CB_Point[LineX][LineY][1]+Tmplength/2,CB_Point[LineX][LineY][0]+Tmplength/2,CB_Point[LineX][LineY][1]+Interval/2,tag='MouseCheck',width=CheckFrameWidth,fill=CheckFrameColor)
def MouseMovePos(event): #鼠标移动时动作
    global MousePos,MouseReInto
    TmpXY=MouseIn(event.x,event.y)
    if TmpXY != None:
        if (MousePos[0] != TmpXY[0]) or ((MousePos[1] != TmpXY[1])) or (MouseReInto==True):
            MousePos[0]=TmpXY[0]
            MousePos[1]=TmpXY[1]
            NowMousePos[0]=TmpXY[0]
            NowMousePos[1]=TmpXY[1]
            MouseReInto=False
            MouseCheckFrame(TmpXY[0],TmpXY[1])
    else:
        ChessBoard.delete('MouseCheck')
        MouseReInto=True
        NowMousePos[0]=None
        NowMousePos[1]=None
def MouseMoveOut(event): #鼠标移除时动作
    ChessBoard.delete('MouseCheck')
def ChessPut(event):
    global ChessOrder,NowMousePos,CheckFrameColor,ChessBoard
    if NowMousePos==[None,None]:
        return
    if ChessPoint[NowMousePos[0]][NowMousePos[1]]==-1:
        ChessPoint[NowMousePos[0]][NowMousePos[1]]=ChessOrder
        ChessGenerator()
        if ChessOrder==1:
            ChessOrder=2
            CheckFrameColor='white'
            for item in ChessBoard.find_withtag('MouseCheck'):
                ChessBoard.itemconfig(item,fill = 'white')            
        elif ChessOrder==2:
            ChessOrder=1
            CheckFrameColor='black'
            for item in ChessBoard.find_withtag('MouseCheck'):
                ChessBoard.itemconfig(item,fill = 'black')               
def ChessReset(event):
    global ChessPoint,MemChessPoint,ChessBoard,ChessOrder,CheckFrameColor
    for x in range(0,15):
        for y in range(0,15):
            ChessPoint[x][y]=-1
    for x in range(0,15):
        for y in range(0,15):
            MemChessPoint[x][y]=-1
    ChessBoard.delete('Chess')
    ChessOrder=1
    CheckFrameColor='black'
    for item in ChessBoard.find_withtag('MouseCheck'):
        ChessBoard.itemconfig(item,fill = 'black')      
#方法绑定
ChessBoard.bind('<Motion>',MouseMovePos)
ChessBoard.bind('<Leave>',MouseMoveOut)
ChessBoard.bind('<Button-1>',ChessPut)
ChessBoard.bind_all('<KeyPress-r>',ChessReset)
#窗口执行进入事件监控
root.after(10,ChessGenerator)
root.mainloop()
