from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views import View
from django.conf import settings
import random
import requests

from sns.views import NotificationListView

class JankenView(View):
    template_name = 'games/janken.html'
    HANDS = {
        'グー': '✊',
        'チョキ': '✌',
        'パー': '✋',
    }
    def get(self, request):
        # 初回表示用（まだ何も選んでない状態）
        return render(request, self.template_name)

    def post(self, request):
        # キーを取得してリスト化　['グー', 'チョキ', 'パー']
        choices = list(self.HANDS.keys())
        user_choice = request.POST.get('choice')
        computer_choice = random.choice(choices)

        if user_choice == computer_choice:
            result = 'あいこ'
        elif (user_choice == 'グー' and computer_choice == 'チョキ') or \
             (user_choice == 'チョキ' and computer_choice == 'パー') or \
             (user_choice == 'パー' and computer_choice == 'グー'):
            result = 'あなたの勝ち！'
        else:
            result = 'あなたの負け…'
        
        context = {
            'user_choice': f'{user_choice} {self.HANDS[user_choice]}',
            'computer_choice': f'{computer_choice} {self.HANDS[computer_choice]}',
            'result': result,
        }
        return render(request, self.template_name, context)
    
class NumberGuessVeiw(View):
    template_name = 'games/number_guess.html'

    def get(self, request):
        # ゲーム開始時に答えをセッションに保存
        if 'answer' not in request.session:
            request.session['answer'] = random.randint(1, 10)
            request.session['message'] = '1～10の数字を当ててください！'
        return render(request, self.template_name, {
            'message': request.session.get('message', '')
        })
    def post(self, request):
        # セッションをリセット処理
        if 'reset' in request.POST:
            request.session.flush()
            return redirect('games:number_guess')
        
        guess = int(request.POST.get('guess'))
        answer = request.session['answer']

        if guess == answer:
            request.session['message'] = f'正解！答えは {answer} でした！🎉'
        elif guess < answer:
            request.session['message'] = f'もっと大きい数字です！'
        else:
            request.session['message'] = f'もっと小さい数字です！'
        
        return redirect('games:number_guess')

class FortuneWeatherView(View):
    template_name = 'games/fortune_weather.html'

    def get_weather(self, city):
        api_key = settings.OPENWEATHERMAP_API_KEY
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ja'

        try:
            res = requests.get(url)
            data = res.json()
            icon_code = data['weather'][0]['icon']
            weather = {
                'city': city,
                'condition': data['weather'][0]['description'],
                'temperature': round(data['main']['temp']),
                'icon_url': f"http://openweathermap.org/img/wn/{icon_code}@2x.png",
            }
        except Exception as e:
            # APIエラー時はサンプル表示
            weather = {
                'city': city,
                'condition': '情報取得エラー',
                'temperature': '--',
                'icon_url': '',
            }
        return weather

    def get(self, request):
        # 場所
        city = request.session.get('city', 'Tokyo')
        # 天気
        weather = self.get_weather(city)
        # 運勢はまだ引いていないので None
        fortune = request.session.get('fortune', None)

        context = {
            'fortune': fortune,
            'weather': weather,
            'city': city,
        }
        return render(request, self.template_name, context)
        

    def post(self, request):
        # セッションから運勢を削除してリセット
        if 'reset' in request.POST:
            request.session.pop('fortune', None)
            return redirect('games:fortune_weather')
        if 'city' in request.POST:
            city = request.POST.get('city')
            request.session['city'] = city
            return redirect('games:fortune_weather')
        # 運勢リスト
        fortunes = ['大吉', '中吉', '小吉', '吉', '末吉', '凶']
        fortune = random.choice(fortunes)
        # セッションに保存（リロードしても結果を保持したい場合）
        request.session['fortune'] = fortune
    
        return redirect('games:fortune_weather')