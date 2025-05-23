import os
import sys
import pandas as pd
import baostock as bs
from xtquant import xtdata
import qlib
from qlib import data

# 从baostock下载股票数据并存储为csv格式
def download_data_from_baostock(
        start_date, 
        end_date,
        fields = "date,open,close,high,low,volume,turn,pctChg,peTTM",
        frequency = "d",
        adjustflag = "3",
        st = False):
    """
    Input:
        1.start_date：开始日期（包含），格式“YYYY-MM-DD”，为空时取2015-01-01。
        2.end_date：结束日期（包含），格式“YYYY-MM-DD”，为空时取最近一个交易日。
        3.frequency：数据类型，默认为d，日k线；
                    d=日k线、w=周、m=月、5=5分钟、15=15分钟、30=30分钟、60=60分钟k线数据，不区分大小写；
                    指数没有分钟线数据；周线每周最后一个交易日才可以获取，月线每月最后一个交易日才可以获取。
        4.adjustflag：复权类型，1=后复权，2=前复权，3=默认不复权；
                    已支持分钟线、日线、周线、月线前后复权。
        5.st：是否去除st股票，True=保留，False=去除。
    Output:
        1.save_dir：数据存储路径。
    """
    # 根据起始时间创建存储目录
    script_dir = os.path.abspath("..") # 获取当前脚本上一级目录绝对路径
    save_dir = script_dir+"/stock_data/qlib_cn_data_from_baostock/"+start_date+"~"+end_date
    try:
        os.mkdir(save_dir)
        print(f"目录创建成功")
    except FileExistsError:
        print(f"目录已存在")
        return save_dir
    except PermissionError:
        print("权限不足，无法创建目录")
        return save_dir
    try:
        os.mkdir(save_dir+"/csv")
        print(f"目录创建成功")
    except FileExistsError:
        print(f"目录已存在")
        return save_dir
    except PermissionError:
        print("权限不足，无法创建目录")
        return save_dir
    # 登录baostock
    bs.login()
    # 获取起始日期所有股票代码  
    stock_rs = bs.query_all_stock(start_date)
    stock_df = stock_rs.get_data() 
    # 获取结束日期所有股票代码(注:当日最新数据在17:30后更新)
    stock_today_rs = bs.query_all_stock(end_date)
    stock_today_df = stock_today_rs.get_data()
    # 丢弃综合指数代码
    stock_df.drop(stock_df[stock_df["code"] < "sh.600000"].index, inplace = True)
    stock_df.drop(stock_df[stock_df["code"] > "sz.399000"].index, inplace = True)
    stock_today_df.drop(stock_today_df[stock_today_df["code"] < "sh.600000"].index, inplace = True)
    stock_today_df.drop(stock_today_df[stock_today_df["code"] > "sz.399000"].index, inplace = True)
    # 丢弃ST股票
    if st == False:
        stock_df.drop(stock_df[stock_df["code_name"].str.contains("ST")].index, inplace = True)
        stock_today_df.drop(stock_today_df[stock_today_df["code_name"].str.contains("ST")].index, inplace = True)
    # 下载个股数据并存储为csv文件
    for code in stock_df["code"]:
        if code in stock_today_df["code"].values:
            print("Downloading :" + code)
            k_rs = bs.query_history_k_data_plus(code = code, 
                                                fields = fields, 
                                                start_date = start_date, 
                                                end_date = end_date, 
                                                frequency = frequency, 
                                                adjustflag = adjustflag)
            k_df = k_rs.get_data() # type: ignore
            k_df.to_csv(path_or_buf = save_dir+"/csv/"+code.replace("sh.", "SH").replace("sz.", "SZ")+".csv", 
                        encoding = "UTF-8", 
                        index = False)
    # 存储最终所有有效股票代码为csv文件
    stock_df.to_csv(path_or_buf = save_dir+"/"+"stock_list.csv", 
                    encoding = "UTF-8", 
                    index = False,
                    header = True)
    # 退出baostock
    bs.logout()
    return save_dir

# 从baostock下载股票数据并存储为csv格式
def download_data_from_xtquant(
        start_date, 
        end_date,
        fields = "date,open,close,high,low,volume,turn,pctChg,peTTM",
        frequency = "1d",
        adjustflag = "3",
        st = False):
    """
    Input:
        1.start_date：开始日期（包含），格式“YYYY-MM-DD”，为空时取2015-01-01。
        2.end_date：结束日期（包含），格式“YYYY-MM-DD”，为空时取最近一个交易日。
        3.frequency：数据类型，默认为d，日k线；
                    d=日k线、w=周、m=月、5=5分钟、15=15分钟、30=30分钟、60=60分钟k线数据，不区分大小写；
                    指数没有分钟线数据；周线每周最后一个交易日才可以获取，月线每月最后一个交易日才可以获取。
        4.adjustflag：复权类型，1=后复权，2=前复权，3=默认不复权；
                    已支持分钟线、日线、周线、月线前后复权。
        5.st：是否去除st股票，True=保留，False=去除。
    Output:
        1.save_dir：数据存储路径。
    """
    xtdata.download_history_data(stock_code = "000001.SZ",
                                 period = frequency,
                                 start_time = start_date,
                                 end_time = end_date)

# 使用qlib的dump_bin模块将csv文件转换为bin文件
def transform_csv_into_bin(
        date = "2025-02-20~2025-04-02",
        fields = "date,open,close,high,low,volume,turn,pctChg,peTTM"):
    """
    注意：调用完此函数后，需删除缓存文件夹"date,open,close,high,low,volume,turn,pctChg,peTTM"后，才能进行下一次调用
    """
    script_dir = os.path.abspath("..") # 获取当前脚本上一级目录绝对路径
    csv_dir = script_dir+"/stock_data/qlib_cn_data_from_baostock/"+date+"/csv"
    bin_dir = script_dir+"/stock_data/qlib_cn_data_from_baostock/"+date
    sys.path.append(script_dir+"/qlib/scripts") # 添加上一级目录到系统路径
    from dump_bin import DumpDataAll
    dump_util = DumpDataAll(csv_dir, bin_dir, fields)
    dump_util.dump()
    print("转换完成")
    
def generate_dataset(date):
    # 从qlib读取数据
    qlib.init(provider_uri="E:/PythonProject/test/stock_data/qlib_cn_data_from_baostock/"+date)
    stock_list = data.D.instruments(market = "all")
    data_qlib = data.D.features(instruments = stock_list,
                                fields = ['$high','$low','$open','$close','$pctChg','$volume','$turn'], 
                                freq = "day")
    data_pd = pd.DataFrame(data_qlib)
    print(data_pd)

if __name__ == '__main__':
    # download_data_from_baostock(start_date="2025-04-07", end_date="2025-05-19", adjustflag = "1")
    # transform_csv_into_bin("2023-08-30~2024-05-20")
    # generate_dataset("2024-04-10~2025-04-10")
    # download_data_from_xtquant("20250515","20250519")
    print("You can do it!")