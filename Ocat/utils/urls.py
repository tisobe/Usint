from django.conf.urls   import *
from utils.views        import LoginUser
#from utils.views        import login_user

urlpatterns = [
    url(r'^login/', LoginUser.as_view()),
#    url(r'^login/', login_user),
]

