# STARS CLI Architecture

## Overview

STARS (Smart Troubleshooting and Remediation System) is an enterprise-grade Kubernetes CLI tool with AI-powered diagnostics and SRE automation capabilities.

## Design Principles

1. **Security First** - Secure credential storage, input validation, least privilege
2. **User Experience** - Intuitive commands, clear error messages, helpful guidance
3. **Reliability** - Graceful degradation, comprehensive error handling, fallback mechanisms
4. **Extensibility** - Modular architecture, plugin support, API-driven design
5. **Performance** - Efficient resource usage, caching, async operations where beneficial

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         STARS CLI                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   CLI Layer  │  │  Commands    │  │   Utilities  │     │
│  │   (Typer)    │──│   Layer      │──│   (Helpers)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                │
│  ┌─────────────────────────┴──────────────────────────┐    │
│  │              Core Services Layer                    │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  • Kubernetes Client  • AI Integration (Gemini)    │    │
│  │  • Monitoring         • Incident Management        │    │
│  │  • Security Scanner   • Health Checker             │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                │
│  ┌─────────────────────────┴──────────────────────────┐    │
│  │           Configuration & Security Layer            │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  • Config Manager     • Keyring Integration        │    │
│  │  • Credential Store   • Environment Variables      │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
    ┌─────────▼─────────┐        ┌─────────▼─────────┐
    │  Kubernetes API   │        │   Gemini API      │
    │   (kubectl/k8s)   │        │  (AI Analysis)    │
    └───────────────────┘        └───────────────────┘
```

## Component Architecture

### 1. CLI Layer (`cli.py`)

**Responsibility:** Command-line interface and user interaction

**Key Components:**
- Typer application setup
- Command registration
- Argument/option parsing
- User input handling
- Output formatting

**Design Decisions:**
- **Typer Framework:** Chosen for type safety, automatic help generation, and excellent UX
- **Rich Library:** Used for colored output, tables, and progress indicators
- **Modular Commands:** Each command group isolated for maintainability

### 2. Commands Layer

**Responsibility:** Business logic for each CLI command

**Modules:**
- `commands.py` - Kubernetes operations (pods, nodes, deployments)
- `monitoring.py` - Health checks, diagnostics, analysis
- `incident.py` - Incident management for SRE workflows
- `security.py` - Security scanning and compliance checks

**Design Decisions:**
- **Command Pattern:** Each command encapsulated in dedicated function
- **Separation of Concerns:** CLI parsing separate from business logic
- **Error Handling:** Try-catch at command level with user-friendly messages

### 3. Core Services Layer

#### Kubernetes Client

**Implementation:**
```python
from kubernetes import client, config

# Load kubeconfig
config.load_kube_config()

# Create API clients
v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()
```

**Features:**
- Automatic kubeconfig detection
- Context switching support
- RBAC-aware operations
- Connection pooling

#### AI Integration (Gemini)

**Implementation:**
```python
import google.generativeai as genai

genai.configure(api_key=config.gemini_api_key)
model = genai.GenerativeModel('gemini-pro')
```

**Features:**
- Intelligent log analysis
- Root cause detection
- Remediation suggestions
- Natural language queries

**Design Decisions:**
- **Optional AI:** All commands work without AI (--no-ai flag)
- **Privacy First:** User consent required before AI usage
- **Fallback:** Basic analysis when AI unavailable

#### Monitoring Services

**Components:**
- Health checker (cluster, nodes, pods)
- Event monitor (watch and analyze)
- Resource analyzer (CPU, memory, disk)
- Triage system (prioritize issues)

### 4. Configuration & Security Layer

#### Config Manager (`config.py`)

**Responsibility:** Application configuration and settings

```python
@dataclass
class Config:
    kubeconfig_path: str
    prometheus_url: Optional[str]
    
    @property
    def gemini_api_key(self) -> Optional[str]:
        # 3-tier retrieval: keychain → file → env
        return self._get_api_key()
```

**Design Decisions:**
- **Immutable Config:** Dataclass with frozen=True for thread safety
- **Lazy Loading:** API key retrieved only when needed
- **Fallback Chain:** Multiple credential sources for flexibility

#### Secure Credential Storage (`config_secure.py`)

**Implementation:**
```python
import keyring

