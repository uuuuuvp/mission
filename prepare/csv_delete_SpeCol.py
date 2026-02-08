import os
import pandas as pd
from extract_acline import attain_parse_args

def del_spe_col(csv_file_path, col_name, new_csv_file_path):
    df = pd.read_csv(csv_file_path, encoding='GB18030')
    df_cleaned = df.drop(columns=col_name)
    df_cleaned.to_csv(new_csv_file_path, index=False, encoding='GB18030')

def batch_del_spe_col(input_dir, col_name, output_dir):
    if not os.path.exists(output_dir):
        print("输出文件夹不存在，正在创建...")
        os.makedirs(output_dir)
    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            input_csv_path = os.path.join(input_dir, filename)
            output_csv_path = os.path.join(output_dir, filename)
            del_spe_col(input_csv_path, col_name, output_csv_path)

if __name__ == "__main__":
    columns_to_delete = ['volt','Eq','R','X','B','I_node','J_node','I_off','J_off','Ih','Pi_meas','Qi_meas','Pj_meas','Qj_meas','I_nd','J_nd','I_bs','J_bs','I_island','J_island','R*','X*','B*','region_id']
    columns_to_delete_flag = ['volt','Eq','R','X','B','I_node','J_node','Ih','Pi_meas','Qi_meas','Pj_meas','Qj_meas','I_nd','J_nd','I_bs','J_bs','I_island','J_island','R*','X*','B*','region_id']
    flag = attain_parse_args()      # 默认 1 : 单个测试
    if not flag:
        input_csv = "E:\\data\\国调_20230921_2000.csv"
        output_csv = "E:\\data\\ACline_CSV_Cleaned.csv"
        del_spe_col(input_csv, columns_to_delete, output_csv)
    else:
        input_directory = "E:\\data\\ACline_CSV"
        output_directory = "E:\\data\\ACline_CSV_Cleaned_flag"
        batch_del_spe_col(input_directory, columns_to_delete_flag, output_directory)