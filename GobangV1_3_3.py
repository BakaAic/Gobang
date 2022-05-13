# -*- coding:utf-8 -*-
from Tkinter import *
from ttk import *
import os,sys
from time import sleep as delay
from time import clock
import tkFont
import random
import traceback
from copy import deepcopy

#初始化定义#
DebugMode=False #调试模式
TimeShow=True #计时模式
Chess3D=False  #3D棋子
SlopeStreng=False #强化斜线
LevelRank=['Alpha','alpha','Beta','beta','Gamma','gamma','Omega','omega']
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
Chess_Num=0 #棋子数
ChessPoint=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #棋子位置
MemChessPoint=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #记忆棋子位置
HistoryChess=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
ChessOrder=[1] #执棋顺序 1:黑 -1:百
ManClick=False #人点击
SlopeList=['LEFTUP','LEFTDOWN','RIGHTUP','RIGHTDOWN'] #斜面元素
ChessCostList={'B5':100000,'L4':12000,'S4':95,'LowS4':90,'L3':100,'JL3':96,'L2':10,'LowL2':9,'S3':5,'S2':2,'DS4':10000,'S4L3':10000,'DL3':5000,'S3L3':15,'DL2':30,'Slope':15}
              #成5         活4        冲4      低级冲4   活3      跳3      活2     低级活2   眠3    眠2    双冲4       冲4活3        双活3     眠3活3     双活2    斜线
#棋盘点位
for x in range(0,15):
    for y in range(0,15):
        CB_Point[x].append([PosLEFT+x*LineStep,PosTOP+y*LineStep])
#棋子初始化
for x in range(0,15):
    for y in range(0,15):
        ChessPoint[x].append(0)
        MemChessPoint[x].append(0)
        HistoryChess[x].append(0)
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
        global ChessBoard,Chess_Num
        cost=0
        for y in range(0,15):
            for x in range(0,15):
                cost=GobangRule._BaseRuleCheck(x,y)
                if cost!=0:
                    break
            if cost!=0:
                break
        if cost==0:
            Chess_Num=Chess_Num+1
            if Chess_Num==225:
                ChessOrder[0]=0
                ChessBoard.create_text((400,400),text = 'Draw The Game',anchor = CENTER,fill='Black',font=font_Big,tag='WinText')
                ChessBoard.create_text((401,401),text = 'Draw The Game',anchor = CENTER,fill='Red',font=font,tag='WinText')
                ChessBoard.unbind('<Button-1>')
                ChessBoard.bind('<Button-1>',WinAndReset)                
            return 0
        if cost==1:
            ChessBoard.create_text((400,400),text = 'Black Win',anchor = CENTER,fill='White',font=font_Big,tag='WinText')
            ChessBoard.create_text((401,401),text = 'Black Win',anchor = CENTER,fill='Black',font=font,tag='WinText')
        elif cost==-1:
            ChessBoard.create_text((400,400),text = 'White Win',anchor = CENTER,fill='Black',font=font_Big,tag='WinText')
            ChessBoard.create_text((401,401),text = 'White Win',anchor = CENTER,fill='White',font=font,tag='WinText')
        #复位
        ChessBoard.unbind('<Button-1>')
        ChessBoard.bind('<Button-1>',WinAndReset)
        return cost
    @staticmethod
    def _BaseRuleCheck(x,y):
        global ChessPoint
        if x>=4 and y<=10: #左下
            value=ChessPoint[x][y]+ChessPoint[x-1][y+1]+ChessPoint[x-2][y+2]+ChessPoint[x-3][y+3]+ChessPoint[x-4][y+4]
            if value==5:
                return 1
            elif value==-5:
                return -1            
        if y<=10:  #下
            value=ChessPoint[x][y]+ChessPoint[x][y+1]+ChessPoint[x][y+2]+ChessPoint[x][y+3]+ChessPoint[x][y+4]
            if value==5:
                return 1
            elif value==-5:
                return -1
        if y<=10 and x<10:  #右下
            value=ChessPoint[x][y]+ChessPoint[x+1][y+1]+ChessPoint[x+2][y+2]+ChessPoint[x+3][y+3]+ChessPoint[x+4][y+4]
            if value==5:
                return 1
            elif value==-5:
                return -1
        if x<10:  #右
            value=ChessPoint[x][y]+ChessPoint[x+1][y]+ChessPoint[x+2][y]+ChessPoint[x+3][y]+ChessPoint[x+4][y]
            if value==5:
                return 1
            elif value==-5:
                return -1
        return 0
#=====五子棋规则=====#

