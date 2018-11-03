# from django.contrib import admin
# from . import models
#
# admin.site.register(models.GoodsCategory)
# admin.site.register(models.GoodsChannel)
# admin.site.register(models.Goods)
# admin.site.register(models.Brand)
# admin.site.register(models.GoodsSpecification)
# admin.site.register(models.SpecificationOption)
# admin.site.register(models.SKU)
# admin.site.register(models.SKUSpecification)
# admin.site.register(models.SKUImage)

from django.contrib import admin
from . import models
from celery_tasks.html.tasks import generate_static_sku_detail_html


class SKUAdmin(admin.ModelAdmin):

#admin.site.register(models.SKU, SKUAdmin) 这个放在后面
    # 定义列表页的属性(修改Iadmin后台的操作页面)
    list_display = ['id', 'name', 'price']

    # 定义编辑页的属性
    # 重写保存、删除方法
    def save_model(self, request, obj, form, change):
        # 当新增、修改对象时，这个方法会执行,检测到执行,原有动作不变,添加新的celery功能
        super().save_model(request, obj, form, change)
        # 生成静态文件
        generate_static_sku_detail_html.delay(obj.id)

    def delete_model(self, request, obj):
        # 当删除对象时，这个方法会执行
        super().delete_model(request, obj)


admin.site.register(models.GoodsCategory)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUAdmin)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage)
