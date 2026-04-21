import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.roles import RoleModel, PermissionModel
from app.models.categories import CategoryModel
from app.models.products import ProductModel
from app.models.users import UserModel

SYNC_DATABASE_URL = settings.database_url.replace('postgresql+asyncpg', 'postgresql')
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)
SyncSession = sessionmaker(sync_engine)

def init_products_and_categories():
    with SyncSession() as db:
        categories_data = [
            {'name': 'Техника'},
            {'name': 'Мебель'},
            {'name': 'Книги'},
            {'name': 'Еда'},
            {'name': 'Одежда'},
            {'name': 'Посуда'},
        ]
    
        categories = {}
        for ctg_data in categories_data:
            ctg = db.query(CategoryModel).filter(
                CategoryModel.name == ctg_data['name']
            ).first()
            if not ctg:
                ctg = CategoryModel(**ctg_data)
                db.add(ctg)
                db.flush()
            categories[ctg_data['name']] = ctg

        products_data = [
            {
                'name': 'Соль из слёз бывших', 
                'description': 'Идеальна для маринада и пассивной агрессии. Морская, вроде бы.', 
                'price': 14.99, 
                'category_id': categories['Еда'].id, 
                'manufacturer': 'SaltyFeelings Co.', 
                'rating': 5, 
                'quantity_in_stock': 999, 
                'tags': ['еда', 'специи']
            },
            {
                'name': 'Антистрессовый йогурт YoguCalm', 
                'description': 'Меняет вкус в зависимости от твоего настроения. Не помогает, но хотя бы вкусно.', 
                'price': 4.99, 
                'category_id': categories['Еда'].id, 
                'manufacturer': 'SaltyFeelings Co.', 
                'rating': 4.1, 
                'quantity_in_stock': 999, 
                'tags': ['еда']
            },
            {
                'name': 'Антигравитационные Тапки GravityZero', 
                'description': 'Идеальны для утреннего кофе... на потолке. Теперь можно избегать очередей в туалет, просто пройдя по стене.', 
                'price': 129.99, 
                'category_id': categories['Техника'].id, 
                'manufacturer': 'Quantum Sole Industries', 
                'rating': 4.5, 
                'quantity_in_stock': 100, 
                'tags': ['техника для жизни', 'девайсы']
            },
            {
                'name': 'Чашка, которая судит тебя SipJudge', 
                'description': 'Каждый глоток сопровождается фразой: Снова кофе?', 
                'price': 18.99, 
                'category_id': categories['Посуда'].id, 
                'manufacturer': 'PassiveMug Inc.', 
                'rating': 4.5, 
                'quantity_in_stock': 200, 
                'tags': ['техника для жизни', 'девайсы', 'посуда', 'все для дома']
            },
            {
                'name': 'Носки с GPS LostNoMore', 
                'description': 'Теперь ты всегда найдёшь второй носок. Или он найдёт тебя.', 
                'price': 29.99, 
                'category_id': categories['Одежда'].id, 
                'manufacturer': 'ThinkLess', 
                'rating': 4.9, 
                'quantity_in_stock': 200, 
                'tags': ['техника для жизни', 'девайсы', 'одежда']
            },
        ]

        for pr_data in products_data:
            product = db.query(ProductModel).filter(
                ProductModel.name == pr_data['name']
            ).first()
            
            if not product:
                product = ProductModel(**pr_data)
                db.add(product)
                db.flush()
                        
        db.commit()
        print('Categories and products added successfully!')

