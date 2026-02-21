"""Configuration management for SSTARS CLI"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
import yaml

# Directories with secure permissions
STARS_DIR = Path.home() / ".stars"
STARS_DIR.mkdir(exist_ok=True, mode=0o700)  # Only owner can read/write/execute

CONFIG_FILE = STARS_DIR / "config.yaml"
LOG_FILE = STARS_DIR / "tars.log"
HISTORY_FILE = STARS_DIR / "history.json"
AUDIT_LOG = STARS_DIR / "audit.log"
CONSENT_FILE = STARS_DIR / "ai_consent"
LOGS_DIR = STARS_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True, mode=0o700)

# Ensure secure permissions on existing files
for file_path in [CONFIG_FILE, LOG_FILE, HISTORY_FILE, AUDIT_LOG]:
    if file_path.exists():
        os.chmod(file_path, 0o600)  # Only owner can read/write


def check_ai_consent() -> bool:
    """Check if user has consented to AI data sharing"""
    return CONSENT_FILE.exists()


def grant_ai_consent():
    """Record user consent for AI data sharing"""
    CONSENT_FILE.touch(mode=0o600)
    with open(CONSENT_FILE, 'w') as f:
        from datetime import datetime
        f.write(f"AI consent granted: {datetime.utcnow().isoformat()}\n")


def revoke_ai_consent():
    """Revoke user consent for AI data sharing"""
    if CONSENT_FILE.exists():
        CONSENT_FILE.unlink()


def audit_log(action: str, resource: str, namespace: str, user: str = None):
    """Log actions for audit trail"""
    import json
    from datetime import datetime
    
    if user is None:
        user = os.getenv('USER', 'unknown')
    
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'user': user,
        'action': action,
        'resource': resource,
        'namespace': namespace
    }
    
    with open(AUDIT_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    os.chmod(AUDIT_LOG, 0o600)


class ThresholdsConfig(BaseModel):
    """Threshold configuration"""
    cpu: int = Field(default=80, ge=0, le=100)
    memory: int = Field(default=85, ge=0, le=100)
    restarts: int = Field(default=5, ge=0)


class TarsSettings(BaseSettings):
    """STARS CLI settings from environment and config file"""
    
    # Kubernetes
    default_namespace: Optional[str] = Field(default=None, env='STARS_NAMESPACE')
    default_cluster: Optional[str] = Field(default=None, env='STARS_CLUSTER')
    
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
    
    @property
    def gemini_api_key(self) -> Optional[str]:
        """Get API key from secure storage (keychain -> local file -> env var)"""
        # Priority 1: OS Keychain
        try:
            import keyring
            key = keyring.get_password("stars-cli", "gemini_api_key")
            if key:
                return key
        except Exception:
            pass
        
        # Priority 2: Local credentials file
        try:
            from pathlib import Path
            creds_file = Path.home() / ".stars" / "credentials"
            if creds_file.exists():
                with open(creds_file, 'r') as f:
                    key = f.read().strip()
                    if key:
                        return key
        except Exception:
            pass
        
        # Priority 3: Environment variable
        return os.getenv('GEMINI_API_KEY')
    
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
        import os
        data = {
            'thresholds': self.settings.thresholds.dict(),
            'interval': self.settings.interval,
        }
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        os.chmod(CONFIG_FILE, 0o600)
    
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
