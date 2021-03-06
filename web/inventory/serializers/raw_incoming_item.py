from rest_framework import serializers

from scrap import serializers as sc_serializers
from .. import models as inv_models
from .category import CategorySerializer
from .common_item_name_group import CommonItemNameGroupSerializer
from .department import DepartmentSerializer
from .raw_item import RawItemSerializer
from .raw_state import RawStateSerializer
from .source import SourceSerializer


class HyperlinkedRawIncomingItemSerializer(serializers.HyperlinkedModelSerializer):
    # TODO: this is broken when called from APIRawIncomingItemDetailView
    url = serializers.HyperlinkedIdentityField(
        view_name='inventory:api_rawincomingitem_detail',
        lookup_field='pk'
    )
    # without this, the state is reduced to the value int.
    state = RawStateSerializer()

    class Meta:
        model = inv_models.RawIncomingItem
        fields = '__all__'


class XRawIncomingItemSerializer(sc_serializers.DatedModelSerializer):
    source = sc_serializers.CharField()
    department = sc_serializers.CharField()
    customer_number = sc_serializers.CharField()
    order_number = sc_serializers.CharField()
    po_text = sc_serializers.CharField()
    order_comment = sc_serializers.CharField()
    order_date = serializers.DateField(allow_null=True)
    delivery_date = serializers.DateField(allow_null=True)
    total_price = sc_serializers.MoneyField()
    total_packs = sc_serializers.DecimalField()
    line_item_position = serializers.IntegerField(allow_null=True)
    category = sc_serializers.CharField(allow_blank=False)
    name = sc_serializers.CharField(allow_blank=False)
    ordered_quantity = sc_serializers.DecimalField()
    delivered_quantity = sc_serializers.DecimalField()
    item_code = sc_serializers.CharField()
    extra_code = sc_serializers.CharField()
    unit_size = sc_serializers.CharField()
    total_weight = sc_serializers.DecimalField()
    pack_quantity = sc_serializers.DecimalField()
    pack_price = sc_serializers.MoneyField()
    pack_tax = sc_serializers.MoneyField()
    extended_price = sc_serializers.MoneyField()
    item_comment = sc_serializers.CharField()
    scanned_image_filename = sc_serializers.CharField()
    state = RawStateSerializer()
    failure_reason = sc_serializers.CharField(allow_null=True, allow_blank=True)

    def update(self, instance, validated_data):
        # XTODO: If this actually gets used, try to find a "better" way than just repetition.  Better = ModelSerializer
        instance.source = validated_data.get('source', instance.source)
        instance.department = validated_data.get('department', instance.department)
        instance.customer_number = validated_data.get('customer_number', instance.customer_number)
        instance.order_number = validated_data.get('order_number', instance.order_number)
        instance.po_text = validated_data.get('po_text', instance.po_text)
        instance.order_comment = validated_data.get('order_comment', instance.order_comment)
        instance.order_date = validated_data.get('order_date', instance.order_date)
        instance.delivery_date = validated_data.get('delivery_date', instance.delivery_date)
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.total_packs = validated_data.get('total_packs', instance.total_packs)
        instance.line_item_position = validated_data.get('line_item_position', instance.line_item_position)
        instance.category = validated_data.get('category', instance.category)
        instance.name = validated_data.get('name', instance.name)
        instance.ordered_quantity = validated_data.get('ordered_quantity', instance.ordered_quantity)
        instance.delivered_quantity = validated_data.get('delivered_quantity', instance.delivered_quantity)
        instance.item_code = validated_data.get('item_code', instance.item_code)
        instance.extra_code = validated_data.get('extra_code', instance.extra_code)
        instance.unit_size = validated_data.get('unit_size', instance.unit_size)
        instance.total_weight = validated_data.get('total_weight', instance.total_weight)
        instance.pack_quantity = validated_data.get('pack_quantity', instance.pack_quantity)
        instance.pack_price = validated_data.get('pack_price', instance.pack_price)
        instance.pack_tax = validated_data.get('pack_tax', instance.pack_tax)
        instance.extended_price = validated_data.get('extended_price', instance.extended_price)
        instance.item_comment = validated_data.get('item_comment', instance.item_comment)
        instance.scanned_image_filename = validated_data.get('scanned_image_filename', instance.scanned_image_filename)
        instance.state = validated_data.get('state', instance.state)
        instance.failure_reason = validated_data.get('failure_reason', instance.failure_reason)
        instance.save()
        return instance

    def create(self, validated_data):
        return inv_models.RawIncomingItem.objects.create(**validated_data)


class RawIncomingItemInOrderSerializer(sc_serializers.DatedModelSerializer):
    line_item_position = serializers.IntegerField(allow_null=True)
    category = sc_serializers.CharField(allow_blank=False)
    name = sc_serializers.CharField(allow_blank=False)
    ordered_quantity = sc_serializers.DecimalField()
    delivered_quantity = sc_serializers.DecimalField()
    item_code = sc_serializers.CharField()
    extra_code = sc_serializers.CharField()
    unit_size = sc_serializers.CharField()
    total_weight = sc_serializers.DecimalField()
    pack_quantity = sc_serializers.DecimalField()
    pack_price = sc_serializers.MoneyField()
    pack_tax = sc_serializers.MoneyField()
    extended_price = sc_serializers.MoneyField()
    item_comment = sc_serializers.CharField()
    scanned_image_filename = sc_serializers.CharField()
    state = RawStateSerializer()
    failure_reason = sc_serializers.CharField(allow_null=True, allow_blank=True)


class RawIncomingItemSerializer(serializers.ModelSerializer):
    source_obj = SourceSerializer()
    category_obj = CategorySerializer()
    department_obj = DepartmentSerializer()
    rawitem_obj = RawItemSerializer()
    state = serializers.StringRelatedField()

    class Meta:
        model = inv_models.RawIncomingItem
        fields = '__all__'


class RawIncomingItemFlatSerializer(serializers.ModelSerializer):
    better_name = serializers.SerializerMethodField()
    category_obj = serializers.SlugRelatedField('name', read_only=True)
    common_item_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    department_obj = serializers.SlugRelatedField('name', read_only=True)
    rawitem_comment = serializers.SerializerMethodField()
    rawitem_obj = RawItemSerializer()
    source_obj = serializers.SlugRelatedField('name', read_only=True)
    state = serializers.StringRelatedField()

    class Meta:
        model = inv_models.RawIncomingItem
        fields = '__all__'

    def get_better_name(self, obj):
        if obj.rawitem_obj:
            return obj.rawitem_obj.better_name
        return ""

    def get_common_item_name(self, obj):
        if obj.rawitem_obj:
            if obj.rawitem_obj.common_item_name_group:
                if obj.rawitem_obj.common_item_name_group.name:
                    return obj.rawitem_obj.common_item_name_group.name.name
        return ""

    def get_department(self, obj):
        if obj.department_obj:
            return obj.department_obj.abbreviation or obj.department_obj.name or obj.department
        return obj.department

    def get_rawitem_comment(self, obj):
        if obj.rawitem_obj:
            return obj.rawitem_obj.item_comment
        return ""
