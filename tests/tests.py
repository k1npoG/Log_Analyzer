import unittest
from log_analyzer import *
from collections import namedtuple


class Testing(unittest.TestCase):

    def setUp(self) -> None:

        with open('config.json', 'r') as fileconfig:
            self.config = json.load(fileconfig)

    def test_get_log_file_correct(self):

        LogFileInfo = namedtuple('LogFileInfo', ['path', 'datetime', 'extension'])
        correct_get_log_file = LogFileInfo(
            './log/nginx-access-ui.log-20170630.txt',
            datetime(2017, 6, 30, 0, 0),
            '.txt'
        )
        self.assertEqual(correct_get_log_file, get_log_file(self.config))

    def test_get_log_file_wrong_path(self):
        bad_config = self.config.copy()
        bad_config.update({"LOG_DIR": "./bad_path"})
        self.assertEqual(None, get_log_file(bad_config))

    def test_read_log(self):
        LogFileInfo = namedtuple('LogFileInfo', ['path', 'datetime', 'extension'])
        correct_get_log_file = LogFileInfo(
            './log/nginx-access-ui.log-20170630.txt',
            datetime(2017, 6, 30, 0, 0),
            '.txt'
        )
        correct_read_log = ['1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390\n', '1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.133\n', '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/16852664 HTTP/1.1" 200 19415 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752769" "712e90144abee9" 0.199\n', '1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4705/groups HTTP/1.1" 200 2613 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752745" "2a828197ae235b0b3cb" 0.704\n', '1.168.65.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/internal/banner/24294027/info HTTP/1.1" 200 407 "-" "-" "-" "1498697422-2539198130-4709-9928846" "89f7f1be37d" 0.146\n', '1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/1769230/banners HTTP/1.1" 200 1020 "-" "Configovod" "-" "1498697422-2118016444-4708-9752747" "712e90144abee9" 0.628\n', '1.194.135.240 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/7786679/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28 HTTP/1.1" 200 22 "-" "python-requests/2.13.0" "-" "1498697422-3979856266-4708-9752772" "8a7741a54297568b" 0.067\n', '1.200.76.128 f032b48fb33e1e692  - [29/Jun/2017:03:50:24 +0300] "GET /api/1/campaigns/?id=7789717 HTTP/1.1" 200 608 "-" "-" "-" "1498697424-4102637017-4708-9752827" "-" 0.145']

        self.assertEqual(correct_read_log, [line for line in read_log(correct_get_log_file)])

    def test_get_report_path(self):
        LogFileInfo = namedtuple('LogFileInfo', ['path', 'datetime', 'extension'])
        correct_get_log_file = LogFileInfo(
            './log/nginx-access-ui.log-20170631.txt',
            datetime(2017, 6, 29, 0, 0),
            '.txt'
        )
        correct_report_path = './reports/report-2017.06.29.html'
        self.assertEqual(correct_report_path, get_report_path(correct_get_log_file, self.config))

    def test_analyze_log(self):
        LogFileInfo = namedtuple('LogFileInfo', ['path', 'datetime', 'extension'])
        correct_get_log_file = LogFileInfo(
            './log/nginx-access-ui.log-20170630.txt',
            datetime(2017, 6, 30, 0, 0),
            '.txt'
        )
        correct_analyze_result = [{'count': 1, 'count_perc': 12.5, 'time_sum': 0.704, 'time_perc': 29.187, 'time_avg': 0.704, 'time_max': 0.704, 'time_med': 0.704, 'url': '/api/v2/slot/4705/groups'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.628, 'time_perc': 26.036, 'time_avg': 0.628, 'time_max': 0.628, 'time_med': 0.628, 'url': '/api/v2/group/1769230/banners'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.39, 'time_perc': 16.169, 'time_avg': 0.39, 'time_max': 0.39, 'time_med': 0.39, 'url': '/api/v2/banner/25019354'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.199, 'time_perc': 8.25, 'time_avg': 0.199, 'time_max': 0.199, 'time_med': 0.199, 'url': '/api/v2/banner/16852664'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.146, 'time_perc': 6.053, 'time_avg': 0.146, 'time_max': 0.146, 'time_med': 0.146, 'url': '/api/v2/internal/banner/24294027/info'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.145, 'time_perc': 6.012, 'time_avg': 0.145, 'time_max': 0.145, 'time_med': 0.145, 'url': '/api/1/campaigns/?id=7789717'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.133, 'time_perc': 5.514, 'time_avg': 0.133, 'time_max': 0.133, 'time_med': 0.133, 'url': '/api/1/photogenic_banners/list/?server_name=WIN7RB4'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.067, 'time_perc': 2.778, 'time_avg': 0.067, 'time_max': 0.067, 'time_med': 0.067, 'url': '/api/v2/group/7786679/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28'}]

        self.assertEqual(correct_analyze_result, analyze_log(correct_get_log_file, self.config))

    def test_create_report(self):

        correct_report_path = './reports/report-2017.06.30.html'
        correct_analyze_result = [{'count': 1, 'count_perc': 12.5, 'time_sum': 0.704, 'time_perc': 29.187, 'time_avg': 0.704, 'time_max': 0.704, 'time_med': 0.704, 'url': '/api/v2/slot/4705/groups'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.628, 'time_perc': 26.036, 'time_avg': 0.628, 'time_max': 0.628, 'time_med': 0.628, 'url': '/api/v2/group/1769230/banners'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.39, 'time_perc': 16.169, 'time_avg': 0.39, 'time_max': 0.39, 'time_med': 0.39, 'url': '/api/v2/banner/25019354'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.199, 'time_perc': 8.25, 'time_avg': 0.199, 'time_max': 0.199, 'time_med': 0.199, 'url': '/api/v2/banner/16852664'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.146, 'time_perc': 6.053, 'time_avg': 0.146, 'time_max': 0.146, 'time_med': 0.146, 'url': '/api/v2/internal/banner/24294027/info'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.145, 'time_perc': 6.012, 'time_avg': 0.145, 'time_max': 0.145, 'time_med': 0.145, 'url': '/api/1/campaigns/?id=7789717'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.133, 'time_perc': 5.514, 'time_avg': 0.133, 'time_max': 0.133, 'time_med': 0.133, 'url': '/api/1/photogenic_banners/list/?server_name=WIN7RB4'}, {'count': 1, 'count_perc': 12.5, 'time_sum': 0.067, 'time_perc': 2.778, 'time_avg': 0.067, 'time_max': 0.067, 'time_med': 0.067, 'url': '/api/v2/group/7786679/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28'}]

        create_report(correct_analyze_result, correct_report_path, self.config)

        self.assertEqual(True, os.path.isfile(correct_report_path))


if __name__ == '__main__':
    unittest.main()
