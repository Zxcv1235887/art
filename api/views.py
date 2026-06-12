from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Student, Registration,User,Makeup, Invoice, Artwork,Attendance
from datetime import date, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string

@api_view(['GET'])
def get_students(request):
    students = Student.objects.all()
    data = [{'id': s.id, 'name': s.name, 'term': s.term, 'done': s.done} for s in students]
    return Response(data)

@api_view(['GET'])
def get_student(request, pk):
    try:
        s = Student.objects.get(id=pk)
        return Response({'id': s.id, 'name': s.name, 'term': s.term, 'done': s.done})
    except Student.DoesNotExist:
        return Response({'error': '找不到學生'}, status=404)

@api_view(['POST'])
def add_student(request):
    s = Student.objects.create(
        name=request.data['name'],
        term=request.data['term'],
        done=request.data.get('done', 0)
    )
    return Response({'id': s.id, 'name': s.name, 'term': s.term, 'done': s.done})

@api_view(['PUT'])
def update_student(request, pk):
    try:
        s = Student.objects.get(id=pk)
        s.name = request.data.get('name', s.name)
        s.term = request.data.get('term', s.term)
        s.save()
        return Response({'id': s.id, 'name': s.name, 'term': s.term, 'done': s.done})
    except Student.DoesNotExist:
        return Response({'error': '找不到學生'}, status=404)

@api_view(['DELETE'])
def delete_student(request, pk):
    try:
        s = Student.objects.get(id=pk)
        s.delete()
        return Response({'message': '已刪除'})
    except Student.DoesNotExist:
        return Response({'error': '找不到學生'}, status=404)

@api_view(['POST'])
def register(request):
    data = request.data
    r = Registration.objects.create(
        student_name=data['student_name'],
        birth_date=data['birth_date'],
        phone=data['phone'],
        email=data.get('email', ''),
        address=data.get('address', ''),
        parent_name=data['parent_name'],
        parent_phone=data['parent_phone'],
        parent_email=data.get('parent_email', ''),
        course=data['course'],
        day=data['day'],
        time_slot=data['time_slot'],
    )
    return Response({'id': r.id, 'message': '報名成功'})

@api_view(['GET'])
def get_registrations(request):
    regs = Registration.objects.all().order_by('-created_at')
    data = [{
        'id': r.id,
        'student_name': r.student_name,
        'course': r.get_course_display(),
        'day': r.get_day_display(),
        'time_slot': r.time_slot,
        'parent_name': r.parent_name,
        'parent_phone': r.parent_phone,
        'created_at': r.created_at.strftime('%Y-%m-%d'),
    } for r in regs]
    return Response(data)

def get_tw_holidays(year):
    holidays = {
        2026: [
            date(2026, 1, 1),
            date(2026, 2, 16),
            date(2026, 2, 17),
            date(2026, 2, 18),
            date(2026, 2, 19),
            date(2026, 2, 20),
            date(2026, 4, 4),
            date(2026, 4, 5),
            date(2026, 5, 1),
            date(2026, 5, 31),
            date(2026, 9, 19),
            date(2026, 10, 10),
        ]
    }
    return holidays.get(year, [])

def next_class_date(start_date):
    holidays = get_tw_holidays(start_date.year)
    next_date = start_date
    while next_date in holidays:
        next_date += timedelta(weeks=1)
    return next_date

@api_view(['GET'])
def check_holiday(request):
    date_str = request.GET.get('date')
    if not date_str:
        return Response({'error': '請提供日期'}, status=400)
    try:
        check_date = date.fromisoformat(date_str)
        holidays = get_tw_holidays(check_date.year)
        is_holiday = check_date in holidays
        next_date = next_class_date(check_date) if is_holiday else check_date
        return Response({
            'date': date_str,
            'is_holiday': is_holiday,
            'next_class_date': next_date.isoformat(),
            'message': f'遇到國定假日，上課日期延至 {next_date}' if is_holiday else '正常上課'
        })
    except ValueError:
        return Response({'error': '日期格式錯誤'}, status=400)
    
@api_view(['GET'])
def get_students(request):
    students = Student.objects.all()
    data = [{
        'id': s.id,
        'name': s.name,
        'student_class': s.get_student_class_display(),
        'term': s.term,
        'done': s.done,
        'parent_email': s.parent_email
    } for s in students]
    return Response(data)

