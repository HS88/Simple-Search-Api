from rest_framework.serializers import ModelSerializer
from api.models import Search


class SearchSerializer(ModelSerializer):

    class Meta:
        model = Search
