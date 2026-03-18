import os
import sys
import pandas as pd
import qlib
from qlib import data

# 使用qlib的dump_bin模块将csv文件转换为bin文件
def transform_csv_into_bin(
        date = "2025-02-20~2025-04-02",
        fields = "date,open,close,high,low,volume,turn,pctChg,peTTM"):
    """
    注意：调用完此函数后，需删除缓存文件夹"date,open,close,high,low,volume,turn,pctChg,peTTM"后，才能进行下一次调用
    """
    script_dir = os.path.abspath("..") # 获取当前脚本上一级目录绝对路径
    sys.path.insert(0, script_dir+"/qlib/scripts")
    from dump_bin import DumpDataAll
    print(script_dir)
    csv_dir = script_dir+"/stock_data/qilb_cn_data_from_baostock/"+date+"/csv"
    bin_dir = script_dir+"/stock_data/qilb_cn_data_from_baostock/"+date
    dump_util = DumpDataAll(csv_dir, bin_dir, fields)
    dump_util.dump()
    print("转换完成")
    
def generate_dataset(date):
    # 从qlib读取数据
    qlib.init(provider_uri="E:/PythonProject/test/stock_data/qilb_cn_data_from_baostock/"+date)
    stock_list = data.D.instruments(market = "all")
    data_qlib = data.D.features(instruments = stock_list,
                                fields = ['$high','$low','$open','$close','$pctChg','$volume','$turn'], 
                                freq = "day")
    data_pd = pd.DataFrame(data_qlib)
    print(data_pd)

if __name__ == '__main__':
    # download_data_from_baostock(start_date="2025-04-07", end_date="2025-05-19", adjustflag = "1")
    # transform_csv_into_bin("2023-09-01~2023-10-23")
    # generate_dataset("2024-04-10~2025-04-10")
    download_data_from_xtquant("20250515","20250519")
    print("You can do it!")
