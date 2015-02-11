from ferris import Controller, scaffold
from ..models.user import UserTag


class UserTags(Controller):
    class Meta:
        prefixes = ('admin',)
        Model = UserTag
        components = (scaffold.Scaffolding,)

    admin_list = scaffold.list
    admin_add = scaffold.add
    admin_delete = scaffold.delete
