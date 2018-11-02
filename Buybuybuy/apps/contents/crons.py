import os

from django.conf import settings
from django.shortcuts import render

from contents.models import ContentCategory
from utils import get_goods_category


def generate_index_html():
    # 1.查询分类数据、广告数据
    # 1.1查询分类数据

    categories =get_goods_category()
    # 1.2查询广告数据
    contents = {}
    content_categories = ContentCategory.objects.all()
    for category in content_categories:
        contents[category.key] = category.content_set.filter(status=True).order_by('sequence')


    response = render(None, 'index.html', {'categories': categories, 'contents': contents})
    html_str = response.content.decode()
    # 2.2写文件
    filename = os.path.join(settings.GENERATE_STATIC_HTML_PATH, 'index.html')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_str)

    print('OK')
