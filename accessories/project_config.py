#!/usr/bin/env python3
"""
Project Configuration Utility - Gaussian Splatting
==================================================
Utility module to read and manage project-wide configuration
All scripts can import this module to access configuration parameters
"""

import configparser
import os
from pathlib import Path
import platform

class ProjectConfig:
    """
    Centralized configuration manager for the Gaussian Splatting project
    """
    
    def __init__(self, config_file="project_config.ini"):
        """
        Initialize configuration from file
        
        Args:
            config_file: Name of the config file (default: project_config.ini)
        """
        # Detect project root automatically
        script_dir = Path(__file__).parent
        if script_dir.name == "accessories":
            self.project_root = script_dir.parent
        else:
            self.project_root = script_dir
            
        self.config_path = self.project_root / config_file
        self.config = configparser.ConfigParser()
        
        # Load configuration
        if self.config_path.exists():
            self.config.read(self.config_path)
        else:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
    
    def get_path(self, section, key, create_if_missing=False):
        """
        Get a path value and resolve it relative to project root
        
        Args:
            section: Configuration section
            key: Configuration key
            create_if_missing: Create directory if it doesn't exist
            
        Returns:
            Absolute Path object
        """
        relative_path = self.config.get(section, key)
        absolute_path = self.project_root / relative_path
        
        if create_if_missing and not absolute_path.exists():
            absolute_path.mkdir(parents=True, exist_ok=True)
            
        return absolute_path
    
    def get_string(self, section, key, fallback=None):
        """Get a string value from configuration"""
        return self.config.get(section, key, fallback=fallback)
    
    def get_int(self, section, key, fallback=None):
        """Get an integer value from configuration"""
        return self.config.getint(section, key, fallback=fallback)
    
    def get_float(self, section, key, fallback=None):
        """Get a float value from configuration"""
        return self.config.getfloat(section, key, fallback=fallback)
    
    def get_boolean(self, section, key, fallback=None):
        """Get a boolean value from configuration"""
        return self.config.getboolean(section, key, fallback=fallback)
    
    def get_list(self, section, key, separator=',', fallback=None):
        """Get a list value from configuration (comma-separated by default)"""
        value = self.config.get(section, key, fallback=fallback)
        if value is None:
            return fallback
        return [item.strip() for item in value.split(separator)]
    
    def get_iterations_list(self, param_name):
        """
        Get iteration lists (save_iterations, test_iterations, etc.) as integers
        Handles both comma-separated strings and lists
        
        Args:
            param_name: Parameter name in gaussian_splatting section
            
        Returns:
            List of integers
        """
        iterations_str = self.get_string('gaussian_splatting', param_name)
        if ',' in iterations_str:
            return [int(x.strip()) for x in iterations_str.split(',')]
        else:
            return [int(iterations_str)]
    
    # Convenience methods for common configurations
    
    @property
    def project_name(self):
        """Get project name"""
        return self.get_string('project', 'name')
    
    @property
    def data_dir(self):
        """Get data directory path"""
        return self.get_path('paths', 'data_dir')
    
    @property
    def output_dir(self):
        """Get output directory path"""
        return self.get_path('paths', 'output_dir')
    
    @property
    def current_project_dir(self):
        """Get current project directory path"""
        data_dir = self.get_path('paths', 'data_dir')
        current_project = self.get_string('paths', 'current_project')
        return data_dir / current_project
    
    @property
    def equirect_dir(self):
        """Get equirectangular images directory"""
        project_dir = self.current_project_dir
        equirect_subdir = self.get_string('video_processing', 'equirect_subdir')
        return project_dir / equirect_subdir
    
    @property
    def cubemap_dir(self):
        """Get cubemap images directory"""
        project_dir = self.current_project_dir
        cubemap_subdir = self.get_string('video_processing', 'cubemap_subdir')
        return project_dir / cubemap_subdir
    
    @property
    def combined_dir(self):
        """Get combined cubemap output directory"""
        project_dir = self.current_project_dir
        combined_subdir = self.get_string('cubemap_combination', 'combined_subdir')
        return project_dir / combined_subdir
    
    @property
    def train_dir(self):
        """Get training dataset directory (user-selected dataset for training)"""
        project_dir = self.current_project_dir
        train_subdir = self.get_string('training', 'train_subdir')
        return project_dir / train_subdir
    
    @property
    def face_names(self):
        """Get cubemap face names as list"""
        return self.get_list('cubemap', 'face_names')
    
    @property
    def video_processing_params(self):
        """Get video processing parameters as dict"""
        return {
            'skip_frames': self.get_int('video_processing', 'skip_frames'),
            'output_format': self.get_string('video_processing', 'output_format'),
            'video_quality': self.get_int('video_processing', 'video_quality'),
        }
    
    @property
    def cubemap_params(self):
        """Get cubemap processing parameters as dict"""
        return {
            'face_size': self.get_int('cubemap', 'face_size'),
            'start_idx': self.get_int('cubemap_combination', 'start_idx'),      # Changed from 'cubemap'
            'end_idx': self.get_int('cubemap_combination', 'end_idx'),          # Changed from 'cubemap'
            'num_intermediate': self.get_int('cubemap_combination', 'num_intermediate'),  # Changed
            'vfov': self.get_int('cubemap_combination', 'vfov'),                # Changed from 'cubemap'
            'out_size': self.get_int('cubemap_combination', 'out_size'),        # Changed from 'cubemap'
        }
    
    @property
    def gaussian_splatting_params(self):
        """Get Gaussian Splatting training parameters as dict"""
        return {
            'iterations': self.get_int('gaussian_splatting', 'iterations'),
            'position_lr_init': self.get_float('gaussian_splatting', 'position_lr_init'),
            'position_lr_final': self.get_float('gaussian_splatting', 'position_lr_final'),
            'feature_lr': self.get_float('gaussian_splatting', 'feature_lr'),
            'opacity_lr': self.get_float('gaussian_splatting', 'opacity_lr'),
            'scaling_lr': self.get_float('gaussian_splatting', 'scaling_lr'),
            'rotation_lr': self.get_float('gaussian_splatting', 'rotation_lr'),
            'percent_dense': self.get_float('gaussian_splatting', 'percent_dense'),
            'densification_interval': self.get_int('gaussian_splatting', 'densification_interval'),
            'opacity_reset_interval': self.get_int('gaussian_splatting', 'opacity_reset_interval'),
            'densify_from_iter': self.get_int('gaussian_splatting', 'densify_from_iter'),
            'densify_until_iter': self.get_int('gaussian_splatting', 'densify_until_iter'),
            'densify_grad_threshold': self.get_float('gaussian_splatting', 'densify_grad_threshold'),
            'lambda_dssim': self.get_float('gaussian_splatting', 'lambda_dssim'),
            'save_iterations': self.get_list('gaussian_splatting', 'save_iterations'),
            'checkpoint_iterations': self.get_list('gaussian_splatting', 'checkpoint_iterations'),
            'test_iterations': self.get_list('gaussian_splatting', 'test_iterations'),
        }
    
    @property
    def colmap_params(self):
        """Get COLMAP processing parameters as dict"""
        return {
            'camera_model': self.get_string('colmap', 'camera_model'),
            'feature_extractor_gpu': self.get_boolean('colmap', 'feature_extractor_gpu'),
            'matcher_gpu': self.get_boolean('colmap', 'matcher_gpu'),
            'dense_reconstruction': self.get_boolean('colmap', 'dense_reconstruction'),
        }
    
    @property
    def platform_params(self):
        """Get platform-specific parameters as dict"""
        return {
            'max_threads': self.get_int('platform', 'max_threads'),
            'memory_limit': self.get_string('platform', 'memory_limit'),            
            'python_executable': self.get_python_executable(),
        }
    
    def get_video_path(self):
        """Get video path from video_name in current project directory"""
        video_name = self.get_string('video_processing', 'video_name')
        return self.current_project_dir / video_name
    
    def get_cubemap_directions(self):
        """
        Get cubemap direction entries as list of tuples (direction, view, path)
        This replaces the need for combcube_multi_config.cfg
        
        Returns:
            List of tuples: (direction, view, absolute_path)
        """
        entries = []
        
        # Get all keys in cubemap section that start with forward_ or backward_
        for key in self.config['cubemap_combination']:
            if key.startswith(('forward_', 'backward_')):
                # Parse key: "forward_posz" -> direction="forward", view="posz"
                parts = key.split('_', 1)
                if len(parts) == 2:
                    direction, view = parts
                    relative_path = self.config.get('cubemap_combination', key)
                    absolute_path = self.project_root / relative_path
                    entries.append((direction.lower(), view.lower(), str(absolute_path.resolve())))
        
        return entries
    
    def get_python_executable(self):
        """Get platform-appropriate Python executable"""
        if platform.system() == "Windows":
            return self.get_string('platform', 'windows_python', fallback='python')
        else:
            return self.get_string('platform', 'linux_python', fallback='python3')
    
    def copy_config_to_output(self, output_dir, script_name=None):
        """
        Copy the current config file to an output directory for reproducibility
        
        Args:
            output_dir: Directory where config should be copied
            script_name: Optional script name to include in filename
        """
        import shutil
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create filename with timestamp and script name
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if script_name:
            config_filename = f"config_{script_name}_{timestamp}.ini"
        else:
            config_filename = f"config_{timestamp}.ini"
        
        dest_path = output_path / config_filename
        
        # Copy the config file
        shutil.copy2(self.config_path, dest_path)
        print(f"Config saved to: {dest_path}")
        return dest_path
    
    def print_config_summary(self):
        """Print a summary of current configuration"""
        print("=== Project Configuration Summary ===")
        print(f"Project: {self.project_name}")
        print(f"Root: {self.project_root}")
        print(f"Platform: {platform.system()}")
        print()
        print("Paths:")
        print(f"  Data Dir: {self.data_dir}")
        print(f"  Current Project: {self.current_project_dir}")
        print(f"  Equirect Dir: {self.equirect_dir}")
        print(f"  Cubemap Dir: {self.cubemap_dir}")
        print(f"  Combined Dir: {self.combined_dir}")
        print(f"  Train Dir: {self.train_dir}")
        print()
        print("Video Processing:")
        video_params = self.video_processing_params
        print(f"  Skip Frames: {video_params['skip_frames']}")
        print(f"  Output Format: {video_params['output_format']}")
        print(f"  Quality: {video_params['video_quality']}")
        print()
        print("Cubemap:")
        cubemap_params = self.cubemap_params
        print(f"  Face Size: {cubemap_params['face_size']}")
        print(f"  VFOV: {cubemap_params['vfov']}")
        print(f"  Start/End Index: {cubemap_params['start_idx']}-{cubemap_params['end_idx']}")
        print(f"  Intermediates: {cubemap_params['num_intermediate']}")
        print()
        print("Gaussian Splatting:")
        gs_params = self.gaussian_splatting_params
        print(f"  Iterations: {gs_params['iterations']}")
        print(f"  Position LR: {gs_params['position_lr_init']} → {gs_params['position_lr_final']}")
        print(f"  Feature LR: {gs_params['feature_lr']}")
        print(f"  Densification: {gs_params['densify_from_iter']}-{gs_params['densify_until_iter']} (every {gs_params['densification_interval']} iters)")
        print(f"  Densify threshold: {gs_params['densify_grad_threshold']}")
        print(f"  Lambda DSSIM: {gs_params['lambda_dssim']}")
        print(f"  Save Iterations: {gs_params['save_iterations']}")
        print()
        print("COLMAP:")
        colmap_params = self.colmap_params
        print(f"  Camera Model: {colmap_params['camera_model']}")
        print(f"  GPU Feature Extraction: {colmap_params['feature_extractor_gpu']}")
        print(f"  GPU Matching: {colmap_params['matcher_gpu']}")
        print()
        print("Platform:")
        platform_params = self.platform_params
        print(f"  Max Threads: {platform_params['max_threads']}")
        print(f"  Memory Limit: {platform_params['memory_limit']}")
        print(f"  Python: {platform_params['python_executable']}")
        gaussian_params = self.gaussian_splatting_params
        print(f"  Iterations: {gaussian_params['iterations']}")
        colmap_params = self.colmap_params
        print(f"  Camera Model: {colmap_params['camera_model']}")

# Create a global config instance for easy importing
config = None
_current_config_file = None

def get_config(config_file):
    """
    Get or create the global configuration instance
    
    Args:
        config_file: Configuration file name (required - no default)
        
    Returns:
        ProjectConfig instance
    """
    global config, _current_config_file
    
    # If config file changed, recreate the config instance
    if config is None or _current_config_file != config_file:
        config = ProjectConfig(config_file)
        _current_config_file = config_file
    return config

# Example usage
if __name__ == "__main__":
    # Test the configuration with explicit config file
    cfg = get_config("project_config.ini")
    cfg.print_config_summary()
