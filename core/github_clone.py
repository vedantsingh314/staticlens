"""
GitHub Repository Cloner
"""
import os
import shutil
import tempfile
from git import Repo
from pathlib import Path


class GitHubCloner:
    def __init__(self):
        self.temp_dir = None
    
    def clone_repo(self, repo_url, progress_callback=None):
        """
        Clone a GitHub repository to a temporary directory.
        
        Args:
            repo_url: GitHub repository URL
            progress_callback: Optional callback for progress updates
        
        Returns:
            Path to cloned repository
        """
        try:
            # Create temp directory
            self.temp_dir = tempfile.mkdtemp(prefix="repo_analysis_")
            
            if progress_callback:
                progress_callback("Cloning repository...")
            
            # Clone the repo (shallow clone for speed)
            Repo.clone_from(repo_url, self.temp_dir, depth=1)
            
            if progress_callback:
                progress_callback("Repository cloned successfully!")
            
            return self.temp_dir
        
        except Exception as e:
            self.cleanup()
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def cleanup(self):
        """Remove temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            except Exception as e:
                print(f"Warning: Could not clean up temp directory: {e}")