# EC商城电商系统 — 项目验收总结

## 一、项目概述

基于 **Django + Vue 3** 的全栈电子商务平台，支持普通用户商品浏览、购物车、下单、评价，以及管理员后台数据分析、用户管理、商品管理、优惠券发放等功能。

---

## 二、技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Django | 5.1 |
| API 框架 | Django REST Framework | 3.17 |
| 认证 | djangorestframework-simplejwt (JWT) | 5.5 |
| 数据库 | MySQL | 8.0 (utf8mb4) |
| 分类树 | django-mptt | 0.18 |
| API 文档 | drf-spectacular (Swagger) | 0.29 |
| 前端框架 | Vue 3 | 3.5 |
| UI 组件 | Element Plus | 2.14 |
| 图表 | ECharts + vue-echarts | 5.6 |
| 状态管理 | Pinia | 2.3 |
| 构建工具 | Vite | 8.0 |

---

## 三、系统架构

```
frontend (Vue 3 :5173)
    ↓ HTTP/Axios
backend (Django :8000)
    ├── config/          # 项目配置 (settings/urls)
    └── apps/
        ├── core/        # 基础设施 (BaseModel/分页/权限/异常/响应封装)
        ├── accounts/    # 用户 + 地址 + JWT认证 + 邮箱验证码 + 操作日志
        ├── products/    # 商品分类(MPTT树) + 商品 + 搜索筛选 + CSV导入
        ├── cart/        # 购物车
        ├── orders/      # 订单 + 状态流转 + 物流 + 退款 + 数据分析
        ├── coupons/     # 优惠券(满减) + 筛选用户发放
        └── reviews/     # 商品评价(已完成订单可评) + 自动更新评分
    ↓ ORM
MySQL (ecommerce 数据库)
```

---

## 四、数据库设计

### 11 张业务表（+ 系统表）

| 表名 | 模型 | 字段数 | 说明 |
|------|------|--------|------|
| `accounts_user` | User | 15 | 邮箱/手机/密码/年龄/性别/是否VIP |
| `accounts_address` | Address | 13 | 收货地址(UUID主键/省市区/邮编/默认) |
| `accounts_operation_log` | OperationLog | 5 | 用户操作日志 |
| `products_category` | Category | 9 | MPTT多级分类树 |
| `products_product` | Product | 11 | 商品(名称/描述/价格/库存/销量/评分/图片) |
| `cart_cart` | Cart | 4 | 购物车(用户1:1) |
| `cart_cart_item` | CartItem | 6 | 购物车明细(商品/数量) |
| `orders_order` | Order | 12 | 订单(金额/优惠券/地址快照/状态/物流/退款) |
| `orders_order_item` | OrderItem | 7 | 订单明细(冻结商品单价) |
| `reviews_review` | Review | 9 | 商品评价(评分/评论/图片) |
| `coupons_coupon` | Coupon | 10 | 优惠券(满减/时效/状态) |

**设计特点**：
- 所有表使用 **UUID 主键**（除 User 外），避免自增 ID 暴露数据量
- 订单明细**冻结商品单价**（`OrderItem.price`），商品后续改价不影响历史订单
- 订单**地址快照**（`address_snapshot` JSON），地址修改不影响历史订单
- 用户密码使用 Django 内置 **PBKDF2 + SHA256** 加密
- 字符集 **utf8mb4**，支持中文和 Emoji

---

## 五、API 接口

### 5.1 接口总览

| 模块 | 端点数 | 说明 |
|------|--------|------|
| Auth | 8 | 注册/登录/登出/刷新/改密码/重置密码/发送验证码 |
| Profile | 2 | 个人信息/消费统计 |
| Address | 7 | CRUD + 搜索 + 设默认 |
| Products | 10 | 分类树/商品列表筛选/商品详情/管理员CRUD |
| Cart | 4 | 购物车CRUD + 批量删除 |
| Orders | 17 | 下单/支付/取消/收货/退款 + 管理员发货/完成 + 数据分析 |
| Reviews | 7 | CRUD + 管理员审核 |
| Coupons | 7 | 我的优惠券/管理员CRUD/批量发放 |
| **合计** | **62** | |

