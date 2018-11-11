APPROVE_INVENTORY = 'product.inventory'


def can_approve_inventory(instance, user):
    return APPROVE_INVENTORY in user.get_all_permissions()
