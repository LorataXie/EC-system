"""
批量导入商品命令

用法:
  python manage.py import_products products.csv

CSV 文件列（必填列标 *）:
  category*    分类名称，如 "手机"
  name*        商品名称
  price*       售价
  stock*       库存
  description  描述（可选）
  image        图片路径（可选，如 products/iphone.jpg）

示例 CSV:
  category,name,price,stock,description
  手机,iPhone 15,5999,100,Apple iPhone 15 256GB
  手机,三星 S24,4999,80,三星旗舰
  电脑,MacBook Pro,12999,50,
"""
import csv
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.products.models import Category, Product


class Command(BaseCommand):
    """
    Django 管理命令：从 CSV 文件批量导入商品数据

    读取指定 CSV 文件，逐行解析商品信息，自动创建或查找对应分类，
    然后批量创建商品记录。支持 --dry-run 参数进行预览而不实际写入。

    使用场景：运营人员需要一次性导入大量商品时，准备 CSV 文件后执行此命令。
    """
    # 命令帮助文本
    help = '从 CSV 文件批量导入商品'

    def add_arguments(self, parser):
        """
        定义命令接受的命令行参数。

        csv_file: CSV 文件的路径（必选）
        --dry-run: 可选标志，启用后仅预览导入内容，不写入数据库
        """
        parser.add_argument('csv_file', type=str, help='CSV 文件路径')
        parser.add_argument('--dry-run', action='store_true', help='仅预览，不实际写入')

    def handle(self, *args, **options):
        """
        命令主逻辑：读取 CSV 文件并逐行导入商品。

        处理流程：
        1. 检查 CSV 文件是否存在
        2. 验证必填列（category, name, price, stock）是否存在
        3. 逐行解析，校验数据合法性
        4. 查找或创建分类（Category）
        5. 创建商品（Product）或预览输出
        6. 统计并输出导入结果

        dry-run 模式下不会实际写入数据库，仅输出预览信息，
        方便运营人员在正式导入前检查数据是否正确。
        """
        filepath = options['csv_file']
        dry_run = options['dry_run']

        # 检查文件是否存在，不存在则报错退出
        if not os.path.exists(filepath):
            self.stderr.write(self.style.ERROR(f'File not found: {filepath}'))
            return

        # 使用 utf-8-sig 编码打开文件，兼容带 BOM 的 UTF-8 文件
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            # 检查必填列是否都存在
            required = {'category', 'name', 'price', 'stock'}
            missing = required - set(reader.fieldnames or [])
            if missing:
                self.stderr.write(self.style.ERROR(f'Missing columns: {missing}'))
                self.stderr.write(f'Found columns: {reader.fieldnames}')
                return

            created = 0
            skipped = 0

            # 逐行处理，从第2行开始计数（第1行为表头）
            for row_num, row in enumerate(reader, start=2):
                # 读取并清洗各字段值
                cat_name = row['category'].strip()
                name = row['name'].strip()
                price = row['price'].strip()
                stock = row['stock'].strip()
                description = row.get('description', '').strip()
                image = row.get('image', '').strip()

                # 必填字段为空时跳过该行
                if not all([cat_name, name, price, stock]):
                    self.stderr.write(f'  row {row_num}: required fields empty, skipped')
                    skipped += 1
                    continue

                # 查找或创建分类：如果分类已存在则复用，否则新建
                category, cat_created = Category.objects.get_or_create(
                    name=cat_name,
                    defaults={'name': cat_name}
                )
                if cat_created:
                    self.stdout.write(f'  [NEW] category: {cat_name}')

                # 校验价格和库存的数据类型
                try:
                    price = float(price)
                    stock = int(stock)
                except (ValueError, TypeError):
                    self.stderr.write(f'  row {row_num}: invalid price/stock, skipped')
                    skipped += 1
                    continue

                # dry-run 模式：仅输出预览，不写入数据库
                if dry_run:
                    self.stdout.write(f'  [preview] {name} | {cat_name} | {price} | stock={stock}')
                    created += 1
                    continue

                # 正常模式：创建商品记录
                Product.objects.create(
                    name=name,
                    description=description,
                    price=price,
                    stock=stock,
                    category=category,
                    image=image if image else None,
                )
                self.stdout.write(f'  [OK] {name}')
                created += 1

        # 输出最终统计结果
        action = 'Dry-run' if dry_run else 'Import'
        self.stdout.write(self.style.SUCCESS(f'\n{action} done: {created} created, {skipped} skipped'))
