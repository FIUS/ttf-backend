from flask import g, request
from time import time
from functools import wraps
from collections import namedtuple
from sqlalchemy.engine import Engine
from sqlalchemy import event
from logging import getLogger, INFO

from . import APP

from typing import Any, List


QueryRecord = namedtuple('QueryRecord', ['duration', 'statement', 'write'])


class RequestPerformance:

    req_start: float
    req_end: float
    view_start: float
    view_end: float
    duration: float
    query_start: float
    queries: List[QueryRecord]

    def __init__(self):
        t = time()
        self.req_start = t
        self.req_end = t
        self.query_start = t
        self.view_start = t
        self.view_end = t
        self.duration = 0
        self.queries = []

    def end_request(self):
        self.req_end = time()
        self.duration = self.req_end - self.req_start
        logger = getLogger("ttf.performance")
        if self.duration > APP.config.get('LONG_REQUEST_THRESHHOLD', 1):
            self.log_performance_record(logger.warning)
        elif logger.getEffectiveLevel() <= INFO :
            self.log_performance_record(logger.info)
            

    def start_query(self):
        self.query_start = time()

    def end_query(self, statement):
        query_end = time()
        write = not statement.upper().startswith('SELECT')
        self.queries.append(QueryRecord(query_end - self.query_start, statement, write))
        self.query_start = query_end

    def start_view_function(self):
        t = time()
        self.view_start = t
        self.view_end = t

    def end_view_function(self):
        if self.view_start == self.view_end:
            self.view_end = time()

    def __repr__(self):
        return '<RequestPerformance duration={}s, {} queries>'.format(self.duration, len(self.queries))

    def log_performance_record(self, methodToLogWith):
        url = request.url
        method = request.method
        time_in_view = ''
        if self.view_end is not None and self.view_end != self.view_start:
            duration_view = self.view_end - self.view_start
            duration_wo_view = self.duration - duration_view
            time_in_view = f'time spent in view {duration_view: 2.2f}s, duration without view {duration_wo_view: 2.2f}s, '
        if self.queries:
            q_number = len(self.queries)
            q_write_number = sum(1 if q.write else 0 for q in self.queries)
            tot_query_duration = sum(q.duration for q in self.queries)
            duration_wo_queries = self.duration - tot_query_duration
            self.queries.sort(key=lambda q: q.duration)
            longest_query_duration = self.queries[0].duration
            methodToLogWith(f'performance report: duration {self.duration: 2.2f}s, {time_in_view}duration without queries {duration_wo_queries: 2.2f}s, query-duration {tot_query_duration: 2.2f}s, {q_number: 2d} queries ({q_write_number: 2d} write), longest query {longest_query_duration: 2.2f}s, url {method:6} {url}')
            for q in self.queries:
                if q.duration > 1:
                    methodToLogWith(f'performance report: long query detected: duration {q.duration: 2.2f}s, statement "{q.statement}"')
        else:
            methodToLogWith(f'performance report: duration {self.duration: 2.2f}s, {time_in_view}url {method} {url}')


def before_request(*args, **kwargs):
    g.ttf_request_performance = RequestPerformance()


APP.before_request(before_request)


def aftter_request(request, *args, **kwargs):
    r_perf: RequestPerformance = g.get('ttf_request_performance')
    if r_perf is not None:
        r_perf.end_request()
    return request


APP.after_request(aftter_request)


@event.listens_for(Engine, 'before_cursor_execute')
def before_query(conn, cursor, statement, parameters, context, executemany):
    r_perf: RequestPerformance = g.get('ttf_request_performance')
    if r_perf is not None:
        r_perf.start_query()


@event.listens_for(Engine, 'after_cursor_execute')
def after_query(conn, cursor, statement, parameters, context, executemany):
    r_perf: RequestPerformance = g.get('ttf_request_performance')
    if r_perf is not None:
        r_perf.end_query(statement)


def record_view_performance():
    def record_view_performance_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            r_perf: RequestPerformance = g.get('ttf_request_performance')
            if r_perf is not None:
                r_perf.start_view_function()
            result = f(*args, **kwargs)
            if r_perf is not None:
                r_perf.end_view_function()
            return result
        return wrapper
    return record_view_performance_decorator
