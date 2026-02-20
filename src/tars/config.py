"""Configuration management for TARS CLI"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
import yaml

# Directories with secure permissions
TARS_DIR = Path.home() / ".tars"
TARS_DIR.mkdir(exist_ok=True, mode=0o700)  # Only owner can read/write/execute

CONFIG_FILE = TARS_DIR / "config.yaml"
LOG_FILE = TARS_DIR / "tars.log"
HISTORY_FILE = TARS_DIR / "history.json"
LOGS_DIR = TARS_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True, mode=0o700)

# Ensure secure permissions on existing files
for file_path in [CONFIG_FILE, LOG_FILE, HISTORY_FILE]:
    if file_path.exists():
        os.chmod(file_path, 0o600)  # Only owner can read/write


class ThresholdsConfig(BaseModel):
    """Threshold configuration"""
    cpu: int = Field(default=80, ge=0, le=100)
    memory: int = Field(default=85, ge=0, le=100)
    restarts: int = Field(default=5, ge=0)


class TarsSettings(BaseSettings):
    """TARS CLI settings from environment and config file"""
    
    # API Keys
    gemini_api_key: Optional[str] = Field(default=None, env='GEMINI_API_KEY')
    
    # Kubernetes
    default_namespace: Optional[str] = Field(default=None, env='TARS_NAMESPACE')
    default_cluster: Optional[str] = Field(default=None, env='TARS_CLUSTER')
    
    # Prometheus
    prometheus_url: Optional[str] = Field(default=None, env='PROMETHEUS_URL')
    
    # Thresholds
    thresholds: ThresholdsConfig = Field(default_factory=ThresholdsConfig)
    
    # Monitoring
    interval: int = Field(default=30, ge=1)
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
    
    @validator('gemini_api_key')
    def validate_api_key(cls, v):
        if v and not v.startswith(('AIza', 'test-')):
            raise ValueError('Invalid Gemini API key format')
        return v
    
    @validator('prometheus_url')
    def validate_prometheus_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Prometheus URL must start with http:// or https://')
        return v


class Config:
    """Configuration manager with file persistence"""
    
    def __init__(self):
        self.settings = TarsSettings()
        self._load_from_file()
    
    def _load_from_file(self):
        """Load additional config from YAML file"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                data = yaml.safe_load(f) or {}
                # Merge file config with env settings
                if 'thresholds' in data:
                    self.settings.thresholds = ThresholdsConfig(**data['thresholds'])
                if 'interval' in data:
                    self.settings.interval = data['interval']
    
    def save(self):
        """Save configuration to file"""
        data = {
            'thresholds': self.settings.thresholds.dict(),
            'interval': self.settings.interval,
        }
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def get(self, key: str, default=None):
        """Get configuration value by dot notation"""
        try:
            value = self.settings
            for part in key.split('.'):
                value = getattr(value, part)
            return value
        except AttributeError:
            return default
    
    def set(self, key: str, value):
        """Set configuration value"""
        parts = key.split('.')
        if len(parts) == 2 and parts[0] == 'thresholds':
            setattr(self.settings.thresholds, parts[1], value)
        else:
            setattr(self.settings, key, value)
        self.save()


# Global config instance
config = Config()
