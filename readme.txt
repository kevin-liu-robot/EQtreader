###########量化交易系统安装流程###########

注意：远程服务器部署需要关闭自动屏保功能 
      远程断开连接时需要专业代码控以保持桌面系统运行
      如果长时间不查看远程服务器请主动使用代码断开连接

建议python 安装32位的 或者安装conda虚拟环境，
如果使用64位python，请使用改进版本的easyquotation和easytrader

		https://blog.csdn.net/linxinfa/article/details/108914011
		在anaconda下安装虚拟32位python，打开ananconda prompt，命令set CONDA_FORCE_32BIT=1, 32位环境
		conda create -n env_name python=3.7
		conda activate env_name

安装同花顺交易软件




pip install easyquotation
pip install easytrader
pip install easyquant 可选
pip install chinesecalendar

pip install pywin32
pip install pyperclip
使用剪切板来填充字符

pip install pytesseract
需安装tesseract并设置环境变量
下载https://digi.bib.uni-mannheim.de/tesseract/
教程：https://blog.csdn.net/weixin_45129876/article/details/107860986?spm=1001.2101.3001.6650.2&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7Edefault-2-107860986-blog-75443785.pc_relevant_aa2&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7Edefault-2-107860986-blog-75443785.pc_relevant_aa2&utm_relevant_index=5

###########安装结束###########


###########测试代码###########
import easytrader

000426
7.58
800

user = easytrader.use('universal_client') 
user.connect(r'D:\同花顺软件\同花顺\xiadan.exe')

user.balance

user.position



import easyquotation

quotation = easyquotation.use('sina') # 新浪 ['sina'] 腾讯 ['tencent', 'qq'] 


quotation.market_snapshot(prefix=False)

quotation.real('000568')

quotation.stocks(['000001', '162411'])


quotation.stock_codes = quotation.load_stock_codes()
quotation.stock_list = quotation.gen_stock_list(quotation.stock_codes)

quotation.get_stock_data(quotation.stock_list, prefix=True)

quotation.real(quotation.stock_codes,prefix=True)

quotation.get_sina_lhb1()

quotation.requests.get("https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=80&sort=changepercent&asc=0&node=hs_a&symbol=&_s_r_a=init")

https://vip.stock.finance.sina.com.cn/mkt/#stock_sh_up

https://vip.stock.finance.sina.com.cn/mkt/#stock_hs_up


http://www.shdjt.com/sort.asp?sort=desc&hs=ON&sortname=zf

http://www.shdjt.com/sort.asp?sort=desc&page=2&sortname=zf&hs=ON&kz=0

http://finance.sina.com.cn/basejs/MarketTS.js

https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=80&sort=changepercent&asc=0&node=hs_a&symbol=&_s_r_a=init

https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=2&num=80&sort=changepercent&asc=0&node=hs_a&symbol=&_s_r_a=page

https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=3&num=80&sort=changepercent&asc=0&node=hs_a&symbol=&_s_r_a=page


https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=160&sort=changepercent&asc=0&node=hs_a&symbol=&_s_r_a=init




TuShare是一个著名的免费、开源的python财经数据接口包，主要实现对股票等金融数据从数据采集、清洗加工到数据存储的过程，能够为金融分析人员提供快速、整洁、和多样的便于分析的数据，为他们在数据获取方面极大地减轻工作量，使他们更加专注于策略和模型的研究与实现上。考虑到Python pandas包在金融量化分析中体现出的优势，Tushare返回的绝大部分的数据格式都是pandas DataFrame类型，非常便于用pandas/NumPy/Matplotlib进行数据分析和可视化。
https://tushare.pro/
pip install tushare


歪枣网 能够获取沪深股票、港股、大盘指数、基金净值、基金排行等财经数据,歪枣网平台上提供免费的财经数据下载接口。
http://waizaowang.com/

token = 22a3690f745844e5c51d8a80a62793b1

http://api.waizaowang.com/doc/getMinuteKLine?type=1&code=000001,000002&startDate=2022-08-24&endDate=2022-08-25&fields=code,tdate,open&export=0&token=22a3690f745844e5c51d8a80a62793b1

http://waizaowang.com/api/detail/106