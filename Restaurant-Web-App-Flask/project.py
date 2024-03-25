from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html',restaurant = restaurant,items = items)


@app.route('/restaurant/<int:restaurant_id>/new/', methods=['GET','POST']) # can now respond to both GET/POST
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(
            name=request.form['name'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash("New menu item created!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newMenuItem.html', restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['itemName']:
            editedItem.name = request.form['itemName']
        session.add(editedItem)
        session.commit()
        flash("Item was edited!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editMenuItem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/',methods = ['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    deletedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash("Item was deleted!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=deletedItem)


# List out all restaurants
@app.route('/restaurants/')
def restaurantsInfo():
    restaurants = session.query(Restaurant).all()
    output = ''
    for restaurant in restaurants:
        output += restaurant.name
        output += '    '
        output += str(restaurant.id)
        items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
        for item in items:
            output += '</br>'
            if isinstance(item.price, str):
                output += item.price
            output += '  -  '
            output += item.name
        output += '</br>'
        output += '</br>'
        
    return output

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    #restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])
'''
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuSpecificJSON(restaurant_id,menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(item.serialize)
'''

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuSpecificJSON(restaurant_id,menu_id):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    for item in items:
        if item.id==menu_id:
            return jsonify(item.serialize)
    return "Not and item in the restaurant!"


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)