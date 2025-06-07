from datetime import datetime
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from database.engine import session_maker
from database.orm import orm_get_posts_with_media_details_by_status

months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
              'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']

def month(date):
    return f'{months[int(date) - 1]}'


async def calendar_month():
    current_year=str(datetime.now().year)+' год'
    select_month=InlineKeyboardBuilder()
    select_month.add(InlineKeyboardButton(text=current_year, callback_data='year'))
    for mont in months:
        select_month.add(InlineKeyboardButton(text=mont, callback_data=f'{mont}'))
    return select_month.adjust(1,3).as_markup()


async def calendar_day(mont):
    mont=str(months.index(mont)+1)
    days_in_month_dict = {'1': 31, '2': 28,
                          '3': 31, '4': 30,
                          '5': 31, '6': 30,
                          '7': 31, '8': 31,
                          '9': 30, '10': 31,
                          '11': 30, '12': 31}
    weekdays_dict={0:'пн', 1:'вт',
                   2:'ср', 3:'чт',
                   4:'пт', 5:'сб',
                   6:'вс'}
    select_days=InlineKeyboardBuilder()
    len_month=days_in_month_dict[mont]
    current_year = str(datetime.now().year) + ' год'
    current_month=month(mont)
    datetime(int(datetime.now().year), int(mont), 1).weekday()
    select_days.add(InlineKeyboardButton(text=current_year, callback_data='year'))
    select_days.add(InlineKeyboardButton(text=current_month, callback_data='month'))
    for i in range(1,8):
        week_day=datetime(int(datetime.now().year), int(mont), i).weekday()
        select_days.add(InlineKeyboardButton(text=weekdays_dict[week_day], callback_data='weekday'))
    for days in range(1, len_month+1):
        select_days.add(InlineKeyboardButton(text=f'{days}', callback_data=f'{days}'))
    select_days.add((InlineKeyboardButton(text='назад', callback_data='назад')))
    return select_days.adjust(2,7).as_markup()


async def calendar_time(data):
    hours=['00', '01', '02', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
    minutes=['00', '30']
    async with session_maker() as session:
        posts = await orm_get_posts_with_media_details_by_status(session, 'Одобрено')
        time_post_list = []
        if posts:
            for i in posts:
                post = i["post"]
                post_time = post.publish_time
                post_date = str(post.publish_date).replace('-', '.')[5:].split('.')
                post_date = post_date[1] + '.' + post_date[0]
                if post_date == data:
                    time_post_list.append(post_time)
        select_time=InlineKeyboardBuilder()
        for hour in hours:
            for minute in minutes:
                time=hour+':'+minute
                if time not in time_post_list:
                    select_time.add(InlineKeyboardButton(text=time, callback_data=f'{time}'))
        select_time.add((InlineKeyboardButton(text='назад', callback_data='назад')))
    return select_time.adjust(5).as_markup()