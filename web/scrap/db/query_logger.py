import logging
import time

from django.db import connection
from django.utils.deprecation import MiddlewareMixin


class QueryLogger:
    # Copied from https://docs.djangoproject.com/en/4.0/topics/db/instrumentation/

    def __init__(self):
        self.queries = []

    def __call__(self, execute, sql, params, many, context):
        current_query = {'sql': sql, 'params': params, 'many': many}
        start = time.monotonic()
        try:
            result = execute(sql, params, many, context)
        except Exception as e:
            current_query['status'] = 'error'
            current_query['exception'] = e
            raise
        else:
            current_query['status'] = 'ok'
            return result
        finally:
            duration = time.monotonic() - start
            current_query['duration'] = duration
            self.queries.append(current_query)

    def reset(self):
        self.queries.clear()

    def summarize_queries(self, reset=False):
        query_counts = {}
        for query in self.queries:
            # TODO: Do something with status and exception?  Currently not worrying about those as I'm just tuning.
            if query['sql'] not in query_counts:
                sql = query['sql'] if len(query['sql']) < 50 else f"{query['sql'][:47]}..."
                query_counts[query['sql']] = {
                    'count': 0, 'min_time': None, 'max_time': None, 'times': [], 'sql_abbr': sql, 'total_time': 0}
            query_counts[query['sql']]['count'] += 1
            query_counts[query['sql']]['times'].append(query['duration'])
            if query_counts[query['sql']]['min_time'] is None:
                query_counts[query['sql']]['min_time'] = query['duration']
            elif query_counts[query['sql']]['min_time'] > query['duration']:
                query_counts[query['sql']]['min_time'] = query['duration']
            if query_counts[query['sql']]['max_time'] is None:
                query_counts[query['sql']]['max_time'] = query['duration']
            elif query_counts[query['sql']]['max_time'] < query['duration']:
                query_counts[query['sql']]['max_time'] = query['duration']
        for query_data in query_counts.values():
            query_data['total_time'] = sum(query_data['times'])
        if reset:
            self.reset()
        return query_counts


logger = logging.getLogger(__name__)


class QueryCountDebugMiddleware(MiddlewareMixin):
    # Initially copied from https://gist.github.com/daniestrella1/869b664b08e11615f542814f39ca6f15
    # Then gutted as the original code didn't do what I wanted, but I used the concept.
    ql = None
    request_counter = 0
    request_timer_start = 0

    def __init__(self, get_response):
        self.ql = QueryLogger()
        super().__init__(get_response)

    def process_request(self, request):
        self.request_counter += 1
        self.request_timer_start = time.monotonic()
        with connection.execute_wrapper(self.ql):
            return self.get_response(request)

    def process_response(self, request, response):
        if self.ql:
            request_duration = time.monotonic() - self.request_timer_start
            request_data = {
                'method': request.method,
                # 'content_type': request.content_type,  # was empty so disabling and leaving this note.
                'REMOTE_ADDR': request.META['REMOTE_ADDR'],
                'path_info': request.path_info,
                # GET and POST variables?
                'count': self.request_counter,
                'request_duration': request_duration,
            }
            queries = self.ql.summarize_queries(reset=True)
            query_total_time = 0
            for query_data in queries.values():
                query_total_time += query_data['total_time']
                logger.debug(f"request={request_data}|QueryLogger: {query_data}")
            logger.debug(f"request={request_data}|QueryLogger: query_total_time={query_total_time}|request_total_time={request_duration}")
        return response
