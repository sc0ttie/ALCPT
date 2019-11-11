import re
from string import punctuation

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .models import *
from .exceptions import *
from .decorators import permission_check
from .managerfuncs import systemmanager


# 系統管理員首頁
@permission_check(UserType.SystemManager)
@require_http_methods(["GET"])
def index(request):
    try:
        page = int(request.GET.get('page', 0))
    except ValueError:
        page = 0

    keywords = {
        'name': request.GET.get('name')
    }

    if keywords['name'] and any(char in punctuation for char in keywords['name']):
        keywords['name'] = None
        messages.warning(request, "Name cannot contains any special character.")

    for keyword in ['department', 'grade', 'squadron']:
        try:
            keywords[keyword] = int(request.GET.get(keyword))
        except (KeyError, TypeError, ValueError):
            keywords[keyword] = None

    if keywords['department']:
        try:
            keywords['department'] = Department.objects.get(id=keywords['department'])
        except ObjectDoesNotExist:
            keywords['department'] = None

    if keywords['squadron']:
        try:
            keywords['squadron'] = Squadron.objects.get(id=keywords['squadron'])
        except ObjectDoesNotExist:
            keywords['squadron'] = None

    num_pages, users = systemmanager.query_users(**keywords, page=page)

    data = {
        'users': users,
        'departments': Department.objects.all(),
        'squadrons': Squadron.objects.all(),
        'priviledges': UserType.__members__,
        'num_types': range(1, len(UserType.__members__) + 1),
        'keywords': keywords,
        'page': page,
        'page_range': range(num_pages),
    }

    return render(request, 'user/list.html', data)


# 系統管理員新增使用者頁面
@permission_check(UserType.SystemManager)
@require_http_methods(["GET", "POST"])
def create_user(request):
    if request.method == 'POST':
        new_accounts = []
        for account in request.POST.get('accounts').split(','):
            account = account.strip().lower()
            if not re.match('[a-z0-9]+', account):
                raise IllegalArgumentError('Account can only contain letters and numbers.')

            new_accounts.append(account)

        priviledge_value = 0
        if request.user.has_perm(UserType.SystemManager):
            i = 0
            for priviledge in UserType.__members__.values():
                if priviledge and request.POST.get('priviledge_{}'.format(i)):
                    priviledge_value |= priviledge.value[0]

                i += 1

        else:
            priviledge_value = UserType.Testee.value[0]

        new_users = systemmanager.create_users(reg_ids=new_accounts,
                                               priviledge=priviledge_value,)

        if priviledge_value & UserType.Testee.value[0]:
            Student.objects.bulk_create([Student(user=new_user) for new_user in new_users])

        messages.success(request, 'Create user "{}" successful.'.format(len(new_users)))

        return redirect('/user')

    else:
        data = {'priviledges': UserType.__members__}

        return render(request, 'user/create.html', data)


# 系統管理員＆使用者修改使用者資料頁面
@login_required
@require_http_methods(["GET", "POST"])
def edit_user(request, reg_id: str):
    if request.user.reg_id != reg_id:
        if request.user.has_perm(UserType.SystemManager):
            try:
                edited_user = User.objects.get(reg_id=reg_id)

            except ObjectDoesNotExist:
                raise ObjectNotFoundError('Can\'t find user whose serial number:{}'.format(reg_id))

        else:
            raise PermissionWrongError()

    else:
        edited_user = request.user

    try:
        student = Student.objects.get(user=request.user)

    except ObjectDoesNotExist:
        student = None

    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'priviledge': None,
        }

        if any(char in punctuation for char in data['name']):
            raise IllegalArgumentError('Name can\'t have special character.')

        for field_value in ['department', 'grade', 'squadron', 'gender']:
            try:
                data[field_value] = request.POST.get(field_value)

            except (KeyError, TypeError):
                raise ArgumentError('Missing "{}".'.format(field_value))

            except KeyError:
                raise IllegalArgumentError('"{}" can\'t blank.'.format(field_value))

        try:
            data['department'] = Department.objects.get(id=data['department'])
        except ObjectDoesNotExist:
            pass
            # 非學生的使用者因為沒科系跟中隊能選所以用pass不然會一直出錯
            # raise ResourceNotFoundError("Cannot find department id={}".format(data['department']))

        try:
            data['squadron'] = Squadron.objects.get(id=data['squadron'])
        except ObjectDoesNotExist:
            pass
            # raise ResourceNotFoundError("Cannot find squadron id={}".format(data['squadron']))

        if request.user.has_perm(UserType.SystemManager):
            data['priviledge'] = 0
            i = 0
            for priviledge in UserType.__members__.values():
                if priviledge is not UserType.SystemManager and request.POST.get('priviledge_{}'.format(i)):
                    data['priviledge'] |= priviledge.value[0]

                i += 1

        new_password = request.POST.get('password')
        if new_password:
            if new_password != request.POST.get('check-password'):
                raise IllegalArgumentError('Password not equal.')

            elif not re.match('^[a-z0-9]{8,}$', new_password):
                print(bool(re.match('^[a-z0-9]{8,}$', new_password)))
                raise IllegalArgumentError('Password context is illegal.')

            systemmanager.update_password(edited_user, new_password)

        systemmanager.updata_user(edited_user, **data)

        messages.success(request, 'Updated user: {}'.format(edited_user.reg_id))

        if request.user.reg_id is edited_user.reg_id:
            return redirect('/user/{}'.format(reg_id))

        else:
            return redirect('/user')

    else:
        if request.GET.get('reset-password'):
            if not request.user.has_perm(UserType.SystemManager):
                raise PermissionWrongError()

            systemmanager.update_password(user=edited_user)

            messages.success(request, 'Reset password to serial number successfully.')

            return redirect('/user')

        data = {
            'user': edited_user,
            'student': student,
            'departments': Department.objects.all(),
            'squadrons': Squadron.objects.all(),
            'priviledges': UserType.__members__,
            'num_types': range(1, len(UserType.__members__) + 1),
            # 'password_pattern': '^(?!.*[^\x21-\x7e])[A-Za-z\d]{6,32}$',
            'password_pattern': '^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
        }

        return render(request, 'user/edit.html', data)


