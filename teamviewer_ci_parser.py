import csv
import argparse
import os
import sys
import logging
import peewee
import jinja2
import hashlib

__author__ = 'Tom Newman'
__version__ = "Version 1.2"
__description__ = 'Python script that uses SQLite to store parsed data from TeamViewer incoming_connections logs and can write results to CSV or HTML'
logger = logging.getLogger(__name__)
database_proxy = peewee.Proxy()


class BaseModel(peewee.Model):
    class Meta:
        database = database_proxy


class Case(BaseModel):
    case_ref = peewee.TextField(unique=True)


class TeamViewerLogs(BaseModel):
    id = peewee.PrimaryKeyField(unique=True, primary_key=True)
    teamviewer_id = peewee.IntegerField()
    teamviewer_name = peewee.TextField()
    connection_start = peewee.DateTimeField()
    connection_end = peewee.DateTimeField()
    local_user = peewee.TextField()
    connection_type = peewee.TextField()
    unique_id = peewee.TextField()
    case_ref = peewee.ForeignKeyField(Case.case_ref)


def get_template():
    """
      The getTemplate function returns a basic template for our HTML report
      :return: Jinja2 Template
    """

    html_string = """
      <html>\n<head>\n
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css"></head>\n
      <body>\n<h1>TeamViewer incoming_connections log for case ref: {{ case }}</h1>\n

      <table class="table table-hover table-striped">\n

      <tr>\n
      {% for header in table_headers %}
          <th>{{ header }}</th>
      {% endfor %}
      </tr>\n

      {% for entry in file_listing %}
          <tr>
              <td>{{ entry.id }}</td>
              <td>{{ entry.case_ref }}</td>
              <td>{{ entry.teamviewer_id }}</td></td>
              <td>{{ entry.teamviewer_name }}</td>
              <td>{{ entry.connection_start }}</td>
              <td>{{ entry.connection_end }}</td>
              <td>{{ entry.local_user }}</td>
              <td>{{ entry.connection_type }}</td>
              <td>{{ entry.unique_id }}</td>
              


          </tr>\n
      {% endfor %}

      </table>\n
      </body>\n
      </html\n\n
      """
    return jinja2.Template(html_string)


def main(case, target, db):
    '''
    Function that creates the database, handles errors and logs
    param case: Case reference
    param target: tuple containing the mode input or output as the first element and file path as the second
    param db: filepath for the database
    return: None
    '''
    # Step 1: uses init_db functions to initialise the SQLite Datacase
    logger.info('Initiating SQLite Database: ' + db)
    init_db(db)
    logger.info('Initialisation successful...')

    # Step 2: uses get_or_add_custodian function to retrieve or add a new custodian
    logger.info('Retrieving or adding case: ' + case)
    #oic = input('OIC Name?')
    #hash = get_hash_value(target[1])
    get_or_add_case(case)

    # Step 3: Is the specified source input or output?
    if target[0] == 'input':
        logger.info(
            'Parsing TeamViewer incoming_connections log file: {}'.format(target[1]))
        get_teamviewer_connections(target[1], case)
        logger.info('Parsing complete')
    elif target[0] == 'output':
        logger.info('Preparing to write output: {}'.format(target[1]))
        write_output(target[1], case)
    else:
        logger.error('Could not interpret run time arguments')

    logger.info('Script complete.')


def init_db(db):
    """
    Opens and creates and database
    :param db: The file path for the database
    :return: conn, the sqlite db connection
    """

    database = peewee.SqliteDatabase(db)
    database_proxy.initialize(database)
    table_list = [Case, TeamViewerLogs]  # Update with any new tables
    database.create_tables(table_list, safe=True)


def get_or_add_case(case):
    """
    Gets a custodian by name and adds it to the table
    :param custodian: The name of the custodian
    :return: custodian_model, custodian peewee model instance
    """
    case_model, created = Case.get_or_create(case_ref=case)
    if created:
        logger.info('Case added')
    else:
        logger.info('Case retrieved')

    return case_model


def get_teamviewer_connections(logfile, case):
    '''
    Function to take the user supplied input file and parse the data into a list ready to be extracted to csv
    :param file: takes the file provided by the user that has been validated through main
    :return: a list with tuples contained relevant log file data
    '''

    teamviewer_list = []

    with open(logfile, 'r') as log_file:
        # log_file = log_file.readlines()[1:]
        log_file = filter(None, (line.rstrip() for line in log_file))

        for lines in log_file:

            tv_data = dict()

            split = lines.split('\t')

            try:
                tv_data['teamviewer_id'] = split[0]
                tv_data['teamviewer_name'] = split[1]
                tv_data['connection_start'] = split[2]
                tv_data['connection_end'] = split[3]
                tv_data['local_user'] = split[4]
                tv_data['connection_type'] = split[5]
                tv_data['unique_id'] = split[6]
                tv_data['case_ref'] = case
            except Exception:
                logger.error('Could not parse data from: ' + logfile)
            teamviewer_list.append(tv_data)

        for x in range(0, len(teamviewer_list), 50):
            task = TeamViewerLogs.insert_many(teamviewer_list[x:x+50])
            task.execute()
        logger.info('Stored log data for {} files.'.format(
            len(teamviewer_list)))


