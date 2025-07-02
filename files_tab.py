import streamlit as st
import pandas as pd
from collections import defaultdict
import os

def render_files_tab(user, supabase, bucket):
    """Render the My Files tab with file explorer style"""
    st.header("📁 My Uploaded Files")
    
    try:
        # Get all files for the user by checking both root and subdirectories
        file_tree = defaultdict(list)
        
        # Check root directory first
        try:
            root_files = supabase.storage.from_(bucket).list(f"{user['email']}")
            for file_item in root_files:
                if file_item.get('name'):
                    # Check if it's a directory (no file extension)
                    if '.' not in file_item['name']:
                        # This is a subdirectory, list its contents
                        subdir_path = f"{user['email']}/{file_item['name']}"
                        try:
                            subdir_files = supabase.storage.from_(bucket).list(subdir_path)
                            for subfile in subdir_files:
                                if subfile.get('name'):
                                    file_tree[file_item['name']].append({
                                        'filename': subfile['name'],
                                        'full_path': f"{subdir_path}/{subfile['name']}",
                                        'metadata': subfile
                                    })
                        except:
                            # Directory might be empty or inaccessible
                            pass
                    else:
                        # This is a file in root
                        file_tree["root"].append({
                            'filename': file_item['name'],
                            'full_path': f"{user['email']}/{file_item['name']}",
                            'metadata': file_item
                        })
        except:
            pass
        
        # Also explicitly check known directories
        known_dirs = ['garmin', 'kestrel', 'weather']
        for dir_name in known_dirs:
            try:
                dir_path = f"{user['email']}/{dir_name}"
                dir_files = supabase.storage.from_(bucket).list(dir_path)
                for file_item in dir_files:
                    if file_item.get('name'):
                        # Avoid duplicates
                        existing_files = [f['filename'] for f in file_tree[dir_name]]
                        if file_item['name'] not in existing_files:
                            file_tree[dir_name].append({
                                'filename': file_item['name'],
                                'full_path': f"{dir_path}/{file_item['name']}",
                                'metadata': file_item
                            })
            except:
                # Directory doesn't exist
                pass
        
        # Remove empty directories
        file_tree = {k: v for k, v in file_tree.items() if v}
        
        if not file_tree:
            st.info("No files uploaded yet. Use the 'Upload Files' tab to get started!")
            return
        
        # Display file explorer
        st.markdown("### 🗂️ File Explorer")
        
        # Show directory structure
        for directory, files in file_tree.items():
            # Directory header with icon and file count
            directory_icon = get_directory_icon(directory)
            with st.expander(f"{directory_icon} **{directory.upper()}** ({len(files)} files)", expanded=True):
                
                # Files table for this directory
                if files:
                    # Create columns for file table
                    col_name, col_size, col_type, col_uploaded, col_actions = st.columns([3, 1, 1.5, 1.5, 2])
                    
                    with col_name:
                        st.markdown("**📄 File Name**")
                    with col_size:
                        st.markdown("**📏 Size**")
                    with col_type:
                        st.markdown("**🏷️ Type**")
                    with col_uploaded:
                        st.markdown("**📅 Uploaded**")
                    with col_actions:
                        st.markdown("**⚙️ Actions**")
                    
                    st.markdown("---")
                    
                    # Display each file
                    for file_info in sorted(files, key=lambda x: x['filename']):
                        filename = file_info['filename']
                        full_path = file_info['full_path']
                        metadata = file_info['metadata']
                        
                        col_name, col_size, col_type, col_uploaded, col_actions = st.columns([3, 1, 1.5, 1.5, 2])
                        
                        with col_name:
                            file_icon = get_file_icon(filename)
                            st.write(f"{file_icon} `{filename}`")
                        
                        with col_size:
                            size_text = get_file_size(metadata)
                            st.write(size_text)
                        
                        with col_type:
                            file_type = get_file_type(filename, metadata)
                            st.write(file_type)
                        
                        with col_uploaded:
                            upload_time = get_upload_time(metadata)
                            st.write(upload_time)
                        
                        with col_actions:
                            # Action buttons in a row
                            action_col1, action_col2 = st.columns(2)
                            
                            with action_col1:
                                if st.button("📥", key=f"download_{full_path}", help="Download file"):
                                    download_file(supabase, bucket, full_path, filename)
                            
                            with action_col2:
                                if st.button("🗑️", key=f"delete_{full_path}", help="Delete file"):
                                    st.session_state[f"confirm_delete_{full_path}"] = True
                        
                        # Handle delete confirmation
                        if st.session_state.get(f"confirm_delete_{full_path}", False):
                            st.warning(f"⚠️ Delete **{filename}**? This cannot be undone!")
                            confirm_col1, confirm_col2 = st.columns(2)
                            
                            with confirm_col1:
                                if st.button("✅ Yes", key=f"confirm_yes_{full_path}", type="primary"):
                                    delete_file(supabase, bucket, full_path, filename)
                                    del st.session_state[f"confirm_delete_{full_path}"]
                                    st.rerun()
                            
                            with confirm_col2:
                                if st.button("❌ Cancel", key=f"confirm_no_{full_path}"):
                                    del st.session_state[f"confirm_delete_{full_path}"]
                                    st.rerun()
                        
                        st.markdown("---")
                else:
                    st.info(f"No files in {directory} directory")
    
    except Exception as e:
        st.error(f"Error loading files: {e}")

