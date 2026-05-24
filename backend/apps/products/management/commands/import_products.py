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
    help = '从 CSV 文件批量导入商品'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='CSV 文件路径')
        parser.add_argument('--dry-run', action='store_true', help='仅预览，不实际写入')

    def handle(self, *args, **options):
        filepath = options['csv_file']
        dry_run = options['dry_run']

        if not os.path.exists(filepath):
            self.stderr.write(self.style.ERROR(f'File not found: {filepath}'))
            return

        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            # 检查必填列
            required = {'category', 'name', 'price', 'stock'}
            missing = required - set(reader.fieldnames or [])
            if missing:
                self.stderr.write(self.style.ERROR(f'Missing columns: {missing}'))
                self.stderr.write(f'Found columns: {reader.fieldnames}')
                return

            created = 0
            skipped = 0

            for row_num, row in enumerate(reader, start=2):
                cat_name = row['category'].strip()
                name = row['name'].strip()
                price = row['price'].strip()
                stock = row['stock'].strip()
                description = row.get('description', '').strip()
                image = row.get('image', '').strip()

                if not all([cat_name, name, price, stock]):
                    self.stderr.write(f'  row {row_num}: required fields empty, skipped')
                    skipped += 1
                    continue

                # 查找或创建分类
                category, cat_created = Category.objects.get_or_create(
                    name=cat_name,
                    defaults={'name': cat_name}
                )
                if cat_created:
                    self.stdout.write(f'  [NEW] category: {cat_name}')

                try:
                    price = float(price)
                    stock = int(stock)
                except (ValueError, TypeError):
                    self.stderr.write(f'  row {row_num}: invalid price/stock, skipped')
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(f'  [preview] {name} | {cat_name} | {price} | stock={stock}')
                    created += 1
                    continue

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

        action = 'Dry-run' if dry_run else 'Import'
        self.stdout.write(self.style.SUCCESS(f'\n{action} done: {created} created, {skipped} skipped'))
