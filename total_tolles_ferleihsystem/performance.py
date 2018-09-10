from flask import g, request
from time import time
from collections import namedtuple
from sqlalchemy.engine import Engine
from sqlalchemy import event

from . import APP

from typing import Any, List


QueryRecord = namedtuple('QueryRecord', ['duration', 'statement', 'write'])


class RequestPerformance:

    req_start: float
    req_end: float
    duration: float
    query_start: float
    queries: List[QueryRecord]

    def __init__(self):
        t = time()
        self.req_start = t
        self.req_end = t
        self.query_start = t
        self.duration = 0
        self.queries = []

    def end_request(self):
        self.req_end = time()
        self.duration = self.req_end - self.req_start
        if self.duration > APP.config.get('LONG_REQUEST_THRESHHOLD', 1):
            self.log_performance_record()

    def start_query(self):
        self.query_start = time()

    def end_query(self, statement):
        query_end = time()
        write = not statement.upper().startswith('SELECT')
        self.queries.append(QueryRecord(query_end - self.query_start, statement, write))
        self.query_start = query_end

    def __repr__(self):
        return '<RequestPerformance duration={}s, {} queries>'.format(self.duration, len(self.queries))

    def log_performance_record(self):
        url = request.url
        method = request.method
        if self.queries:
            q_number = len(self.queries)
            q_write_number = sum(1 if q.write else 0 for q in self.queries)
            tot_query_duration = sum(q.duration for q in self.queries)
            duration_wo_queries = self.duration - tot_query_duration
            self.queries.sort(key=lambda q: q.duration)
            longest_query_duration = self.queries[0].duration
            APP.logger.warning(f'performance report: duration {self.duration: 2.2f}s, duration without queries {duration_wo_queries: 2.2f}s, query-duration {tot_query_duration: 2.2f}s, {q_number: 2d} queries ({q_write_number: 2d} write), longest query {longest_query_duration: 2.2f}, url {method:6} {url}')
            for q in self.queries:
                if q.duration > 1:
                    APP.logger.warning(f'performance report: long query detected: duration {q.duration: 2.2f}s, statement "{q.statement}"')
        else:
            APP.logger.warning(f'performance report: duration {self.duration: 2.2f}s, url {method} {url}')


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
