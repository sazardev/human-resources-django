from rest_framework import serializers


class DynamicFieldsMixin:
    """
    A mixin that allows dynamically selecting fields in serializers
    based on query parameters or context.
    
    Usage:
    - ?fields=field1,field2,field3 - Include only these fields
        - ?exclude=field1,field2 - Exclude these fields
    - ?fields=department.name,department.description - Nested field selection
    """
    
    def __init__(self, *args, **kwargs):
        # Get fields from kwargs
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        
        # Initialize the parent serializer first
        super().__init__(*args, **kwargs)
        
        # Now context is available, get fields from request if not provided directly
        if not fields and not exclude and hasattr(self, 'context') and self.context:
            request = self.context.get('request')
            if request:
                fields = self._get_fields_from_request(request)
                exclude = self._get_exclude_from_request(request)
        
        # Apply field filtering
        if fields is not None:
            self._filter_fields(fields)
        
        if exclude is not None:
            self._exclude_fields(exclude)
    
    def _get_fields_from_request(self, request):
        """Get fields parameter from request query params"""
        fields_param = request.query_params.get('fields')
        if fields_param:
            return [field.strip() for field in fields_param.split(',') if field.strip()]
        return None
    
    def _get_exclude_from_request(self, request):
        """Get exclude parameter from request query params"""
        exclude_param = request.query_params.get('exclude')
        if exclude_param:
            return [field.strip() for field in exclude_param.split(',') if field.strip()]
        return None
    
    def _filter_fields(self, fields):
        """Filter serializer fields to only include specified fields"""
        if not fields:
            return
        
        # Separate nested fields from direct fields
        direct_fields = []
        nested_fields = {}
        
        for field in fields:
            if '.' in field:
                # Handle nested field like 'department.name'
                parent_field, nested_field = field.split('.', 1)
                if parent_field not in nested_fields:
                    nested_fields[parent_field] = []
                nested_fields[parent_field].append(nested_field)
                # Also include the parent field
                if parent_field not in direct_fields:
                    direct_fields.append(parent_field)
            else:
                direct_fields.append(field)
        
        # Get all existing field names
        existing_fields = set(self.fields.keys())
        # Get requested field names that exist
        allowed_fields = set(direct_fields) & existing_fields
        
        # Remove fields that weren't requested
        for field_name in existing_fields - allowed_fields:
            self.fields.pop(field_name)
        
        # Handle nested field filtering
        self._apply_nested_field_filtering(nested_fields)
    
    def _apply_nested_field_filtering(self, nested_fields):
        """Apply field filtering to nested serializers"""
        for field_name, nested_field_list in nested_fields.items():
            if field_name in self.fields:
                field_instance = self.fields[field_name]
                
                # Handle ListSerializer (many=True)
                if hasattr(field_instance, 'child'):
                    child_serializer = field_instance.child
                    if hasattr(child_serializer, '_filter_fields'):
                        child_serializer._filter_fields(nested_field_list)
                # Handle regular nested serializer
                elif hasattr(field_instance, '_filter_fields'):
                    field_instance._filter_fields(nested_field_list)
    
    def _exclude_fields(self, exclude):
        """Remove specified fields from serializer"""
        if not exclude:
            return
        
        for field_name in exclude:
            self.fields.pop(field_name, None)


class OptimizedQueryMixin:
    """
    A mixin that optimizes database queries based on requested fields
    """
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get fields from request
        request = getattr(self, 'request', None)
        if not request:
            return queryset
        
        fields_param = request.query_params.get('fields')
        if not fields_param:
            return queryset
        
        # Parse requested fields
        fields = [field.strip() for field in fields_param.split(',') if field.strip()]
        
        # Determine which related fields need to be selected/prefetched
        select_related = []
        prefetch_related = []
        
        for field in fields:
            if '.' in field:
                # This is a nested field
                parent_field = field.split('.')[0]
                
                # Check if this is a ForeignKey (select_related) or ManyToMany/reverse FK (prefetch_related)
                if hasattr(self.queryset.model, parent_field):
                    field_obj = self.queryset.model._meta.get_field(parent_field)
                    
                    if hasattr(field_obj, 'related_model'):
                        if field_obj.many_to_one or field_obj.one_to_one:
                            select_related.append(parent_field)
                        elif field_obj.many_to_many or field_obj.one_to_many:
                            prefetch_related.append(parent_field)
        
        # Apply optimizations
        if select_related:
            queryset = queryset.select_related(*select_related)
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
        
        return queryset


class SelectableFieldsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """
    Base serializer that provides dynamic field selection functionality
    """
    pass


class NestedFieldsMixin:
    """
    A mixin that allows specifying fields for nested serializers
    using dot notation in query parameters.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if hasattr(self, 'context') and self.context:
            request = self.context.get('request')
            if request:
                self._handle_nested_fields(request)
    
    def _handle_nested_fields(self, request):
        """Handle nested field selection using dot notation"""
        fields_param = request.query_params.get('fields')
        if not fields_param:
            return
        
        fields = [field.strip() for field in fields_param.split(',') if field.strip()]
        nested_fields = {}
        
        for field in fields:
            if '.' in field:
                # Handle nested field like 'department.name'
                parent_field, nested_field = field.split('.', 1)
                if parent_field not in nested_fields:
                    nested_fields[parent_field] = []
                nested_fields[parent_field].append(nested_field)
        
        # Apply nested field selection to nested serializers
        for field_name, nested_field_list in nested_fields.items():
            if field_name in self.fields:
                field_instance = self.fields[field_name]
                if hasattr(field_instance, 'child'):
                    # Handle many=True serializers
                    child_serializer = field_instance.child
                    if hasattr(child_serializer, '_filter_fields'):
                        child_serializer._filter_fields(nested_field_list)
                elif hasattr(field_instance, '_filter_fields'):
                    # Handle single nested serializers
                    field_instance._filter_fields(nested_field_list)
