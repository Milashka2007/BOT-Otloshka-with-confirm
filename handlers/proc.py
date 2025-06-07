from database.orm import orm_get_expenses_by_month, orm_get_sell_by_month, orm_get_all_sale, orm_get_all_expenses, \
    orm_get_investors
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

async def month_income(session: AsyncSession):
    rashody=0
    for i in await orm_get_expenses_by_month(session, datetime.now().year, datetime.now().month):
        rashody+=i.price

    doxody=0
    prodali={}
    for i in await orm_get_sell_by_month(session, datetime.now().year, datetime.now().month):
        doxody+=i.price
        if i.name in prodali:
            prodali[i.name]+=1
        else:
            prodali[i.name]=1
    pribl=doxody-rashody
    msg=f'Чистая прибль в этом месяце составила {pribl} рублей\n'
    for k,v in prodali.items():
        msg+=f'{k} продали {v} раза\n'
    return msg

async def all_income(session: AsyncSession):
    rashody = 0
    doxody = 0
    prodali = {}
    for i in await orm_get_all_sale(session):
        doxody += i.price
        if i.name in prodali:
            prodali[i.name]+=1
        else:
            prodali[i.name]=1
    for i in await orm_get_all_expenses(session):
        rashody += i.price

    pribl=doxody-rashody
    msg = f'Чистая прибль за все время составила {pribl} рублей\n'
    for k, v in prodali.items():
        msg += f'{k} продали {v} раза\n'
    return msg

async def vyplaty(session: AsyncSession):
    rashody = 0
    for i in await orm_get_expenses_by_month(session, datetime.now().year, datetime.now().month):
        rashody += i.price

    doxody = 0
    prodali = {}
    for i in await orm_get_sell_by_month(session, datetime.now().year, datetime.now().month):
        doxody += i.price
        if i.name in prodali:
            prodali[i.name] += 1
        else:
            prodali[i.name] = 1
    pribl = doxody - rashody

    msg='Выплаты каждому инвестору составляют:\n'
    count=1
    for i in await orm_get_investors(session):
        msg+=(f'{count}. Вклад инвестора {i.name} составляет {i.vklad} рублей\n'
              f'Выплата составляет {i.procent_ot_dohoda}% дохода, что составляет {pribl*i.procent_ot_dohoda//100} рублей\n')
        count+=1
    return msg