@api_view(['GET'])
def get_student(request, pk):
    try:
        s = Student.objects.get(id=pk)
        return Response({
            'id': s.id,
            'name': s.name,
            'student_class': s.get_student_class_display(),
            'term': s.term,
            'done': s.done,
            'parent_email': s.parent_email
        })
    except Student.DoesNotExist:
        return Response({'error': '找不到學生'}, status=404)

@api_view(['POST'])
def add_student(request):
    s = Student.objects.create(
        name=request.data['name'],
        student_class=request.data.get('student_class', 'thu'),
        term=request.data['term'],
        done=request.data.get('done', 0),
        parent_email=request.data.get('parent_email', '')
    )
    return Response({'id': s.id, 'name': s.name})

@api_view(['PUT'])
def update_student(request, pk):
    try:
        s = Student.objects.get(id=pk)
        s.name = request.data.get('name', s.name)
        s.student_class = request.data.get('student_class', s.student_class)
        s.term = request.data.get('term', s.term)
        s.parent_email = request.data.get('parent_email', s.parent_email)
        s.save()
        return Response({'id': s.id, 'name': s.name})
    except Student.DoesNotExist:
        return Response({'error': '找不到學生'}, status=404)
    
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = User.objects.get(username=username, password=password)
        data = {
            'id': user.id,
            'username': user.username,
            'role': user.role,
        }
        if user.student:
            data['student_id'] = user.student.id
            data['student_name'] = user.student.name
        return Response(data)
    except User.DoesNotExist:
        return Response({'error': '帳號或密碼錯誤'}, status=401)

@api_view(['GET'])
def get_makeups(request):
    makeups = Makeup.objects.all().order_by('-created_at')
    data = [{
        'id': m.id,
        'student_id': m.student.id,
        'student_name': m.student.name,
        'student_class': m.student.get_student_class_display(),
        'term': m.student.term,
        'absent_date': m.absent_date.strftime('%Y年%m月%d日'),
        'class_number': m.class_number,
        'status': m.status,
        'status_display': m.get_status_display(),
        'makeup_date': m.makeup_date.strftime('%Y年%m月%d日') if m.makeup_date else None,
        'makeup_time': m.makeup_time.strftime('%H:%M') if m.makeup_time else None,
        'teacher': m.teacher,
        'note': m.note,
    } for m in makeups]
    return Response(data)

@api_view(['POST'])
def schedule_makeup(request, pk):
    try:
        m = Makeup.objects.get(id=pk)
        m.makeup_date = request.data.get('makeup_date')
        m.makeup_time = request.data.get('makeup_time')
        m.teacher = request.data.get('teacher', '')
        m.status = 'scheduled'
        m.save()
        return Response({'message': '補課已排定'})
    except Makeup.DoesNotExist:
        return Response({'error': '找不到記錄'}, status=404)

@api_view(['POST'])
def complete_makeup(request, pk):
    try:
        m = Makeup.objects.get(id=pk)
        m.status = 'done'
        m.save()
        return Response({'message': '補課完成'})
    except Makeup.DoesNotExist:
        return Response({'error': '找不到記錄'}, status=404)

@api_view(['POST'])
def add_makeup(request):
    student_id = request.data.get('student_id')
    try:
        student = Student.objects.get(id=student_id)
        m = Makeup.objects.create(
            student=student,
            absent_date=request.data.get('absent_date'),
            class_number=request.data.get('class_number', 0),
            status='pending'
        )
        return Response({'id': m.id, 'message': '補課記錄已建立'})
    except Student.DoesNotExist:
        return Response({'error': '找不到學生'}, status=404)

@api_view(['GET'])
def get_invoices(request):
    invoices = Invoice.objects.all().order_by('-sent_date')
    data = [{
        'id': i.id,
        'student_id': i.student.id,
        'student_name': i.student.name,
        'term': i.term,
        'sent_date': i.sent_date.strftime('%m月%d日'),
        'original_amount': i.original_amount,
        'discount': i.discount,
        'final_amount': i.final_amount,
        'status': i.status,
        'status_display': i.get_status_display(),
    } for i in invoices]
    return Response(data)