def init_roles_and_permissions():
    with SyncSession() as db:
        permissions_data = [
            {'name': 'users:read', 'resource': 'users', 'action': 'read'},
            {'name': 'users:create', 'resource': 'users', 'action': 'create'},
            {'name': 'users:update', 'resource': 'users', 'action': 'update'},
            {'name': 'users:delete', 'resource': 'users', 'action': 'delete'},
            {'name': 'users:manage_roles', 'resource': 'users', 'action': 'manage_roles'},
            {'name': 'users:block', 'resource': 'users', 'action': 'block'},  # Блокировка пользователей
            {'name': 'users:export', 'resource': 'users', 'action': 'export'},  # Экспорт списка пользователей
            
            {'name': 'products:read', 'resource': 'products', 'action': 'read'},
            {'name': 'products:create', 'resource': 'products', 'action': 'create'},
            {'name': 'products:update', 'resource': 'products', 'action': 'update'},
            {'name': 'products:delete', 'resource': 'products', 'action': 'delete'},
            {'name': 'products:manage_stock', 'resource': 'products', 'action': 'manage_stock'},  # Управление складом
            {'name': 'products:manage_prices', 'resource': 'products', 'action': 'manage_prices'},  # Управление ценами
            {'name': 'products:import', 'resource': 'products', 'action': 'import'},  # Массовый импорт
            {'name': 'products:export', 'resource': 'products', 'action': 'export'},  # Экспорт товаров
            
            {'name': 'categories:read', 'resource': 'categories', 'action': 'read'},
            {'name': 'categories:create', 'resource': 'categories', 'action': 'create'},
            {'name': 'categories:update', 'resource': 'categories', 'action': 'update'},
            {'name': 'categories:delete', 'resource': 'categories', 'action': 'delete'},
            {'name': 'categories:reorder', 'resource': 'categories', 'action': 'reorder'},  # Изменение порядка
            
            {'name': 'orders:read', 'resource': 'orders', 'action': 'read'},
            {'name': 'orders:read_any', 'resource': 'orders', 'action': 'read_any'},  # Читать чужие заказы
            {'name': 'orders:create', 'resource': 'orders', 'action': 'create'},
            {'name': 'orders:update_status', 'resource': 'orders', 'action': 'update_status'},  # Изменение статуса
            {'name': 'orders:update_any', 'resource': 'orders', 'action': 'update_any'},  # Редактировать любые заказы
            {'name': 'orders:cancel', 'resource': 'orders', 'action': 'cancel'},  # Отмена заказов
            {'name': 'orders:refund', 'resource': 'orders', 'action': 'refund'},  # Возврат средств
            {'name': 'orders:delete', 'resource': 'orders', 'action': 'delete'},
            {'name': 'orders:export', 'resource': 'orders', 'action': 'export'},  # Экспорт заказов
            
            {'name': 'reviews:read', 'resource': 'reviews', 'action': 'read'},
            {'name': 'reviews:create', 'resource': 'reviews', 'action': 'create'},
            {'name': 'reviews:update', 'resource': 'reviews', 'action': 'update'},
            {'name': 'reviews:delete', 'resource': 'reviews', 'action': 'delete'},
            {'name': 'reviews:moderate', 'resource': 'reviews', 'action': 'moderate'},  # Модерация отзывов
            {'name': 'reviews:reply', 'resource': 'reviews', 'action': 'reply'},  # Ответ на отзывы
            
            {'name': 'discounts:read', 'resource': 'discounts', 'action': 'read'},
            {'name': 'discounts:create', 'resource': 'discounts', 'action': 'create'},
            {'name': 'discounts:update', 'resource': 'discounts', 'action': 'update'},
            {'name': 'discounts:delete', 'resource': 'discounts', 'action': 'delete'},
            
            {'name': 'shipping:read', 'resource': 'shipping', 'action': 'read'},
            {'name': 'shipping:update', 'resource': 'shipping', 'action': 'update'},  # Обновление статуса доставки
            {'name': 'shipping:methods_manage', 'resource': 'shipping', 'action': 'methods_manage'},  # Управление способами
            
            {'name': 'payments:read', 'resource': 'payments', 'action': 'read'},
            {'name': 'payments:refund', 'resource': 'payments', 'action': 'refund'},
            {'name': 'payments:methods_manage', 'resource': 'payments', 'action': 'methods_manage'},
            
            {'name': 'admin:access', 'resource': 'admin', 'action': 'access'},  # Доступ в админ-панель
            {'name': 'admin:logs', 'resource': 'admin', 'action': 'logs'},  # Просмотр логов
            {'name': 'admin:backup', 'resource': 'admin', 'action': 'backup'},  # Управление бэкапами
            {'name': 'admin:settings', 'resource': 'admin', 'action': 'settings'},  # Настройки магазина
            {'name': 'admin:analytics', 'resource': 'admin', 'action': 'analytics'},  # Аналитика и отчеты
            {'name': 'admin:clear_cache', 'resource': 'admin', 'action': 'clear_cache'},  # Очистка кеша
            
            {'name': 'content:banners', 'resource': 'content', 'action': 'banners'},
            {'name': 'content:pages', 'resource': 'content', 'action': 'pages'},  # Статические страницы
            {'name': 'content:newsletter', 'resource': 'content', 'action': 'newsletter'},  # Рассылки
        ]
        
        permissions = {}
        for perm_data in permissions_data:
            perm = db.query(PermissionModel).filter(
                PermissionModel.name == perm_data['name']
            ).first()
            if not perm:
                perm = PermissionModel(**perm_data)
                db.add(perm)
                db.flush()
            permissions[perm_data['name']] = perm
        
        roles_data = [
            {
                'name': 'customer',
                'description': 'Обычный покупатель',
                'permissions': [
                    permissions['products:read'],     # Может смотреть товары
                    permissions['orders:create'],    # Может создавать заказы
                    permissions['orders:read'],      # Может смотреть СВОИ заказы
                    permissions['reviews:create'],   # Может писать отзывы
                    permissions['reviews:update'],   # Может редактировать СВОИ отзывы
                    permissions['reviews:delete'],   # Может удалять СВОИ отзывы
                    # permissions['users:update'],     # Может редактировать СВОЙ профиль
                ]
            },
            {
                'name': 'manager',
                'description': 'Менеджер магазина',
                'permissions': [
                    permissions['products:read'],
                    permissions['products:create'],
                    permissions['products:update'],
                    permissions['orders:read'],
                    permissions['orders:read_any'],   # Может видеть все заказы
                    permissions['orders:update_status'],     # Может обновлять статус заказов
                    permissions['orders:update_any'], # Может обновлять любые заказы
                    permissions['users:read'],        # Может смотреть пользователей
                    permissions['reviews:moderate'],  # Может модерировать отзывы
                    # permissions['admin:access'],      # Доступ к админ-панели
                ]
            },
            {
                'name': 'admin',
                'description': 'Полный доступ к системе',
                'permissions': list(permissions.values())  # Все разрешения
            },
            {
                'name': 'support',
                'description': 'Служба поддержки',
                'permissions': [
                    permissions['users:read'],        # Видеть профили пользователей
                    permissions['orders:read_any'],   # Видеть все заказы
                    permissions['orders:update_status'],     # Может обновлять статус заказов
                    permissions['orders:update_any'], # Помогать с заказами
                    permissions['reviews:read'],      # Читать отзывы
                    permissions['reviews:moderate'],  # Модерировать отзывы
                    permissions['products:read'],     # Смотреть товары
                ]
            },
            {
                'name': 'content_manager',
                'description': 'Управление контентом',
                'permissions': [
                    permissions['products:create'],
                    permissions['products:update'],
                    permissions['products:delete'],
                    permissions['reviews:moderate'],
                    # permissions['admin:access'],
                ]
            },
            {
                'name': 'analyst',
                'description': 'Аналитик',
                'permissions': [
                    permissions['orders:read_any'],
                    permissions['users:read'],
                    permissions['products:read'],
                    permissions['admin:access'],  # Доступ к отчетам
                ]
            }
        ]
        
        roles = {}
        for role_data in roles_data:
            role = db.query(RoleModel).filter(
                RoleModel.name == role_data['name']
            ).first()
            
            if not role:
                role = RoleModel(
                    name=role_data['name'],
                    description=role_data['description']
                )
                db.add(role)
                db.flush()
                role.permissions = role_data['permissions']
            roles[role_data['name']] = role
        db.commit()
        print('Roles and permissions initialized successfully!')

        return roles

