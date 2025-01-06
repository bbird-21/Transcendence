from prometheus_client import generate_latest, REGISTRY
from prometheus_client.exposition import basic_auth_handler
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def metrics(request):
    return HttpResponse(generate_latest(REGISTRY), content_type="text/plain; charset=utf-8")