@api_view(['POST'])
def confirm_invoice(request, pk):
    try:
        i = Invoice.objects.get(id=pk)
        i.status = 'confirmed'
        i.save()
        return Response({'message': '已確認'})
    except Invoice.DoesNotExist:
        return Response({'error': '找不到帳單'}, status=404)

@api_view(['POST'])
def add_invoice(request):
    student_id = request.data.get('student_id')
    try:
        student = Student.objects.get(id=student_id)
        discount = request.data.get('discount', False)
        original = 3600
        final = int(original * 0.9) if discount else original
        i = Invoice.objects.create(
            student=student,
            term=request.data.get('term', student.term),
            sent_date=request.data.get('sent_date'),
            original_amount=original,
            discount=discount,
            final_amount=final,
            status='pending'
        )
        return Response({'id': i.id, 'message': '帳單已建立'})
    except Student.DoesNotExist:
        return Response({'error': '找不到學生'}, status=404)

from .models import Student, Registration, User, Makeup, Invoice, Artwork

@api_view(['GET'])
def get_artworks(request):
    artworks = Artwork.objects.all().order_by('-uploaded_at')
    data = [{
        'id': a.id,
        'student_id': a.student.id,
        'student_name': a.student.name,
        'title': a.title,
        'caption': a.caption,
        'notify_parent': a.notify_parent,
        'notified': a.notified,
        'uploaded_at': a.uploaded_at.strftime('%m月%d日 %H:%M'),
        'image_url': request.build_absolute_uri(a.image.url) if a.image else None,
    } for a in artworks]
    return Response(data)

@api_view(['GET'])
def get_student_artworks(request, pk):
    artworks = Artwork.objects.filter(student_id=pk).order_by('-uploaded_at')
    data = [{
        'id': a.id,
        'title': a.title,
        'caption': a.caption,
        'uploaded_at': a.uploaded_at.strftime('%Y年%m月%d日'),
        'image_url': request.build_absolute_uri(a.image.url) if a.image else None,
    } for a in artworks]
    return Response(data)

@api_view(['POST'])
def upload_artwork(request):
    student_id = request.data.get('student_id')
    try:
        student = Student.objects.get(id=student_id)
        artwork = Artwork.objects.create(
            student=student,
            title=request.data.get('title', ''),
            caption=request.data.get('caption', ''),
            notify_parent=request.data.get('notify_parent', 'true') == 'true',
            image=request.FILES.get('image'),
        )
        return Response({'id': artwork.id, 'message': '上傳成功'})
    except Student.DoesNotExist:
        return Response({'error': '找不到學生'}, status=404)

@api_view(['POST'])
def notify_artwork(request, pk):
    try:
        a = Artwork.objects.get(id=pk)
        a.notified = True
        a.save()
        return Response({'message': '已通知家長'})
    except Artwork.DoesNotExist:
        return Response({'error': '找不到作品'}, status=404)

@api_view(['POST'])
def submit_attendance(request):
    records = request.data.get('records', [])
    date = request.data.get('date')

    for record in records:
        student_id = record.get('student_id')
        status = record.get('status')
        class_number = record.get('class_number', 0)

        try:
            student = Student.objects.get(id=student_id)

            Attendance.objects.update_or_create(
                student=student,
                date=date,
                defaults={
                    'status': status,
                    'class_number': class_number,
                }
            )

            if status == 'present':
                student.done += 1
                student.save()
                if student.done == 11:
                    discount = False
                    Invoice.objects.create(
                        student=student,
                        term=student.term,
                        sent_date=date,
                        discount=discount,
                        final_amount=3600,
                        status='pending'
                    )

            elif status == 'absent':
                student.done += 1
                student.save()
                Makeup.objects.create(
                    student=student,
                    absent_date=date,
                    class_number=class_number,
                    status='pending'
                )
                if student.parent_email:
                    try:
                        send_mail(
                            f'【繪苑藝廊】{student.name} 請假通知及補課安排',
                            f'親愛的家長您好，\n\n{student.name} 同學於 {date} 請假，我們將盡快安排補課時間。\n\n請假日期：{date}\n第幾堂：第 {class_number} 堂\n\n我們會盡快與您聯繫確認補課時間，請保持電話暢通。\n\n繪苑藝廊 敬上',
                            None,
                            [student.parent_email],
                            fail_silently=True,
                        )
                    except:
                        pass

        except Student.DoesNotExist:
            pass

    return Response({'message': '點名完成'})

