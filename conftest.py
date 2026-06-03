import os
from datetime import datetime


def pytest_addoption(parser):
    parser.addoption(
        '--no-html',
        action='store_true',
        default=False,
        help='Skip HTML report generation'
    )


def pytest_configure(config):
    if getattr(config.option, 'no_html', False):
        return
    os.makedirs('reports', exist_ok=True)
    if not getattr(config.option, 'htmlpath', None):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        config.option.htmlpath = f'reports/report_{timestamp}.html'
        config.option.self_contained_html = True


def pytest_html_report_title(report):
    report.title = 'Framework_SV — Test Report'
