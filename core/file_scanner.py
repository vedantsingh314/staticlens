import os
from pathlib import Path
class FileScanner:
   
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'cpp',
        '.hpp': 'cpp',
    }
 
    IGNORE_DIRS = {
        'node_modules', '.git', '__pycache__', 'venv', 'env',
        'build', 'dist', '.idea', '.vscode', 'target', '.next',
        'coverage', '.pytest_cache', '__pycache__', 'saved_files'
    }
    
    IGNORE_FILES = {
        '.gitignore', '.env', 'package-lock.json', 'yarn.lock'
    }
    
    def scan_directory(self, root_path, progress_callback=None):
        """
        Scan directory for code files.
        
        Args:
            root_path: Root directory to scan
            progress_callback: Optional callback for progress updates
        
        Returns:
            List of tuples (file_path, language)
        """
        files = []
        root_path = Path(root_path)
        
        for root, dirs, filenames in os.walk(root_path):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            
            for filename in filenames:
                if filename in self.IGNORE_FILES:
                    continue
                
                ext = Path(filename).suffix.lower()
                
                if ext in self.LANGUAGE_MAP:
                    file_path = os.path.join(root, filename)
                    language = self.LANGUAGE_MAP[ext]
                    files.append((file_path, language))
                    
                    if progress_callback:
                        progress_callback(f"Found: {filename}")
        
        return files
    
    def get_file_stats(self, files):
        """Get statistics about scanned files."""
        stats = {
            'total_files': len(files),
            'by_language': {}
        }
        
        for _, language in files:
            stats['by_language'][language] = stats['by_language'].get(language, 0) + 1
        
        return stats