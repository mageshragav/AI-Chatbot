"""Query validation utilities for safety checks"""
import re
from typing import Tuple, Optional, List


class ORMQueryValidator:
    """
    Validate generated ORM queries for safety.
    Ensures queries are read-only and don't contain dangerous operations.
    """
    
    # Dangerous patterns that modify data
    DANGEROUS_PATTERNS = [
        r'\.delete\s*\(',
        r'\.update\s*\(',
        r'\.create\s*\(',
        r'\.bulk_create\s*\(',
        r'\.bulk_update\s*\(',
        r'\.get_or_create\s*\(',
        r'\.update_or_create\s*\(',
        r'\.save\s*\(',
        r'\.raw\s*\(',
        r'\.execute\s*\(',
        r'exec\s*\(',
        r'eval\s*\(',
        r'__import__\s*\(',
        r'compile\s*\(',
        r'globals\s*\(',
        r'locals\s*\(',
    ]
    
    # Allowed read-only operations
    ALLOWED_OPERATIONS = [
        'filter', 'exclude', 'all', 'get', 'first', 'last',
        'exists', 'count', 'values', 'values_list',
        'annotate', 'aggregate', 'order_by', 'distinct',
        'select_related', 'prefetch_related', 'only', 'defer',
        'none', 'reverse', 'iterator', 'latest', 'earliest',
    ]
    
    def __init__(self):
        self.dangerous_regex = re.compile('|'.join(self.DANGEROUS_PATTERNS), re.IGNORECASE)
    
    def is_safe(self, orm_query: str) -> Tuple[bool, Optional[str]]:
        """
        Check if ORM query is safe (read-only).
        
        Args:
            orm_query: The Django ORM query string to validate
            
        Returns:
            Tuple of (is_safe: bool, error_message: Optional[str])
        """
        if not orm_query or not orm_query.strip():
            return False, "Query is empty"
        
        # Check for dangerous patterns
        match = self.dangerous_regex.search(orm_query)
        if match:
            return False, f"Dangerous operation detected: {match.group()}"
        
        # Check for SQL injection attempts
        if self._contains_sql_injection(orm_query):
            return False, "Potential SQL injection detected"
        
        # Check for import statements
        if 'import ' in orm_query.lower():
            return False, "Import statements not allowed"
        
        # Validate basic structure
        if not self._has_valid_structure(orm_query):
            return False, "Invalid ORM query structure"
        
        return True, None
    
    def _contains_sql_injection(self, query: str) -> bool:
        """Check for common SQL injection patterns"""
        sql_patterns = [
            r';\s*DROP\s+TABLE',
            r';\s*DELETE\s+FROM',
            r';\s*UPDATE\s+',
            r';\s*INSERT\s+INTO',
            r'UNION\s+SELECT',
            r'--\s*$',
            r'/\*.*\*/',
        ]
        sql_regex = re.compile('|'.join(sql_patterns), re.IGNORECASE)
        return bool(sql_regex.search(query))
    
    def _has_valid_structure(self, query: str) -> bool:
        """Validate that query has basic ORM structure"""
        # Should contain .objects
        if '.objects' not in query:
            return False
        
        # Should not have multiple statements
        if ';' in query and not query.strip().endswith(';'):
            return False
        
        return True
    
    def get_allowed_operations(self) -> List[str]:
        """Return list of allowed ORM operations"""
        return self.ALLOWED_OPERATIONS.copy()
    
    def validate_and_sanitize(self, orm_query: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate and sanitize ORM query.
        
        Returns:
            Tuple of (is_valid: bool, sanitized_query: str, error: Optional[str])
        """
        # Remove leading/trailing whitespace
        sanitized = orm_query.strip()
        
        # Remove trailing semicolon if present
        if sanitized.endswith(';'):
            sanitized = sanitized[:-1].strip()
        
        # Validate
        is_safe, error = self.is_safe(sanitized)
        
        return is_safe, sanitized, error


# Global validator instance
validator = ORMQueryValidator()