#---------AI---------#
class GobangAI():  #五子棋AI
    def __init__(self,root,ChessOrder,ChessPoint,ChessBoard,AIType='Alpha'):
        global LevelRank
        self.AIType=AIType
        if self.AIType.get() not in LevelRank:
            raise AITypeError(self.AIType)
        self._root=root
        self._ChessOrder=ChessOrder
        self._ChessPoint=ChessPoint
        self._ChessBoard=ChessBoard
        self._SimulatePoint=None
        self._root.after(10,self._RUN)
    def _RUN(self): #自动循环运行
        global PvMode
        if self._ChessOrder[0]==-1 and PvMode.get()=='Computer':
            if self.AIType.get()=='Alpha':
                CalValue=self.Alpha_Cal()
            if self.AIType.get()=='Beta':
                CalValue=self.Beta_Cal()
            if self.AIType.get()=='Gamma':
                CalValue=self.Gamma_Cal()
            if self.AIType.get()=='Omega':
                CalValue=self.Omega_Cal()                
            self._ChessBoard.unbind_all('<KeyPress-r>')
            #self.AIChessPut(CalValue[0],CalValue[1])
            self._root.after(10,lambda:self.AIChessPut(CalValue[0],CalValue[1]))
            self._ChessOrder[0]=0
        self._root.after(10,self._RUN)
    def ChessTypeJudge(self,ChessInvoke,result,*args): #(Reuslt,[x-4,y],[x-3,y],[x-2,y],[x-1,y],[x,y])
        aList=[]
        for i in range(0,len(args)):
            if type(args[i])==list:
                if (args[i][0]<0) or (args[i][1]<0) or (args[i][0]>14) or (args[i][1]>14):
                    return False
                if ChessInvoke==True:
                    aList.append(self._ChessPoint[args[i][0]][args[i][1]])
                else:
                    aList.append(self._SimulatePoint[args[i][0]][args[i][1]])
            else:
                aList.append(args[i])
        if aList==result:
            return True
        else:
            return False
    def Base_CostCal(self,x,y,Order,ChessInvoke=True,Priority=None): #基本分数算法
        global ChessCostList,SlopeList,StrengSlopeVar,TimeShow
        TimeStart=clock()
        #特殊方向判定S4,S3,L3        
        S4Forward=[] #冲4方向
        S3Forward=[] #眠3方向
        L3Forward=[] #活3方向
        JL3Forward=[] #跳活3方向
        SleepFourTimes=0 #眠4次数
        LiveThreeTimes=0 #活3次数
        JumpLiveThreeTimes=0 #跳活3次数
        SleepThreeTimes=0 #眠3次数
        LiveTwoTimes=0 #活2次数
        Cost=0
        Pri5Mark=False
        Pri4Mark=False
        Pri3Mark=False
        #方向均从[左,左上,上,右上,右,右下,下,左下]进行
        if self._ChessPoint[x][y]!=0:
            TimeStop=clock()
            if TimeShow==True:
                #print TimeStop-TimeStart
                pass
            if Priority==None:
                return 0
            else:
                return 0,0
        #--成5--#
        TmpResult=[Order,Order,Order,Order,Order]
        TmpCost=ChessCostList['B5'] / 2 #重复补偿
        #位置1
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
            Pri5Mark=True
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        #位置3
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        #位置4
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        #位置5    
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            Pri5Mark=True
        #--活4--#
        TmpResult=[0,Order,Order,Order,Order,0]
        TmpCost=ChessCostList['L4'] / 2 #重复补偿
        #位置1       
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        #位置3
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        #位置4      
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
        #--冲4=1--#
        TmpResult=[-Order,Order,Order,Order,Order,0]
        TmpCost=ChessCostList['S4']
        #位置1       
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')            
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')            
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #位置3
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')               
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')                
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')       
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')   
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')        
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')       
        #位置4      
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')   
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')       
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #--冲4=2--#
        TmpResult=[Order,Order,0,Order,Order]
        TmpCost=ChessCostList['LowS4'] / 2 #重复补偿
        #位置1
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTDOWN')
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTDOWN')
        #位置3
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTDOWN')
        #位置4    
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTDOWN')
        #--冲4=3--#
        #Sp1
        TmpResult=[0,Order,Order,Order,0,Order]
        TmpCost=ChessCostList['S4']
        SPC=0 #特殊棋
        #位置1
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-5,y],[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
            SPC=1
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-5,y-5],[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')
            SPC=2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-5],[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')
            SPC=3
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+5,y-5],[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
            SPC=4
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+5,y],[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
            SPC=5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+5,y+5],[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
            SPC=6
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+5],[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP')
            SPC=7
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-5,y+5],[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
            SPC=8
        #Sp2
        TmpResult=[-Order,Order,Order,Order,0,Order]
        TmpCost=ChessCostList['S4']
        #位置1
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-5,y],[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-5,y-5],[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-5],[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')     
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+5,y-5],[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+5,y],[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+5,y+5],[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+5],[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-5,y+5],[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        TmpResult=[Order,Order,Order,0,Order]
        TmpCost=ChessCostList['S4']            
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')   
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #位置3
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')   
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')    
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #位置4
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')   
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')    
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            Pri4Mark=True
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #--眠3=1--#
        TmpResult=[-Order,Order,Order,Order,0,0]
        TmpCost=ChessCostList['S3']
        #位置1       
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')   
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')    
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置3     
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #--眠3=2--#
        TmpResult=[-Order,Order,Order,0,Order,0]
        TmpCost=ChessCostList['S3']
        #位置1       
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置3 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #--眠3=3--#
        TmpResult=[-Order,Order,0,Order,Order,0]
        TmpCost=ChessCostList['S3']
        #位置1       
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置3
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #--眠3=4--#
        TmpResult=[Order,0,0,Order,Order]
        TmpCost=ChessCostList['S3']
        #位置1
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置3 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #--眠3=5--#
        TmpResult=[Order,0,Order,0,Order]
        TmpCost=ChessCostList['S3'] / 2
        #位置1
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFTDOWN')
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFTDOWN')
        #位置3   
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFTDOWN')
        #--眠3=6--#
        TmpResult=[-Order,0,Order,Order,Order,0,-Order]
        TmpCost=ChessCostList['S3'] / 2
        SleepThreeCheck=0
        #位置1
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFTDOWN')
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFTDOWN')
        #位置3
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFTDOWN')
        #--活3=1--#
        TmpResult=[0,Order,Order,Order,0]
        TmpCost=ChessCostList['L3'] / 2
        #位置1
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            if ('LEFT' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            if ('LEFTUP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            if ('UP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            if ('RIGHTUP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            if ('RIGHT' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            if ('RIGHTDOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            if ('DOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            if ('LEFTDOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFTDOWN')
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            if ('LEFT' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            if ('LEFTUP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            if ('UP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            if ('RIGHTUP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            if ('RIGHT' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            if ('RIGHTDOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            if ('DOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            if ('LEFTDOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFTDOWN')
        #位置3
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            if ('LEFT' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            if ('LEFTUP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            if ('UP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('UP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            if ('RIGHTUP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            if ('RIGHT' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            if ('RIGHTDOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            if ('DOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('DOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            if ('LEFTDOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                Pri3Mark=True
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFTDOWN')
        #--活3=2--# 跳活3
        TmpResult=[0,Order,Order,0,Order,0]
        TmpCost=ChessCostList['JL3']
        #位置1       
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFT')
            JL3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFTUP')
            JL3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('UP')
            JL3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHTUP')
            JL3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHT')
            JL3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHTDOWN')
            JL3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('DOWN')
            JL3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFTDOWN')
            JL3Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFT')
            JL3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFTUP')
            JL3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('UP')
            JL3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHTUP')
            JL3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHT')
            JL3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHTDOWN')
            JL3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('DOWN')
            JL3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFTDOWN')
            JL3Forward.append('RIGHTUP')
        #位置3     
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFT')
            JL3Forward.append('RIGHT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFTUP')
            JL3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('UP')
            JL3Forward.append('DOWN')  
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHTUP')
            JL3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHT')
            JL3Forward.append('LEFT')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHTDOWN')
            JL3Forward.append('LEFTUP')
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('DOWN')
            JL3Forward.append('UP') 
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            Pri3Mark=True
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFTDOWN')
            JL3Forward.append('RIGHTUP')
        #--活2=1--#
        TmpResult=[0,0,Order,Order,0,0]
        TmpCost=ChessCostList['L2'] / 2
        #位置1
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        #--活2=2--#
        TmpResult=[0,Order,0,Order,0]
        TmpCost=ChessCostList['L2'] / 2
        #位置1
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        #--活2=3--#
        TmpResult=[0,Order,0,0,Order,0]
        TmpCost=ChessCostList['LowL2'] / 2             
        #位置1       
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        #位置2      
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        #--眠2=1--#
        TmpResult=[Order,0,0,0,Order]
        TmpCost=ChessCostList['S2'] / 2
        #位置1
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
        #位置5    
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost     
        #--眠2=2--#
        TmpResult=[-Order,Order,Order,0,0,0]
        TmpCost=ChessCostList['S2']
        #位置1       
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
        #位置2      
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
        #--眠2=3--#
        TmpResult=[-Order,Order,0,Order,0,0]
        TmpCost=ChessCostList['S2']
        #位置1       
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
        #位置2
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
        #--眠2=4--#
        TmpResult=[-Order,Order,0,0,Order,0]
        TmpCost=ChessCostList['S2']
        #位置1       
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
        #位置2      
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(ChessInvoke,TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost  
        #++特殊棋型++# {'B5':100000,'L4':10000,'S4':250,'L3':100,'JL3':90,'L2':10,'LowL2':9,'S3':5,'S2':2,'DS4':10000,'S4L3':10000,'DL3':5000,'S3L3':1000,'DL2':30}
 

        #--双死4--#
        if SleepFourTimes >= 2:
            Cost=Cost+ChessCostList['DS4']
            Pri4Mark=True
            if DebugMode==True:
                print 'DoubleSleep4',Order,[x,y]
        #--死4活3--#
        if (SleepFourTimes > 0) and (LiveThreeTimes > 0):
            if self._DifForward(S4Forward,L3Forward):
                Cost=Cost+ChessCostList['S4L3']
                Pri4Mark=True
            if (self._ListInclude(S4Forward,SlopeList) or self._ListInclude(L3Forward,SlopeList)) and (StrengSlopeVar.get()==True):
                Cost=Cost+ChessCostList['Slope']
                if DebugMode==True:
                    print 'Sleep4Live3',Order,[x,y],[S4Forward,L3Forward]
        elif (SleepFourTimes > 0) and (JumpLiveThreeTimes > 0):
            if self._DifForward(S4Forward,JL3Forward):
                Cost=Cost+ChessCostList['S4L3']
                Pri4Mark=True
            if (self._ListInclude(S4Forward,SlopeList) or self._ListInclude(JL3Forward,SlopeList)) and (StrengSlopeVar.get()==True):
                Cost=Cost+ChessCostList['Slope']                               
                if DebugMode==True:
                    print 'Sleep4LiveJ3',Order,[x,y],[S4Forward,JL3Forward]
        else:
            SPC=0
        #--双活3--#
        if LiveThreeTimes >= 2:
            if self._ExcludeForward(L3Forward):
                Cost=Cost+ChessCostList['DL3']
                Pri3Mark=True
            if self._ListIncludeTwo(L3Forward,SlopeList) and (StrengSlopeVar.get()==True):
                Cost=Cost+ChessCostList['Slope']                                         
                if (SleepFourTimes > 0) and (self._DifForward(S4Forward,L3Forward)):
                    Cost=Cost+ChessCostList['DL3']
                if DebugMode==True:    
                    print 'DoubleLive3',Order,[x,y],[L3Forward]                    
        elif JumpLiveThreeTimes >= 2:
            if self._ExcludeForward(JL3Forward):
                Cost=Cost+ChessCostList['DL3']
                Pri3Mark=True
            if self._ListIncludeTwo(JL3Forward,SlopeList) and (StrengSlopeVar.get()==True):
                Cost=Cost+ChessCostList['Slope']                
                if (SleepFourTimes > 0) and (self._DifForward(S4Forward,JL3Forward)):
                    Cost=Cost+ChessCostList['DL3']           
                if DebugMode==True:
                    print 'DoubleLiveJJ3',Order,[x,y],[JL3Forward]
        elif JumpLiveThreeTimes + LiveThreeTimes >= 2:
            if self._DifForward(L3Forward,JL3Forward):
                Cost=Cost+ChessCostList['DL3']
                Pri3Mark=True
            if (self._ListInclude(JL3Forward,SlopeList) or self._ListInclude(L3Forward,SlopeList)) and (StrengSlopeVar.get()==True):
                Cost=Cost+ChessCostList['Slope']                                                            
                if (SleepFourTimes > 0) and (self._DifForward(S4Forward,JL3Forward)):
                    Cost=Cost+ChessCostList['DL3']
                if DebugMode==True:                    
                    print 'DoubleLiveJ3',Order,[x,y],[L3Forward,JL3Forward]
        #--死3活3--#
        if (SleepThreeTimes > 0) and (LiveThreeTimes > 0):
            if self._DifForward(S3Forward,L3Forward):
                Cost=Cost+ChessCostList['S3L3']
                Pri3Mark=True
            if (self._ListInclude(L3Forward,SlopeList) or self._ListInclude(S3Forward,SlopeList)) and (StrengSlopeVar.get()==True):
                Cost=Cost+ChessCostList['Slope']
                if DebugMode==True:
                    print 'Sleep3Live3',Order,[x,y],[S3Forward,L3Forward]   
        elif (SleepThreeTimes > 0) and (JumpLiveThreeTimes > 0):
            if self._DifForward(S3Forward,JL3Forward):
                Cost=Cost+ChessCostList['S3L3']
                Pri3Mark=True
            if (self._ListInclude(JL3Forward,SlopeList) or self._ListInclude(S3Forward,SlopeList)) and (StrengSlopeVar.get()==True):
                Cost=Cost+ChessCostList['Slope']                  
                if DebugMode==True:
                    print 'Sleep3LiveJ3',Order,[x,y],[S3Forward,JL3Forward]
        #--双活2--#
        if LiveTwoTimes >= 2:
            Cost=Cost+ChessCostList['DL2']
            if DebugMode==True:
                print 'DoubleLive2',Order,[x,y]
        #++其他情况++#
        if Cost==0 or Chess_Num==1:
            Cost=0
            if x>=1:
                if [self._ChessPoint[x-1][y],Order]==[Order,Order]:
                    Cost=1
            if x>=1 and y>=1:
                if [self._ChessPoint[x-1][y-1],Order]==[Order,Order]:
                    Cost=1
            if y>=1:
                if [self._ChessPoint[x][y-1],Order]==[Order,Order]:
                    Cost=1
            if x<=13 and y>=1:
                if [self._ChessPoint[x+1][y-1],Order]==[Order,Order]:
                    Cost=1
            if x<=13:
                if [self._ChessPoint[x+1][y],Order]==[Order,Order]:
                    Cost=1
            if x<=13 and y<=13:
                if [self._ChessPoint[x+1][y+1],Order]==[Order,Order]:
                    Cost=1
            if y<=13:
                if [self._ChessPoint[x][y+1],Order]==[Order,Order]:
                    Cost=1
            if x>=1 and y<=13:
                if [self._ChessPoint[x-1][y+1],Order]==[Order,Order]:
                    Cost=1
        if Pri5Mark==True:
            PriorityLevel=5
        elif Pri4Mark==True:
            PriorityLevel=4
        elif Pri3Mark==True:
            PriorityLevel=3
        else:
            PriorityLevel=1
        TimeStop=clock()
        if TimeShow==True:
            #print TimeStop-TimeStart
            pass
        if Priority=='Expand':
            return Cost,PriorityLevel,SPC
        else:
            return Cost
    #列表中包含该列表元素
    def _ListInclude(self,ListA,ListB):
        Result=False
        for i in ListB:
            if i in ListA:
                Result=True
        return Result
    #列表中包含两次该列表元素
    def _ListIncludeTwo(self,ListA,ListB):
        Result=False
        aCount=0
        for i in ListB:
            if i in ListA:
                aCount=aCount+1
        if aCount>=4:
            Result=True
        return Result
    #处理不同方向
    def _DifForward(self,InListA,InListB): 
        ListA=[]
        ListB=[]
        for i in InListA:
            ListA.append(i)
        for i in InListB:
            ListB.append(i)
        for x in ListA:
            if x in ListB:
                ListA.remove(x)
                ListB.remove(x)
        for x in ListB:
            if x in ListA:
                ListA.remove(x)
                ListB.remove(x)
        if len(ListA)+len(ListB)==0:
            return False
        else:
            return True
    #排除方向
    def _ExcludeForward(self,aList): 
        ExList=[]
        DelList=[]
        for i in aList:
            if i not in ExList:
                ExList.append(i)
            else:
                if i not in DelList:
                    DelList.append(i)
        if len(DelList)==0:
            return True
        for x in DelList:
            ExList.remove(x)     
        if len(ExList)==0:
            return False
        return True
    def _CheckListMax(self,XYList,Costlist): #比较被选取列表中大小取最大值,若仍然相同取随机值
        Max=0
        SameList=[]
        for [x,y] in XYList:
            Tmp=Costlist[x][y]
            if Tmp>Max:
                Max=Tmp
                SameList=[]
            elif Tmp==Max:
                SameList.append([x,y])
        if SameList!=[]:
            return SameList[random.randint(0,len(SameList)-1)]
        else:
            return [x,y]   
    def Alpha_Cal(self): #Alpha级别战术
        Tactics='A'  #A:进攻偏向 #D:防守偏向
        HisMaxScore=0   #人最大积分
        HisMaxPoint=[-1,-1]  #人最大积分位置
        HisSamePoint=[]  #人相同最大积分列表
        MyMaxScore=0    #AI最大积分
        MyMaxPoint=[-1,-1] #AI最大积分位置
        MySamePoint=[]  #AI相同最大积分列表
        HisCost=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #人积分表
        MyCost=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #AI积分表
        for y in range(0,15):  #遍历棋盘Y
            for x in range(0,15):  #遍历棋盘X
                HisScore=self.Base_CostCal(x,y,1)
                if HisScore > HisMaxScore:
                    HisMaxScore=HisScore
                    HisMaxPoint=[x,y]
                    HisSamePoint=[]
                    HisSamePoint.append([x,y])
                elif HisScore == HisMaxScore:
                    HisMaxScore=HisScore
                    HisSamePoint.append([x,y])
                HisCost[x].append(HisScore)
                MyScore=self.Base_CostCal(x,y,-1)
                if MyScore > MyMaxScore:
                    MyMaxScore=MyScore
                    MyMaxPoint=[x,y]
                    MySamePoint=[]
                    MySamePoint.append([x,y])
                elif MyScore == MyMaxScore:
                    MyMaxScore=MyScore
                    MySamePoint.append([x,y])                    
                MyCost[x].append(MyScore)
        if DebugMode==True:
            print str(HisMaxScore) + '|' + str(MyMaxScore)
        if Tactics=='A':
            if (MyMaxScore>10000 and HisMaxScore<100000) or (MyMaxScore >= HisMaxScore):
                if len(MySamePoint)>1:
                    MyMaxPoint=self._CheckListMax(MySamePoint,HisCost)
                if MyMaxPoint==[-1,-1]:
                    raise CalError
                else:
                    if DebugMode==True:
                        print HisMaxPoint,MyMaxPoint
                    return MyMaxPoint            
            else:
                if len(HisSamePoint)>1:
                    HisMaxPoint=self._CheckListMax(HisSamePoint,MyCost)
                if HisMaxPoint==[-1,-1]:
                    raise CalError
                else:
                    if DebugMode==True:
                        print HisMaxPoint,MyMaxPoint
                    return HisMaxPoint
        elif Tactics=='D':
            if (MyMaxScore>10000 and HisMaxScore<100000) or (MyMaxScore >= HisMaxScore):
                if len(MySamePoint)>1:
                    MyMaxPoint=self._CheckListMax(MySamePoint,HisCost)
                if MyMaxPoint==[-1,-1]:
                    raise CalError
                else:
                    if DebugMode==True:
                        print HisMaxPoint,MyMaxPoint
                    return MyMaxPoint
            else:
                if len(HisSamePoint)>1:
                    HisMaxPoint=self._CheckListMax(HisSamePoint,MyCost)
                if HisMaxPoint==[-1,-1]:
                    raise CalError
                else:
                    if DebugMode==True:
                        print HisMaxPoint,MyMaxPoint
                    return HisMaxPoint                
        else:
            raise TacticsError
    def Beta_Cal(self): #Beta级别战术
        AttackTactics=0.5  #进攻程度
        DefenseTactics=0.75  #防守程度
        HisMaxScore=0   #人最大积分
        HisMaxPoint=[-1,-1]  #人最大积分位置
        HisSamePoint=[]  #人相同最大积分列表
        MyMaxScore=0    #AI最大积分
        MyMaxPoint=[-1,-1] #AI最大积分位置
        MySamePoint=[]  #AI相同最大积分列表
        HisCost=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #人积分表
        MyCost=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #AI积分表
        for y in range(0,15):  #遍历棋盘Y
            for x in range(0,15):  #遍历棋盘X
                HisScore=self.Base_CostCal(x,y,1)
                if HisScore >= HisMaxScore:
                    HisMaxScore=HisScore
                HisCost[x].append(HisScore)                
                MyScore=self.Base_CostCal(x,y,-1)
                if MyScore >= MyMaxScore:
                    MyMaxScore=MyScore
                MyCost[x].append(MyScore)
                
        if (MyMaxScore>=10000 and HisMaxScore<100000) or (MyMaxScore>=100000) or (MyMaxScore >= HisMaxScore):
            for y in range(0,15):  #遍历棋盘Y
                for x in range(0,15):  #遍历棋盘X
                    MyScore=MyCost[x][y] + AttackTactics * HisCost[x][y] #计算攻击系数
                    if MyScore > MyMaxScore:
                        MyMaxScore=MyScore
                        MyMaxPoint=[x,y]
                        MySamePoint=[]
                        MySamePoint.append([x,y])
                    elif MyScore == MyMaxScore:
                        MyMaxScore=MyScore
                        MySamePoint.append([x,y])
            if DebugMode==True:
                print str(HisMaxScore) + '|' + str(MyMaxScore)                             
            if len(MySamePoint)>0:
                MyMaxPoint=self._CheckListMax(MySamePoint,HisCost)
                if len(MySamePoint)>1 and DebugMode==True:
                    print 'AI',MySamePoint
            if MyMaxPoint==[-1,-1]:
                if DebugMode==True:
                    print 'AIMaxScore:',MyMaxScore
                    print 'AIMaxPoint:',MyMaxPoint
                    print 'AISamePoint',MySamePoint
                raise CalError
            else:
                if DebugMode==True:
                    print HisMaxPoint,MyMaxPoint
                return MyMaxPoint
        else:
            for y in range(0,15):  #遍历棋盘Y
                for x in range(0,15):  #遍历棋盘X
                    HisScore=HisCost[x][y] + DefenseTactics * MyCost[x][y] #计算防御系数
                    if HisScore > HisMaxScore:
                        HisMaxScore=HisScore
                        HisMaxPoint=[x,y]
                        HisSamePoint=[]
                        HisSamePoint.append([x,y])
                    elif HisScore == HisMaxScore:
                        HisMaxScore=HisScore
                        HisSamePoint.append([x,y])
            if DebugMode==True:
                print str(HisMaxScore) + '|' + str(MyMaxScore)            
            if len(HisSamePoint)>0:
                HisMaxPoint=self._CheckListMax(HisSamePoint,MyCost)
            if HisMaxPoint==[-1,-1]:
                if DebugMode==True:
                    print 'HumanMaxScore:',HisMaxScore
                    print 'HumanMaxPoint:',HisMaxPoint
                    print 'HumanSamePoint',HisSamePoint
                raise CalError
            else:
                if DebugMode==True:
                    print HisMaxPoint,MyMaxPoint
                return HisMaxPoint
    #=====================Gamma=======================#
    def Gamma_Cal(self): #Gamma级别战术,暂无
        HisDangerousPoint={}  #人危险积分位置
        MyDangerousPoint={} #AI危险积分位置
        HisCost=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #人积分表
        MyCost=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] #AI积分表
        Result=None
        KillPoint=[]
        SPCS=[] #特殊棋位置起始
        SPCE=[] #特殊棋位置结束
        for y in range(0,15):  #遍历棋盘Y
            for x in range(0,15):  #遍历棋盘X
                try:
                    MyScore,Priority,TmpSPC=self.Base_CostCal(x,y,-1,True,'Expand')
                except ValueError:
                    MyScore,Priority=self.Base_CostCal(x,y,-1,True,'Expand')
                    SPC=0
                if MyScore >= 100000:
                    return (x,y)
                if MyScore >= 5000 or Priority >= 4:
                    MyDangerousPoint[str(x)+','+str(y)]=Priority
                MyCost[x].append(MyScore)
                Priority=None
                try:
                    HisScore,Priority,SPC=self.Base_CostCal(x,y,1,True,'Expand')
                except ValueError:
                    HisScore,Priority=self.Base_CostCal(x,y,1,True,'Expand')
                    SPC=0
                if SPC!=0:
                    SPCS.append((x,y))
                    if SPC==1:
                        SPCE.append((x-1,y))
                    elif SPC==2:
                        SPCE.append((x-1,y-1))
                    elif SPC==3:
                        SPCE.append((x,y-1))
                    elif SPC==4:
                        SPCE.append((x+1,y-1))
                    elif SPC==5:
                        SPCE.append((x+1,y))
                    elif SPC==6:
                        SPCE.append((x+1,y+1))
                    elif SPC==7:
                        SPCE.append((x,y+1))
                    elif SPC==8:
                        SPCE.append((x-1,y+1))
                if HisScore >= 100000:
                    KillPoint.append((x,y))
                if HisScore >= 5000:
                    HisDangerousPoint[str(x)+','+str(y)]=Priority
                    if DebugMode==True:
                        print HisScore,x,y
                HisCost[x].append(HisScore)
        if KillPoint!=[]:
            KillList=[]
            for l in KillPoint:
                KillList.append(MyCost[l[0]][l[1]])
            return KillPoint[self._GetListMax(KillList)]
        DMCL=False #特殊棋型锁定
        if SPCS!=[]:
            DMCL=True
            TmpLock=False
            PopList=[]
            for o in xrange(0,len(SPCS)):
                HisCost[SPCS[o][0]][SPCS[o][1]]=HisCost[SPCS[o][0]][SPCS[o][1]]-ChessCostList['S4L3']
                HisCost[SPCE[o][0]][SPCE[o][1]]=HisCost[SPCE[o][0]][SPCE[o][1]]+ChessCostList['S4L3']*1.5
                if HisCost[SPCE[o][0]][SPCE[o][1]] >= 5000:
                    TmpLock=True
            for i in HisDangerousPoint:
                TmpResult=i.split(',')
                for u in SPCS:
                    if (int(TmpResult[0]),int(TmpResult[1]))==u:
                        if str(u[0])+','+str(u[0]) in HisDangerousPoint:
                            if HisDangerousPoint[str(u[0])+','+str(u[0])] > HisDangerousPoint[str(u[0])+','+str(u[0])]:
                                HisDangerousPoint[str(u[0])+','+str(u[0])]=HisDangerousPoint[i]
                        if TmpLock==False:
                            PopList.append(i)
            for q in PopList:
                HisDangerousPoint.pop(q)
        if len(HisDangerousPoint) > 0:
            Result=self.Gamma_Defense(HisDangerousPoint,MyDangerousPoint,HisCost,MyCost,DMCL)
        else:
            Result=self.Gamma_Attack(MyDangerousPoint,HisDangerousPoint,MyCost,HisCost) #进攻策略,若无好的进攻点则最优化防守
        return Result
    def Gamma_Defense(self,HDangerP,ADangerP,HCostL,ACostL,aLock): #Gamma防御策略
        if len(HDangerP)==1: #对方有单个高分致死点
            for i in HDangerP:
                Result=i.split(',')
                return (int(Result[0]),int(Result[1]))
        elif len(HDangerP)>1: #对方有多个高分致死点
            DangerCheck=False
            ListPoint=[]
            for i in HDangerP:
                Result=i.split(',')
                Rescue=True
                if aLock==False:
                    TmpPoint,Rescue=self._Deepness_Def(int(Result[0]),int(Result[1]))
                else:
                    TmpPoint=(int(Result[0]),int(Result[1]))
                    return TmpPoint
                if Rescue==True:
                    DangerCheck=True
                ListPoint.append(TmpPoint)
            if DangerCheck==False or len(ADangerP)==0: #危险解除或我方无危险点
                return self._Repeat_Chiose(ListPoint)
            #危险仍然存在
            AIMaxScore,AIPoint=self._PriorityLevelCal(ADangerP)
            HumanMaxScore,HumanPoint=self._PriorityLevelCal(HDangerP)
            if AIMaxScore >= HumanMaxScore: #我方优先级大于对方
                if len(AIPoint)==1:
                    return AIPoint(0)
                elif len(AIPoint)>1:
                    TmpDict={}
                    for x in AIPoint:
                        TmpDict[x]=HCostL[x[0]][x[1]]+ACostL[x[0]][x[1]]
                    return self._GetDictMax(TmpDict)
            else:
                return self._Repeat_Chiose(ListPoint)
    def _GetDictMax(self,aDict): #获取字典最大值
        MaxValue=0
        MaxKey=[]
        for i in aDict:
            TmpValue=aDict[i]
            if TmpValue>MaxValue:
                MaxValue=TmpValue
                MaxKey=[i]
            elif TmpValue==MaxValue:
                MaxValue=TmpValue
                MaxKey.append(i)
        if len(MaxKey)==1:
            return MaxKey[0]
        elif len(MaxKey)>1:
            return MaxKey[random.randint(0,len(MaxKey)-1)]
    def _GetListMax(self,aList): #获取列表最大值
        MaxValue=-1
        MaxKey=[]
        for i in xrange(0,len(aList)):
            TmpValue=aList[i]
            if TmpValue>MaxValue:
                MaxValue=TmpValue
                MaxKey=[i]
            elif TmpValue==MaxValue:
                MaxValue=TmpValue
                MaxKey.append(i)
        if len(MaxKey)==1:
            return MaxKey[0]
        elif len(MaxKey)>1:
            return MaxKey[random.randint(0,len(MaxKey)-1)]        
    def _PriorityLevelCal(self,aDict):  #优先度计算
        MaxLevel=0
        MaxPoint=[]
        for i in aDict:
            aLevel=aDict[i]
            if aLevel>MaxLevel:
                MaxLevel=aLevel
                TmpStr=i.split(',')
                MaxPoint=[(int(TmpStr[0]),int(TmpStr[1]))]
            elif aLevel==MaxLevel:
                MaxLevel==aLevel
                TmpStr=i.split(',')
                MaxPoint.append((int(TmpStr[0]),int(TmpStr[1])))
        return MaxLevel,MaxPoint
    def _Repeat_Chiose(self,aList):
        TmpList=[]
        ResultList=[]
        for i in aList:
            if i in TmpList:
                ResultList.append(i)
            else:
                TmpList.append(i)
        if ResultList==[]:
            return TmpList[random.randint(0,len(TmpList)-1)]
        else:
            return ResultList[random.randint(0,len(ResultList)-1)]
    def _Deepness_Def(self,x,y): #深度防御  检索高分棋子周围棋位并返回 检查危机解除
        DefenseLevel=2 #1:8格  2:24  3:48  4:80  5:120
        TmpMin=9999999
        SamePoint=[]
        StepScore=[]
        DangerCheck=True #危险确认
        for lineY in range(y-DefenseLevel,y+DefenseLevel+1):  #模拟每一步落子
            for lineX in range(x-1,x+2):
                if lineX<0 or lineX>14 or lineY<0 or lineY>14:
                    continue
                if self._ChessPoint[lineX][lineY]!=0:
                    continue
                self._SimulatePoint=deepcopy(self._ChessPoint)
                self._SimulatePoint[lineX][lineY]=-1
                TmpNum=0
                for ExY in range(y-DefenseLevel,y+DefenseLevel+1):  #模拟中每一步的结果
                    for ExX in range(x-DefenseLevel,x+DefenseLevel+1):
                        if ExX<0 or ExX>14 or ExY<0 or ExY>14:
                            continue
                        if self._SimulatePoint[ExX][ExY]!=0:
                            continue
                        TmpValue=self.Base_CostCal(ExX,ExY,1,False)
                        TmpNum=TmpValue+TmpNum
                if TmpNum<TmpMin:
                    TmpMin=TmpNum
                    SamePoint=[(lineX,lineY)]
                elif TmpNum==TmpMin:
                    SamePoint.append((lineX,lineY))
                StepScore.append(TmpNum)
        for i in StepScore:
            if i<5000:
                DangerCheck=False
        if len(SamePoint)>1:
            return SamePoint[random.randint(0,len(SamePoint)-1)],DangerCheck  #危机检查
        elif len(SamePoint)==1:
            return SamePoint[0],DangerCheck
        else:
            raise
    def Gamma_Attack(self,ADangerP,HDangerP,ACostL,HCostL):
        '''进攻需要考虑布局,抢先,防守偏向/布局偏向,进攻若无力则放置对方后手'''
        #临时进攻方案(测试用)
        MaxValue=-1
        MaxKey=[]
        for y in xrange(0,15):
            for x in xrange(0,15):
                TmpValue=ACostL[x][y]
                if TmpValue>MaxValue:
                    MaxValue=TmpValue
                    MaxKey=[(x,y)]
                elif TmpValue==MaxValue:
                    MaxValue=TmpValue
                    MaxKey.append((x,y))
        if len(MaxKey)==1:
            return MaxKey[0]
        elif len(MaxKey)>1:
            return MaxKey[random.randint(0,len(MaxKey)-1)]
    #=====================Gamma=======================#
    def Omega_Cal(self): #Omega级别战术,暂无
        x=random.randint(0,14) 
        y=random.randint(0,14)
        while ChessPoint[x][y]!=0:
            x=random.randint(0,14) 
            y=random.randint(0,14)            
        return [x,y]
    def AIChessPut(self,LineX,LineY):
        global CheckFrameColor,HistoryChess,Chess_Num
        self._ChessPoint[LineX][LineY]=-1
        self._ChessOrder[0]=1
        ChessBoard.delete('MouseCheck')
        MouseCheckFrame(LineX,LineY)
        HistoryChess[LineX][LineY]=Chess_Num+1
        CheckFrameColor='black'
        for item in self._ChessBoard.find_withtag('MouseCheck'):
            ChessBoard.itemconfig(item,fill = 'White')
        self._ChessBoard.bind_all('<KeyPress-r>',ChessReset)
                   
#---------AI---------#
#==Error==#
class AITypeError(Exception):
    def __init__(self,value):
        TmpRank=''
        for i in range(0,len(LevelRank)):
            TmpRank=TmpRank + LevelRank[i] + ','
        TmpRank=TmpRank[:-1]
        Message='AI Type Error!','Type Can\'t Be <' + value + '>,You Can Use <' + TmpRank + '>'
        self.args=Message
class CalError(Exception):
    pass
class TacticsError(Exception):
    def __init__(self):
        self.args='Tactics Error!','You Can Choise \'A\'(Attack) or \'D\'(Defense) Tactics'
#==Error==#
Level='Alpha'
#StartGUI
StartMain=Tk()
StartMain.wm_title('Difficulty Level')
StartMain.resizable(False,False)
StartMain.geometry('360x50+500+400')
def AlphaStart():
    global Level
    Level = 'Alpha'
    StartMain.destroy()
def BetaStart():
    global Level
    Level = 'Beta'
    StartMain.destroy()
def GammaStart():
    global Level
    Level = 'Gamma'
    StartMain.destroy()
def OmegaStart():
    global Level
    Level = 'Omega'
    StartMain.destroy()
TypeButtonAlpha=Button(StartMain,text='Alpha',command=AlphaStart)
TypeButtonBeta=Button(StartMain,text='Beta',command=BetaStart)
TypeButtonGamma=Button(StartMain,text='Gamma',command=GammaStart)
TypeButtonOmega=Button(StartMain,text='Omega',command=OmegaStart,state='disabled')
TypeButtonAlpha.place(anchor=CENTER,relx=0.13,rely=0.5)
TypeButtonBeta.place(anchor=CENTER,relx=0.38,rely=0.5)
TypeButtonGamma.place(anchor=CENTER,relx=0.63,rely=0.5)
TypeButtonOmega.place(anchor=CENTER,relx=0.88,rely=0.5)
StartMain.mainloop() 
#创建root窗口对象
root=Tk()
PvMode=StringVar(root,'Computer') #人机/人人
LevelVar=StringVar(root,Level) #难度等级
Chess3DVar=BooleanVar(root,Chess3D) #3D棋子
StrengSlopeVar=BooleanVar(root,SlopeStreng) #强化斜线
root.wm_title('Gobang')
root.resizable(False,False)
root.geometry('800x800+200+20')
#Menu
MenuBar=Menu(root)
FunctionButton=Menu(MenuBar,tearoff=0) #功能菜单
#悔棋#
def TakeChessBack():
    global HistoryChess,Chess_Num,ChessPoint,ChessOrder,MemChessPoint,PvMode,CheckFrameColor
    TakeLast=[-1,-1]
    TakeSecond=[-1,-1]
    if PvMode.get()=='Computer':
        for x in range(0,15):
            for y in range(0,15):
                if HistoryChess[x][y]==Chess_Num:
                    TakeLast=[x,y]
                    HistoryChess[x][y]=0
                if HistoryChess[x][y]==Chess_Num-1:
                    TakeSecond=[x,y]
                    HistoryChess[x][y]=0
                if TakeLast!=[-1,-1] and TakeSecond!=[-1,-1]:
                    break
        Chess_Num=Chess_Num-3
        ChessPoint[TakeLast[0]][TakeLast[1]]=0
        ChessPoint[TakeSecond[0]][TakeSecond[1]]=0
        if Chess_Num<2:
            FunctionButton.entryconfig(0,state='disabled')        
    elif PvMode.get()=='People':
        for x in range(0,15):
            for y in range(0,15):
                if HistoryChess[x][y]==Chess_Num:
                    TakeLast=[x,y]
                    HistoryChess[x][y]=0
                if TakeLast!=[-1,-1]:
                    break            
        if ChessOrder[0]==1:
            ChessOrder[0]=-1
            CheckFrameColor='white'
        elif ChessOrder[0]==-1:
            ChessOrder[0]=1
            CheckFrameColor='black'
        Chess_Num=Chess_Num-2
        ChessPoint[TakeLast[0]][TakeLast[1]]=0
        if Chess_Num<1:
            FunctionButton.entryconfig(0,state='disabled')
#悔棋#
FunctionButton.add_command(label='Take Back',state='disabled',command=TakeChessBack)  #悔棋
FunctionButton.add_command(label='Restart',command=lambda:ChessReset(None))  #重开
FunctionButton.add_separator() #分割线
def Chess3DSetting():
    global Chess3DVar
    Chess3DVar.set(not Chess3DVar.get())
FunctionButton.add_checkbutton(label='Chess3D',command=Chess3DSetting)
MenuBar.add_cascade(label='Function',menu=FunctionButton)
SettingButton=Menu(MenuBar,tearoff=0) #设置菜单
SettingButton.add_radiobutton(label='Alpha',variable=LevelVar,value='Alpha') #难度Alpha
SettingButton.add_radiobutton(label='Beta',variable=LevelVar,value='Beta') #难度Beta
SettingButton.add_radiobutton(label='Gamma',variable=LevelVar,value='Gamma') #难度Gamma
SettingButton.add_radiobutton(label='Omega',variable=LevelVar,value='Omega',state='disabled') #难度Omega ,state='disabled'
SettingButton.add_separator() #分割线
DetailedButton=Menu(SettingButton,tearoff=0) #详细设置菜单
SettingButton.add_cascade(label='Detailed Setting',menu=DetailedButton)
def StrengSlopeSetting():
    global StrengSlopeVar 
    StrengSlopeVar.set(not StrengSlopeVar.get())
DetailedButton.add_checkbutton(label='StrengSlope',command=StrengSlopeSetting) #强化斜线
DetailedButton.invoke(DetailedButton.index(True))
SettingButton.add_separator() #分割线
SettingButton.add_radiobutton(label='PVP MODE',variable=PvMode,value='People') #人人对战
SettingButton.add_radiobutton(label='PVC MODE',variable=PvMode,value='Computer') #人人对战
MenuBar.add_cascade(label='Setting',menu=SettingButton)
ExitButton=Menu(MenuBar,tearoff=0) #退出菜单
ExitButton.add_command(label='Exit',command=lambda:sys.exit(0)) #退出
MenuBar.add_cascade(label='Exit',menu=ExitButton)
root.config(menu=MenuBar)
#创建画布
ChessFrame=Frame(root)
ChessBoard=Canvas(ChessFrame,bg='#EEE8AA',width=800,height=800,highlightthickness=0)
ChessFrame.pack(side='bottom')
ChessBoard.pack(fill='both')
font = tkFont.Font(family = 'System',size = 40)
font_Big = tkFont.Font(family = 'System',size = 43)
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
    global ChessPoint,MemChessPoint,ManClick,Chess_Num,Chess3DVar,PvMode
    if ChessPoint != MemChessPoint:
        for x in range(0,15):
            for y in range(0,15):
                MemChessPoint[x][y]=ChessPoint[x][y]
        ChessBoard.delete('Chess')
        for x in range(0,15):
            for y in  range(0,15):
                if ChessPoint[x][y]==1:
                    ChessBoard.create_oval(CB_Point[x][y][0]-ChessSize,CB_Point[x][y][1]-ChessSize,CB_Point[x][y][0]+ChessSize,CB_Point[x][y][1]+ChessSize,fill='black',outline='black',tag='Chess')
                    if Chess3DVar.get()==True:
                        ChessBoard.create_oval(CB_Point[x][y][0]-0.55*ChessSize,CB_Point[x][y][1]-0.55*ChessSize,CB_Point[x][y][0]-0.25*ChessSize,CB_Point[x][y][1]-0.25*ChessSize,fill='#FFFFFF',outline='#D0D0D0',tag='Chess')
                if ChessPoint[x][y]==-1:
                    ChessBoard.create_oval(CB_Point[x][y][0]-ChessSize,CB_Point[x][y][1]-ChessSize,CB_Point[x][y][0]+ChessSize,CB_Point[x][y][1]+ChessSize,fill='#F0F0F0',outline='#F0F0F0',tag='Chess')
                    if Chess3DVar.get()==True:
                        ChessBoard.create_oval(CB_Point[x][y][0]-0.55*ChessSize,CB_Point[x][y][1]-0.55*ChessSize,CB_Point[x][y][0]-0.25*ChessSize,CB_Point[x][y][1]-0.25*ChessSize,fill='#FFFFFF',outline='#FFFFFF',tag='Chess')
        checkwin=GobangRule.BaseRule()
        if checkwin==0:
            if PvMode.get()=='Computer':
                if ChessOrder[0]==1 and ManClick==True:
                    ManClick=False
                    ChessOrder[0]=-1
            elif PvMode.get()=='People':
                pass
        root.update()
        ChessBoard.update()
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
    global MousePos,MouseReInto,ChessOrder,NowMousePos,PvMode
    if ChessOrder[0]==1 or PvMode.get()=='People':
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
    global ChessOrder
    if PvMode.get()=='Computer':
        if ChessOrder[0]==1:
            ChessBoard.delete('MouseCheck')
    elif PvMode.get()=='People':
        ChessBoard.delete('MouseCheck')
def ChessPut(event):
    global ChessOrder,NowMousePos,CheckFrameColor,ChessBoard,ManClick,Chess_Num,HistoryChess
    if NowMousePos==[None,None]:
        return
    if PvMode.get()=='Computer':
        if ChessOrder[0]==1:
            if ChessPoint[NowMousePos[0]][NowMousePos[1]]==0:
                ChessPoint[NowMousePos[0]][NowMousePos[1]]=1
                HistoryChess[NowMousePos[0]][NowMousePos[1]]=Chess_Num+1
                ManClick=True
                CheckFrameColor='white'
    elif PvMode.get()=='People':
        if ChessPoint[NowMousePos[0]][NowMousePos[1]]==0:
            ChessPoint[NowMousePos[0]][NowMousePos[1]]=ChessOrder[0]
            HistoryChess[NowMousePos[0]][NowMousePos[1]]=Chess_Num+1
            if ChessOrder[0]==1:
                ChessOrder[0]=-1
                CheckFrameColor='white'
                ManClick=False
                for item in ChessBoard.find_withtag('MouseCheck'):
                    ChessBoard.itemconfig(item,fill = 'white')            
            elif ChessOrder[0]==-1:
                ChessOrder[0]=1
                CheckFrameColor='black'
                ManClick=False
                for item in ChessBoard.find_withtag('MouseCheck'):
                    ChessBoard.itemconfig(item,fill = 'black')
    if Chess_Num>0:
        FunctionButton.entryconfig(0,state='normal')
def ChessReset(event):
    global ChessPoint,MemChessPoint,ChessBoard,ChessOrder,CheckFrameColor,Chess_Num,HistoryChess
    for x in range(0,15):
        for y in range(0,15):
            ChessPoint[x][y]=0
            MemChessPoint[x][y]=0
            HistoryChess[x][y]=0
    Chess_Num=0
    ChessBoard.delete('Chess')
    ChessOrder[0]=1
    CheckFrameColor='black'
    for item in ChessBoard.find_withtag('MouseCheck'):
        ChessBoard.itemconfig(item,fill = 'black')
def WinAndReset(event):
    global ChessPoint,MemChessPoint,ChessBoard,ChessOrder,CheckFrameColor
    ChessReset(event)
    ChessBoard.delete('WinText')
    ChessBoard.unbind('<Button-1>')
    ChessBoard.bind('<Button-1>',ChessPut)    
#方法绑定
ChessBoard.bind('<Motion>',MouseMovePos)
ChessBoard.bind('<Leave>',MouseMoveOut)
ChessBoard.bind('<Button-1>',ChessPut)
ChessBoard.bind_all('<KeyPress-r>',ChessReset)
#窗口执行进入事件监控
GBAI=GobangAI(root,ChessOrder,ChessPoint,ChessBoard,LevelVar)
root.after(10,ChessGenerator)
root.mainloop()
