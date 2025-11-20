# Reflow Plugin

Intended to assist with research on a cadence.

## Installation

```bash
/plugin install https://github.com/yourname/reflow
```

## Structure

Plugin files are organized in `src/reflow/`:

- **src/reflow/commands/** - Custom slash commands
- **src/reflow/agents/** - Specialized agents
- **src/reflow/skills/** - Agent Skills
- **src/reflow/hooks/** - Event handlers
- **src/reflow/.claude-plugin/plugin.json** - Plugin manifest

## Development

Add your commands, agents, skills, and hooks to their respective directories.

## Documentation

See individual directories for specific component documentation.

https://code.claude.com/docs/en/plugins-reference#plugin-directory-structure