### 5.2 关键 API

| 功能 | 方法 | 端点 |
|------|------|------|
| 邮箱验证码注册 | POST | `/api/v1/auth/register` |
| 登录(邮箱或手机) | POST | `/api/v1/auth/login` |
| 邮箱找回密码 | POST | `/api/v1/auth/password/reset` |
| 商品搜索/筛选/排序 | GET | `/api/v1/products?keyword=&category=&min_price=&max_price=&sort=` |
| 加入购物车 | POST | `/api/v1/cart/items` |
| 下单 | POST | `/api/v1/orders/place` |
| 支付(自动发货) | POST | `/api/v1/orders/{id}/pay` |
| 确认收货 | POST | `/api/v1/orders/{id}/confirm-delivery` |
| 申请退款 | POST | `/api/v1/orders/{id}/refund` |
| 提交评价 | POST | `/api/v1/reviews` |
| 仪表盘KPI | GET | `/api/v1/admin/analytics/overview` |
| CSV批量导入商品 | CMD | `python manage.py import_products file.csv` |

### 5.3 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 5.4 认证方案

- JWT 双 Token：Access Token 30 分钟 + Refresh Token 7 天
- Refresh Token 轮转 + 黑名单
- 前端 Axios 拦截器自动刷新 Token

---

## 六、前端页面

### 6.1 页面清单（24 页）

**用户端（13 页）**：

| 页面 | 路由 | 功能 |
|------|------|------|
| 首页 | `/` | 分类导航 + 热门商品 |
| 商品列表 | `/products` | 关键词/分类/价格/排序筛选 |
| 商品详情 | `/products/:id` | 图片/价格/库存/评价列表 |
| 购物车 | `/cart` | 修改数量/删除/批量删除 |
| 结算 | `/checkout` | 选择地址/优惠券/提交订单 |
| 登录 | `/login` | 邮箱+密码 / 手机+密码 |
| 注册 | `/register` | 邮箱验证码注册 |
| 忘记密码 | `/reset-password` | 邮箱验证码重置 |
| 个人信息 | `/profile` | 修改资料 |
| 地址管理 | `/profile/addresses` | CRUD + 地图搜索 + 默认 |
| 消费统计 | `/profile/statistics` | ECharts趋势图/类别饼图/CSV导出 |
| 我的订单 | `/orders` | 状态筛选/订单卡片 |
| 订单详情 | `/orders/:id` | 物流/金额/评价 |

**管理员端（11 页）**：

| 页面 | 路由 | 功能 |
|------|------|------|
| 仪表盘 | `/admin` | KPI卡片/销售趋势图/最近订单 |
| 数据分析 | `/admin/analytics` | 销售额/热销商品/趋势 |
| 用户管理 | `/admin/users` | 列表/VIP切换/启用禁用 |
| 用户详情 | `/admin/users/:id` | 信息/消费总额/操作日志 |
| 商品管理 | `/admin/products` | CRUD/图片上传 |
| 分类管理 | `/admin/categories` | 多级分类/树形编辑 |
| 订单管理 | `/admin/orders` | 状态筛选/完成/退款处理 |
| 优惠券管理 | `/admin/coupons` | 创建/删除/筛选用户批量发放 |

### 6.2 组件清单（12 个可复用组件）

ProductCard、ProductFilter、ProductImages、OrderCard、OrderItemTable、OrderStatusBadge、OrderStatusTimeline、CartItemRow、CartSummary、AddressCard、AddressForm、AppPagination

### 6.3 状态管理（4 个 Pinia Store）

authStore、cartStore、productStore、orderStore

---

## 七、功能完成度对照表

