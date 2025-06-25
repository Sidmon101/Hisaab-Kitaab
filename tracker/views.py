from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render,redirect
from .forms import GroupCreateForm, GroupJoinForm
from .forms import ExpenseForm
from collections import defaultdict
from .models import Group, Expense

import matplotlib
matplotlib.use('Agg')# Use non-GUI backend for server environments
import matplotlib.pyplot as plt
import io
from decimal import Decimal, ROUND_HALF_UP
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Message




@login_required
def home(request):
    user = request.user
    groups = Group.objects.filter(members=user)

    total_balance = Decimal('0.00')

    for group in groups:
        members = group.members.all()
        num_members = members.count()

        # Get all expenses in the group
        expenses = Expense.objects.filter(group=group)
        total_group_expense = sum(exp.amount for exp in expenses)

        # User's contribution
        user_paid = sum(exp.amount for exp in expenses if exp.user == user)

        # Equal share per member
        if num_members > 0:
            share = total_group_expense / num_members
        else:
            share = Decimal('0.00')

        # Net balance for this group
        balance = user_paid - share
        total_balance += balance

    return render(request, 'tracker/home.html', {
        'groups': groups,
        'total_balance': round(total_balance, 2)
    })







def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect after successful signup
    else:
        form = UserCreationForm()

    return render(request, 'tracker/signup.html', {'form': form})  # Always return a response



@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user
            group.save()
            group.members.add(request.user)
            return redirect('home')
    else:
        form = GroupCreateForm()
    return render(request, 'tracker/create_group.html', {'form': form})

@login_required
def join_group(request):
    if request.method == 'POST':
        form = GroupJoinForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            group.members.add(request.user)
            return redirect('home')
    else:
        form = GroupJoinForm()

    return render(request, 'tracker/join_group.html', {'form': form})


@login_required
def add_expense(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.group = group
            expense.save()
            return redirect('group_dashboard',group_id=group_id)
    else:
        form = ExpenseForm()
    return render(request, 'tracker/add_expense.html', {'form': form, 'group': group})

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    group = expense.group

    if request.user != expense.user and request.user != group.admin:
        return HttpResponse("You are not authorized to delete this expense.", status=403)

    group_id = group.id
    expense.delete()
    return redirect('group_dashboard', group_id=group_id)


@login_required
def group_dashboard(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user not in group.members.all():
        return HttpResponse("You are not a member of this group.", status=403)

    expenses = group.expenses.all().order_by('-date')
    total = sum(exp.amount for exp in expenses)
    members = group.members.all()

    if members.exists():
        per_member_share = (total / Decimal(members.count())).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    else:
        per_member_share = Decimal('0.00')

    contributions = defaultdict(Decimal)
    for exp in expenses:
        contributions[exp.user] += exp.amount

    balances = []
    for member in members:
        spent = contributions[member]
        balance = spent - per_member_share
        balances.append({
            'member': member,
            'spent': spent,
            'balance': balance,
        })

    return render(request, 'tracker/group_dashboard.html', {
        'group': group,
        'expenses': expenses,
        'total': total,
        'balances': balances,
    })




@login_required
def generate_pie_charts(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user not in group.members.all():
        return HttpResponse("You are not a member of this group.", status=403)

    expenses = group.expenses.all()

    # Pie chart 1: Individual Contributions
    contributions = {}
    for exp in expenses:
        contributions[exp.user.username] = contributions.get(exp.user.username, Decimal('0.00')) + exp.amount

    labels_contrib = list(contributions.keys())
    sizes_contrib = [float(amount) for amount in contributions.values()]

    # Pie chart 2: Expense Categories
    categories = {}
    for exp in expenses:
        categories[exp.category] = categories.get(exp.category, Decimal('0.00')) + exp.amount

    labels_cat = list(categories.keys())
    sizes_cat = [float(amount) for amount in categories.values()]

    # Plotting both pie charts side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    ax1.pie(sizes_contrib, labels=labels_contrib, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    ax1.set_title('Individual Contributions')

    ax2.pie(sizes_cat, labels=labels_cat, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    ax2.set_title('Expense Categories')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type='image/png')






def chat_history(request, group_id):
    page_number = request.GET.get('page', 1)
    messages = Message.objects.filter(group_id=group_id).order_by('-timestamp')
    paginator = Paginator(messages, 25)

    page = paginator.get_page(page_number)
    data = [
        {
            'username': msg.user.username,
            'message': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M')
        }
        for msg in page.object_list
    ]

    return JsonResponse({
        'messages': data[::-1],  # reverse to show oldest first
        'has_next': page.has_next(),
        'next_page': page.next_page_number() if page.has_next() else None
    })

