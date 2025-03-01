# services/filter_service.py
import json
import os

class FilterService:
    """Service for managing filters"""
    
    def __init__(self, filters_file):
        self.filters_file = filters_file
    
    def load_filters(self):
        """Load filters from the JSON file"""
        try:
            if os.path.exists(self.filters_file):
                with open(self.filters_file, "r") as file:
                    return json.load(file)
            return {}
        except json.JSONDecodeError:
            return {}
    
    def save_filters(self, filters_data):
        """Save filters to the JSON file"""
        with open(self.filters_file, "w") as file:
            json.dump(filters_data, file, indent=4)
    
    def get_user_filters(self, user_id):
        """Get all filters for a specific user"""
        filters_data = self.load_filters()
        return filters_data.get(user_id, [])
    
    def add_filter(self, user_id, filter_data):
        """Add a new filter for a user"""
        filters_data = self.load_filters()
        
        if user_id not in filters_data:
            filters_data[user_id] = []
        
        filters_data[user_id].append(filter_data)
        self.save_filters(filters_data)
        return True
    
    def update_filter(self, user_id, filter_index, filter_data):
        """Update an existing filter"""
        filters_data = self.load_filters()
        
        if user_id not in filters_data or filter_index >= len(filters_data[user_id]):
            return False
        
        filters_data[user_id][filter_index] = filter_data
        self.save_filters(filters_data)
        return True
    
    def delete_filter(self, user_id, filter_index):
        """Delete a filter"""
        filters_data = self.load_filters()
        
        if user_id not in filters_data or filter_index >= len(filters_data[user_id]):
            return False
        
        del filters_data[user_id][filter_index]
        self.save_filters(filters_data)
        return True