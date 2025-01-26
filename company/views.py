from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from company.models import Inquiry, Todo
from order.models import Post, Company
from project_management.models import Ticket
from django.views.generic.edit import CreateView, UpdateView
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect
from company.models import Inquiry, Todo
from order.models import Post, Company
from project_management.models import Ticket


def company_detail(request, company_id):
    """
    会社に関連するデータ（発注情報、タスク、問い合わせ、TODOリスト）を表示し、
    TODOおよび問い合わせ情報の追加、削除、チェックを管理するビュー
    """
    # 会社情報を取得
    company = get_object_or_404(Company, id=company_id)

    # 会社に関連するデータを取得
    todos = Todo.objects.filter(company=company)
    orders = Post.objects.filter(company=company)
    tickets = Ticket.objects.filter(project__companies=company)
    inquiries = Inquiry.objects.filter(company=company)

    if request.method == 'POST':
        # TODOの追加
        if 'add_todo' in request.POST:
            task = request.POST.get('task', '').strip()
            if task:
                Todo.objects.create(company=company, task=task)
            return redirect('company:company_detail', company_id=company.id)

        # TODOの削除
        if 'delete_todo' in request.POST:
            todo_id = request.POST.get('todo_id')
            if todo_id:
                todo = get_object_or_404(Todo, id=todo_id, company=company)
                todo.delete()
            return redirect('company:company_detail', company_id=company.id)

        # TODOのチェック更新
        for todo in todos:
            is_completed = f'completed_{todo.id}' in request.POST
            if todo.is_completed != is_completed:
                todo.is_completed = is_completed
                todo.save()

        # 問い合わせ情報の追加
        if 'add_inquiry' in request.POST:
            category = request.POST.get('category', '').strip()
            question = request.POST.get('question', '').strip()
            question_date = request.POST.get('question_date', '').strip()
            answer_date = request.POST.get('answer_date', '').strip()
            answer = request.POST.get('answer', '').strip()

            if category and question and question_date:
                Inquiry.objects.create(
                    company=company,
                    category=category,
                    question=question,
                    question_date=question_date,
                    answer_date=answer_date or None,
                    answer=answer or None,
                )
            return redirect('company:company_detail', company_id=company.id)

        # 問い合わせ情報の削除
        if 'delete_inquiry' in request.POST:
            inquiry_id = request.POST.get('inquiry_id')
            if inquiry_id:
                inquiry = get_object_or_404(Inquiry, id=inquiry_id, company=company)
                inquiry.delete()
            return redirect('company:company_detail', company_id=company.id)

    return render(request, 'company/company_detail.html', {
        'company': company,
        'todos': todos,
        'orders': orders,
        'tickets': tickets,
        'inquiries': inquiries,
    })


class InquiryCreateView(CreateView):
    model = Inquiry
    fields = ['category', 'question', 'question_date', 'answer_date', 'answer']
    template_name = 'company/inquiry_form.html'

    def form_valid(self, form):
        company_id = self.kwargs.get('company_id')
        form.instance.company = get_object_or_404(Company, id=company_id)
        return super().form_valid(form)

    def get_success_url(self):
        company_id = self.kwargs.get('company_id')
        return reverse_lazy('company:company_detail', kwargs={'company_id': company_id})


class InquiryUpdateView(UpdateView):
    model = Inquiry
    fields = ['category', 'question', 'question_date', 'answer_date', 'answer']
    template_name = 'company/inquiry_form.html'

    def get_success_url(self):
        company_id = self.object.company.id
        return reverse_lazy('company:company_detail', kwargs={'company_id': company_id})


def delete_inquiry(request, pk):
    """
    問い合わせ情報を削除するビュー
    """
    if request.method == 'POST':
        inquiry = get_object_or_404(Inquiry, id=pk)
        inquiry.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)