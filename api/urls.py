from rest_framework.routers import SimpleRouter
from api import views


router = SimpleRouter()

router.register(r'search', views.SearchViewSet)

urlpatterns = router.urls