def save_api_key_secure(api_key: str) -> bool:
    try:
        keyring.set_password("stars-cli", "gemini_api_key", api_key)
        return True
    except Exception:
        # Fallback to local file with chmod 600
        return _save_to_file(api_key)
```

**Security Features:**
- **OS Keychain:** macOS Keychain (AES-256), Windows Credential Manager (DPAPI)
- **File Permissions:** chmod 600 for local credential file
- **No Plaintext:** Never log or display credentials
- **Secure Input:** getpass for hidden password prompts

## Data Flow

### Command Execution Flow

```
User Input
    │
    ▼
CLI Parser (Typer)
    │
    ▼
Command Handler
    │
    ├─► Validate Input
    │
    ├─► Load Configuration
    │   └─► Retrieve Credentials (keychain → file → env)
    │
    ├─► Initialize K8s Client
    │   └─► Load kubeconfig
    │
    ├─► Execute Operation
    │   ├─► Query Kubernetes API
    │   ├─► Process Data
    │   └─► Optional: AI Analysis
    │
    ├─► Format Output
    │   └─► Rich tables/colors
    │
    └─► Display Result
```

### Credential Retrieval Flow

```
Request API Key
    │
    ▼
Check OS Keychain
    │
    ├─► Found? ──► Return Key
    │
    └─► Not Found
        │
        ▼
    Check Local File (~/.stars/credentials)
        │
        ├─► Found? ──► Return Key
        │
        └─► Not Found
            │
            ▼
        Check Environment Variable (GEMINI_API_KEY)
            │
            ├─► Found? ──► Return Key
            │
            └─► Not Found ──► Prompt User
```

## Security Architecture

### Defense in Depth

**Layer 1: Input Validation**
- Kubernetes resource name validation (DNS-1123)
- Namespace validation
- Command injection prevention
- Path traversal protection

**Layer 2: Authentication & Authorization**
- Kubernetes RBAC enforcement
- API key encryption at rest
- Secure credential storage
- No hardcoded secrets

**Layer 3: Network Security**
- TLS for all API communications
- Certificate validation
- No credential transmission in URLs
- Secure token handling

**Layer 4: Data Protection**
- Credentials encrypted in keychain
- File permissions (chmod 600)
- No sensitive data in logs
- Redaction of secrets in output

**Layer 5: Supply Chain Security**
- Pinned GitHub Actions (commit SHAs)
- Hashed dependencies (pip --require-hashes)
- Binary checksum verification (SHA-256)
- Automated security scanning

### Threat Model

**Threats Addressed:**

1. **Credential Theft**
   - Mitigation: OS keychain encryption, file permissions
   
2. **Man-in-the-Middle**
   - Mitigation: TLS enforcement, certificate validation
   
3. **Code Injection**
   - Mitigation: Input validation, parameterized queries
   
4. **Supply Chain Attack**
   - Mitigation: Dependency hashing, action pinning, checksums
   
5. **Privilege Escalation**
   - Mitigation: RBAC enforcement, least privilege principle

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**
   - Import heavy modules only when needed
   - Defer API client initialization

2. **Caching**
   - Cache kubeconfig parsing
   - Cache cluster information
   - TTL-based cache invalidation

3. **Efficient Queries**
   - Field selectors to reduce data transfer
   - Label selectors for targeted queries
   - Pagination for large result sets

4. **Async Operations** (Future Enhancement)
   - Parallel pod queries
   - Concurrent health checks
   - Background monitoring

### Resource Usage

**Target Metrics:**
- Startup time: < 1 second
- Memory usage: < 100MB
- CPU usage: < 5% idle
- Network: Minimal (only necessary API calls)

## Error Handling Strategy

### Error Categories

1. **User Errors**
   - Invalid input
   - Missing required arguments
   - Incorrect resource names
   - **Response:** Clear error message with guidance

2. **Configuration Errors**
   - Missing kubeconfig
   - Invalid API key
   - Unreachable cluster
   - **Response:** Setup instructions and troubleshooting

3. **Permission Errors**
   - RBAC denied
   - Insufficient privileges
   - **Response:** Required permissions list

4. **System Errors**
   - Network failures
   - API timeouts
   - Resource exhaustion
   - **Response:** Retry logic, fallback options

### Error Handling Pattern

```python
try:
    # Operation
    result = perform_operation()
