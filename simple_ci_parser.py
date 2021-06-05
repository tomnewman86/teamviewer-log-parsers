import csv
import argparse
import os
import sys
import time

__author__ = 'Tom Newman'
__description__ = 'Short python script to parse TeamViewer Logs to a CSV file for further analysis'


def main(input_file, output_file):
    """
    Main function to perform validation on input file
    :param file: string to path of Connections_incoming.txt
    :return: None
    """
    if os.path.isfile(input_file):
        if not 'tv_master' in os.path.basename(output_file):
            print(input_file)
            print('='*22)
            print('TeamViewer log file parser \n')
            print(__description__ + '\n')
            print(f"Built by {__author__}. Version 1.0")
            print('='*22)
            print('[*] Parsing log file...')
            results_list = teamViewerData(input_file)
            time.sleep(1)
            print('[*] Copying output to CSV')
            printtofile(output_file, results_list)

            time.sleep(1)
            print('[+] Complete! Please check your output location...')
        else:
            print(
                '[-] Output file cannot have the same name as the master. Please choose a different input filename.')
    else:
        print(
            '[-] Input is not the expected file type. Please select a valid log file and try again.')
        sys.exit(1)


def teamViewerData(input_file):
    '''
    Function to take the user supplied input file and parse the data into a list ready to be extracted to csv
    :param file: takes the file provided by the user that has been validated through main
    :return: a list with tuples contained relevant log file data
    '''
    tv_list = []

    with open(input_file) as in_file:
        in_file = filter(None, (line.rstrip() for line in in_file))

        for lines in in_file:
            split_lines = lines.split('\t')
            #del split_lines[-1]
            tv_list.append(split_lines)

        return tv_list


def printtofile(output_file, results_list):
    with open(output_file, 'w') as file:
        tsv_writer = csv.writer(file, delimiter='\t')
        tsv_writer.writerow(["Teamviewer ID", "Teamviewer Name", "Connection start",
                             "Connection End", "Local User", "Connections Type", "Unique ID"])

        for groupings in results_list:
            tsv_writer.writerow(groupings)

        return output_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog='Built by {}. Version 1.0'.format(__author__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i', '--input_file', help='path to Teamviewer log file', required=True, action="store")
    parser.add_argument(
        '-o', '--output_file', help='path to outfile to record parsed data', required=True, action="store")
    args = parser.parse_args()

    main(args.input_file, args.output_file)
