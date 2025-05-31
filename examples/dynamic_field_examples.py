"""
Dynamic Field Selection Examples

This file contains practical examples of how to use the dynamic field selection
feature in your applications.
"""

# Example 1: Employee dropdown for forms
# Only fetch the minimal data needed for a dropdown
employee_dropdown_url = "/api/employees/?fields=id,first_name,last_name,employee_id"

# Example response:
employee_dropdown_response = {
    "results": [
        {"id": 1, "first_name": "John", "last_name": "Doe", "employee_id": "EMP001"},
        {"id": 2, "first_name": "Jane", "last_name": "Smith", "employee_id": "EMP002"}
    ]
}

# Example 2: Employee directory with department info
employee_directory_url = "/api/employees/?fields=id,first_name,last_name,email,department.name,position"

# Example response:
employee_directory_response = {
    "results": [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe", 
            "email": "john.doe@company.com",
            "department": {"name": "Engineering"},
            "position": "Senior Developer"
        }
    ]
}

# Example 3: Performance dashboard data
performance_dashboard_url = "/api/performance-reviews/?fields=id,overall_rating,review_date,employee.first_name,employee.last_name,employee.department.name"

# Example response:
performance_dashboard_response = {
    "results": [
        {
            "id": 1,
            "overall_rating": 4,
            "review_date": "2024-01-15",
            "employee": {
                "first_name": "John",
                "last_name": "Doe",
                "department": {"name": "Engineering"}
            }
        }
    ]
}

# Example 4: Goal tracking view
goal_tracking_url = "/api/performance-goals/?fields=id,title,status,progress_percentage,target_date,is_overdue,employee.first_name,employee.last_name"

# Example response:
goal_tracking_response = {
    "results": [
        {
            "id": 1,
            "title": "Complete Django certification",
            "status": "in_progress",
            "progress_percentage": 75,
            "target_date": "2024-03-31",
            "is_overdue": False,
            "employee": {
                "first_name": "John",
                "last_name": "Doe"
            }
        }
    ]
}

# Example 5: Exclude sensitive data for public reports
public_employee_list_url = "/api/employees/?exclude=salary,address,phone"

# Example 6: Combined with search and filtering
filtered_employees_url = "/api/employees/?fields=id,first_name,last_name,department.name&department=1&search=john&ordering=last_name"

# Example 7: Nested performance data
employee_performance_url = "/api/employees/1/performance_overview/?fields=id,full_name,latest_performance_review.overall_rating,active_goals.title,active_goals.progress_percentage"

# Example response:
employee_performance_response = {
    "id": 1,
    "full_name": "John Doe",
    "latest_performance_review": {"overall_rating": 4},
    "active_goals": [
        {"title": "Complete certification", "progress_percentage": 75},
        {"title": "Lead team project", "progress_percentage": 50}
    ]
}

# JavaScript/Frontend Examples
# ==============================

# React component example
react_example = """
// Employee List Component
import React, { useState, useEffect } from 'react';

const EmployeeList = () => {
    const [employees, setEmployees] = useState([]);
    
    useEffect(() => {
        // Only fetch fields needed for the list view
        fetch('/api/employees/?fields=id,first_name,last_name,department.name,position')
            .then(response => response.json())
            .then(data => setEmployees(data.results));
    }, []);
    
    return (
        <ul>
            {employees.map(employee => (
                <li key={employee.id}>
                    {employee.first_name} {employee.last_name} - 
                    {employee.department?.name} - {employee.position}
                </li>
            ))}
        </ul>
    );
};
"""

# Vue.js component example
vue_example = """
<!-- Employee Dashboard Component -->
<template>
    <div class="employee-dashboard">
        <div v-for="employee in employees" :key="employee.id" class="employee-card">
            <h3>{{ employee.first_name }} {{ employee.last_name }}</h3>
            <p>Department: {{ employee.department.name }}</p>
            <p>Latest Rating: {{ employee.latest_performance_review?.overall_rating || 'N/A' }}</p>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            employees: []
        };
    },
    async mounted() {
        // Fetch only required fields for dashboard
        const response = await fetch(
            '/api/employees/?fields=id,first_name,last_name,department.name,latest_performance_review.overall_rating'
        );
        const data = await response.json();
        this.employees = data.results;
    }
};
</script>
"""

