# coding:utf8
import easyquotation
import easytrader
import time
import datetime
from chinese_calendar import is_workday
import math

testmode = 0
Estop_mode = 0
sell_stop = 0
buy_stop = 0

trade_amount_min = 5000
trade_amount_max = 7000
changepercent_th = 9.7
changepercent_alarm = -0.035
changepercent_sell = 0.09
#volume = volume_min/volume_ft
#       = volume_min/(math.ceil(price_now/volume_price/volume_time))
volume_min = 500000#需根据股票价格和交易时间浮动，越大越谨慎
volume_max = 1000000#需根据股票价格和交易时间浮动，越大越谨慎
volume_price = 20  #需根据股票价格和交易时间浮动，越大越谨慎
volume_time = 1  #需根据股票价格和交易时间浮动，越大越谨慎
volume_ft = math.ceil(30/volume_price/volume_time)

repeat_times = 20
max_page = 3
time_interval = 1 #交易时间连续获取间隔需大于1s
timeprepare = datetime.datetime.strptime('09:10:00.000000','%H:%M:%S.%f')
time0915 = datetime.datetime.strptime('09:15:00.000000','%H:%M:%S.%f')
time0920 = datetime.datetime.strptime('09:20:00.000000','%H:%M:%S.%f')
time0925 = datetime.datetime.strptime('09:25:00.000000','%H:%M:%S.%f')
timestart = datetime.datetime.strptime('09:30:00.000000','%H:%M:%S.%f')
time0940 = datetime.datetime.strptime('09:39:30.000000','%H:%M:%S.%f')
timeearly = datetime.datetime.strptime('09:49:30.000000','%H:%M:%S.%f')
timesellall = datetime.datetime.strptime('09:59:30.000000','%H:%M:%S.%f')
timepause = datetime.datetime.strptime('11:30:00.000000','%H:%M:%S.%f')
timecont = datetime.datetime.strptime('13:00:00.000000','%H:%M:%S.%f')
timetail = datetime.datetime.strptime('14:19:00.000000','%H:%M:%S.%f')
timeend = datetime.datetime.strptime('15:00:00.000000','%H:%M:%S.%f')

datetimenow = datetime.datetime.now()

def log_msg(path,msg):    
    #print(msg)
    with open(path,"a+") as logfile:
        logfile.write('\r\n')
        logfile.write(msg)

buy_log_path = './log/' + datetimenow.strftime("%Y-%m-%d") + '_buy_log.txt'
sell_log_path = './log/' + datetimenow.strftime("%Y-%m-%d") + '_sell_log.txt'
total_value_path = './log/' + datetimenow.strftime("%Y-%m-%d") + '_total_value.txt'

log_msg(buy_log_path,'\r\n######restart EQtreader buy_log!!######')
log_msg(buy_log_path,str(datetimenow))

log_msg(sell_log_path,'\r\n######restart EQtreader sell_log!!######')
log_msg(sell_log_path,str(datetimenow))

log_msg(total_value_path,'\r\n######restart EQtreader total_value!!######')
log_msg(total_value_path,str(datetimenow))

print(datetimenow)
print('连接实时行情...')
#连接实时行情
quotation = easyquotation.use('sina') # 新浪 ['sina'] 腾讯 ['tencent', 'qq']

print('连接交易系统...')
#连接交易系统
trader = easytrader.use('universal_client') 
#trader.connect(r'D:\同花顺软件\同花顺\xiadan.exe')
trader.prepare(user='301719727041', password='123456', exe_path=r'C:\同花顺软件\同花顺\xiadan.exe')

#量化交易获取当前持仓股票代码和数量
realtime_data_last = []
stock_exclude_code = []
stock_buying_code = []
stock_selling_code = []
stock_position_code = []
stock_position_list = []
today_buying_list = []
money_balance = []
money_balance = trader.balance
cash_available = money_balance['可用金额']
print(cash_available)

repeat_cnt = 1
lhb_page = 1
timeflag = 0