@login_required
@require_http_methods(["GET", "POST"])
def delete_user(request, reg_id: str):
    try:
        user = User.objects.get(reg_id=reg_id)

    except ObjectDoesNotExist:
        raise ResourceNotFoundError('Cannot find user serial number = {}.'.format(user.reg_id))

    user.delete()

    messages.success(request, 'Delete user={}.'.format(user.name))

    return redirect(request.META.get('HTTP_REFERER', '/user'))


# 蘇典煒
# 顯示所有單位
@permission_check(UserType.SystemManager)
@require_http_methods(["GET"])
def unit(request):
    departments = Department.objects.all()
    squadrons = Squadron.objects.all()
    return render(request, 'user/unit.html', locals())


# 編輯學系
@permission_check(UserType.SystemManager)
@require_http_methods(["GET", "POST"])
def edit_department(request, department_id):
    try:
        department = Department.objects.get(id = department_id)

    except ObjectDoesNotExist:
        raise ResourceNotFoundError('Cannot find department id = {}.'.format(department_id))

    if request.method == 'POST':
        name = request.POST.get('name')

        department.name = name
        department.save()

        messages.success(request, "Successfully update department :{}.".format(department.name))

        return redirect('/user/unit_list')
    else:
        return render(request, 'user/edit_department.html', {'department':department})


# 編輯中隊
@permission_check(UserType.SystemManager)
@require_http_methods(["GET", "POST"])
def edit_squadron(request, squadron_name):
    try:
        squadron = Squadron.objects.get(name = squadron_name)

    except ObjectDoesNotExist:
        raise ResourceNotFoundError('Cannot find department id = {}.'.format(squadron_name))

    if request.method == 'POST':
        name = request.POST.get('name')

        squadron.name = name
        squadron.save()

        messages.success(request, "Successfully update squadron :{}.".format(squadron.name))

        return redirect('/user/unit_list')
    else:
        return render(request, 'user/edit_squadron.html', {'squadron':squadron})


# 新增單位（學系、中隊）
@permission_check(UserType.SystemManager)
@require_http_methods(["GET", "POST"])
def insert_unit(request):
    name = request.POST.get('unit_name')
    if request.method == 'POST':
        if request.POST.get('unit') == 'department':
            Department.objects.create(name = name)

        elif request.POST.get('unit') == 'squadron':
            Squadron.objects.create(name = name)
        
        else:
            messages.error(request, 'Choose the unit which you want to insert.')
            return redirect('/user/unit_list/insert')
        
        messages.success(request, 'Success insert new unit: {}.'.format(name))

        return redirect('/user/unit_list')
    else:
        return render(request, 'user/insert_unit.html')


# 刪除學系
@permission_check(UserType.TestManager)
@require_http_methods(["GET"])
def delete_department(request, department_id):
    try:
        department = Department.objects.get(id = department_id)
    
    except ObjectDoesNotExist:
        raise ResourceNotFoundError('Cannot find object id = {}.'.format(department.name))

    department.delete()

    messages.success(request, 'Delete unit name = {}.'.format(department.name))

    return redirect(request.META.get('HTTP_REFERER', '/user/unit_list'))


# 刪除中隊
@permission_check(UserType.TestManager)
@require_http_methods(["GET"])
def delete_squadron(request, squadron_name):
    try:
        squadron = Squadron.objects.get(name = squadron_name)
    
    except ObjectDoesNotExist:
        raise ResourceNotFoundError('Cannot find object id = {}.'.format(squadron_name))

    squadron.delete()

    messages.success(request, 'Delete unit name = {}.'.format(squadron.name))

    return redirect(request.META.get('HTTP_REFERER', '/user/unit_list'))