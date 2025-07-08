import streamlit as st
from typing import List, Dict, Any


class SessionStateManager:
    """Manages session state for mapping pages to prevent conflicts during navigation."""
    
    # Define page-specific session state keys
    PAGE_STATE_KEYS = {
        "nominate": [
            "range_name",
            "range_description",
            "nominate_model"
        ],
        "public_ranges": [
            "delete_selected_public_ranges",
            "confirm_delete_public_ranges",
            "public_ranges_table_checkboxes",
            "public_ranges_state_filter",
            "public_ranges_location_search",
            "public_ranges_admin_state_filter",
            "public_ranges_admin_location_search"
        ],
        "submission": [
            "delete_selected_ranges",
            "selected_ranges",
            "ranges_table_checkboxes"
        ],
        "admin": [
            "selected_submissions",
            "admin_submissions_table_checkboxes"
        ]
    }
    
    # Global state that should persist across pages
    GLOBAL_STATE_KEYS = [
        "user_info_displayed",
        "app"
    ]
    
    @classmethod
    def get_current_page(cls) -> str:
        """Determine current page from query params or URL."""
        # Check query params first
        if "page" in st.query_params:
            return st.query_params["page"]
        
        # Fallback: try to infer from the current page context
        # This is a simple heuristic based on common patterns
        try:
            # Get the script run context to determine current file
            import inspect
            frame = inspect.currentframe()
            while frame:
                filename = frame.f_code.co_filename
                if "nominate" in filename.lower():
                    return "nominate"
                elif "ranges" in filename.lower() or "public" in filename.lower():
                    return "public_ranges"
                elif "submission" in filename.lower():
                    return "submission"
                elif "admin" in filename.lower():
                    return "admin"
                frame = frame.f_back
        except:
            pass
        
        return "unknown"
    
    @classmethod
    def clear_page_state(cls, page: str) -> None:
        """Clear session state for a specific page."""
        if page in cls.PAGE_STATE_KEYS:
            keys_to_clear = cls.PAGE_STATE_KEYS[page]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
    
    @classmethod
    def clear_other_pages_state(cls, current_page: str) -> None:
        """Clear session state for all pages except the current one."""
        for page, keys in cls.PAGE_STATE_KEYS.items():
            if page != current_page:
                for key in keys:
                    if key in st.session_state:
                        del st.session_state[key]
    
    @classmethod
    def clear_all_page_state(cls) -> None:
        """Clear all page-specific session state, keeping only global state."""
        for page_keys in cls.PAGE_STATE_KEYS.values():
            for key in page_keys:
                if key in st.session_state:
                    del st.session_state[key]
    
    @classmethod
    def set_current_page(cls, page: str) -> None:
        """Set the current page and clear other pages' state."""
        # Store the current page
        if "current_mapping_page" not in st.session_state:
            st.session_state["current_mapping_page"] = page
        elif st.session_state["current_mapping_page"] != page:
            # Page has changed, clear previous page state
            cls.clear_other_pages_state(page)
            st.session_state["current_mapping_page"] = page
    
    @classmethod
    def get_page_state_keys(cls, page: str) -> List[str]:
        """Get the session state keys for a specific page."""
        return cls.PAGE_STATE_KEYS.get(page, [])
    
    @classmethod
    def is_global_state_key(cls, key: str) -> bool:
        """Check if a key is global state that should persist across pages."""
        return key in cls.GLOBAL_STATE_KEYS
    
    @classmethod
    def debug_session_state(cls, page: str = None) -> Dict[str, Any]:
        """Return current session state for debugging, optionally filtered by page."""
        if page and page in cls.PAGE_STATE_KEYS:
            relevant_keys = cls.PAGE_STATE_KEYS[page] + cls.GLOBAL_STATE_KEYS
            return {k: v for k, v in st.session_state.items() if k in relevant_keys}
        else:
            return dict(st.session_state)