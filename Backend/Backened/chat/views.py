from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import get_chatbot_response

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_query = data.get("message", "")
        response = get_chatbot_response(user_query)
        return JsonResponse(response, safe=False)
    return JsonResponse({"error": "POST request required"}, status=400)
