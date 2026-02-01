import os,csv,argparse

def attain_parse_args():
    parse = argparse.ArgumentParser(description="flag for test of a file or a total processing")
    parse.add_argument('--flag', type=int, default = 1, help="0:test;1:total processing")
    args = parse.parse_args()
    return args.flag

def write_into_csv(line_content, csv_file_path):
    items = line_content.split()
    del items[0]
    with open(csv_file_path, 'a', newline='', encoding='GB18030') as csv_file:
        csv.writer(csv_file).writerow(items)

def extract_acline_data(qs_file_path, csv_file_path):
    if not os.path.exists(qs_file_path):
        raise FileNotFoundError
    in_acline = False
    with open(qs_file_path, 'r', encoding='GB18030') as file:
        for line in file:
            line = line.strip()
            if in_acline and (line.startswith('#') or line.startswith('@') or line.startswith('/')):
                write_into_csv(line, csv_file_path)
            
            if line.startswith('<ACline::'):
                in_acline = True
                continue
            
            if line.startswith('</ACline::'):
                in_acline = False
                break

def iterate_extrct_acline_data(qs_dir_path, csv_dir_path):
    if not os.path.exists(csv_dir_path):
        os.makedirs(csv_dir_path)
    for filename in os.listdir(qs_dir_path):
        qs_file_path = os.path.join(qs_dir_path, filename)
        csv_file_path = os.path.join(csv_dir_path, filename.replace('.QS', '.csv'))
        extract_acline_data(qs_file_path, csv_file_path)

if __name__ == "__main__":
    flag = attain_parse_args()
    if not flag:
        qs_file_path = "E:\\data\\QS文件\\国调_20230921_2000.QS"
        csv_file_path = 'E:\\data\\国调_20230921_2000.csv'
        extract_acline_data(qs_file_path, csv_file_path)
    else:
        qs_dir_path = "E:\\data\\QS文件"
        csv_dir_path = "E:\\data\\ACline_CSV"
        iterate_extrct_acline_data(qs_dir_path, csv_dir_path)