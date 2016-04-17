from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from api.serializers import SearchSerializer
from api.models import Search
from crawler import api_search
#from rest_framework.views import APIView



class SearchViewSet(ModelViewSet):
	queryset = Search.objects.all()
	new_result = Search.testMethod()
	serializer_class = SearchSerializer
	def retrieve(self, request, pk=None):
		my_query_param = request.GET['q']
		my_max_result_param = 15
		res_search = api_search(my_query_param,my_max_result_param)
		return Response({'result':res_search})