# Python/Backend Examples
# ========================

# Django template context example
django_view_example = """
from django.shortcuts import render
import requests

def employee_directory(request):
    # Fetch minimal employee data for directory
    api_url = 'http://localhost:8000/api/employees/'
    params = {
        'fields': 'id,first_name,last_name,email,department.name,position',
        'employment_status': 'active'
    }
    
    response = requests.get(api_url, params=params)
    employees = response.json()['results'] if response.status_code == 200 else []
    
    return render(request, 'employee_directory.html', {'employees': employees})
"""

# FastAPI integration example
fastapi_example = """
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/public-employees")
async def get_public_employees():
    # Fetch employees without sensitive data
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/employees/",
            params={"exclude": "salary,address,phone,user.email"}
        )
        return response.json()
        
@app.get("/employee-performance/{employee_id}")
async def get_employee_performance(employee_id: int):
    # Fetch specific performance metrics
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/employees/{employee_id}/performance_overview/",
            params={
                "fields": "id,full_name,average_performance_rating,active_goals.title,active_goals.progress_percentage"
            }
        )
        return response.json()
"""

# Mobile App Examples (React Native)
# ===================================

mobile_example = """
// Mobile Employee Search Component
import React, { useState } from 'react';
import { View, TextInput, FlatList, Text } from 'react-native';

const EmployeeSearch = () => {
    const [employees, setEmployees] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    
    const searchEmployees = async (term) => {
        if (term.length < 2) return;
        
        // Minimal data for mobile list
        const url = `/api/employees/?fields=id,first_name,last_name,position&search=${term}`;
        const response = await fetch(url);
        const data = await response.json();
        setEmployees(data.results);
    };
    
    return (
        <View>
            <TextInput
                value={searchTerm}
                onChangeText={(text) => {
                    setSearchTerm(text);
                    searchEmployees(text);
                }}
                placeholder="Search employees..."
            />
            <FlatList
                data={employees}
                keyExtractor={(item) => item.id.toString()}
                renderItem={({ item }) => (
                    <View>
                        <Text>{item.first_name} {item.last_name}</Text>
                        <Text>{item.position}</Text>
                    </View>
                )}
            />
        </View>
    );
};
"""

# Performance Optimization Examples
# ==================================

performance_tips = """
Performance Optimization Tips:

1. **Paginated Lists**: Use minimal fields for list views
   /api/employees/?fields=id,first_name,last_name,position&page=1

2. **Detail Views**: Only fetch additional data when needed
   /api/employees/1/?fields=id,first_name,last_name,email,department.name,salary

3. **Dashboard Aggregations**: Use computed fields
   /api/performance-reviews/?fields=id,overall_rating,average_rating,employee.first_name

4. **Export Functionality**: Exclude sensitive fields for exports
   /api/employees/?exclude=salary,address,phone&format=csv

5. **Mobile Optimization**: Minimize data for mobile clients
   /api/employees/?fields=id,first_name,last_name,position

6. **Caching Strategy**: Cache responses for common field combinations
   - Cache key: "employees_minimal" for fields=id,first_name,last_name
   - Cache key: "employees_directory" for directory view fields

7. **Monitoring**: Track most requested field combinations to optimize defaults
"""

# Testing Examples
# =================

testing_examples = """
# Unit Test Example for Dynamic Fields
from django.test import TestCase
from rest_framework.test import APIClient

class DynamicFieldsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test data...
    
    def test_basic_field_selection(self):
        response = self.client.get('/api/employees/?fields=id,first_name,last_name')
        self.assertEqual(response.status_code, 200)
        
        # Check that only requested fields are present
        employee = response.json()['results'][0]
        expected_fields = {'id', 'first_name', 'last_name'}
        self.assertEqual(set(employee.keys()), expected_fields)
    
    def test_nested_field_selection(self):
        response = self.client.get('/api/employees/?fields=id,department.name')
        employee = response.json()['results'][0]
        
        # Check nested structure
        self.assertIn('department', employee)
        self.assertIn('name', employee['department'])
        self.assertEqual(len(employee['department']), 1)  # Only 'name' field
    
    def test_field_exclusion(self):
        response = self.client.get('/api/employees/?exclude=salary')
        employee = response.json()['results'][0]
        
        # Check that excluded field is not present
        self.assertNotIn('salary', employee)
"""
