# -*- coding:utf-8 -*-
from Tkinter import *
import os,sys
from time import sleep as delay
import tkFont
import random

#初始化定义#
DebugMode=True #调试模式
SlopeStreng=True #强化斜线
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
ChessOrder=[1] #执棋顺序 1:黑 -1:百
ManClick=False #人点击
SlopeList=['LEFTUP','LEFTDOWN','RIGHTUP','RIGHTDOWN'] #斜面元素
ChessCostList={'B5':100000,'L4':10000,'S4':95,'LowS4':90,'L3':100,'JL3':96,'L2':10,'LowL2':9,'S3':5,'S2':2,'DS4':10000,'S4L3':10000,'DL3':5000,'S3L3':15,'DL2':30,'Slope':15}
              #成5         活4        冲4      低级冲4   活3      跳3      活2     低级活2   眠3    眠2    双冲4       冲4活3        双活3     眠3活3     双活2    斜线
#棋盘点位
for x in range(0,15):
    for y in range(0,15):
        CB_Point[x].append([PosLEFT+x*LineStep,PosTOP+y*LineStep])
#棋子初始化
for x in range(0,15):
    for y in range(0,15):
        ChessPoint[x].append(0)
for x in range(0,15):
    for y in range(0,15):
        MemChessPoint[x].append(0)
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
        if self.AIType not in LevelRank:
            raise AITypeError(self.AIType)
        self._root=root
        self._ChessOrder=ChessOrder
        self._ChessPoint=ChessPoint
        self._ChessBoard=ChessBoard
        self._root.after(10,lambda:self._RUN(self.AIType))
    def _RUN(self,Type): #自动循环运行
        if self._ChessOrder[0]==-1:
            if Type=='Alpha':
                CalValue=self.Alpha_Cal()
            if Type=='Beta':
                CalValue=self.Beta_Cal()
            if Type=='Gamma':
                CalValue=self.Gamma_Cal()
            self._ChessBoard.unbind_all('<KeyPress-r>')
            self._root.after(10,lambda:self.AIChessPut(CalValue[0],CalValue[1]))
            self._ChessOrder[0]=0
        self._root.after(10,lambda:self._RUN(self.AIType))
    def ChessTypeJudge(self,result,*args): #(Reuslt,[x-4,y],[x-3,y],[x-2,y],[x-1,y],[x,y])
        aList=[]
        for i in range(0,len(args)):
            if type(args[i])==list:
                if (args[i][0]<0) or (args[i][1]<0) or (args[i][0]>14) or (args[i][1]>14):
                    return False
                aList.append(self._ChessPoint[args[i][0]][args[i][1]])
            else:
                aList.append(args[i])
        if aList==result:
            return True
        else:
            return False
    def Base_CostCal(self,x,y,Order): #基本分数算法
        global ChessCostList,SlopeList,SlopeStreng
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
        #方向均从[左,左上,上,右上,右,右下,下,左下]进行
        if self._ChessPoint[x][y]!=0:
            return 0
        #--成5--#
        TmpResult=[Order,Order,Order,Order,Order]
        TmpCost=ChessCostList['B5'] / 2 #重复补偿
        #位置1
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
        #位置3
        if self.ChessTypeJudge(TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
        #位置4
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
        #位置5    
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost           
        #--活4--#
        TmpResult=[0,Order,Order,Order,Order,0]
        TmpCost=ChessCostList['L4'] / 2 #重复补偿
        #位置1       
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost  
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost  
        if self.ChessTypeJudge(TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
        #位置3
        if self.ChessTypeJudge(TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost  
        if self.ChessTypeJudge(TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
        #位置4      
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost  
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost         
        #--冲4=1--#
        TmpResult=[-Order,Order,Order,Order,Order,0]
        TmpCost=ChessCostList['S4']
        #位置1       
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')            
        if self.ChessTypeJudge(TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')            
        if self.ChessTypeJudge(TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #位置3
        if self.ChessTypeJudge(TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')               
        if self.ChessTypeJudge(TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')                
        if self.ChessTypeJudge(TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')       
        if self.ChessTypeJudge(TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')   
        if self.ChessTypeJudge(TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')        
        if self.ChessTypeJudge(TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')       
        #位置4      
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')   
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')       
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #--冲4=2--#
        TmpResult=[Order,Order,0,Order,Order]
        TmpCost=ChessCostList['LowS4'] / 2 #重复补偿
        #位置1
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTDOWN')
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTDOWN')
        #位置3
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTDOWN')
        #位置4    
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+0.5
            S4Forward.append('LEFTDOWN')
        #--冲4=3--#
        TmpResult=[Order,Order,Order,0,Order]
        TmpCost=ChessCostList['S4']
        #位置1
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')     
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')   
        if self.ChessTypeJudge(TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #位置3
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')   
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')    
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #位置4
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFT')
            S4Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTUP')
            S4Forward.append('RIGHTDOWN')   
        if self.ChessTypeJudge(TmpResult,Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('UP')
            S4Forward.append('DOWN')    
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTUP')
            S4Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHT')
            S4Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('RIGHTDOWN')
            S4Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('DOWN')
            S4Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepFourTimes=SleepFourTimes+1
            S4Forward.append('LEFTDOWN')
            S4Forward.append('RIGHTUP')
        #--眠3=1--#
        TmpResult=[-Order,Order,Order,Order,0,0]
        TmpCost=ChessCostList['S3']
        #位置1       
        if self.ChessTypeJudge(TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')   
        if self.ChessTypeJudge(TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')    
        if self.ChessTypeJudge(TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置3     
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #--眠3=2--#
        TmpResult=[-Order,Order,Order,0,Order,0]
        TmpCost=ChessCostList['S3']
        #位置1       
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置3 
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #--眠3=3--#
        TmpResult=[-Order,Order,0,Order,Order,0]
        TmpCost=ChessCostList['S3']
        #位置1       
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置3
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #--眠3=4--#
        TmpResult=[Order,0,0,Order,Order]
        TmpCost=ChessCostList['S3']
        #位置1
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #位置3 
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFT')
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTUP')
            S3Forward.append('RIGHTDOWN')  
        if self.ChessTypeJudge(TmpResult,Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('UP')
            S3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTUP')
            S3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHT')
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('RIGHTDOWN')
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('DOWN')
            S3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+1
            S3Forward.append('LEFTDOWN')
            S3Forward.append('RIGHTUP')
        #--眠3=5--#
        TmpResult=[Order,0,Order,0,Order]
        TmpCost=ChessCostList['S3'] / 2
        #位置1
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFTDOWN')
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFTDOWN')
        #位置3   
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            S3Forward.append('LEFTDOWN')
        #--眠3=6--#
        TmpResult=[-Order,0,Order,Order,Order,0,-Order]
        TmpCost=ChessCostList['S3'] / 2
        SleepThreeCheck=0
        #位置1
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFTDOWN')
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFTDOWN')
        #位置3
        if self.ChessTypeJudge(TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            SleepThreeTimes=SleepThreeTimes+0.5
            SleepThreeCheck=1
            S3Forward.append('LEFTDOWN')
        #--活3=1--#
        TmpResult=[0,Order,Order,Order,0]
        TmpCost=ChessCostList['L3'] / 2
        #位置1
        if self.ChessTypeJudge(TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            if ('LEFT' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            if ('LEFTUP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            if ('UP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            if ('RIGHTUP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            if ('RIGHT' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            if ('RIGHTDOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            if ('DOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            if ('LEFTDOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFTDOWN')
            #位置2
        if self.ChessTypeJudge(TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            if ('LEFT' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            if ('LEFTUP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            if ('UP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            if ('RIGHTUP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            if ('RIGHT' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            if ('RIGHTDOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            if ('DOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            if ('LEFTDOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFTDOWN')
            #位置3
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            if ('LEFT' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            if ('LEFTUP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            if ('UP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('UP')
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            if ('RIGHTUP' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHTUP')
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            if ('RIGHT' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            if ('RIGHTDOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            if ('DOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('DOWN')
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            if ('LEFTDOWN' not in S3Forward) or (SleepThreeCheck==0):
                Cost=Cost+TmpCost
                LiveThreeTimes=LiveThreeTimes+0.5
                L3Forward.append('LEFTDOWN')
        #--活3=2--# 跳活3
        TmpResult=[0,Order,Order,0,Order,0]
        TmpCost=ChessCostList['JL3']
        #位置1       
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFT')
            JL3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFTUP')
            JL3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('UP')
            JL3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHTUP')
            JL3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHT')
            JL3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHTDOWN')
            JL3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('DOWN')
            JL3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFTDOWN')
            JL3Forward.append('RIGHTUP')
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFT')
            JL3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFTUP')
            JL3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('UP')
            JL3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHTUP')
            JL3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHT')
            JL3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHTDOWN')
            JL3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('DOWN')
            JL3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFTDOWN')
            JL3Forward.append('RIGHTUP')
        #位置3     
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFT')
            JL3Forward.append('RIGHT')
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFTUP')
            JL3Forward.append('RIGHTDOWN')
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('UP')
            JL3Forward.append('DOWN')  
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHTUP')
            JL3Forward.append('LEFTDOWN')
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHT')
            JL3Forward.append('LEFT')
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('RIGHTDOWN')
            JL3Forward.append('LEFTUP')
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('DOWN')
            JL3Forward.append('UP') 
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            JumpLiveThreeTimes=JumpLiveThreeTimes+1
            JL3Forward.append('LEFTDOWN')
            JL3Forward.append('RIGHTUP')
        #--活2=1--#
        TmpResult=[0,0,Order,Order,0,0]
        TmpCost=ChessCostList['L2'] / 2
        #位置1
        if self.ChessTypeJudge(TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        #--活2=2--#
        TmpResult=[0,Order,0,Order,0]
        TmpCost=ChessCostList['L2'] / 2
        #位置1
        if self.ChessTypeJudge(TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        #--活2=3--#
        TmpResult=[0,Order,0,0,Order,0]
        TmpCost=ChessCostList['LowL2'] / 2             
        #位置1       
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        #位置2      
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
            LiveTwoTimes=LiveTwoTimes+0.5
        #--眠2=1--#
        TmpResult=[Order,0,0,0,Order]
        TmpCost=ChessCostList['S2'] / 2
        #位置1
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order):
            Cost=Cost+TmpCost
        #位置5    
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost     
        #--眠2=2--#
        TmpResult=[-Order,Order,Order,0,0,0]
        TmpCost=ChessCostList['S2']
        #位置1       
        if self.ChessTypeJudge(TmpResult,[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3]):
            Cost=Cost+TmpCost
        #位置2      
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
        #--眠2=3--#
        TmpResult=[-Order,Order,0,Order,0,0]
        TmpCost=ChessCostList['S2']
        #位置1       
        if self.ChessTypeJudge(TmpResult,[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y],[x+2,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1],[x+2,y+2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1],[x,y+2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1],[x-2,y+2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y],[x-2,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1],[x-2,y-2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1],[x,y-2]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1],[x+2,y-2]):
            Cost=Cost+TmpCost
        #位置2
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost
        #--眠2=4--#
        TmpResult=[-Order,Order,0,0,Order,0]
        TmpCost=ChessCostList['S2']
        #位置1       
        if self.ChessTypeJudge(TmpResult,[x-4,y],[x-3,y],[x-2,y],[x-1,y],Order,[x+1,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-4,y-4],[x-3,y-3],[x-2,y-2],[x-1,y-1],Order,[x+1,y+1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-4],[x,y-3],[x,y-2],[x,y-1],Order,[x,y+1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+4,y-4],[x+3,y-3],[x+2,y-2],[x+1,y-1],Order,[x-1,y+1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+4,y],[x+3,y],[x+2,y],[x+1,y],Order,[x-1,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+4,y+4],[x+3,y+3],[x+2,y+2],[x+1,y+1],Order,[x-1,y-1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+4],[x,y+3],[x,y+2],[x,y+1],Order,[x,y-1]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-4,y+4],[x-3,y+3],[x-2,y+2],[x-1,y+1],Order,[x+1,y-1]):
            Cost=Cost+TmpCost
        #位置2      
        if self.ChessTypeJudge(TmpResult,[x-1,y],Order,[x+1,y],[x+2,y],[x+3,y],[x+4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-1,y-1],Order,[x+1,y+1],[x+2,y+2],[x+3,y+3],[x+4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y-1],Order,[x,y+1],[x,y+2],[x,y+3],[x,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y-1],Order,[x-1,y+1],[x-2,y+2],[x-3,y+3],[x-4,y+4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y],Order,[x-1,y],[x-2,y],[x-3,y],[x-4,y]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x+1,y+1],Order,[x-1,y-1],[x-2,y-2],[x-3,y-3],[x-4,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x,y+1],Order,[x,y-1],[x,y-2],[x,y-3],[x,y-4]):
            Cost=Cost+TmpCost
        if self.ChessTypeJudge(TmpResult,[x-1,y+1],Order,[x+1,y-1],[x+2,y-2],[x+3,y-3],[x+4,y-4]):
            Cost=Cost+TmpCost  
        #++特殊棋型++# {'B5':100000,'L4':10000,'S4':250,'L3':100,'JL3':90,'L2':10,'LowL2':9,'S3':5,'S2':2,'DS4':10000,'S4L3':10000,'DL3':5000,'S3L3':1000,'DL2':30}
 

        #--双死4--#
        if SleepFourTimes >= 2:
            Cost=Cost+ChessCostList['DS4']
            if DebugMode==True:
                print 'DoubleSleep4',Order,[x,y]
        #--死4活3--#
        if (SleepFourTimes > 0) and (LiveThreeTimes > 0):
            if self._DifForward(S4Forward,L3Forward):
                Cost=Cost+ChessCostList['S4L3']
            if (self._ListInclude(S4Forward,SlopeList) or self._ListInclude(L3Forward,SlopeList)) and (SlopeStreng==True):
                Cost=Cost+ChessCostList['Slope']                
                if DebugMode==True:
                    print 'Sleep4Live3',Order,[x,y],[S4Forward,L3Forward]
        elif (SleepFourTimes > 0) and (JumpLiveThreeTimes > 0):
            if self._DifForward(S4Forward,JL3Forward):
                Cost=Cost+ChessCostList['S4L3']
            if (self._ListInclude(S4Forward,SlopeList) or self._ListInclude(JL3Forward,SlopeList)) and (SlopeStreng==True):
                Cost=Cost+ChessCostList['Slope']                               
                if DebugMode==True:
                    print 'Sleep4LiveJ3',Order,[x,y],[S4Forward,JL3Forward]
        #--双活3--#
        if LiveThreeTimes >= 2:
            if self._ExcludeForward(L3Forward):
                Cost=Cost+ChessCostList['DL3']
            if self._ListIncludeTwo(L3Forward,SlopeList) and (SlopeStreng==True):
                Cost=Cost+ChessCostList['Slope']                                         
                if (SleepFourTimes > 0) and (self._DifForward(S4Forward,L3Forward)):
                    Cost=Cost+ChessCostList['DL3']
                if DebugMode==True:    
                    print 'DoubleLive3',Order,[x,y],[L3Forward]                    
        elif JumpLiveThreeTimes >= 2:
            if self._ExcludeForward(JL3Forward):
                Cost=Cost+ChessCostList['DL3']
            if self._ListIncludeTwo(JL3Forward,SlopeList) and (SlopeStreng==True):
                Cost=Cost+ChessCostList['Slope']                
                if (SleepFourTimes > 0) and (self._DifForward(S4Forward,JL3Forward)):
                    Cost=Cost+ChessCostList['DL3']           
                if DebugMode==True:
                    print 'DoubleLiveJJ3',Order,[x,y],[JL3Forward]
        elif JumpLiveThreeTimes + LiveThreeTimes >= 2:
            if self._DifForward(L3Forward,JL3Forward):
                Cost=Cost+ChessCostList['DL3']
            if (self._ListInclude(JL3Forward,SlopeList) or self._ListInclude(L3Forward,SlopeList)) and (SlopeStreng==True):
                Cost=Cost+ChessCostList['Slope']                                                            
                if (SleepFourTimes > 0) and (self._DifForward(S4Forward,JL3Forward)):
                    Cost=Cost+ChessCostList['DL3']
                if DebugMode==True:                    
                    print 'DoubleLiveJ3',Order,[x,y],[L3Forward,JL3Forward]
        #--死3活3--#
        if (SleepThreeTimes > 0) and (LiveThreeTimes > 0):
            if self._DifForward(S3Forward,L3Forward):
                Cost=Cost+ChessCostList['S3L3']
            if (self._ListInclude(L3Forward,SlopeList) or self._ListInclude(S3Forward,SlopeList)) and (SlopeStreng==True):
                Cost=Cost+ChessCostList['Slope']                  
                if DebugMode==True:
                    print 'Sleep3Live3',Order,[x,y],[S3Forward,L3Forward]   
        elif (SleepThreeTimes > 0) and (JumpLiveThreeTimes > 0):
            if self._DifForward(S3Forward,JL3Forward):
                Cost=Cost+ChessCostList['S3L3']
            if (self._ListInclude(JL3Forward,SlopeList) or self._ListInclude(S3Forward,SlopeList)) and (SlopeStreng==True):
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
                
        if (MyMaxScore>10000 and HisMaxScore<100000) or (MyMaxScore >= HisMaxScore):
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
                print 'HumanMaxScore:',HisMaxScore
                print 'HumanMaxPoint:',HisMaxPoint
                print 'HumanSamePoint',HisSamePoint
                raise CalError
            else:
                if DebugMode==True:
                    print HisMaxPoint,MyMaxPoint
                return HisMaxPoint

        


            
    def Gamma_Cal(self): #Gamma级别战术,暂无
        x=random.randint(0,14) 
        y=random.randint(0,14)
        while ChessPoint[x][y]!=0:
            x=random.randint(0,14) 
            y=random.randint(0,14)            
        return [x,y]
    def Omega_Cal(self): #Omega级别战术,暂无
        return [1,1]
    def AIChessPut(self,LineX,LineY):
        global CheckFrameColor
        ChessBoard.delete('MouseCheck')
        MouseCheckFrame(LineX,LineY)
        self._ChessPoint[LineX][LineY]=-1
        self._ChessOrder[0]=1
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

#创建root窗口对象
root=Tk()
root.wm_title('Gobang')
root.resizable(False,False)
root.geometry('800x800+200+20')
#创建画布
ChessBoard=Canvas(root,bg='#EEE8AA',width=800,height=800,highlightthickness=0)
ChessBoard.pack()
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
    global ChessPoint,MemChessPoint,ManClick,Chess_Num
    if ChessPoint != MemChessPoint:
        for x in range(0,15):
            for y in range(0,15):
                MemChessPoint[x][y]=ChessPoint[x][y]
        ChessBoard.delete('Chess')
        for x in range(0,15):
            for y in  range(0,15):
                if ChessPoint[x][y]==1:
                    ChessBoard.create_oval(CB_Point[x][y][0]-ChessSize,CB_Point[x][y][1]-ChessSize,CB_Point[x][y][0]+ChessSize,CB_Point[x][y][1]+ChessSize,fill='black',outline='black',tag='Chess')
                if ChessPoint[x][y]==-1:
                    ChessBoard.create_oval(CB_Point[x][y][0]-ChessSize,CB_Point[x][y][1]-ChessSize,CB_Point[x][y][0]+ChessSize,CB_Point[x][y][1]+ChessSize,fill='white',outline='white',tag='Chess')
        checkwin=GobangRule.BaseRule()
        if checkwin==0:
            if ChessOrder[0]==1 and ManClick==True:
                ManClick=False
                ChessOrder[0]=-1
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
    global MousePos,MouseReInto,ChessOrder,NowMousePos
    if ChessOrder[0]==1:
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
    if ChessOrder[0]==1:
        ChessBoard.delete('MouseCheck')
def ChessPut(event):
    global ChessOrder,NowMousePos,CheckFrameColor,ChessBoard,ManClick
    if NowMousePos==[None,None]:
        return
    if ChessOrder[0]==1:
        if ChessPoint[NowMousePos[0]][NowMousePos[1]]==0:
            ChessPoint[NowMousePos[0]][NowMousePos[1]]=ChessOrder[0]
            #ChessOrder[0]=-1
            ManClick=True
            CheckFrameColor='white'
            #for item in ChessBoard.find_withtag('MouseCheck'):
            #    ChessBoard.itemconfig(item,fill = 'white')            
def ChessReset(event):
    global ChessPoint,MemChessPoint,ChessBoard,ChessOrder,CheckFrameColor,Chess_Num
    for x in range(0,15):
        for y in range(0,15):
            ChessPoint[x][y]=0
    for x in range(0,15):
        for y in range(0,15):
            MemChessPoint[x][y]=0
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
GBAI=GobangAI(root,ChessOrder,ChessPoint,ChessBoard,'Beta')
root.after(10,ChessGenerator)
root.mainloop()