def process_get_position():
    global stock_position_list
    global stock_position_code
    global today_buying_list
    global stock_selling_code
    global stock_exclude_code
    
    stock_position_list = trader.position
    stock_position_code.clear()
    for stock_position_s in stock_position_list:
        #if(stock_position_s['持仓数量'] > 0):
        stock_position_code.append(stock_position_s['证券代码'])
    print(stock_position_list)

    stock_exclude_code.clear()
    stock_buying_code.clear()
    #统计已委托正在购买的股票
    stock_selling_code.clear()
    today_buying_list = trader.today_entrusts
    for today_buying_s in today_buying_list:
        if(today_buying_s['备注'] == '未成交' and today_buying_s['操作'] == '证券买入'):
            stock_buying_code.append(today_buying_s['证券代码'])
            if not(today_buying_s['证券代码'] in stock_position_code):
                stock_position_code.append(today_buying_s['证券代码'])
        if(today_buying_s['备注'] == '未成交' and today_buying_s['操作'] == '证券卖出'):
            stock_selling_code.append(today_buying_s['证券代码'])
    print('买入待成交股票：',stock_buying_code)
    print('卖出待成交股票：',stock_selling_code)

    #today_trades = trader.today_trades
    #print(today_trades)



#量化交易
def process_main():

    global datetimenow
    global lhb_page
    global timeflag
    global repeat_cnt
    global stock_exclude_code
    global stock_buying_code
    global cash_available
    global money_balance
    global stock_position_code
    global stock_position_list
    global volume_min
    global volume_max
    global volume_ft
    global volume_time
    global changepercent_alarm
    global buy_log_path
    global sell_log_path
    global total_value_path
    global realtime_data_last
    
    repeat_cnt = repeat_cnt + 1
    if repeat_cnt > repeat_times :
        repeat_cnt = 0

    datetimenow=datetime.datetime.now()
    datenow = datetime.datetime.strptime(datetimenow.strftime("%Y-%m-%d"),'%Y-%m-%d')
    timenow = datetime.datetime.strptime(datetimenow.strftime("%H:%M:%S.%f"),'%H:%M:%S.%f')    
    buy_log_path = './log/' + datetimenow.strftime("%Y-%m-%d") + '_buy_log.txt'
    sell_log_path = './log/' + datetimenow.strftime("%Y-%m-%d") + '_sell_log.txt'
    total_value_path = './log/' + datetimenow.strftime("%Y-%m-%d") + '_total_value.txt'
    
    if testmode == 0 :
        if not is_workday(datenow):
            time.sleep(time_interval*5)
            print('节假日休市中...')
            return
        if timenow < timeprepare:
            time.sleep(time_interval*5)      
            print('早盘开市等待中...')
            return
        if timenow > timeprepare and timenow < time0915 :
            time.sleep(time_interval*2)
            if(repeat_cnt == 0):
                process_get_position()        
            print('早盘开市准备...',repeat_cnt)
            lhb_page = 1
            buy_log_path = './log/' + datetimenow.strftime("%Y-%m-%d") + '_buy_log.txt'
            sell_log_path = './log/' + datetimenow.strftime("%Y-%m-%d") + '_sell_log.txt'
            total_value_path = './log/' + datetimenow.strftime("%Y-%m-%d") + '_total_value.txt'
            return
        if timenow > time0925 and timenow < timestart:
            time.sleep(time_interval)
            print('集合竞价结束等待开盘...')
            return
        if timenow > timepause and timenow < timecont:
            time.sleep(time_interval)
            print('午间休息...')
            return
        if timenow > timeend :
            time.sleep(time_interval*5)
            print('当日行情已结束...')
            return
    else:
        print('调试模式......',repeat_cnt)
        
    if(timenow > time0915 and timenow <= time0925):
        timeflag = 0
        volume_time = 1
        volume_min = 1200000
        volume_max = 3500000
        changepercent_alarm = -0.03
        changepercent_sell = 0.09
    elif (timenow > timestart and timenow <= time0940):
        timeflag = 1
        volume_time = 1
        volume_min = 800000
        volume_max = 3000000
        changepercent_alarm = -0.03
        changepercent_sell = 0.09
    elif (timenow > time0940 and timenow <= timeearly):
        timeflag = 1
        volume_time = 1
        volume_min = 800000
        volume_max = 2500000
        changepercent_alarm = -0.02
        changepercent_sell = 0.08
    elif (timenow > timeearly and timenow <= timetail):
        timeflag = 2
        volume_time = 2
        volume_min = 500000
        volume_max = 1000000
        changepercent_alarm = -0.02
        changepercent_sell = 0.05
    elif (timenow > timetail and timenow <= timeend):
        timeflag = 3
        volume_time = 3
        volume_min = 500000
        volume_max = 1000000
        changepercent_alarm = -0.015
        changepercent_sell = 0.02
    else:
        timeflag = 4
        volume_time = 3
        volume_min = 500000
        volume_max = 1000000
        changepercent_alarm = -0.015
        changepercent_sell = 0.02
        
    if(repeat_cnt == 0):
        money_balance = trader.balance
        cash_available = money_balance['可用金额']
        msg = str(datetimenow) + '@' + str(money_balance['总资产'])
        log_msg(total_value_path,msg)             
    
    try:
        if lhb_page == 1:
            time.sleep(time_interval)
            stock_lhb = quotation.get_sina_lhb1()
        if lhb_page == 2:
            time.sleep(time_interval)
            stock_lhb = quotation.get_sina_lhb2()
        if lhb_page == 3:
            time.sleep(time_interval)
            stock_lhb = quotation.get_sina_lhb3()
    except Exception as msg:  # 
        print('######获取lhb数据异常######',msg)
        return
    
            
    stock_lhb_zb = []
    #筛选股票 深证 000000~100000  上证 600000~680000
    #剔除创业科创新三版北交所等 300000~400000  680000~700000 800000~900000
    for stock_lhb_s in stock_lhb:
        if int(stock_lhb_s['code'], 10) < 100000 :            
            stock_lhb_zb.append(stock_lhb_s)
        if int(stock_lhb_s['code'], 10) < 680000 and int(stock_lhb_s['code'], 10) >= 600000:            
            stock_lhb_zb.append(stock_lhb_s)
            
    #筛选股票 剔除新股、ST股、退市股
    for stock_lhb_s in stock_lhb_zb:
        if 'N' in stock_lhb_s['name']:
            stock_lhb_zb.remove(stock_lhb_s)
        if 'ST' in stock_lhb_s['name']:
            stock_lhb_zb.remove(stock_lhb_s)
        if '退' in stock_lhb_s['name']:
            stock_lhb_zb.remove(stock_lhb_s)
            
    stock_rising_list = []
    stock_buy_list = []
    stock_buy_code = []
    #初步筛选策略：筛选实时涨幅 剔除已购买或已持仓股票        
    for stock_lhb_s in stock_lhb_zb:
        if stock_lhb_s['changepercent'] > changepercent_th:
            stock_rising_list.append(stock_lhb_s)
            if not(stock_lhb_s['code'] in stock_position_code) and not(stock_lhb_s['code'] in stock_exclude_code):
                stock_buy_list.append(stock_lhb_s)
                stock_buy_code.append(stock_lhb_s['code'])
    #
    #龙虎榜数据更新策略
    if(stock_lhb[len(stock_lhb)-1]['changepercent'] > 9.9):
        if(lhb_page < 3):
            lhb_page = lhb_page + 1
        else:
            lhb_page = 1    
    
    
    realtime_data = [] 
    realtime_data_confirm  = []   
    #买入清单+现有持仓清单获取实时行情
    realtime_code = stock_buy_code
    for stock_position_s in stock_position_code:
        realtime_code.append(stock_position_s)
    if(len(realtime_code)  > 0):
        time.sleep(time_interval/2)       
        try:
            realtime_data = quotation.stocks(realtime_code)
        except Exception as msg:  #
            print('######获取数据异常######',msg)
            return
        
    #print(realtime_data)
    if not is_workday(datenow):
        time.sleep(time_interval*5)
        print('节假日休市中...')
        return        
    
       
    print('')
    print('')
    print(repeat_cnt,'############实时量化交易############')    
    print('######获取实时交易数据######')
    print(datetimenow)
    print('######获取数据lhb_page =',lhb_page)
    
    #量化交易卖出 
    print('#######监控持仓股票准备卖出策略#######')
    print('    当日持仓股票清单：',stock_position_code)
    for stock_position_s in stock_position_list:
        name = stock_position_s['证券名称']
        code = stock_position_s['证券代码']
        amount_all = stock_position_s['持仓数量']
        amount_sell = stock_position_s['可用数量']        
        price_now = realtime_data[code]['now']
        price_bid1 = realtime_data[code]['bid1']
        price_close = realtime_data[code]['close']
        changepercent = (price_now - price_close)/price_close
        price_raise_stop = math.ceil((realtime_data[code]['close']*1.1-0.004)*100)/100
        bid1_volume = realtime_data[code]['bid1_volume']
        volume_ft = math.ceil(price_now/volume_price/volume_time)
        print('   ',name,code,',持仓:',amount_all,',',amount_sell,',现价:',price_now,',涨幅:',round(changepercent,4),',bid1:',bid1_volume)
        if(amount_sell == 0  or price_now == 0):
            continue
        if(sell_stop==1):
            break
        #卖出策略1
        #尾盘清仓
        '''if timeflag < 3 : 
            if changepercent < changepercent_alarm :
                print('    盘中：跌幅过大清仓',name,code,',价格：',price_bid1,',数量：',amount_sell)
                trader.sell(code, price=price_now, amount=amount_sell)
                stock_position_list.remove(stock_position_s)
                stock_position_code.remove(code)
        elif timeflag == 3:#尾盘未涨停仓位全部清仓
            if not (price_now == price_raise_stop and bid1_volume > volume_min/volume_ft):                
                print('    尾盘：清仓未涨停',name,code,',价格：',price_now,',数量：',amount_sell)
                trader.sell(code, price=price_now, amount=amount_sell)
                stock_position_list.remove(stock_position_s)
                stock_position_code.remove(code)
                '''
        #卖出策略2
        #早盘结束清仓
        if Estop_mode==1:
            trader.sell(security=code, price=price_now, amount=amount_sell)
            #trader.market_sell(security=code,amount=amount_sell)
            msg = '\r\n' + str(datetimenow)
            msg += '\r\n    紧急事件清仓:' + str(name) + str(code) +',价格：'+ str(price_now)+',数量：'+str(amount_sell)
            msg += '\r\n    bid1_volume:' + str(bid1_volume) + ',changepercent:' + str(changepercent)
            log_msg(sell_log_path,msg)
            stock_position_list.remove(stock_position_s)
            stock_position_code.remove(code)
            stock_exclude_code.append(code)
        elif timenow > time0920 and timenow < time0925 and changepercent > changepercent_sell :
            trader.sell(security=code, price=price_now, amount=amount_sell)
            #trader.market_sell(security=code,amount=amount_sell)
            msg = '\r\n' + str(datetimenow)
            msg += '\r\n    集合竞价止盈清仓:' + str(name) + str(code) +',价格：'+ str(price_now)+',数量：'+str(amount_sell)
            msg += '\r\n    bid1_volume:' + str(bid1_volume) + ',changepercent:' + str(changepercent)
            log_msg(sell_log_path,msg)
            stock_position_list.remove(stock_position_s)
            stock_position_code.remove(code)
            stock_exclude_code.append(code)
        elif timeflag > 0 and changepercent > changepercent_sell:
            trader.sell(security=code, price=price_now, amount=amount_sell)
            #trader.market_sell(security=code,amount=amount_sell)
            msg = '\r\n' + str(datetimenow)
            msg += '\r\n    盘中止盈清仓:' + str(name) + str(code) +',价格：'+ str(price_now)+',数量：'+str(amount_sell)
            msg += '\r\n    bid1_volume:' + str(bid1_volume) + ',changepercent:' + str(changepercent)
            log_msg(sell_log_path,msg)
            stock_position_list.remove(stock_position_s)
            stock_position_code.remove(code)
            stock_exclude_code.append(code)
        elif timeflag > 0 and changepercent < changepercent_alarm and changepercent > (changepercent_alarm-0.02):
            trader.sell(security=code, price=price_now, amount=amount_sell)
            #trader.market_sell(security=code,amount=amount_sell)
            msg = '\r\n' + str(datetimenow)
            msg += '\r\n    盘中止损清仓:' + str(name) + str(code) +',价格：'+ str(price_now)+',数量：'+str(amount_sell)
            msg += '\r\n    bid1_volume:' + str(bid1_volume) + ',changepercent:' + str(changepercent)
            log_msg(sell_log_path,msg)
            stock_position_list.remove(stock_position_s)
            stock_position_code.remove(code)
            stock_exclude_code.append(code)
        else:         
            if timenow > timesellall:#全部清仓
                #if not (price_now == price_raise_stop and bid1_volume > volume_min):                
                    #trader.market_sell(security=code,amount=amount_sell)
                    trader.sell(code, price=price_now, amount=amount_sell)
                    msg = '\r\n' + str(datetimenow)
                    msg += '\r\n    定时全部清仓:' + str(name) + str(code) +',价格：'+ str(price_now)+',数量：'+str(amount_sell)
                    msg += '\r\n    bid1_volume:' + str(bid1_volume) + ',changepercent:' + str(changepercent)
                    log_msg(sell_log_path,msg)                    
                    stock_position_list.remove(stock_position_s)
                    stock_position_code.remove(code)
                    stock_exclude_code.append(code)
                
        #卖出策略3
        '''#集合竞价清仓 
        if timeflag == 0 and timenow > time0920 :
            price_now = stock_position_s['当前价']
            #print('    集合竞价：开盘清仓...')
            #print('    集合竞价：清仓未涨停',name,code,',价格：',price_now,',数量：',amount_sell)
            trader.sell(code, price=price_now, amount=amount_sell)
            msg = '\r\n' + str(datetimenow)
            msg += '\r\n    集合竞价：开盘清仓:' + str(name) + str(code) +',价格：'+ str(price_now)+',数量：'+str(amount_sell)
            msg += '\r\n    bid1_volume:' + str(bid1_volume) + ',changepercent:' + str(changepercent)
            log_msg(sell_log_path,msg)
            stock_position_list.remove(stock_position_s)
            stock_position_code.remove(code)
        '''    
    
    print('######准备执行买入策略，可用现金：',cash_available)
    print('    涨幅预警清单：',stock_buy_code)        
    print('    当日已购买股票清单：',stock_buying_code)    
    print('    当日已购买或者已排除清单：',stock_exclude_code)
    
    
            
    #买入筛选策略 交易并买入
    confirm_cnt = 0;    
    for stock_lhb_s in stock_buy_list:
        price_raise_stop = math.ceil((realtime_data[stock_lhb_s['code']]['close']*1.1-0.004)*100)/100
        bid1_volume = realtime_data[stock_lhb_s['code']]['bid1_volume']
        price = realtime_data[stock_lhb_s['code']]['bid1']
        volume_ft = math.ceil(price/volume_price/volume_time)
        
        #print(volume_ft,volume_max/volume_ft,volume_min/volume_ft)
        #买入策略1和2时需跳过集合竞价时段
        if(Estop_mode == 1):
            print('紧急事件暂停买入...')
            break
        if(buy_stop==1):
            print('暂停买入...')
            break
        if(timeflag == 0):
            print('跳过集合竞价时段...')
            break
        if cash_available < trade_amount_min:            
            print('可用金额不足，跳过买入策略，余额：',cash_available)
            break
        #买入策略1 盘中实时打板 配合卖出策略1尾盘清仓 交易周期2天 保守
        #                     或配合卖出策略2早盘结束清仓 交易周期1天  常规
        
        if (price == price_raise_stop and bid1_volume < volume_max/volume_ft and bid1_volume > volume_min/volume_ft) :#筛选
        #买入策略2 早盘抢入打板  配合卖出策略3 集合竞价清仓 交易周期1天 激进
        #if (策略待研究) :#筛选

        #买入策略3 集合竞价打板  配合卖出策略3 集合竞价清仓 交易周期2天 激进
        #if (策略待研究) :#筛选
        
            #print(price,bid1_volume,price_raise_stop)
            price = price_raise_stop            
            #计算买入仓位            
            amount_100 = trade_amount_min/price/100
            amount = math.ceil(amount_100)*100
            if(amount*price >= trade_amount_max):
                amount = math.floor(amount_100)*100
            total_price = amount*price
            if(amount > 0):
                #确认涨停趋势
                try:
                    time.sleep(time_interval/2)
                    confirm_cnt = confirm_cnt + 1
                    realtime_data_confirm = quotation.real(stock_lhb_s['code'])
                except Exception as msg:  #
                    print('######获取数据异常######',msg)
                bid1_volume_confirm = realtime_data_confirm[stock_lhb_s['code']]['bid1_volume']
                #print(stock_lhb_s['code'],',',bid1_volume,',',bid1_volume_confirm,',',volume_max/volume_ft,',',volume_min/volume_ft)
                msg = '\r\n' + str(datetimenow) + 'confirm_cnt:' + str(confirm_cnt)
                msg += '\r\n    买入预警确认趋势：' + str(stock_lhb_s['name'])+ str(stock_lhb_s['code']) + '价格：' + str(price) + '数量：'+ str(amount)
                msg += '\r\n    bid1_volume:' + str(bid1_volume) + ',bid1_volume_confirm:' + str(bid1_volume_confirm) + ',volume_min:'+ str(volume_min/volume_ft)
                log_msg(buy_log_path,msg)
                #print('    ######确认涨停趋势：',stock_lhb_s['name'],stock_lhb_s['code'],',',price,',',bid1_volume_confirm)
                if ((bid1_volume_confirm) > (bid1_volume *1.06)):                    
                    #print('    ######准备买入股票：',stock_lhb_s['name'],stock_lhb_s['code'])
                    if total_price < cash_available:        
                        #trader.market_buy(security=stock_lhb_s['code'], amount=amount)
                        trader.buy(stock_lhb_s['code'], price=price, amount=amount)                
                        msg = '\r\n' + str(datetimenow)
                        msg += '\r\n    买入股票：' + str(stock_lhb_s['name'])+ str(stock_lhb_s['code']) + '价格：' + str(price) + '数量：'+ str(amount)
                        msg += '\r\n    bid1_volume:' + str(bid1_volume) + ',bid1_volume_confirm:' + str(bid1_volume_confirm)
                        log_msg(buy_log_path,msg)
                        cash_available = cash_available - total_price
                        print('    买入成功，剩余现金：',cash_available)
                        if not(stock_lhb_s['code'] in stock_position_code):
                            stock_position_code.append(stock_lhb_s['code'])
                        if not(stock_lhb_s['code'] in stock_buying_code):
                            stock_buying_code.append(stock_lhb_s['code'])
                    else:
                        print('    可用金额偏低，忽略此股...')
                        continue
            else:                
                #价格过高的放入排除列表
                if not(stock_lhb_s['code'] in stock_exclude_code):
                    stock_exclude_code.append(stock_lhb_s['code'])
    realtime_data_last.clear()                
    realtime_data_last = realtime_data

def main():    
    try:
        process_get_position()
    except Exception as msg:  #
        print('######get_position运行异常######',msg)
    while True:
        try:
            process_main()
        except Exception as msg:  #
            print('######main运行异常######',msg)
            continue
        
    

if __name__ == '__main__':
    main()
