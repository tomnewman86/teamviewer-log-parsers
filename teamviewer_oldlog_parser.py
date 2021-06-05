import csv
import argparse
import os
import time
import re


__author__ = 'Tom Newman'
__description__ = 'Python script to parse TeamViewer Logfile_OLD to a CSV file for further analysis'


def main(input):
    if os.path.isfile(input):
        print('='*22)
        print('TeamViewer OLD Logfile parser \n')
        print(__description__ + '\n')
        print(f"Built by {__author__}. Version 1.0")
        print('='*22)
        print('[*] Parsing log file...')
        results = data_parser(input)
        time.sleep(1)
        print('[*] Copying output to CSV')
        log_output = './logfile_OLD_output.csv'
        write_to_csv(log_output, results)
        time.sleep(1)
        print('[*] Extracting IP related related logs')
        results = ip_parser(input)
        time.sleep(1)
        ip_output = 'ip_results.csv'
        write_to_csv(ip_output, results)
        print('[*] Creating individual IP list to txt file')
        print('[+] Complete! Please check your output location...')
    else:
        print(
            '[-] Output file cannot have the same name as the master. Please choose a different input filename.')


def data_parser(input):

    log_list = []

    with open(input) as in_file:

        for lines in in_file:
            if lines[0].isdigit():
                remove_newline = lines.strip(' \n')
                stripped_lines = remove_newline.strip()
                split_lines = stripped_lines.split(' ')
                split_lines = list(filter(None, split_lines))
                split_lines[5:] = [''.join(split_lines[5:7])]
                log_list.append(split_lines)

        return log_list


def ip_parser(input):
    ip_logs = []
    ip_addr = []

    with open(input) as in_file:

        for lines in in_file:
            if lines[0].isdigit():
                ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', lines)

                if ip:
                    for i in ip:
                        ip_addr.append(i)
                        with open('ip_list.txt', 'w') as file:
                            for ip in ip_addr:
                                file.write(ip + '\n')

                    remove_newline = lines.strip(' \n')
                    stripped_lines = remove_newline.strip()
                    split_lines = stripped_lines.split(' ')
                    split_lines = list(filter(None, split_lines))
                    split_lines[5:] = [''.join(split_lines[5:])]
                    ip_logs.append(split_lines)

        return ip_logs


def write_to_csv(output, results):
    with open(output, 'w') as file:
        tsv_writer = csv.writer(file, delimiter='\t')
        for groupings in results:
            tsv_writer.writerow(groupings)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog='Built by {}. Version 1.0'.format(__author__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i', '--input_file', help='path to Teamviewer OLD log file', required=True, action="store")
    args = parser.parse_args()
    main(args.input_file)
