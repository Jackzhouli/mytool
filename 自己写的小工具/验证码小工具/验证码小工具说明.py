from django.shortcuts import render,HttpResponse
from app01 import models
def index(request,*args,**kwargs):
    # 获取当前URL
    print(request.path_info)

    condition = {}
    type_id = int(kwargs.get('type_id')) if kwargs.get('type_id') else None
    if type_id:
        condition['article_type_id'] = type_id

    article_list = models.Article.objects.filter(**condition)

    type_choice_list = models.Article.type_choices
    return render(
        request,
        'index.html',
        {
            'type_choice_list':type_choice_list,
            'article_list':article_list,
            'type_id':type_id
        }
    )

def login(request):
    if request.method == "GET":
        return render(request,'login.html')
    else:
        input_code = request.POST.get('code')
        session_code = request.session.get('code')
        if input_code.upper() == session_code.upper():
            pass
        else:
            pass


def check_code(request):
    from io import BytesIO
    from utils.random_check_code import rd_check_code  # 引入小工具
    img,code = rd_check_code()
    stream = BytesIO()
    img.save(stream,'png')
    request.session['code'] = code
    return HttpResponse(stream.getvalue())