from string import punctuation

from django.shortcuts import render, redirect

from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from alcpt.managerfuncs import testmanager
from alcpt.decorators import permission_check
from alcpt.definitions import UserType, QuestionType, QuestionTypeCounts
from alcpt.models import Exam, TestPaper, Group, Student, User
from alcpt.exceptions import *


@permission_check(UserType.TestManager)
@require_http_methods(["GET"])
def group_list(request):
    group_name = request.GET.get('group_name')

    if group_name:
        groups = Group.objects.filter(name__contains=group_name)
    else:
        groups = Group.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(groups, 10)

    try:
        groupList = paginator.page(page)
    except PageNotAnInteger:
        groupList = paginator.page(1)
    except EmptyPage:
        groupList = paginator.page(paginator.num_pages)

    return render(request, 'group/testee_group_list.html', locals())


@permission_check(UserType.TestManager)
def group_create(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name',)

        try:
            group = Group.objects.create(name=group_name, created_by=request.user)
        except:
            messages.error(request, "Failed created, this name has existed.")
            return render(request, 'group/testee_group_create.html', locals())

        messages.success(request, 'Successfully created.')
        return redirect('testee_group_edit', group_id=group.id)

    else:
        return render(request, 'group/testee_group_create.html', locals())


@permission_check(UserType.TestManager)
def group_edit(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
        group_members = group.member.all()
        testees = []
        for user in User.objects.all().filter(name__contains=''):
            if user.has_perm(UserType.Testee):
                testees.append(user)
            else:
                pass

    except ObjectDoesNotExist:
        messages.error(request, 'Group does not exist, group id: {}'.format(group_id))
        return redirect('testee_group_list')

    if request.method == 'POST':
        selected_testees = request.POST.getlist('testee',)

        selected_testee_list = []
        for selected_testee in selected_testees:
            selected_testee_list.append(User.objects.get(id=selected_testee))

        for selected_student in selected_testee_list:  # add all selected students into group
            group.member.add(selected_student)
        for member in group.member.all():               # check those who were unselected, and remove from the group
            if member not in selected_testee_list:
                group.member.remove(member)

        group.save()

        messages.success(request, 'Update group member successfully.')
        return redirect('testee_group_list')
    else:
        return render(request, 'group/testee_group_edit.html', locals())


@permission_check(UserType.TestManager)
def group_delete(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
        group.member.clear()
        group.delete()
        messages.success(request, "Successfully deleted.")
        return redirect(request.META.get('HTTP_REFERER'))

    except ObjectDoesNotExist:
        messages.error(request, "Group does not exist, group id - {}".format(group_id))
        return redirect(request.META.get('HTTP_REFERER'))


@permission_check(UserType.TestManager)
def group_content(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
        group_members = group.member.all()
        return render(request, 'group/testee_group_member_list.html', locals())

    except ObjectDoesNotExist:
        messages.error(request, 'Group does not exist, group id: {}'.format(group_id))
        return redirect('testee_group_list')
