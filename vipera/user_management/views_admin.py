from rest_framework.views import APIView
from user_management.permissions import IsAdmin

class AdminOnlyView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({"msg": "Welcome Admin"})