### 7.1 用户功能（需求 2.1）

| 功能 | 状态 | 说明 |
|------|------|------|
| 邮箱验证码注册 | ✅ | QQ邮箱SMTP发送 |
| 邮箱+密码登录 | ✅ | |
| 手机号+密码登录 | ✅ | |
| 修改密码 | ✅ | |
| 忘记密码(邮箱验证码) | ✅ | |
| 个人信息管理 | ✅ | 姓名/性别/年龄/手机 |
| 地址CRUD+默认 | ✅ | 省市区级联+地图搜索 |
| 消费统计 | ✅ | 日/周/月趋势图+类别饼图+CSV导出 |
| 商品搜索筛选 | ✅ | 关键词/分类/价格/销量/新品/评分 |
| 商品详情 | ✅ | 图片/描述/价格/库存/评价 |
| 购物车 | ✅ | 添加/修改/删除/批量删除/总价 |
| 优惠券应用 | ✅ | 结算页选择/自动计算折扣 |
| 下单 | ✅ | 自动扣库存+冻结单价 |
| 订单状态流转 | ✅ | 待支付→已支付→已发货→已送达→已完成 |
| 取消订单 | ✅ | 恢复库存 |
| 确认收货 | ✅ | |
| 申请退款 | ✅ | |
| 商品图文评价 | ✅ | 星级+文字+图片(可选) |
| 第三方登录 | ❌ | 需企业资质 |

### 7.2 管理员功能（需求 2.2）

| 功能 | 状态 | 说明 |
|------|------|------|
| 用户列表 | ✅ | 邮箱/用户名/消费总额/注册时间 |
| 权限管控 | ✅ | 启用禁用/VIP切换 |
| 操作日志 | ✅ | 记录密码修改+管理员操作 |
| 商品管理CRUD | ✅ | 含图片上传 |
| 多级分类管理 | ✅ | MPTT树形结构 |
| 优惠券创建 | ✅ | 满减类型 |
| 筛选用户发放优惠券 | ✅ | VIP/消费额/有过购买 |
| 订单筛选 | ✅ | 状态/用户ID/日期 |
| 退换货处理 | ✅ | 同意退款+恢复库存/拒绝 |
| 手动标记完成 | ✅ | 已送达→已完成 |
| 仪表盘KPI | ✅ | 销售额/订单/用户/商品 |
| 销售趋势图 | ✅ | ECharts折线图 |
| 热销商品 | ✅ | 按销量排行 |
| 数据分析 | ✅ | 趋势/热销/最近订单 |
| 批量导入商品 | ✅ | CSV命令行导入 |

---

## 八、订单状态流转

```
用户下单 → [待支付] ──支付(自动发货+生成物流单号)──→ [已发货]
   │                                                    │
   └──取消──→ [已取消](恢复库存)                    确认收货
                                                        │
                                                    [已完成] ──评价
                                                    
申请退款: [已支付/已发货] ──申请──→ 管理员同意 ──→ [已取消+退款+恢复库存]
                                    管理员拒绝 ──→ 拒绝退款
```

---

## 九、项目规模统计

| 指标 | 数量 |
|------|------|
| Django App | 7 个 |
| 数据库表 | 11 张 |
| API 端点 | 62 个 |
| Python 源文件 | 58 个 |
| Vue 页面 | 24 个 |
| Vue 组件 | 12 个 |
| Pinia Store | 4 个 |
| 布局 | 3 套 |
| 代码总行数 | ~10,000 行 |

---

## 十、启动说明

```bash
# 后端
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# 前端
cd frontend
npm install
npm run dev
```

- API 文档：`http://127.0.0.1:8000/api/v1/docs/`
- Django Admin：`http://127.0.0.1:8000/admin/`
- 前端：`http://localhost:5173`

**测试账号**：
- 管理员：`admin@example.com` / `admin123456`
- 普通用户：`test@example.com` / `test123456`
