# import os
# from collections import OrderedDict
#
# from django.conf import settings
#
# from .models import ContentCategory, Content
# from goods.models import GoodsCategory, GoodsChannel
# from django.shortcuts import render
#
#
# def generate_index_html():
#     # 1.查询分类数据、广告数据
#     # 1.1查询分类数据
#     '''
#     {
#         组编号（同频道）:{
#             一级分类channels：[]
#             二级分类sub_cats：[]
#         }
#     }
#     如：
#     {
#         1:{
#             channels:[
#                 {手机},{相机},{数码}
#             ],
#             sub_cats:[二级分类]
#         },
#         2:{
#             channels:[
#                 {电脑},{办公},{家用电器}
#             ],
#             sub_cats:[二级分类]
#         },
#         ....
#     }
#     '''
#     categories = OrderedDict()
#     channels = GoodsChannel.objects.order_by('group_id', 'sequence')
#     for channel in channels:
#         # channel.group_id===>组编号
#         # channel.category====>一级分类
#         # channel.url=========>一级分类的链接
#         if channel.group_id not in categories:
#             categories[channel.group_id] = {'channels': [], 'sub_cats': []}
#         # 添加一级分类
#         categories[channel.group_id]['channels'].append({
#             'id': channel.id,
#             'name': channel.category.name,
#             'url': channel.url
#         })
#         # 添加二级分类
#         sub_cats = channel.category.goodscategory_set.all()
#         # 添加三级分类
#         for sub in sub_cats:
#             sub.sub_cats = sub.goodscategory_set.all()
#             categories[channel.group_id]['sub_cats'].append(sub)
#
#     # 1.2查询广告数据
#     contents = {}
#     content_categories = ContentCategory.objects.all()
#     for category in content_categories:
#         contents[category.key] = category.content_set.filter(status=True).order_by('sequence')
#
#     # 2.生成html标签，写到html文件中
#     # 2.1生成html字符串
#     response = render(None, 'index.html', {'categories': categories, 'contents': contents})
#     html_str = response.content.decode()
#     # 2.2写文件
#     filename = os.path.join(settings.GENERATE_STATIC_HTML_PATH, 'index.html')
#     with open(filename, 'w', encoding='utf-8') as f:
#         f.write(html_str)
#
#     print('OK')
#
# import os
# from collections import OrderedDict
#
# from django.conf import settings
#
# from .models import ContentCategory, Content
# from goods.models import GoodsCategory, GoodsChannel
# from django.shortcuts import render
# from utils.goods_category import get_goods_category
#
#
# def generate_index_html():
#     # 1.查询分类数据、广告数据
#     # 1.1查询分类数据
#     categories = get_goods_category()
#     # 1.2查询广告数据
#     contents = {}
#     content_categories = ContentCategory.objects.all()
#     for category in content_categories:
#         contents[category.key] = category.content_set.filter(status=True).order_by('sequence')
#
#     # 2.生成html标签，写到html文件中
#     # 2.1生成html字符串
#     response = render(None, 'index.html', {'categories': categories, 'contents': contents})
#     html_str = response.content.decode()
#     # 2.2写文件
#     filename = os.path.join(settings.GENERATE_STATIC_HTML_PATH, 'index.html')
#     with open(filename, 'w', encoding='utf-8') as f:
#         f.write(html_str)
#
#     print('OK')