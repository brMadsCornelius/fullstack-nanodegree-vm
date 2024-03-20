from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()   # session=interface to DB - no changes on session will happen untill i call session commit

myFirstRestaurant = Restaurant(name = "Pizza Palace")
session.add(myFirstRestaurant)
session.commit()
print(session.query(Restaurant).all()) # will also show object and where it is in mem

cheesepizza = MenuItem(name = "Cheese Pizza", description= "Made with all natural ingredients", course = "Entree", price ="$8.99", restaurant = myFirstRestaurant) # foreign key relationship to myFirst restaurant
session.add(cheesepizza)
session.commit()
print(session.query(MenuItem).all()) # will also show object and where it is in mem

# read items
items = session.query(MenuItem).all()
for item in items:
    print(item.name)
    print("\n")


# Update item
veggieBurgers = session.query(MenuItem).filter_by(name = 'Veggie Burger')
for veggieBurger in veggieBurgers:
    print(veggieBurger.id)
    print(veggieBurger.price)
    print(veggieBurger.restaurant.name)
    print("\n")


UrbanVeggieBuger = session.query(MenuItem).filter_by(id = 2).one() # .one() make sure sqlalchemy only give 1 obj instead of a list to iterate over
print(UrbanVeggieBuger.price)

UrbanVeggieBuger.price = '$2.99'
session.add(UrbanVeggieBuger)
session.commit()


# Delete (find, delete, commit)
spinach = session.query(MenuItem).filter_by(name = 'Spinach Ice Cream').one()
session.delete(spinach)
session.commit()

