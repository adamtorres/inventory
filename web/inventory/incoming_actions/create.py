from .. import models as inv_models


def _do_create(batch_size=1):
    """
    step 4
    """
    qs = inv_models.RawIncomingItem.objects.ready_to_create()
    if batch_size > 0:
        qs = qs[:batch_size]
    print(f"do_create found {qs.count()} records to create.")

    sources = create_sources(qs)
    print(f"do_create:source created {len(sources)} sources: {sources}")
    assigned_source_count = assign_sources(qs)
    print(f"do_create:source assigned {assigned_source_count} sources")

    departments = create_departments(qs)
    print(f"do_create:department created {len(departments)} departments: {departments}")
    assigned_department_count = assign_departments(qs)
    print(f"do_create:department assigned {assigned_department_count} departments")

    categories = create_categories(qs)
    print(f"do_create:category created {len(categories)} categories: {categories}")
    assigned_category_count = assign_categories(qs)
    print(f"do_create:category assigned {assigned_category_count} categories")

    raw_items = create_raw_items(qs)
    # print(f"do_create created {len(raw_items)} raw_items: {raw_items}")
    items_to_update = []
    fields_to_update = {'state'}
    for i, item in enumerate(qs):
        item.state = item.state.next_state
        items_to_update.append(item)
    return items_to_update, fields_to_update


def assign_categories(qs):
    return assign_things(qs, 'category', 'category_obj')


def assign_departments(qs):
    return assign_things(qs, 'department', 'department_obj')


def assign_sources(qs):
    return assign_things(qs, 'source', 'source_obj')


def assign_things(qs, field_name, fk_field_name):
    """
    field_name = name of the string on RawIncomingItem
    fk_field_name = name of the ForeignKey field on RawIncomingItem
    """
    results = []
    fk_model = inv_models.RawIncomingItem._meta.get_field(fk_field_name).related_model

    for fk_obj in fk_model.objects.all():
        ret = qs.filter(**{field_name: fk_obj.name}).update(**{fk_field_name: fk_obj})
        results.append(ret)
    return sum(results)


def create_things(qs, model, manager_func_name, raw_field):
    """
    generic function used to create categories, department, and sources
    """
    manager_func = getattr(inv_models.RawIncomingItem.objects, manager_func_name)
    objs_to_create = []
    obj_names = []
    for raw_thing in manager_func(qs=qs, only_new=True):
        objs_to_create.append(model(name=raw_thing[raw_field]))
        obj_names.append(raw_thing[raw_field])
    if objs_to_create:
        model.objects.bulk_create(objs_to_create)
        return obj_names
    return []


def create_categories(qs):
    return create_things(qs, inv_models.Category, 'categories', 'category')


def create_departments(qs):
    return create_things(qs, inv_models.Department, 'departments', 'department')


def create_raw_items(qs):
    manager_func_name = 'items'
    model = inv_models.RawItem
    raw_fields = ['source', 'name', 'unit_size', 'pack_quantity', 'category', 'item_code', 'extra_code']
    new_fields = ['source', 'name', 'unit_size', 'pack_quantity', 'category', 'item_code', 'extra_code']

    manager_func = getattr(inv_models.RawIncomingItem.objects, manager_func_name)
    objs_to_create = []
    obj_names = []
    for raw_thing in manager_func(qs=qs, only_new=True):
        kwargs = {nf: raw_thing[rf] for nf, rf in zip(new_fields, raw_fields)}
        new_item = model(**kwargs)
        obj_names.append(str(new_item))
        objs_to_create.append(new_item)
    if objs_to_create:
        model.objects.bulk_create(objs_to_create)
        return obj_names
    return []


def create_sources(qs):
    return create_things(qs, inv_models.Source, 'sources', 'source')