except KubernetesError as e:
    print_error(f"Kubernetes error: {e}")
    print_info("Check your kubeconfig and permissions")
    raise typer.Exit(1)
except APIError as e:
    print_error(f"API error: {e}")
    print_info("Retrying with exponential backoff...")
    result = retry_with_backoff(perform_operation)
except Exception as e:
    print_error(f"Unexpected error: {e}")
    print_info("Please report this issue on GitHub")
    raise typer.Exit(1)
```

## Testing Strategy

### Test Pyramid

```
        ┌─────────────┐
        │   E2E Tests │  (10%)
        │  Integration│
        └─────────────┘
       ┌───────────────┐
       │  Integration  │  (30%)
       │     Tests     │
       └───────────────┘
      ┌─────────────────┐
      │   Unit Tests    │  (60%)
      │                 │
      └─────────────────┘
```

**Unit Tests:**
- Individual function testing
- Mock external dependencies
- Edge case validation
- Error handling verification

**Integration Tests:**
- Command execution flow
- API client interactions
- Configuration loading
- Credential retrieval

**E2E Tests:**
- Full command workflows
- Real Kubernetes cluster
- Actual API calls
- User scenarios

### Test Coverage Goals

- **Overall:** 80%+
- **Critical paths:** 95%+
- **Security functions:** 100%
- **Error handlers:** 90%+

## Deployment Architecture

### Binary Distribution

```
GitHub Release
    │
    ├─► Linux Binary (amd64)
    │   └─► SHA-256 checksum
    │
    ├─► macOS Binary (arm64/amd64)
    │   └─► SHA-256 checksum
    │
    └─► Windows Binary (amd64)
        └─► SHA-256 checksum
```

### Installation Methods

1. **One-line Install Script**
   ```bash
   curl -sSL https://raw.githubusercontent.com/.../install.sh | bash
   ```
   - Auto-detects OS/architecture
   - Downloads latest release
   - Verifies SHA-256 checksum
   - Installs to /usr/local/bin

2. **Manual Download**
   - Download binary from GitHub releases
   - Verify checksum manually
   - Move to PATH

3. **Package Managers** (Future)
   - Homebrew (macOS)
   - apt/yum (Linux)
   - Chocolatey (Windows)

## Future Enhancements

### Planned Features

1. **Plugin System**
   - Custom command plugins
   - Third-party integrations
   - Extension marketplace

2. **Advanced Monitoring**
   - Real-time dashboards
   - Alerting integration
   - Metrics collection

3. **Multi-Cluster Support**
   - Cluster switching
   - Cross-cluster operations
   - Federated queries

4. **Enhanced AI**
   - Custom model training
   - Historical analysis
   - Predictive alerts

5. **Web UI** (Optional)
   - Browser-based interface
   - Visual dashboards
   - Collaborative features

## Technology Stack

### Core Dependencies

- **Python 3.11+** - Modern Python features, performance
- **Typer** - CLI framework with excellent UX
- **Rich** - Terminal formatting and colors
- **kubernetes** - Official Kubernetes Python client
- **google-generativeai** - Gemini AI integration
- **keyring** - OS keychain integration
- **PyInstaller** - Binary compilation

### Development Tools

- **pip-tools** - Dependency management with hashing
- **bandit** - Python security linting
- **pytest** - Testing framework
- **black** - Code formatting
- **mypy** - Static type checking

### CI/CD Tools

- **GitHub Actions** - Automation platform
- **CodeQL** - Security analysis
- **Trivy** - Vulnerability scanning
- **Dependabot** - Dependency updates
- **TruffleHog** - Secret scanning

## Compliance & Standards

### Security Standards

- **OWASP Top 10** - Web application security
- **CWE Top 25** - Common weakness enumeration
- **NIST Cybersecurity Framework** - Security controls

### Code Quality Standards

- **PEP 8** - Python style guide
- **Type Hints** - Full type annotation
- **Docstrings** - Comprehensive documentation
- **Test Coverage** - 80%+ coverage

### Operational Standards

- **Semantic Versioning** - Version management
- **Keep a Changelog** - Change documentation
- **Conventional Commits** - Commit message format
- **Security Advisories** - Vulnerability disclosure

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-21  
**Maintained By:** STARS CLI Team
