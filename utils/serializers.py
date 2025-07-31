from rest_framework import serializers
from drf_writable_nested.mixins import NestedUpdateMixin
from django.db.models import SET_DEFAULT, SET_NULL


class BaseManyToManyNestedSerializer(NestedUpdateMixin):
    """
    A base serializer for nested many to many fields
    """

    def perform_nested_delete_or_update(
        self, pks_to_delete, model_class, instance, related_field, field_source
    ):
        """We override this method to handle the case where the related field
        is a many to many field so we can delete the related objects from the
        m2m table"""
        if related_field.many_to_many:
            # Remove relations from m2m table
            m2m_manager = getattr(instance, field_source)
            m2m_manager.remove(*pks_to_delete)
            # Delete the related objects
            model_class.objects.filter(pk__in=pks_to_delete).delete()
        else:
            qs = model_class.objects.filter(pk__in=pks_to_delete)
            on_delete = related_field.remote_field.on_delete
            if on_delete in (SET_NULL, SET_DEFAULT):
                if on_delete == SET_DEFAULT:
                    default = related_field.get_default()
                else:
                    default = None
                qs.update(**{related_field.name: default})
            else:
                qs.delete()

    def create(self, validated_data):
        many_to_many_fields = []
        for field_name, field in self.fields.items():
            if isinstance(field, serializers.ManyRelatedField):
                if field_name in validated_data:
                    many_to_many_fields.append(
                        (field_name, validated_data.pop(field_name))
                    )

        instance = super().create(validated_data)

        for field_name, field_data in many_to_many_fields:
            getattr(instance, field_name).set(field_data)

        return instance

    def update(self, instance, validated_data):
        many_to_many_fields = []
        for field_name, field in self.fields.items():
            if isinstance(field, serializers.ManyRelatedField):
                if field_name in validated_data:
                    many_to_many_fields.append(
                        (field_name, validated_data.pop(field_name))
                    )

        instance = super().update(instance, validated_data)

        for field_name, field_data in many_to_many_fields:
            getattr(instance, field_name).set(field_data)

        return instance