def get_directory_icon(directory):
    """Get icon for directory type"""
    icons = {
        "garmin": "🎯",
        "kestrel": "🌤️",
        "weather": "🌤️",  # Legacy support
        "root": "📁"
    }
    return icons.get(directory.lower(), "📁")

def get_file_icon(filename):
    """Get icon based on file extension"""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    icons = {
        'xlsx': '📊',
        'xls': '📊', 
        'csv': '📋',
        'pdf': '📄',
        'txt': '📝',
        'json': '🔧',
        'zip': '🗜️'
    }
    return icons.get(ext, '📄')

def get_file_size(metadata):
    """Extract and format file size"""
    if 'metadata' in metadata and metadata['metadata'] and 'size' in metadata['metadata']:
        size_bytes = metadata['metadata']['size']
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    return "Unknown"

def get_file_type(filename, metadata):
    """Get file type from extension or metadata"""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    # Try to get from metadata first
    if 'metadata' in metadata and metadata['metadata'] and 'mimetype' in metadata['metadata']:
        mimetype = metadata['metadata']['mimetype']
        type_map = {
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
            'text/csv': 'CSV',
            'application/pdf': 'PDF',
            'text/plain': 'Text'
        }
        return type_map.get(mimetype, ext.upper())
    
    # Fallback to extension
    return ext.upper() if ext else 'Unknown'

def get_upload_time(metadata):
    """Extract upload time from various possible fields"""
    timestamp_fields = ['created_at', 'updated_at', 'last_accessed_at']
    
    # Check main level fields
    for field in timestamp_fields:
        if field in metadata and metadata[field]:
            try:
                return pd.to_datetime(metadata[field]).strftime('%m/%d/%y')
            except:
                continue
    
    # Check metadata
    if 'metadata' in metadata and metadata['metadata']:
        meta = metadata['metadata']
        for field in ['lastModified', 'dateCreated', 'uploadTime']:
            if field in meta and meta[field]:
                try:
                    return pd.to_datetime(meta[field]).strftime('%m/%d/%y')
                except:
                    continue
    
    return "Unknown"

def download_file(supabase, bucket, full_path, filename):
    """Handle file download"""
    try:
        file_data = supabase.storage.from_(bucket).download(full_path)
        st.download_button(
            label=f"💾 Save {filename}",
            data=file_data,
            file_name=filename,
            mime="application/octet-stream",
            key=f"save_{full_path}"
        )
        st.success(f"✅ {filename} ready for download!")
    except Exception as e:
        st.error(f"❌ Error downloading {filename}: {e}")

def delete_file(supabase, bucket, full_path, filename):
    """Handle file deletion"""
    try:
        supabase.storage.from_(bucket).remove([full_path])
        st.success(f"✅ {filename} deleted successfully!")
    except Exception as e:
        st.error(f"❌ Error deleting {filename}: {e}")