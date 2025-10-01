from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, Float, Date, JSON, ARRAY, select, insert, ForeignKey
import json
import asyncio
import os
from dotenv import load_dotenv

'''
load_dotenv()

# создаем движок нашей БД, c данными из .env (echo - выводит всё)
path = "postgresql+asyncpg://" + os.getenv("DB_USER") + ":" + os.getenv("DB_PASS") + "@"\
       + os.getenv("DB_HOST") + ":" + os.getenv("DB_PORT") + "/" + os.getenv("DB_NAME")
'''
path = "postgresql+asyncpg://user:password@localhost:5432/housing_db"
engine = create_async_engine(url=path,
                             echo=True)

# создаем менеджер асинх сессий (сессия, хаха, сессия...)
new_session = async_sessionmaker(engine, expire_on_commit=False)

# базовый класс для таблички
class Base(DeclarativeBase):
    pass

class Housing(Base):
    __tablename__ = 'housing_db'

# база данных с запросом пользователя, получаемым из формы
class ClientData(Base):
    __tablename__ = 'client_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    second_name = Column(String, nullable=False)
    house_id = Column(Integer, ForeignKey('housing_db.id'), nullable=False)

    house = relationship("Housing", backref="clients")

# база данных со значениями для каждого дома
class Housing(Base):
    __tablename__ = 'housing_db'

    # Явное объявление всех колонок, как в примере с User
    id = Column(Integer, primary_key=True)
    overall_qmat = Column(Integer, nullable=False)       # Rates the overall material and finish of the house
    ground_sq = Column(Integer, nullable=False)         # Above grade (ground) living area square feet
    second_sq = Column(Integer, nullable=False)         # Second floor square feet
    possible_cars_in_garage = Column(Integer, nullable=False)        # Size of garage in car capacity
    year_built = Column(Integer, nullable=False)         # Original construction date
    first_sq = Column(Integer, nullable=False)         # First Floor square feet
    total_rooms = Column(Integer, nullable=False)      # Total rooms above grade (does not include bathrooms)
    bas_bath_count = Column(Integer, nullable=False)      # Basement full bathrooms
    overall_cond = Column(Integer, nullable=False)       # Rates the overall condition of the house
    overall_sq = Column(Integer, nullable=False)           # Lot size in square feet
    fireplaces = Column(Integer, nullable=False)           # Amount of Fireplaces

# создаем таблицу с исп. PostgreSQL
async def create_tables() -> None:
   async with engine.begin() as conn:
       await conn.run_sync(Base.metadata.create_all)

# сносим таблицу с исп. PostgreSQL
async def delete_tables() -> None:
   async with engine.begin() as conn:
       await conn.run_sync(Base.metadata.drop_all)

''' ИНТЕРФЕЙС ВЗАИМОДЕЙТСВИЯ '''

async def add_user(first_name : str, second_name : str, house_id : int) -> int:
    """
    Добавляет клиента в таблицу client_data.
    Возвращает ID нового клиента.
    """
    async with new_session() as session:
        async with session.begin():
            new_client = ClientData(
                first_name=first_name,
                second_name=second_name,
                house_id=house_id
            )
            session.add(new_client)
            await session.flush() 
            return new_client.id
        
async def add_housing(
    overall_qmat: int,
    ground_sq: int,
    second_sq: int,
    possible_cars_in_garage: int,
    year_built: int,
    first_sq: int,
    total_rooms: int,
    bas_bath_count: int,
    overall_cond: int,
    overall_sq: int,
    fireplaces: int
) -> int:
    """
    Добавляет дом в таблицу housing_db.
    Возвращает ID нового дома.
    """
    async with new_session() as session:
        async with session.begin():
            new_house = Housing(
                overall_qmat=overall_qmat,
                ground_sq=ground_sq,
                second_sq=second_sq,
                possible_cars_in_garage=possible_cars_in_garage,
                year_built=year_built,
                first_sq=first_sq,
                total_rooms=total_rooms,
                bas_bath_count=bas_bath_count,
                overall_cond=overall_cond,
                overall_sq=overall_sq,
                fireplaces=fireplaces
            )
            session.add(new_house)
            await session.flush()  
            return new_house.id

async def get_client(tag: int) -> ClientData:
    async with new_session() as session:
        result = await session.execute(select(ClientData).filter_by(id = tag))
        user = result.scalar_one_or_none()

    return user

async def get_house(tag: int) -> Housing:
    async with new_session() as session:
        result = await session.execute(select(Housing).filter_by(id = tag))
        house = result.scalar_one_or_none()

    return house


# удаление пользователя (ну сдох чувак, удалился тг). Вообще не знаю надо ли нам это, но пусть будет
async def delete_user(user_id: int) -> bool:

    async with new_session() as session:
        async with session.begin():
            user = await get_client(user_id)

            if user:
                await session.delete(user)
                await session.commit()

                return True
            else:
                return False
            
async def delete_house(user_id: int) -> bool:

    async with new_session() as session:
        async with session.begin():
            user = await get_house(user_id)

            if user:
                await session.delete(user)
                await session.commit()

                return True
            else:
                return False
            
'''
# функция для обновления данных пользователя
async def update_user(user_id: int, user_dict: dict) -> None:
    async with new_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalar_one_or_none()

            for key, value in user_dict.items():
                if key == 'history_req' or key == 'history_ans' or key == 'history_req_stat':
                    ar = user.history_req.copy()
                    for el in value:
                        ar.append(el)
                    setattr(user, key, ar)
                else:
                    setattr(user, key, value)

            await session.commit()

# SELECT *колонка* IN *таблица*
async def get_column(table_name: str, column_name: str) -> list:
    async with new_session() as session:
        # Определим соот. переданного названия таблицы и её модели внутри БД
        table_mapping = {
            'users': User,
            'salary': Salary,
            'experience': Experience,
            'towns': Towns,
            'cities': Cities,
            'employment': Employment,
            'sort': Sort,
        }

        model = table_mapping.get(table_name)

        # Запрос в таблицу model по column_name
        query = select(getattr(model, column_name))

        result = await session.execute(query)

        return [row for row in result.scalars().all()]
'''

async def start_database() -> None:
    await delete_tables()
    await create_tables()
    await add_housing()
    #await add_cities("inp.txt")
    await add_user()

    '''
    # тащим все id
    id_all = await get_column('sort','key')
    # проверяем корректность работы get_tablename 
    get_sort_checker = await get_sort('1','id')
    get_towns_checker = await get_town('1','id')
    get_salary_checker = await get_salary('1','id')
    get_experience_checker = await get_experience('1','id')
    get_employment_checker = await get_employment('1','id')
    
    print(id_all)
    print(get_sort_checker.key, get_towns_checker.key, get_salary_checker.key, get_experience_checker.key, get_employment_checker.key, sep='\n')
    '''

if __name__ == "__main__":
    asyncio.run(start_database())