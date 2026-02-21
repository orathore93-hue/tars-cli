"""Incident management for SREs"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class IncidentManager:
    """Manage incidents with timeline and context"""
    
    def __init__(self):
        self.incidents_dir = Path.home() / ".stars" / "incidents"
        self.incidents_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.current_incident_file = self.incidents_dir / "current.json"
    
    def start_incident(self, title: str, severity: str = "medium") -> str:
        """Start tracking a new incident"""
        incident_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        
        incident = {
            "id": incident_id,
            "title": title,
            "severity": severity,
            "started_at": datetime.utcnow().isoformat(),
            "timeline": [],
            "status": "active",
            "affected_resources": [],
            "actions_taken": []
        }
        
        # Save current incident
        with open(self.current_incident_file, 'w') as f:
            json.dump(incident, f, indent=2)
        os.chmod(self.current_incident_file, 0o600)
        
        # Also save to incidents history
        incident_file = self.incidents_dir / f"{incident_id}.json"
        with open(incident_file, 'w') as f:
            json.dump(incident, f, indent=2)
        os.chmod(incident_file, 0o600)
        
        console.print(f"\n[bold green]✓ Incident {incident_id} started[/bold green]")
        console.print(f"[yellow]Title:[/yellow] {title}")
        console.print(f"[yellow]Severity:[/yellow] {severity}")
        console.print(f"\n[dim]Log actions with: stars incident log <message>[/dim]\n")
        
        return incident_id
    
    def log_action(self, message: str, resource: Optional[str] = None):
        """Log an action during incident"""
        if not self.current_incident_file.exists():
            console.print("[red]No active incident. Start one with: stars incident start[/red]")
            return
        
        with open(self.current_incident_file, 'r') as f:
            incident = json.load(f)
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "resource": resource
        }
        
        incident["timeline"].append(entry)
        incident["actions_taken"].append(message)
        
        if resource:
            if resource not in incident["affected_resources"]:
                incident["affected_resources"].append(resource)
        
        # Save updated incident
        with open(self.current_incident_file, 'w') as f:
            json.dump(incident, f, indent=2)
        os.chmod(self.current_incident_file, 0o600)
        
        incident_file = self.incidents_dir / f"{incident['id']}.json"
        with open(incident_file, 'w') as f:
            json.dump(incident, f, indent=2)
        os.chmod(incident_file, 0o600)
        
        console.print(f"[green]✓[/green] Logged: {message}")
    
    def close_incident(self, resolution: str):
        """Close current incident"""
        if not self.current_incident_file.exists():
            console.print("[red]No active incident[/red]")
            return
        
        with open(self.current_incident_file, 'r') as f:
            incident = json.load(f)
        
        incident["status"] = "resolved"
        incident["resolved_at"] = datetime.utcnow().isoformat()
        incident["resolution"] = resolution
        
        # Calculate duration
        started = datetime.fromisoformat(incident["started_at"])
        resolved = datetime.fromisoformat(incident["resolved_at"])
        duration = resolved - started
        incident["duration_minutes"] = int(duration.total_seconds() / 60)
        
        # Save final state
        incident_file = self.incidents_dir / f"{incident['id']}.json"
        with open(incident_file, 'w') as f:
            json.dump(incident, f, indent=2)
        os.chmod(incident_file, 0o600)
        
        # Remove current incident marker
        self.current_incident_file.unlink()
        
        # Display summary
        self._display_incident_summary(incident)
    
    def _display_incident_summary(self, incident: Dict):
        """Display incident summary"""
        console.print("\n[bold green]✓ Incident Resolved[/bold green]\n")
        
        summary = f"""[bold]Incident ID:[/bold] {incident['id']}
[bold]Title:[/bold] {incident['title']}
[bold]Severity:[/bold] {incident['severity']}
[bold]Duration:[/bold] {incident['duration_minutes']} minutes
[bold]Actions Taken:[/bold] {len(incident['actions_taken'])}
[bold]Affected Resources:[/bold] {len(incident['affected_resources'])}

[bold yellow]Resolution:[/bold yellow]
{incident['resolution']}
"""
        
        console.print(Panel(summary, border_style="green", title="Incident Summary"))
        
        # Timeline
        if incident['timeline']:
            console.print("\n[bold]Timeline:[/bold]")
            table = Table(show_header=True)
            table.add_column("Time", style="cyan")
            table.add_column("Action", style="white")
            table.add_column("Resource", style="yellow")
            
            for entry in incident['timeline']:
                time = datetime.fromisoformat(entry['timestamp']).strftime("%H:%M:%S")
                table.add_row(time, entry['message'], entry.get('resource', '-'))
            
            console.print(table)
        
        console.print(f"\n[dim]Full report saved: ~/.stars/incidents/{incident['id']}.json[/dim]\n")
    
    def get_current_incident(self) -> Optional[Dict]:
        """Get current active incident"""
        if self.current_incident_file.exists():
            with open(self.current_incident_file, 'r') as f:
                return json.load(f)
        return None
    
    def list_incidents(self, limit: int = 10):
        """List recent incidents"""
        incident_files = sorted(self.incidents_dir.glob("*.json"), reverse=True)
        incident_files = [f for f in incident_files if f.name != "current.json"][:limit]
        
        if not incident_files:
            console.print("[yellow]No incidents found[/yellow]")
            return
        
        table = Table(title="Recent Incidents", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Severity", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Duration", style="blue")
        
        for file in incident_files:
            with open(file, 'r') as f:
                incident = json.load(f)
            
            status_color = "green" if incident['status'] == "resolved" else "red"
            duration = incident.get('duration_minutes', '?')
            
            table.add_row(
                incident['id'],
                incident['title'][:40],
                incident['severity'],
                f"[{status_color}]{incident['status']}[/{status_color}]",
                f"{duration}m"
            )
        
        console.print(table)
