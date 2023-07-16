from django.shortcuts import render, redirect
from django.views import View
from .forms import ChatForm
from .models import ChatSession, ChatMessage
import openai
import re
import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def index(request):
    """
    チャット画面
    """
    # 応答結果
    chat_results = ""
    if request.method == "POST":
        # ChatGPTボタン押下時
        form = ChatForm(request.POST)
        if form.is_valid():
            sentence = form.cleaned_data['sentence']
            openai.api_key = OPENAI_API_KEY

            # 新規チャットセッションを開始または既存のチャットセッションを取得
            session_id = request.session.get('chat_session_id')
            if session_id is None:
                chat_session = ChatSession.objects.create()
                request.session['chat_session_id'] = chat_session.id
            else:
                chat_session = ChatSession.objects.get(id=session_id)

            # ユーザのメッセージを保存
            ChatMessage.objects.create(session=chat_session, content=sentence, by_user=True)

            # ChatGPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {   "role": "system", "content": """
===
＃役割：

ユーザーは一生懸命にゴルフの上達を目指しています。上達するための一手段として、自分の左肩、右肩、右足、左足の4つの部位に加速度計を装着し、スイング時の加速度データを収集しています。


＃目標：

ユーザーの目指す目標は、収集した加速度データを分析し、そのデータからスイングの問題点や改善すべきポイントを見つけ出すことです。その結果をもとに具体的で効果的なアドバイスを提供します。

初めに、ユーザーの各部位（左肩、右肩、右足、左足）の加速度データの平均値を教えていただくことで、分析を始め、アドバイスだけをユーザーにあげてください。

分析が終わったら、ユーザーに他のデータがないかを聞き、次の分析ができるように準備をしてください。
                     
＃注意：
                     
サーバーが終わりと言ったらもうこれ以上データの強要はせず、このセッションを終わりにすること。

===
                        """},
                    {"role": "user", "content": sentence},
                ],
            )
            chat_results_raw = response["choices"][0]["message"]["content"]

            # ChatGPTの応答を保存
            ChatMessage.objects.create(session=chat_session, content=chat_results_raw, by_user=False)

            chat_results_cleaned = re.sub(r'(\d+\.)', r'\1\n', chat_results_raw)
            chat_results_items = [item.rstrip('。').strip() for item in chat_results_cleaned.split('\n') if item.strip()]
            chat_results_items = [re.sub(r'\.$', '', item) for item in chat_results_items]

            chat_results = '<table>' + ''.join(f'<tr><td>{item.split(".")[0]}</td><td>{item.split(".")[1].strip() if "." in item else ""}</td></tr>' for item in chat_results_items) + '</table>'
    else:
        form = ChatForm()

    sessions = ChatSession.objects.all()

    context = {
        'form': form,
        'chat_results': chat_results,
        'sessions': sessions
    }
    return render(request, 'index.html', context)



class ChatView(View):
    def get(self, request):
        form = ChatForm()
        sessions = ChatSession.objects.all()
        context = {
            'form': form,
            'sessions': sessions,
            'new_session': request.session.get('new_session', False)
        }
        return render(request, 'index.html', context)

    def post(self, request):
        form = ChatForm(request.POST)
        if form.is_valid():
            sentence = form.cleaned_data['sentence']
            openai.api_key = OPENAI_API_KEY

            session_id = request.session.get('chat_session_id')
            if session_id is None:
                chat_session = ChatSession.objects.create()
                request.session['chat_session_id'] = chat_session.id
            else:
                chat_session = ChatSession.objects.get(id=session_id)

            ChatMessage.objects.create(session=chat_session, content=sentence, by_user=True)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """
===
＃役割：
ユーザーは一生懸命にゴルフの上達を目指しています。上達するための一手段として、自分の左肩、右肩、右足、左足の4つの部位に加速度計を装着し、スイング時の加速度データを収集しています。

＃目標：

ユーザーの目指す目標は、収集した加速度データを分析し、そのデータからスイングの問題点や改善すべきポイントを見つけ出すことです。その結果をもとに具体的で効果的なアドバイスを提供します。

初めに、ユーザーの各部位（左肩、右肩、右足、左足）の加速度データの平均値を教えていただくことで、分析を始め、アドバイスだけをユーザーにあげてください。

分析が終わったら、ユーザーに他のデータがないかを聞き、次の分析ができるように準備をしてください。
                     
＃注意：
                     
サーバーが終わりと言ったらもうこれ以上データの強要はせず、このセッションを終わりにすること。
===
                        """},
                    {"role": "user", "content": sentence},
                ],
            )

            chat_results_raw = response["choices"][0]["message"]["content"]

            # ChatGPTの応答を保存
            ChatMessage.objects.create(session=chat_session, content=chat_results_raw, by_user=False)

            chat_results_cleaned = re.sub(r'(\d+\.)', r'\1\n', chat_results_raw)
            chat_results_items = [item.rstrip('。').strip() for item in chat_results_cleaned.split('\n') if item.strip()]
            chat_results_items = [re.sub(r'\.$', '', item) for item in chat_results_items]

            chat_results = '<table>' + ''.join(f'<tr><td>{item.split(".")[0]}</td><td>{item.split(".")[1].strip() if "." in item else ""}</td></tr>' for item in chat_results_items) + '</table>'
        
            form = ChatForm()

            sessions = ChatSession.objects.all()

            context = {
                'form': form,
                'chat_results': chat_results,
                'sessions': sessions
            }
            return render(request, 'index', context)


def new_session(request):
    request.session.pop('chat_session_id', None)
    request.session['new_session'] = True
    return redirect('index')


def start_new(request):
    """
    Start a new chat session.
    """
    # Create a new ChatSession object and save it to the database.
    chat_session = ChatSession.objects.create()

    # Store the new session's ID in the user's session.
    request.session['chat_session_id'] = chat_session.id

    # Redirect the user to the index page.
    return redirect('chat:index')

def continue_session(request, session_id):
    """
    Continue an existing chat session.
    """
    # Get the ChatSession object with the given ID.
    chat_session = ChatSession.objects.get(id=session_id)

    # Store the session's ID in the user's session.
    request.session['chat_session_id'] = chat_session.id

    # Redirect the user to the index page.
    return redirect('chat:index')

@csrf_exempt
def delete_session(request, session_id):
    if request.method == 'DELETE':
        try:
            session = ChatSession.objects.get(id=session_id)
            session.delete()
            return JsonResponse({'status': 'success'})
        except ChatSession.DoesNotExist:
            return JsonResponse({'status': 'Session not found'}, status=404)
        