def get_hash_value(source):
    BUF_SIZE = 65536  # reads the data in 64kb chunks

    md5 = hashlib.md5()

    with open(source, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()


def write_output(source, case):
    """
    Handles writing the data to either CSV or HTML file format
    :param source: The output file
    :param custodian_model: PeeWee model instance for the custodian
    :return: None
    """
    count = TeamViewerLogs.select().where(
        TeamViewerLogs.case_ref == case).count()
    logger.info('{} files found for custodian'.format(count))

    if not count:
        logger.error(' Files not found for custodian')
    elif source.endswith('.csv'):
        write_to_csv(source, case)
    elif source.endswith('.html'):
        write_to_html(source, case)
    elif not (source.endswith('.csv') or source.endswith('.html')):
        logger.error('Could not determine file type')
    else:
        logger.error('Unknow Error Occured')


def write_tv_id_to_csv(source, id):
    file_data = [entry for entry in TeamViewerLogs.select().where(
        TeamViewerLogs.teamviewer_id == id).dicts()]

    with open(source, 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, ['id', 'case_ref', 'teamviewer_id', 'teamviewer_name',
                                               'connection_start', 'connection_end', 'local_user', 'connection_type', 'unique_id'])
        csv_writer.writeheader()
        csv_writer.writerows(file_data)

    logging.info('CSV Report completed: ' + source)


def write_to_csv(source, case_model):
    """
    Generates CSV report from the Files table
    :param source: The output file loccation
    :param case_model: Peewee model instance for custodian
    :return: None
    """
    file_data = [entry for entry in TeamViewerLogs.select().where(
        TeamViewerLogs.case_ref == case_model).dicts()]
    logger.info('Writing CSV Report')

    with open(source, 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, ['id', 'case_ref', 'teamviewer_id', 'teamviewer_name',
                                               'connection_start', 'connection_end', 'local_user', 'connection_type', 'unique_id'])
        csv_writer.writeheader()
        csv_writer.writerows(file_data)

    logging.info('CSV Report completed: ' + source)


def write_to_html(source, case_model):
    """
    The writeHTML function generates an HTML report from the Files table
    :param source: The output filepath
    :param custodian_model: Peewee model instance for the custodian
    :return: None
    """
    template = get_template()
    table_headers = ['Id', 'Case Reference', 'Teamviewer ID',
                     'Teamviewer Name', 'Connection Start', 'Connection End', 'Local User', 'Connection Typer', 'Unique ID']

    file_data = TeamViewerLogs.select().where(
        TeamViewerLogs.case_ref == case_model).dicts()

    case_info = Case.select()

    template_dict = {'case': case_model,
                     'table_headers': table_headers,
                     'file_listing': file_data,
                     'case_info': case_info}

    logger.info('Writing HTML report')

    with open(source, 'w') as html_file:
        html_file.write(template.render(**template_dict))

    logger.info('HTML report completed: ' + source)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog='Built by {}. Version {}'.format(__author__, __version__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'CASE', help='Name of custodian collection is of.')
    parser.add_argument('--input', help='Path to incoming_connections.txt')
    parser.add_argument(
        '--output', help='Output file to write to. Compatible with .csv or .html')
    parser.add_argument('-l', help='File path and name of log file')
    args = parser.parse_args()

    if args.input:
        arg_source = ('input', args.input)
    elif args.output:
        arg_source = ('output', args.output)
    else:
        raise argparse.ArgumentError('Please specify input or output')

    if args.l:
        if not os.path.exists(args.l):
            os.os.os.makedirs(args.l)
        log_path = os.path.join(args.l, 'teamviewer_ci_parser.log')
    else:
        log_path = 'file_lister.log'

    logger.setLevel(logging.DEBUG)
    msg_fmt = logging.Formatter(
        "%(asctime)-15s %(funcName)-20s" "%(levelname)-8s %(message)s")

    strhnd1 = logging.StreamHandler(sys.stdout)
    strhnd1.setFormatter(fmt=msg_fmt)

    fhnd1 = logging.FileHandler(log_path, mode='a')
    fhnd1.setFormatter(fmt=msg_fmt)

    logger.addHandler(strhnd1)
    logger.addHandler(fhnd1)

    logger.info('Starting File Lister ' + str(__version__))
    logger.debug('System ' + sys.platform)
    logger.debug('System ' + sys.version)
    logger.info('Preparing SQLite Database path...')
    db_path = 'master_teamviewer_log.sqlite'

    args_dict = {'case': args.CASE,
                 'target': arg_source,
                 'db': db_path}

    main(**args_dict)
