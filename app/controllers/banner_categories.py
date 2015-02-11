from ferris import Controller, scaffold, route
from ..models.banner_category import BannerCategory


class BannerCategories(Controller):

    @route
    def manual_put(self):
        _list = ['Corporate', 'Liquor', 'Petrol', 'Masters', 'Supermarkets', 'PEL', 'Logistics', 'Big W']

        for value in _list:
            instance = BannerCategory(name=value)
            instance.put()

        return "Done"