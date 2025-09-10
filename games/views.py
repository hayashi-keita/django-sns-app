from unittest import result
from django.shortcuts import render
from django.views.generic import TemplateView
import random

class JankenView(TemplateView):
    template_name = 'games/janken.html'
    HANDS = {
        'グー': '✊',
        'チョキ': '✌',
        'パー': '✋',
    }

    def post(self, request, **kwargs):
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
        
        context = self.get_context_data(**kwargs)
        context.update({
            'user_choice': f'{user_choice} {self.HANDS[user_choice]}',
            'computer_choice': f'{computer_choice} {self.HANDS[computer_choice]}',
            'result': result,
        })
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        # getの時は空のコンテキスト
        context = super().get_context_data(**kwargs)
        return context