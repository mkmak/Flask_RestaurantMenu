from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db', connect_args = {'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants/')
def restaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = restaurants)


@app.route('/restaurants/JSON/')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants = [restaurant.serilize for restaurant in restaurants])


@app.route('/restaurants/new/', methods = ['POST', 'GET'])
def newRestaurant():
    if request.method == 'POST':
        if request.form.get('name'):
            session.add(Restaurant(name = request.form['name']))
            session.commit()
            flash('Restaurant "%s" added!' % request.form['name'])
            return redirect(url_for('restaurants'))
        else:
            return render_template('new_restaurant.html', error_msg = 'You must specify a restaurant name!')
    else:
        return render_template('new_restaurant.html', error_msg = '')


@app.route('/restaurants/<int:restaurant_id>/edit/', methods = ['POST', 'GET'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if request.form.get('name'):
            restaurant.name = request.form['name']
            session.add(restaurant)
            session.commit()
            flash('Restaurant "%s" updated!' % restaurant.name)
            return redirect(url_for('restaurants'))
        else:
            return render_template('edit_restaurant.html', name = restaurant.name, error_msg = 'You must specify a restaurant name!')
    else:
        return render_template('edit_restaurant.html', name = restaurant.name, error_msg = '')


@app.route('/restaurants/<int:restaurant_id>/delete/', methods = ['POST', 'GET'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        # delete all the menu items associalted with the restaurant first
        menu_items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id).all()
        for item in menu_items:
            session.delete(item)
            session.commit()
        # delete the restaurant
        session.delete(restaurant)
        session.commit()
        flash('Restaurant "%s" and all of its menu items deleted' % restaurant.name)
        return redirect(url_for('restaurants'))
    else:
        return render_template('delete_restaurant.html', name = restaurant.name)


@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menu_items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    return render_template('menu.html', restaurant = restaurant, menu_items = menu_items)


@app.route('/restaurants/<int:restaurant_id>/new/', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        if request.form.get('name'):
            newItem = MenuItem(name = request.form['name'], course = request.form.get('course'), description = request.form.get('description'), price = request.form.get('price'), restaurant_id = restaurant_id)
            session.add(newItem)
            session.commit()
            flash('Menu item "%s" created!' % newItem.name)
            return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
        else:
            return render_template('new_menu.html', error_msg = 'You must specify a name!', restaurant_id = restaurant_id)
    else:
        return render_template('new_menu.html', error_msg= '', restaurant_id = restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        if request.form.get('name'):
            item.name = request.form['name']
            item.course = request.form.get('course')
            item.description = request.form.get('description')
            item.price = request.form.get('price')
            session.add(item)
            session.commit()
            flash('Menu item "%s" updated!' % item.name)
            return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
        else:
            return render_template('edit_menu.html', name = request.form.get('name'), course = request.form.get('course'), description = request.form.get('description'), price = request.form.get('price'), error_msg = 'You must specify a name!', restaurant_id = restaurant_id)
    else:
        return render_template('edit_menu.html', name = item.name, course = item.course, description = item.description, price = item.price, error_msg = '', restaurant_id = restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Menu item "%s" deleted!' % item.name)
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('delete_menu.html', name = item.name, restaurant_id = restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/JSON/')
def resturantMenuJSON(restaurant_id):
    menu_items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems = [item.serialize for item in menu_items])


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON/')
def resturantMenuItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id = menu_id).one()
    return jsonify(MenuItem = item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key' # for flashing
    app.debug = True # so code change automatically reflected
    app.run(host='0.0.0.0', port=5000)