def init_users(roles: dict[RoleModel]):
    with SyncSession() as db:
        users_data = [
            {
                'first_name': 'Mary',
                'last_name': 'James',
                'email': 'mary@example.com',
                'password_hash': '$2b$12$bxWjs7dZ9nxxRn9PRX3uGekeKGgSGywjYzJUtd2sqo7kDhy6MQFke',
                'roles': [
                    roles['admin']
                ]
            },
            {
                'first_name': 'Bob',
                'last_name': 'Brown',
                'email': 'bob@example.com',
                'password_hash': '$2b$12$3rbtxnX6zB/ezEHdiURL2.Igu1xVLg/4xT4nK8ioHOfl7nfDP7VK2',
                'roles': [
                    roles['admin']
                ]
            },
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'password_hash': '$2b$12$SK7Vw9tyO6HKkF2J3k8x1uVL3cYk4qygRHyuKphUmAz.GhcWP7oVe',
                'roles': [
                    roles['customer']
                ]
            },
            {
                'first_name': 'Ann',
                'last_name': 'Smith',
                'email': 'ann@example.com',
                'password_hash': '$2b$12$z.8jSC2R0GjYVWkJmp9WbONJJruW.hHFPuRibyMbIcuBkSG3y8yO.',
                'roles': [
                    roles['analyst'],
                    roles['manager'],
                ]
            },
        ]

        for user_data in users_data:
            user = db.query(UserModel).filter(
                UserModel.email == user_data['email']
            ).first()
            if not user:
                user = UserModel(**user_data)
                db.add(user)
                db.flush()
                user.roles = user_data['roles']
        db.commit()
        print('Users added successfully!')

if __name__ == '__main__':
    init_products_and_categories()
    roles = init_roles_and_permissions()
    init_users(roles)