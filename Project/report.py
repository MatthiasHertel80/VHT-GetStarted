import logging
import re
import sys
from pathlib import Path
from io import StringIO
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

class UnityReport:
    class Result:
        def __init__(self, name, file, line, status):
            self.name = name
            self.file = file
            self.line = line
            self.status = status
            logging.debug(f"Created Result: {self.name}, {self.file}, {self.line}, {self.status}")

    def __init__(self, stream):
        self._stream = stream
        self.results = []
        logging.debug("Initialized UnityReport")

    def parse(self):
        for line in self._stream:
            m = re.match('(.*):(\d+):(\w+):(PASS|FAIL)(:(.*))?', line)
            if m:
                file = Path(m.group(1))
                result = self.Result(m.group(3), file, m.group(2), m.group(4))
                self.results.append(result)
                logging.debug(f"Parsed line: {line.strip()}, Result: {result.name}, {result.file}, {result.line}, {result.status}")

    def to_xunit(self):
        testsuites = Element('testsuites', {'time': '0'})
        testsuite = SubElement(testsuites, 'testsuite', {'time': '0'})
        for result in self.results:
            testcase = SubElement(testsuite, 'testcase', {
                'name': result.name,
                'file': str(result.file),
                'line': result.line,
                'time': '0',
            })
            if result.status == 'FAIL':
                failure = SubElement(testcase, 'failure')
            logging.debug(f"Converted Result to xunit: {result.name}, {result.file}, {result.line}, {result.status}")
        return minidom.parseString(tostring(testsuites)).toprettyxml(indent="   ")

def main():
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 2:
        print("Please provide a report file as a command line argument.")
        return
    report_file = sys.argv[1]
    with open(report_file, 'r') as f:
        report = UnityReport(f)
        report.parse()
        xunit = report.to_xunit()
        xunit_file = Path(report_file).with_suffix('.xml')
        with open(xunit_file, 'w') as f:
            f.write(xunit)
        print(f"junit XML report written to {xunit_file}")

if __name__ == '__main__':
    main()