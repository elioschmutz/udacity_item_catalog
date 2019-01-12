from models import Base
from models import Category
from models import Item
from models import Session
from models import setup
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--with-example-content', action='store_true',
                    dest="with_exmample_content",
                    help='sets up the database with some example content')
parser.add_argument('--purge', action='store_true',
                    help='recreates the database if it is already existing')

session = Session()

init_content = {
    'Food': [
        {'title': 'Banana', 'description': 'Yellow fruit'},
        {'title': 'Apple', 'description': 'Round fruit'},
        {'title': 'Burger', 'description': 'Meat with some bread'},
        {'title': 'Tomato', 'description': 'Round and red'},
    ],
    'Vehicles': [
        {'title': 'Aeroplane', 'description': 'Very fast'},
        {'title': 'Train', 'description': 'Very clean'},
        {'title': 'Ship', 'description': 'Very big'},
        {'title': 'Car', 'description': 'Very flexible'},
        {'title': 'Food', 'description': 'Very green'},
    ],
    'Sport': [
        {'title': 'Foodball', 'description': 'The most popular sport'},
        {'title': 'Golf', 'description': ''},
    ]
}

if __name__ == '__main__':
    parsed_args = parser.parse_args()

    if parsed_args.purge:
        Base.metadata.drop_all()

    setup()

    for category_name, items in init_content.items():
        category = Category(title=category_name)
        session.add(category)
        if parsed_args.with_exmample_content:
            session.add_all([Item(category=category, **item) for item in items])

        session.commit()
