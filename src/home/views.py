from django.shortcuts import render, HttpResponse # type: ignore
from django.http import JsonResponse
from django.views import View


# Create your views here.
def home(request):
    return HttpResponse("Hello, Django with Docker!")


class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "healthy", "service": "django"})