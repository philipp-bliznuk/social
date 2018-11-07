from rest_framework import routers

from .views import UserRegistrationView, PostCreateView


router = routers.SimpleRouter()

router.register(r'user', UserRegistrationView)
router.register(r'post', PostCreateView)

urlpatterns = router.urls
