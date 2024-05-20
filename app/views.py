from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User as User_Auth
from django.shortcuts import get_object_or_404
from django.utils import timezone

import json
from datetime import timedelta

from .addons import *
from .models import *


@require_http_methods(["GET"])
@tryexception
def read_cars_view(request, user_id):
    cars = Cars.objects.filter(owner=user_id).all()

    return JsonResponse({'cars': [
        {
            'id': car.id,
            'car_name': car.name,
            'car_number': car.number
        }
        for car in cars]
    }, status=200)

@require_http_methods(["GET"])
@tryexception
def read_cars_by_id_view(request, car_id):
    car = get_object_or_404(Cars, id=car_id)

    return JsonResponse({'car':
        {
            'id': car.id,
            'car_name': car.name,
            'car_number': car.number
        }
    }, status=200)

@require_http_methods(["POST"])
@tryexception
def create_car_view(request):
    try:
        data = json.loads(request.body)
        owner_id = int(data['owner_id'])
        print('Received owner_id:', owner_id)

        try:
            owner = User_Auth.objects.get(id=owner_id)
        except User_Auth.DoesNotExist:
            return JsonResponse({
                'error': 'User matching query does not exist'
            }, status=404)

        new_car = Cars.objects.create(
            name=data['car_name'],
            number=data['car_number'],
            owner=owner
        )

        return JsonResponse({
            'car_id': new_car.id
        }, status=200)
    except Exception as e:
        print('Internal Server Error:', e)
        return JsonResponse({
            'error': 'Internal Server Error',
            'details': str(e)
        }, status=500)


@require_http_methods(["PUT"])
@tryexception
def update_car_view(request, car_id):
    data = json.loads(request.body)
    car = Cars.objects.get(id=car_id)
    car.name = data['car_name']
    car.number = data['car_number']
    car.save()

    return JsonResponse({
        'car_id': car.id
    }, status=200)


@require_http_methods(["DELETE"])
@tryexception
def delete_car_view(request, car_id):
    car = Cars.objects.get(id=car_id)
    car.delete()
    return JsonResponse({'message': 'Car deleted successfully'}, status=200)


@require_http_methods(["GET"])
@tryexception
def read_service_view(request, car_id):
    services = Service.objects.filter(car_id=car_id).all()
    service_data = []

    for service in services:
        service_dict = {
            'car_id': service.car_id,
            **{field.name: getattr(service, field.name) for field in Service._meta.fields if
               field.name != 'car' and getattr(service, field.name) is not None}
        }
        service_data.append(service_dict)

    return JsonResponse({'service': service_data}, status=200)

@require_http_methods(["GET"])
@tryexception
def read_service_by_id_view(request, serv_id):
    service = get_object_or_404(Service, id=serv_id)

    service_dict = {
            'car_id': service.car_id,
            **{field.name: getattr(service, field.name) for field in Service._meta.fields if
               field.name != 'car' and getattr(service, field.name) is not None}
        }

    print("Сервис: ", service)
    return JsonResponse({'service': service_dict}, status=200)

@require_http_methods(["POST"])
@tryexception
def create_service_view(request):
    data = json.loads(request.body)
    print(data)

    try:
        new_service = Service.objects.create(
            **{field.name: data.get(field.name) for field in Service._meta.fields if
            field.name != 'id' and field.name != 'car_id'},
            car_id=data['car_id']
        )
    except Exception as e:
        print("Ошибка: ", e)

    return JsonResponse({
        'service_id': new_service.id
    }, status=200)


@require_http_methods(["PUT"])
@tryexception
def update_service_view(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Service not found'}, status=404)

    data = json.loads(request.body)

    for field in Service._meta.fields:
        if field.name != 'id' and field.name != 'car_id':
            setattr(service, field.name, data.get(field.name, getattr(service, field.name)))

    if 'car_id' in data:
        service.car_id = data['car_id']

    service.save()

    return JsonResponse({'message': 'Service updated successfully'}, status=200)


@require_http_methods(["DELETE"])
@tryexception
def delete_service_view(request, service_id):
    service = Service.objects.get(id=service_id)
    service.delete()
    return JsonResponse({'message': 'Service deleted successfully'}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
@tryexception
def register_view(request):
    data = json.loads(request.body)
    username = data.get('username')

    if not User_Auth.objects.filter(username=username).exists():
        new_user = User_Auth.objects.create_user(username=data.get('username'), password=data.get('password'))

        return JsonResponse({
            'user_id': new_user.id
        }, status=200)
    else:
        return JsonResponse({
            'error': 'User already exists'
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
@tryexception
def login_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    user = authenticate(username=username, password=password)

    if user is not None:
        csrf_token = get_token(request)
        return JsonResponse({'success': True, 'csrf_token': csrf_token, 'id': user.id})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid credentials'})


@require_http_methods(["GET"])
@tryexception
def notify(request, user_id):
    cars = Cars.objects.filter(owner=user_id).all()
    cars_to_notify = list()

    current_time = timezone.now()
    timest = current_time.timestamp()
    print("Текущее время:", current_time)

    try:
        for car in cars:
            # Получаем последний техосмотр по дате окончания
            latest_service = Service.objects.filter(car_id=car.id).order_by('-end_timestamp').first()

            if latest_service is None:
                continue  # Если техосмотра нет, пропускаем

            # Проверяем, что поля не пустые
            if latest_service.mileage is None or latest_service.end_timestamp is None:
                continue

            end_timestamp = latest_service.end_timestamp

            if latest_service.mileage < 5000 and timest - end_timestamp > timedelta(days=365 * 4).total_seconds():
                cars_to_notify.append(car.name)
                continue
            
            if latest_service.mileage < 7000 and timest - end_timestamp > timedelta(days=365 * 3).total_seconds():
                cars_to_notify.append(car.name)
                continue

            if latest_service.mileage < 10000 and timest - end_timestamp > timedelta(days=365 * 2).total_seconds():
                cars_to_notify.append(car.name)
                continue

            if latest_service.mileage >= 10000 and timest - end_timestamp > timedelta(days=365).total_seconds():
                cars_to_notify.append(car.name)
                continue

        print(cars_to_notify)
        return JsonResponse({'cars_to_check': cars_to_notify}, status=200)
    except Exception as e:
        print('Ошибка: ', e)
        return JsonResponse({}, status=500)
