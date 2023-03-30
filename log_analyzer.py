import os
import re
import logging
import gzip
import json
from argparse import ArgumentParser
from datetime import datetime
from collections import namedtuple, defaultdict
from statistics import median
from string import Template


config = {
	"REPORT_SIZE": 1000,
	"REPORT_DIR": "./reports/1/2",
	"LOG_DIR": "./log"
}


def get_log_file(conf: dict) -> [namedtuple, None]:
	""" Function for finding last logfile """

	LogFileInfo = namedtuple('LogFileInfo', ['path', 'datetime', 'extension'])
	oldest_log_file_name = ""
	try:
		# For all files in directory:
		for filename in os.listdir(conf.get('LOG_DIR')):
			# Check name and format:
			if filename.startswith('nginx-access-ui.log-') and (filename.endswith('.gz') or filename.endswith('.txt')):
				# len('nginx-access-ui.log-') = 20, datetime length = 8, take oldest one:
				oldest_log_file_name = oldest_log_file_name if oldest_log_file_name > filename[20:28] else filename
	except FileNotFoundError:
		logging.info(f'Not found log directory path: "{conf.get("LOG_DIR")}".')
	except BaseException:
		logging.exception('When try to open file...')
		raise

	if not oldest_log_file_name:
		logging.info(f'Log file does not exist. Log directory path: "{conf.get("LOG_DIR")}".')
		return

	return LogFileInfo(
		f'{conf.get("LOG_DIR")}/{oldest_log_file_name}',
		datetime.strptime(oldest_log_file_name[20:28], "%Y%m%d"),
		oldest_log_file_name[28:]
	)


def get_report_path(log_info: namedtuple, conf: dict):

	report_path = f'{conf["REPORT_DIR"]}/report-{datetime.strftime(log_info.datetime, "%Y.%m.%d")}.html'
	# If file exist, return True:
	if os.path.isfile(report_path):
		logging.info(f'Report file exist. Report file path: "{report_path}".')
		return

	return report_path


def read_log(file_info: namedtuple):
	""" Function for read log """

	# Open log file:
	log = gzip.open(file_info.path, 'rt', encoding='utf-8') if file_info.extension == ".gz" else open(file_info.path, encoding='utf-8')
	for record in log:
		yield record  # yield one line
	log.close()


def analyze_log(log_info: namedtuple, conf: dict) -> [list, None]:
	""" Function for analyze log and evaluate metrics """

	logging.info(f'Find new log file for parse! Log file path: "{log_info.path}".')

	# regular for "$request" and $request_time
	request_and__time = re.compile(r'] "\w+ ([\/\w?=&-.%:]+) [\w\/.]+"|(\d+.\d+$)')

	table = defaultdict(list)
	count_erros = 0
	count_total = 0
	request_time_total = 0
	for record in read_log(log_info):
		count_total += 1
		parsed = request_and__time.findall(record)
		# Create url and request time variable to check correct parsing:
		if len(parsed) == 2:
			url, request_time = parsed[0][0], float(parsed[1][1])
			table[url].append(request_time)
			request_time_total += request_time
		else:
			count_erros += 1

	if count_erros / count_total > conf.get('ERROR_THRESHOLD', 0.5):
		logging.error(f'Percent of parse failures more than: {conf.get("ERROR_THRESHOLD", 0.5) * 100}%!')
		return

	json_table = []
	for url in table:
		result = {}
		request_times = table[url]
		result['count'] = len(request_times)
		result['count_perc'] = round(100 * result['count'] / count_total, 3)
		result['time_sum'] = round(sum(request_times), 3)
		result['time_perc'] = round(100 * result['time_sum'] / request_time_total, 3)
		result['time_avg'] = round(result['time_sum'] / result['count'], 3)
		result['time_max'] = max(request_times)
		result['time_med'] = round(median(request_times), 3)
		result['url'] = url
		json_table.append(result)

	json_table = sorted(json_table, key=lambda d: d['time_sum'], reverse=True)  # sort by time_sum value
	return json_table if conf['REPORT_SIZE'] > len(json_table) else json_table[:conf['REPORT_SIZE']]


def create_report(table_json: list, report_path: str, conf):
	""" Function for create report with template report.html """

	logging.info(f'Log file analyzing complete.')
	# Get report template from report.html:
	with open('report.html', encoding='utf-8') as filename:
		report = Template(filename.read()).safe_substitute(table_json=table_json)

	# Create file path if needed:
	try:
		os.makedirs(conf["REPORT_DIR"])
		logging.info(f'Create report directory path: "{conf["REPORT_DIR"]}".')
	except FileExistsError:
		pass

	# Create report file:
	with open(report_path, 'w', encoding='utf-8') as filename:
		filename.write(report)

	logging.info(f'New report ready! Report file path: "{report_path}".')

	return report


def init_work(conf: dict) -> dict:

	logging.basicConfig(
		level=logging.INFO,
		format='[%(asctime)s] %(levelname).1s %(message)s',
		datefmt='%Y.%m.%d%H:%M:%S'
	)

	logging.info(f'Start work.')

	parser = ArgumentParser(
		prog='LogAnalyzer',
		description='This is log analyzer for UI'
	)
	parser.add_argument('-c', '--config', default='config.json')
	args = parser.parse_args()
	with open(args.config, 'r') as file_config:
		conf.update(json.load(file_config))  # update config

	logging.basicConfig(filename=conf.get('SCRIPT_LOG_PATH'))  # now we exactly know SCRIPT_LOG_PATH
	logging.info('Successful read config file.')
	return conf


def main(conf: dict):

	try:
		conf = init_work(conf)
	except FileNotFoundError:
		logging.exception('Config file not found!')
		raise
	except json.decoder.JSONDecodeError:
		logging.exception('Config file contains mistakes!')
		raise
	except KeyboardInterrupt:
		logging.exception('Keyboard interrupt!')
		raise
	except BaseException:
		logging.exception('Unexpected exception!')
		raise

	try:
		file_info = get_log_file(conf)
		if file_info:
			report_path = get_report_path(file_info, conf)
			if report_path:
				table_json = analyze_log(file_info, conf)  # table json for template
				create_report(table_json, report_path, conf)
	except KeyboardInterrupt:
		logging.exception('Keyboard interrupt!')
		raise
	except BaseException:
		logging.exception('Unexpected exception!')
		raise

	logging.info('End work.')


if __name__ == "__main__":
	main(config)
