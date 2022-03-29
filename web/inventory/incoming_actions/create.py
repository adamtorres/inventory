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

    assigned_raw_items_count = assign_raw_items(qs)
    print(f"do_create:raw_item assigned {assigned_raw_items_count} existing raw_items")
    raw_items = create_raw_items(qs)
    print(f"do_create:raw_item created {len(raw_items)}")
    assigned_raw_items_count = assign_raw_items(qs)
    print(f"do_create:raw_item assigned {assigned_raw_items_count} raw_items")
    assign_common_item_names_count = assign_common_item_names()
    print(f"do_create:raw_item assigned {assign_common_item_names_count} common names to raw_items")

    # Get all RawItems associated with this batch.  Was using the raw_items list but that only works when the task
    # doesn't fail and get restarted.
    raw_item_filter_qs = qs.exclude(rawitem_obj__isnull=True).order_by('rawitem_obj').distinct('rawitem_obj')
    raw_item_qs = inv_models.RawItem.objects.filter(raw_incoming_items__in=raw_item_filter_qs)

    assigned_items_count = assign_items(raw_item_qs)
    print(f"do_create:item assigned {assigned_items_count} existing items")
    items = create_items(raw_item_qs)
    print(f"do_create:item created {len(items)}")
    assigned_items_count = assign_items(raw_item_qs)
    print(f"do_create:item assigned {assigned_items_count} items")

    items_to_update = []
    fields_to_update = {'state'}
    for i, item in enumerate(qs):
        item.state = item.state.next_state
        items_to_update.append(item)
    return items_to_update, fields_to_update


def assign_categories(qs):
    return assign_things(qs, 'category', 'category_obj')


def assign_common_item_names():
    cn_update_count = 0
    for cn_group in inv_models.CommonItemNameGroup.objects.all():
        ri_qs = inv_models.RawItem.objects.missing_common_item_name().filter(name__in=cn_group.uncommon_item_names)
        cn_update_count += ri_qs.update(common_item_name_group=cn_group)
    return cn_update_count


def assign_departments(qs):
    return assign_things(qs, 'department', 'department_obj')


def assign_items(qs):
    needs_item_qs = qs.filter(item__isnull=True)
    counts = []
    i_filter = inv_models.RawItem.objects.get_item_filter(qs=needs_item_qs)
    for i in inv_models.Item.objects.filter(i_filter):
        counts.append(needs_item_qs.filter(i.get_item_filter()).update(item=i))
    return sum(counts)


def assign_raw_items(qs):
    needs_raw_item_qs = qs.filter(rawitem_obj__isnull=True)
    counts = []
    ri_filter = inv_models.RawIncomingItem.objects.get_raw_item_filter(qs=needs_raw_item_qs)
    for ri in inv_models.RawItem.objects.filter(ri_filter):
        counts.append(needs_raw_item_qs.filter(ri.get_raw_item_filter()).update(rawitem_obj=ri))
    return sum(counts)


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
        print(f"Updated {ret} RawIncomingItem records where {field_name!r} == {fk_obj.name!r}.")
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


def create_items(qs):
    manager_func_name = 'items'
    source_model = inv_models.RawItem
    model = inv_models.Item
    raw_fields = ['source', 'name']
    new_fields = ['source', 'name']
    manager_func = getattr(source_model.objects, manager_func_name)
    objs_to_create = []
    for raw_thing in manager_func(qs=qs, only_new=True):
        kwargs = {nf: raw_thing[rf] for nf, rf in zip(new_fields, raw_fields)}
        new_item = model(**kwargs)
        objs_to_create.append(new_item)
    if objs_to_create:
        objs = model.objects.bulk_create(objs_to_create)
        return objs
    return []


def create_raw_items(qs):
    manager_func_name = 'items'
    source_model = inv_models.RawIncomingItem
    model = inv_models.RawItem
    raw_fields = ['source', 'name', 'unit_size', 'pack_quantity', 'category', 'item_code']
    new_fields = ['source', 'name', 'unit_size', 'pack_quantity', 'category', 'item_code']

    manager_func = getattr(source_model.objects, manager_func_name)
    objs_to_create = []
    for raw_thing in manager_func(qs=qs, only_new=True):
        kwargs = {nf: raw_thing[rf] for nf, rf in zip(new_fields, raw_fields)}
        new_item = model(**kwargs)
        objs_to_create.append(new_item)
    if objs_to_create:
        objs = model.objects.bulk_create(objs_to_create)
        return objs
    return []


def create_sources(qs):
    return create_things(qs, inv_models.Source, 'sources', 'source')
