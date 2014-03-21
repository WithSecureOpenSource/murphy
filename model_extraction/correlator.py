'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details
'''
import datetime, logging
from model_extraction import csv_unicode

LOGGER = logging.getLogger('root.' + __name__)

def _procmon_time_to_timestamp(time_as_string):
    '''
    Convenient converter from process monitor time string to python time
    '''
    hour, mins, secs = time_as_string.split(":")
    secs, millis = secs.split(",")
    millis = millis[:6]
    return datetime.time(int(hour), int(mins), int(secs), int(millis))

def _should_correlate(edge, operation):
    '''
    Returns True if the given operation for the given edge should be considered
    False otherwise
    '''
    if not edge is None:
        return (operation == "WriteFile" or
                operation.startswith("TCP") or
                operation == "RegSetValue")
    else:
        return False

def _should_ignore_by_path(path):
    '''
    Returns True if the given path should be ignored when correlating
    '''
    if path.startswith("C:\\Users\\testuser\\AppData\\Local\\"):
        return True
    else:
        return False

_IGNORABLE_PROCESSES = ["mobsync.exe", "wmpnetwk.exe", "spoolsv.exe",
                        "smss.exe", "lsm.exe", "wmpnscfg.exe",
                        "python.exe", "cmd.exe", "wermgr.exe",
                        "conhost.exe", "tvnserver.exe", "Explorer.EXE",
                        "Procmon.exe", "Procmon64.exe", "svchost.exe",
                        "DllHost.exe", "System", "taskhost.exe",
                        "services.exe", "lsass.exe", "wmiprvse.exe"]

def _should_ignore_process(process):
    '''
    Returns True if the given process should be ignored when correlating
    '''
    return process in _IGNORABLE_PROCESSES

class Correlator(object):
    '''
    Simple correlation between a scraper timeline and log entries by it's
    time, this correlator is specific to ProcessMonitor csv output.
    TODO: keep track of correlated logs so it can support multiple runs
    '''
    def __init__(self, world, timeline):
        self.timeline = timeline
        self._world = world

    def _dump_timeline(self):
        '''
        Simple debug output print of the timeline
        '''
        print "Timeline is:"
        for i in range(len(self.timeline)):
            if self.timeline[i] == "reboot":
                print "reboot"
            else:
                print "\t%s: %s" % (self.timeline[i]['from'].name,
                                    self.timeline[i]['departure'])

    def _add_trace_to_edge(self, edge, trace_index):
        '''
        Adds a trace, meaning the series of steps used with that index in
        the timeline to pair with the log info
        '''
        steps = []

        if self.timeline[trace_index - 1] == 'reboot':
            trace_index -= 1

        for i in range(trace_index - 1, -1, -1):
            if self.timeline[i] == 'reboot':
                break
            timeline_edge = self.timeline[i]['from']
            steps.insert(0, "%s.%s" % (timeline_edge.tail.name,
                                       timeline_edge.name))

        if not 'traces' in edge.logs['instrumentation']:
            edge.logs['instrumentation']['traces'] = {}
        edge.logs['instrumentation']['traces'][trace_index] = steps

    def _add_logged_event_to_edge(self, edge, operation, trace_index, row):
        '''
        Adds the given row of data to the given edge as instrumentation captured
        data
        '''
        if self.timeline[trace_index - 1] == 'reboot':
            trace_index -= 1

        if not 'instrumentation' in edge.logs:
            edge.logs['instrumentation'] = {}
        if not operation in edge.logs['instrumentation']:
            edge.logs['instrumentation'][operation] = {}
        if not trace_index in edge.logs['instrumentation'][operation]:
            edge.logs['instrumentation'][operation][trace_index] = []
            self._add_trace_to_edge(edge, trace_index)
        edge.logs['instrumentation'][operation][trace_index].append(row)

    def _correlate_log(self, csv_reader, edge, until, timeline_index):
        '''
        Adds events from the given log to the corresponding edge, times are
        matched from the crawler timeline against the edge it was executed.
        In this context edge represents what it was executed and until the
        timestamp of the next edge execution
        '''
        last_message = ""
        #headers
        if csv_reader.next() is None:
            return (None, None)

        while True:
            try:
                row = csv_reader.next()
            except StopIteration:
                break
            time, process, _, operation, path, _, _ = row
            if _should_ignore_process(process):
                pass
            elif _should_ignore_by_path(path):
                pass
            else:
                timestamp = _procmon_time_to_timestamp(time)
                if timestamp <= until:
                    if _should_correlate(edge, operation):
                        message = "%s %s %s" % (process, operation, path)
                        self._add_logged_event_to_edge(edge,
                                                       operation,
                                                       timeline_index,
                                                       row)
                        if message != last_message:
                            LOGGER.debug("\t%s: %s", time, message)
                        last_message = message
                else:
                    last_message = ""
                    while True:
                        timeline_index += 1
                        if timeline_index == len(self.timeline):
                            return (None, None)
                        this_time = self.timeline[timeline_index]
                        if this_time == "reboot":
                            pass
                        elif this_time['departure'].time() > timestamp:
                            until = this_time['departure'].time()
                            if (timeline_index > 2 and
                              self.timeline[timeline_index - 1] == "reboot"):
                                edge = self.timeline[timeline_index - 2]['from']
                                LOGGER.debug("%s.%s", edge.tail.name, edge.name)
                                LOGGER.debug("Reset")
                            else:
                                edge = self.timeline[timeline_index - 1]['from']
                                LOGGER.debug("%s.%s", edge.tail.name, edge.name)
                            break
                        else:
                            if self.timeline[timeline_index - 1] != "reboot":
                                edge = self.timeline[timeline_index - 1]['from']
                                LOGGER.debug("%s.%s", edge.tail.name, edge.name)
        return (edge, timeline_index)

    def correlate_events(self):
        '''
        Matches log events to edge executions
        '''
        self._dump_timeline()

        timeline_index = 0
        until = self.timeline[0]['departure'].time()
        edge = None
        LOGGER.info("Will try to correlate events from log with the timeline")

        for log in self._world.event_logs:
            with open(log, 'r') as log_file:
                csv_reader = csv_unicode.UnicodeReader(log_file,
                                                       encoding="utf-8-sig")
                (edge, timeline_index) = self._correlate_log(csv_reader,
                                                             edge,
                                                             until,
                                                             timeline_index)