@api_view(['GET'])
def get_attendance(request):
    date = request.GET.get('date')
    if date:
        records = Attendance.objects.filter(date=date)
    else:
        records = Attendance.objects.all().order_by('-date')
    
    data = [{
        'id': r.id,
        'student_id': r.student.id,
        'student_name': r.student.name,
        'date': r.date.strftime('%Y-%m-%d'),
        'class_number': r.class_number,
        'status': r.status,
        'status_display': r.get_status_display(),
    } for r in records]
    return Response(data)

@api_view(['DELETE'])
def delete_invoice(request, pk):
    try:
        i = Invoice.objects.get(id=pk)
        i.delete()
        return Response({'message': '已刪除'})
    except Invoice.DoesNotExist:
        return Response({'error': '找不到帳單'}, status=404)

@api_view(['DELETE'])
def delete_artwork(request, pk):
    try:
        a = Artwork.objects.get(id=pk)
        a.delete()
        return Response({'message': '已刪除'})
    except Artwork.DoesNotExist:
        return Response({'error': '找不到作品'}, status=404)

@api_view(['POST'])
def send_invoice_email(request, pk):
    try:
        inv = Invoice.objects.get(id=pk)
        student = inv.student
        parent_email = student.parent_email

        if not parent_email:
            return Response({'error': '家長Email未設定'}, status=400)

        subject = f'【藝廊】第 {inv.term} 期課程費用通知'
        message = f"""
親愛的家長您好，

{student.name} 同學的第 {inv.term} 期課程費用如下：

課程期別：第 {inv.term} 期（共12堂）
課程單價：NT$ 300 / 堂
{'全勤優惠：9折' if inv.discount else ''}
實收金額：NT$ {inv.final_amount:,}

{'🎉 恭喜達成全勤！本期享有9折優惠。' if inv.discount else '💡 下期若12堂全部正常出席，可享有9折優惠（節省 NT$ 360）。'}

請於收到通知後盡快確認繳費意願。

藝廊 敬上
        """

        send_mail(
            subject,
            message,
            None,
            [parent_email],
            fail_silently=False,
        )

        return Response({'message': f'帳單Email已寄送至 {parent_email}'})

    except Invoice.DoesNotExist:
        return Response({'error': '找不到帳單'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def send_artwork_email(request, pk):
    try:
        artwork = Artwork.objects.get(id=pk)
        student = artwork.student
        parent_email = student.parent_email

        if not parent_email:
            return Response({'error': '家長Email未設定'}, status=400)

        subject = f'【藝廊】{student.name} 有新作品上傳！'
        message = f"""
親愛的家長您好，

{student.name} 同學今天上課完成了新作品！

作品名稱：{artwork.title or '未命名'}
上傳時間：{artwork.uploaded_at.strftime('%Y年%m月%d日 %H:%M')}
{'老師備註：' + artwork.caption if artwork.caption else ''}

請登入系統查看孩子的作品。

藝廊 敬上
        """

        send_mail(
            subject,
            message,
            None,
            [parent_email],
            fail_silently=False,
        )

        artwork.notified = True
        artwork.save()

        return Response({'message': f'通知Email已寄送至 {parent_email}'})

    except Artwork.DoesNotExist:
        return Response({'error': '找不到作品'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def contact_makeup(request, pk):
    try:
        m = Makeup.objects.get(id=pk)
        student = m.student
        parent_email = student.parent_email
        options = request.data.get('options', '')
        note = request.data.get('note', '')

        if not parent_email:
            return Response({'error': '家長Email未設定'}, status=400)

        subject = f'【藝廊】{student.name} 補課時間確認'
        message = f"""
親愛的家長您好，

關於 {student.name} 同學於 {m.absent_date} 的請假，
我們提供以下補課備選時間，請您確認方便的時段：

{options if options else '請來電洽詢補課時間'}

{'備註：' + note if note else ''}

請回覆此信或來電確認，謝謝。

藝廊 敬上
        """

        send_mail(
            subject,
            message,
            None,
            [parent_email],
            fail_silently=False,
        )

        m.status = 'waiting'
        m.save()

        return Response({'message': f'補課確認信已寄送至 {parent_email}'})

    except Makeup.DoesNotExist:
        return Response({'error': '找不到補課記錄'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)