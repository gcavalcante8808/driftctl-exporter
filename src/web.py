import os

import prometheus_client
from aiohttp import web
from prometheus_client import CONTENT_TYPE_LATEST

from exporter.domain import Rfc1808Url
from exporter.repositories import S3Repository
from exporter.usecases import generate_metrics_from_drift_results_usecase

routes = web.RouteTableDef()


@routes.get('/metrics')
async def metrics(request):
    s3_repository = S3Repository()
    url = Rfc1808Url.from_url(os.getenv('RESULT_PATH'))

    generate_metrics_from_drift_results_usecase(s3_repository, url)

    resp = web.Response(body=prometheus_client.generate_latest())
    resp.content_type = CONTENT_TYPE_LATEST
    return resp


app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0')
