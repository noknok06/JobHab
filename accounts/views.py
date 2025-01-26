# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')  # 登録後にログイン画面にリダイレクト
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
