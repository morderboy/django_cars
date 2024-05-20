from django.contrib import admin
from django.urls import path
from app.views import *

urlpatterns = [
    path('api/admin', admin.site.urls),

    path('api/car/<int:user_id>', read_cars_view),
    path('api/car/one/<int:car_id>', read_cars_by_id_view),

    path('api/car/create', create_car_view),
    path('api/car/update/<int:car_id>', update_car_view),
    path('api/car/delete/<int:car_id>', delete_car_view),

    path('api/car/service/<int:car_id>', read_service_view),
    path('api/car/service/one/<int:serv_id>', read_service_by_id_view),

    path('api/car/service/create', create_service_view),
    path('api/service/update/<int:service_id>', update_service_view),
    path('api/service/delete/<int:service_id>', delete_service_view),

    path('api/register', register_view),
    path('api/login', login_view),

    path('api/notify/<int:user_id>', notify)
]
