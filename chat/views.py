from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from core.models import Thread, Message


# Create your views here.
def MessageView(request):
    if request.user.is_authenticated: 
        threads = Thread.objects.by_user(user=request.user).prefetch_related('message_thread').order_by('-created_at')

        context = {
            'Threads': threads,
            'now': timezone.now()
        }
        return render(request, "dashboard/chat.html", context)
    else:
        return redirect('account:login')

@csrf_exempt
def SendMessage(request):
    if request.method == 'POST':
        print(request.POST)
        try:
            thread = Thread.objects.get(id=request.POST.get('thread_id'))
            new_message = Message.objects.create(thread=thread, user=request.user, message=request.POST.get('message'))
            return JsonResponse({'message_id': new_message.id})
        except Exception as e:
            print(e)
            pass
    return HttpResponse("ok", status=201)


def get_messages(request):
    try:
        # get the threads for the current user
        threads = Thread.objects.by_user(user=request.user).prefetch_related('message_thread').order_by('created_at')
        # create a dictionary to store the thread and message data
        data = []
        for thread in threads:
            messages = []
            # get the messages for the thread
            for message in thread.message_thread.all():
                # create a dictionary to store the message data
                message_data = {
                    'id': message.id,
                    'user': message.user.username,
                    'user_id' : message.user.id,
                    'message': message.message,
                    'created_at': str(message.created_at)
                }
                messages.append(message_data)
            # create a dictionary to store the thread data
            thread_data = {
                'id': thread.id,
                'first_person': thread.first_person.username,
                'second_person': thread.second_person.username,
                'created_at': thread.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': thread.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'messages': messages
            }
            data.append(thread_data)
        return JsonResponse({'threads': data})
    except:
        pass
