# Dynamic Field Selection API

The Human Resources API now supports dynamic field selection, allowing clients to specify exactly which fields they want to receive in API responses. This feature helps optimize bandwidth usage and improves API performance by reducing the amount of data transferred.

## Features

- **Field Selection**: Request only specific fields using the `fields` parameter
- **Field Exclusion**: Exclude specific fields using the `exclude` parameter
- **Nested Field Selection**: Select specific nested object fields using dot notation
- **Automatic Query Optimization**: Database queries are automatically optimized based on requested fields

## Usage Examples

### Basic Field Selection

Request only specific fields:

```
GET /api/employees/?fields=id,first_name,last_name,email
```

Response:

```json
{
  "results": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@company.com"
    }
  ]
}
```

### Field Exclusion

Exclude specific fields from the response:

```
GET /api/employees/?exclude=salary,address,phone
```

This returns all employee fields except `salary`, `address`, and `phone`.

### Nested Field Selection

Select specific fields from nested objects using dot notation:

```
GET /api/employees/?fields=id,first_name,last_name,department.name,user.email
```

Response:

```json
{
  "results": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "department": {
        "name": "Engineering"
      },
      "user": {
        "email": "john.doe@company.com"
      }
    }
  ]
}
```

### Complex Nested Selections

Request specific fields from multiple levels of nesting:

```
GET /api/performance-reviews/?fields=id,overall_rating,employee.first_name,employee.last_name,employee.department.name,reviewer.username
```

### Combining with Other Parameters

Dynamic field selection works with all existing API features:

```
GET /api/employees/?fields=id,first_name,last_name,department.name&department=1&search=john&ordering=last_name
```

## Performance Benefits

### Automatic Query Optimization

The API automatically optimizes database queries based on the requested fields:

- **select_related()**: Automatically applied for foreign key relationships
- **prefetch_related()**: Applied for many-to-many and reverse foreign key relationships
- **Reduced queries**: Only fetches data that will actually be serialized

Example of automatic optimization:

```
# Request: /api/employees/?fields=id,first_name,department.name
# Generated query automatically includes: .select_related('department')

# Request: /api/employees/?fields=id,first_name,performance_reviews.overall_rating
# Generated query automatically includes: .prefetch_related('performance_reviews')
```

### Bandwidth Reduction

By requesting only needed fields, you can significantly reduce response size:

```python
# Full employee object: ~2KB per employee
GET /api/employees/

# Minimal fields: ~200 bytes per employee (90% reduction)
GET /api/employees/?fields=id,first_name,last_name,email
```

## API Endpoints Supporting Dynamic Fields

All main endpoints support dynamic field selection:

- `/api/employees/` - Employee management
- `/api/departments/` - Department management
- `/api/performance-reviews/` - Performance review management
- `/api/performance-goals/` - Performance goal management
- `/api/performance-notes/` - Performance note management

## Field Reference

### Employee Fields

Available fields for the Employee model:

**Basic Fields:**

- `id`, `employee_id`, `first_name`, `last_name`, `email`, `phone`
- `position`, `hire_date`, `employment_status`, `salary`
- `address`, `city`, `state`, `postal_code`, `country`
- `created_at`, `updated_at`

**Computed Fields:**

- `full_name` - Computed from first_name and last_name

**Nested Objects:**

- `user.*` - Associated User object (username, email, first_name, last_name)
- `department.*` - Associated Department object (id, name, description)

**Related Collections:**

- `performance_reviews.*` - Employee's performance reviews
- `performance_goals.*` - Employee's performance goals
- `performance_notes.*` - Employee's performance notes

### Department Fields

**Basic Fields:**

- `id`, `name`, `description`, `created_at`, `updated_at`

### Performance Review Fields

**Basic Fields:**

- `id`, `review_type`, `review_period_start`, `review_period_end`
- `review_date`, `status`, `overall_rating`
- `technical_skills`, `communication`, `teamwork`, `leadership`
- `problem_solving`, `adaptability`, `strengths`, `areas_for_improvement`
- `goals_for_next_period`, `reviewer_comments`, `employee_comments`
- `promotion_recommendation`, `salary_increase_recommendation`
- `training_recommendations`, `created_at`, `updated_at`

**Computed Fields:**

- `average_rating` - Average of all skill ratings
- `review_type_display` - Human-readable review type
- `status_display` - Human-readable status

**Nested Objects:**

- `employee.*` - Associated Employee object
- `reviewer.*` - Associated User object (reviewer)

### Performance Goal Fields

**Basic Fields:**

- `id`, `title`, `description`, `category`, `priority`
- `start_date`, `target_date`, `completed_date`, `status`
- `progress_percentage`, `success_criteria`, `measurable_outcomes`
- `progress_notes`, `completion_notes`, `created_at`, `updated_at`

**Computed Fields:**

- `is_overdue` - Boolean indicating if goal is overdue
- `days_remaining` - Days until target date
- `priority_display`, `status_display`, `category_display`

**Nested Objects:**

- `employee.*` - Associated Employee object
- `created_by.*` - User who created the goal
- `review.*` - Associated Performance Review (if any)

### Performance Note Fields

**Basic Fields:**

- `id`, `note_type`, `title`, `content`, `date_observed`
- `is_private`, `created_at`, `updated_at`

**Computed Fields:**

- `note_type_display` - Human-readable note type

**Nested Objects:**

- `employee.*` - Associated Employee object
- `author.*` - User who created the note
- `goal.*` - Associated Performance Goal (if any)
- `review.*` - Associated Performance Review (if any)

## Error Handling

The API handles invalid field requests gracefully:

```python
# Invalid field name - silently ignored, returns available fields
GET /api/employees/?fields=id,invalid_field,first_name

# Invalid nested field - silently ignored
GET /api/employees/?fields=id,department.invalid_field,first_name
```

## Best Practices

1. **Request Only What You Need**: Always specify the exact fields your application requires
2. **Use Nested Selection for Related Data**: Instead of making separate API calls, use dot notation to get related data
3. **Cache Field Lists**: Store commonly used field combinations in your application
4. **Test Performance**: Measure the impact of different field selections on your use case

## Migration Guide

Existing API calls continue to work without changes. To optimize your application:

1. **Identify Heavy Endpoints**: Find API calls that return large amounts of data
2. **Analyze Usage**: Determine which fields your application actually uses
3. **Add Field Parameters**: Update API calls to include `fields` parameters
4. **Monitor Performance**: Measure the improvement in response times and bandwidth

## Examples for Common Use Cases

### Employee List for Dropdown

```
GET /api/employees/?fields=id,first_name,last_name,employee_id
```

### Employee Directory

```
GET /api/employees/?fields=id,first_name,last_name,email,department.name,position
```

### Performance Dashboard

```
GET /api/performance-reviews/?fields=id,overall_rating,review_date,employee.first_name,employee.last_name,employee.department.name
```

### Goal Tracking

```
GET /api/performance-goals/?fields=id,title,status,progress_percentage,target_date,employee.first_name,employee.last_name
```

This dynamic field selection feature makes the HR API more efficient and flexible, allowing you to build faster, more responsive applications while reducing server load and bandwidth usage.
